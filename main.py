# Copyright (c) Daniel Richman 2010

from dummy import Stream
from bot import IRCBot
import config

def debug(s):
  print s

def main():
  queue = Queue()

  debug("Main: Setting up")
  bot = IRCBot(config, queue, debug)
  stream = Stream(config, queue, debug)

  debug("Starting...")
  bot.start()
  stream.start()

main()
