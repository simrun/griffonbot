# Copyright 2010 Daniel Richman and Simrun Basuita

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

class irc:
  server   = "irc.freenode.net"
  port     = 6667
  nick     = "griffonbot"
  password = ""
  user     = "griffonbot"
  realname = "Griffon Bot v0.1 http://github.com/ssb/griffonbot"
  channels = [ "##banter" ]

  class flood:
    wait = 1
    queue_max = 10

  @classmethod
  def join_msg(self, action_callback):
    action_callback("is %s" % irc.realname)
    action_callback("is following: %s" % " ".join(twitter.keywords))

class twitter:
  username = "griffonbot"
  password = ""
  keywords = [ "#ukhas", "#hab", "bieber" ]
