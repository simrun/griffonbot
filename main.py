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
import socket

from log import Log
from bot import IRCBot
import config

def main():
  # If all else fails,
  socket.setdefaulttimeout(60)

  sys.stderr.write("Kickbot starting up...\n")
  log = Log(config.log)

  log.debug("Main: Setting up...")
  bot = IRCBot(config.irc, log)

  log.info("Main: Starting...")
  bot.main()

if __name__ == "__main__":
  main()
