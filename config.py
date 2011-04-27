# Copyright 2010 Daniel Richman and Simrun Basuita

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from log import DEBUG, INFO

class log:
  filename = "kickbot.log"
  file     = DEBUG
  stderr   = DEBUG

class irc:
  server   = "irc.freenode.net"
  port     = 6667
  nick     = "kickbot"
  password = ""
  user     = "kickbot"
  realname = "kickbot [adapted http://github.com/ssb/griffonbot branch kickbot]"
  channel  = "#kickbot"
  max_reconnect_wait = 60
  min_period = 300
