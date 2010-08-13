# Copyright 2010 Daniel Richman and Simrun Basuita

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from log import DEBUG, INFO, NOTICE, ERROR

class log:
  filename = "griffonbot.log"
  file     = DEBUG
  stderr   = INFO

class twitter:
  enable = True
  username = "griffonbot"
  password = ""
  keywords = [ "#arhab", "#ukhas", "#cusf" ]
  max_reconnect_wait = 60

class mail:
  enable = True
  imap_server = "imap.gmail.com"
  username = "griffonbot@gmail.com"
  password = ""
  max_reconnect_wait = 60

  match = classmethod(lambda s,e: e['List-ID'] == "<ukhas.googlegroups.com>")
  match_description = "emails sent to ukhas@googlegroups.com"

class irc:
  server   = "irc.freenode.net"
  port     = 6667
  nick     = "griffonbot"
  password = ""
  user     = "griffonbot"
  realname = "GriffonBot [http://github.com/ssb/griffonbot]"
  channels = [ "#griffonbot" ]
  max_reconnect_wait = 60

  class flood:
    wait = 1
    queue_max = 20
    queue_drop = 18

  @classmethod
  def join_msg(self, con):
    con.action("is %s" % irc.realname)

    if twitter.enable:
      con.action("is following: %s" % " ".join(twitter.keywords))

    if mail.enable:
      con.action("is tracking %s" % mail.match_description)

class stdin:
  enable = True
