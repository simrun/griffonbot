# Copyright (c) Daniel Richman 2010

import sys

from stream import Stream
from bot import IRCBot
import config

def debug(s):
  sys.stderr.write("%s\n" % s)

def main():
  debug("Main: Setting up...")
  bot = IRCBot(config.irc, debug)
  stream = Stream(config.twitter, bot.message, debug)

  debug("Starting...")
  bot.start()
  stream.start()

main()
