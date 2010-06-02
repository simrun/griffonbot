# Copyright (c) Daniel Richman 2010

from threading import Thread
import irclib

class IRCBot:
  def __init__(self, config, debug):
    debug("IRC: Setting up...")

    self.irc = irclib.IRC();
    self.config = config
    self.debug = debug

    self.channels = []

  def start(self):
    self.debug("IRC: Starting...")
    Thread(target=self.main).start()

  def main(self):
    self.debug("IRC: Running!")

    self.connect()
    self.irc.process_forever()

  def message(self, msg):
    self.debug("IRC: message() %s" % msg)

    for channel in self.channels:
      self.connection.privmsg(channel, msg)
    
  def connect(self):
    self.debug("IRC: Connecting")

    s = self.config
    self.connection = self.irc.server()
    self.connection.connect(s.server, s.port, s.nick, s.password, s.user, s.realname)

    self.connection.add_global_handler("welcome", self.on_connect)
    self.connection.add_global_handler("join", self.on_join)
    self.connection.add_global_handler("disconncet", self.on_disconnect)

    for event in [ "kick", "part" ]:
      self.connection.add_global_handler(event, self.on_part);

  def on_connect(self, connection, event):
    if connection != self.connection:
      debug("IRC: Incorrect connection in on_connect")
      return

    self.debug("IRC: Connected; joining...")
    for channel in self.config.channels:
      self.connection.join(channel)
 
  def on_join(self, connection, event):
    if connection != self.connection:
      debug("IRC: Incorrect connection in on_join")
      return

    self.debug("IRC: Joined channel %s" % event.target())

    if event.target() in self.channels:
      debug("IRC: Suppressed error: %s is already in self.channels" % event.target())
    else:
      self.channels.append(event.target())

  def on_disconnect(self, connection, event):
    if connection != self.connection:
      debug("IRC: Incorrect connection in on_disconnect")
      return

    self.debug("IRC: Disconnected. Reconnecting...")
    self.channels = []
    self.connect()

  def on_part(self, connection, event):
    if connection != self.connection:
      debug("IRC: Incorrect connection in on_part")
      return

    self.debug("IRC: Left %s" % event.target())
    try:
      self.channels.remove(event.target())
    except:
      debug("IRC: Suppressed error: couldn't remove %s from self.channels" % event.target())

