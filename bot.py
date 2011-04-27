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
import time
import traceback

from lib import irclib
from kickmsg import get_kick_message

def action_message(act):
  return "\x01ACTION %s \x01" % act

class IRCBot:
  def __init__(self, config, log):
    log.debug("IRC: Setting up...")

    self.irc = irclib.IRC()
    self.irc.add_global_handler("welcome", self.on_connect)
    self.irc.add_global_handler("join", self.on_join)
    self.irc.add_global_handler("kick", self.on_kick)
    self.irc.add_global_handler("disconnect", self.on_disconnect)
    self.irc.add_global_handler("part", self.on_part)
    self.irc.add_global_handler("pong", self.on_pong)

    self.config = config
    self.log = log

    self.reconnects = 0
    self.reconnecting = False
    self.ping_reply = True
    self.messaged = False

    self.channels = []

  def main(self):
    self.log.debug("IRC: Running!")

    self.connect()

    self.log.debug("IRC: Queuing first ping-pong.")
    self.irc.execute_delayed(60, self.ping_pong)

    while True:
      self.irc.process_once(1)

  def message(self, msg, channel):
    if self.messaged:
      self.log.debug("IRC: throttled message -> %s '%s'" % (channel, msg))
      return

    self.log.info("IRC: message -> %s '%s'" % (channel, msg))
    self.connection.privmsg(channel, msg)
    self.messaged = True
    self.irc.execute_delayed(self.config.min_period, self.msgrdy)
 
  def msgrdy(self):
    self.log.debug("IRC: time's up! Message ready.")
    self.messaged = False

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
    self.connection.join(self.config.channel)

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
    self._rm_channel(event.target())

  def _rm_channel(self, channel):
    try:
      self.channels.remove(channel)
    except:
      self.log.notice("IRC: Suppressed error: couldn't remove %s from " \
                 "self.channels" % channel)
      self.log.info("".join(traceback.format_exc()))

  def on_kick(self, connection, event):
    if connection != self.connection:
      self.log.info("IRC: Incorrect connection in on_kick")
      return

    kicker = event.source().split("!")[0]
    victim = event.arguments()[0]
    channel = event.target()

    if victim == self.config.nick:
      self.log.info("IRC: Kicked from %s by %s" % (channel, kicker))
      self._rm_channel(event.target())
      return

    self.log.info("IRC: %s kicked from %s" % (victim, channel))
    self.message(get_kick_message(kicker, victim, channel), channel)

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
