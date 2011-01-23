# Copyright 2010 Daniel Richman and Simrun Basuita

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import sys
import Queue
from daemon import DaemonThread
import time
import threading
import traceback

import irclib

# Wooo! Monkey patchz!

class NewIRC(irclib.IRC):
  def __init__(self):
    irclib.IRC.__init__(self)
    self.delayed_commands_lock = threading.RLock()
  def process_timeout(self):
    with self.delayed_commands_lock:
      irclib.IRC.process_timeout(self)
  def execute_delayed(self, *args):
    with self.delayed_commands_lock:
      irclib.IRC.execute_delayed(self, *args)

def action_message(act):
  return "\x01ACTION %s \x01" % act

class IRCBot:
  def __init__(self, config, log):
    log.debug("IRC: Setting up...")

    self.irc = NewIRC();
    self.irc.add_global_handler("welcome", self.on_connect)
    self.irc.add_global_handler("join", self.on_join)
    self.irc.add_global_handler("kick", self.on_part)
    self.irc.add_global_handler("disconnect", self.on_disconnect)
    self.irc.add_global_handler("part", self.on_part)
    self.irc.add_global_handler("pong", self.on_pong)

    self.config = config
    self.log = log
    self.queue = Queue.Queue()

    self.reconnects = 0
    self.reconnecting = False
    self.ping_reply = True

    self.channels = []

  def start(self):
    self.log.debug("IRC: Starting...")
    DaemonThread(self.log, target=self.main).start()
    DaemonThread(self.log, target=self.process_queue).start()

  def main(self):
    self.log.debug("IRC: Running!")

    self.connect()

    self.log.debug("IRC: Queuing first ping-pong.")
    self.irc.execute_delayed(60, self.ping_pong)

    while True:
      self.irc.process_once(1)

  def queue_message(self, msg):
    self.log.debug("IRC: queue.put() %s" % msg)
    self.queue.put(msg)

  def process_queue(self):
    self.log.debug("IRC: Running (process_queue)!")

    while True:
      self.regulate_queue()

      self.log.debug("IRC: waiting on queue.get...")
      msg = self.queue.get()
      self.log.debug("IRC: queue.get() got %s" % msg)

      self.message_all(msg)

  def regulate_queue(self):
    self.log.debug("IRC: Examining Queue...")

    size = self.queue.qsize()
    self.log.debug("IRC: Queue size = %i, queue_max = %i" \
               % (size, self.config.flood.queue_max))

    if size > self.config.flood.queue_max:
      items = 0

      self.log.debug("IRC: Queue - attempting to drop %i items" \
                 % self.config.flood.queue_drop)

      try:
        for i in range(0, self.config.flood.queue_drop):
          self.queue.get_nowait()
          items = items + 1
      except Queue.Empty:
        pass
 
      self.log.debug("IRC: Dropped %i of %i queued messages (flood)" \
                 % (items, size))
      self.message_all(action_message("dropped %i of %i queued messages "\
                                      "in the name of flood-control" % \
                                      (items, size)))

  def message_all(self, msg):
    self.irc.execute_delayed(0, self.do_message_all, (msg, ))

  def do_message_all(self, msg):
    self.log.debug("IRC: message_all() %s" % msg)

    for channel in self.channels:
      self.message(msg, channel)

  def message(self, msg, channel):
    self.log.info("IRC: message -> %s '%s'" % (channel, msg))
    self.connection.privmsg(channel, msg)

    self.log.debug("IRC: flood.wait...")
    time.sleep(self.config.flood.wait)
 
  def connect(self):
    self.reconnecting = False

    self.log.debug("IRC: Connecting")

    s = self.config
    self.channels = []
    self.connection = self.irc.server()

    try:
      self.connection.connect(s.server, s.port, s.nick, s.password, s.user, \
                              s.realname)
    except irclib.ServerConnectionError:
      self.log.notice("IRC: Error whilst connecting...")
      self.log.info("".join(traceback.format_exc()))
      self.reconnect()

  def on_connect(self, connection, event):
    if connection != self.connection:
      self.log.info("IRC: Incorrect connection in on_connect")
      return

    self.log.debug("IRC: Connected; joining...")
    for channel in self.config.channels:
      self.connection.join(channel)

    self.reconnects = 0
 
  def on_join(self, connection, event):
    if connection != self.connection:
      self.log.info("IRC: Incorrect connection in on_join")
      return

    if event.source().split("!")[0] != self.config.nick:
      return

    self.log.debug("IRC: Joined channel %s" % event.target())

    if event.target() in self.channels:
      self.log.debug("IRC: Suppressed error: %s is already in self.channels" \
                 % event.target())
    else:
      self.config.join_msg(JoinMessageConnection(self, event.target()))
      self.channels.append(event.target())

  def on_disconnect(self, connection, event):
    if connection != self.connection:
      self.log.info("IRC: Incorrect connection in on_disconnect")
      return

    self.reconnect()

  def reconnect(self):
    if self.reconnecting:
      self.log.debug("IRC: Avoiding recursion in reconnect()")
      return

    self.reconnecting = True

    self.log.notice("IRC: reconnect(): disconnecting all")
    try:
      self.irc.disconnect_all()
    except:
      self.log.notice("IRC: Suppressed error while disconnecting all")
      self.log.info("".join(traceback.format_exc()))

    self.channels = []
    self.reconnects += 1
    self.log.notice("IRC: Disconnected. self.reconnects = %i" % \
                    self.reconnects)

    proposed_wait = 2 ** self.reconnects
    if proposed_wait > self.config.max_reconnect_wait:
      self.log.info("IRC: Capping reconnect sleep at max")
      proposed_wait = self.config.max_reconnect_wait

    self.log.info("IRC: Queuing reconnection in %s seconds" % proposed_wait)
    self.irc.execute_delayed(0, self.connect)

  def on_part(self, connection, event):
    if connection != self.connection:
      self.log.info("IRC: Incorrect connection in on_part")
      return

    if event.source().split("!")[0] != self.config.nick:
      return

    self.log.info("IRC: Left %s" % event.target())

    try:
      self.channels.remove(event.target())
    except:
      self.log.notice("IRC: Suppressed error: couldn't remove %s from " \
                 "self.channels" % event.target())
      self.log.info("".join(traceback.format_exc()))

  def on_pong(self, connection, event):
    if connection != self.connection:
      self.log.info("IRC: Incorrect connection in on_pong")
      return

    self.log.debug("IRC: Got pong from server <3")
    self.ping_reply = True

  def ping_pong(self):
    self.log.debug("IRC: Ping-pong!")
    self.irc.execute_delayed(600, self.ping_pong)

    if not self.connection.connected:
      self.log.debug("IRC: Ping-pong: not connected")
      return

    self.log.debug("IRC: Pinging %s" % self.connection.real_server_name)
    self.ping_reply = False
    self.connection.ping(self.connection.real_server_name)
    self.irc.execute_delayed(30, self.check_ping_pong)

  def check_ping_pong(self):
    self.log.debug("IRC: Ping-pong: checking")

    if not self.ping_reply:
      self.ping_reply = True
      self.log.error("IRC: No ping reply, disconnecting")
      self.irc.execute_delayed(0, self.reconnect)

class JoinMessageConnection():
  def __init__(self, bot, channel):
    self.bot = bot
    self.channel = channel

  def action(self, msg):
    self.message(action_message(msg))

  def message(self, msg):
    self.bot.log.debug("IRC: JoinMessageConnection message() %s" % msg)
    self.bot.message(msg, self.channel)

