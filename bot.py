# Copyright (c) Daniel Richman 2010

import irclib

class IRCBot:
  def __init__(self, config, msgqueue, debug):
    debug("IRC: Setting up...")

    self.irc = irclib.IRC();
    self.config = config
    self.msgqueue = msgqueue
    self.debug = debug

    self.channels = dict()

  def start(self):
    Thread(target=self.main).start()
    Thread(target=self.process).start()

  def main():
    self.debug("IRC: Running")

    self.connect()
    self.irc.process_forever()

  def process():
    while True:
      message = self.msgqueue.get()

      for channel in self.config.channels:
        connection.privmsg(channel, message)

  def connect():
    self.debug("IRC: Connecting")

    s = self.config
    connection = irc.server()
    connection.connect(s.server, s.port, s.nick, s.password, s.user, s.realname)

    connection.add_global_handler("welcome", self.on_connect)
    connection.add_global_handler("join", self.on_join)
    connection.add_global_handler("disconncet", self.on_disconnect)

    for event in [ "kick", "part" ]:
      connection.add_global_handler(e, self.on_part);

  def on_connect(conection, event):
    self.debug("IRC: Connected; joining...")
    for channel in channels:
      conection.join(channel)
 
  def on_join(connection, event):
    self.debug("IRC: Joined channel %s" % event.target())
    self.channels[event.target()] = True

  def on_disconnect(connection, event):
    self.debug("IRC: Disconnected. Reconnecting...")
    self.channels.clear()
    self.connect()

  def on_part(connection, event):
    self.debug("IRC: Left %s" % event.target())
    try:
      del self.channels[event.target()]
    except:
      debug("IRC: Shouldn't have had error removing left channel from dict, but ignored")


