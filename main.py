#!/usr/bin/env python

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

from log import Log
from stream import Stream
from bot import IRCBot
from daemon import die
from mail import Mail
from stdin import Stdin
import config

def main():
  sys.stderr.write("Griffonbot starting up...\n")
  log = Log(config.log)

  log.debug("Main: Setting up...")
  bot = IRCBot(config.irc, log)

  if config.twitter.enable:
    stream = Stream(config.twitter, bot.queue_message, log)

  if config.mail.enable:
    mail = Mail(config.mail, bot.queue_message, log)

  if config.stdin.enable:
    stdin = Stdin(config.stdin, bot.queue_message, log)

  log.info("Main: Starting...")
  bot.start()

  if config.twitter.enable:
    stream.start()

  if config.mail.enable:
    mail.start()

  if config.stdin.enable:
    stdin.start()

  log.debug("Main: Now waiting...")
  die.wait()

  log.notice("Dead: Exiting...")
  sys.exit(1)

if __name__ == "__main__":
  main()
