# Copyright 2010 Daniel Richman and Simrun Basuita

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

class twitter:
  username = "griffonbot"
  password = ""
  keywords = [ "#griffonbot" ]
  max_reconnect_wait = 60

class irc:
  server   = "irc.freenode.net"
  port     = 6667
  nick     = "griffonbot"
  password = ""
  user     = "griffonbot"
  realname = "GriffonBot [http://github.com/ssb/griffonbot]"
  channels = [ "##banter" ]
  max_reconnect_wait = 60

  class flood:
    wait = 3
    queue_max = 20
    queue_drop = 18

  @classmethod
  def join_msg(self, message, action):
    action("is %s" % irc.realname)
    action("is following: %s" % " ".join(twitter.keywords))
