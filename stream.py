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
import time
import re
import traceback
from daemon import DaemonThread
import unicodedata
from xml.sax import saxutils

import tweetstream

# Monkey Patch
import socket
socket._fileobject.default_bufsize = 1

crush_whitespace_re = re.compile(r"\s+")
def crush_whitespace(s):
  # remove tabs and newlines
  return crush_whitespace_re.sub(" ", unicode(s))

def fix_entities(s):
  return saxutils.unescape(unicode(s))

def fix_unicode(s):
  return unicode(s).encode('utf-8')

def crush_unicode(s):
  return unicodedata.normalize('NFKD', unicode(s)).encode('ascii', 'ignore')

def format_tweet(tweet):
  screenname = tweet["user"]["screen_name"]
  content =  "@%s: %s" % (screenname, tweet["text"])
  url = "http://twitter.com/%s/status/%d" % (screenname, tweet["id"])
  return "%s [%s]" % (content, url)

class ReconnectingTrackStream(tweetstream.TrackStream):
  def __init__(self, log, username, password, keywords, max_reconnect_wait, \
               url="track"):
    self.max_reconnect_wait = max_reconnect_wait
    self.reconnects = 0

    self.keywords = keywords

    self.log = log

    super(ReconnectingTrackStream, self).__init__(username, password, \
                                                  keywords, url)

  def _init_conn(self):
    super(ReconnectingTrackStream, self)._init_conn()

    # This. Is. Disgusting.
    self._conn.fp._sock.fp._sock.settimeout(60)

  def __iter__(self):
    while True:
      super_iter = super(ReconnectingTrackStream, self).__iter__()

      try:
        data = super_iter.next()
        self.reconnects = 0
        yield data
      except (tweetstream.ConnectionError, StopIteration):
        self.reconnects += 1
        self.log.notice("Stream: Connection error; self.reconnects = %i" \
	           % self.reconnects)
        self.log.info("".join(traceback.format_exc()))

        proposed_wait = 2 ** self.reconnects
        if proposed_wait < self.max_reconnect_wait:
          self.log.info("Stream: Sleeping for %i seconds" % proposed_wait)
          time.sleep(proposed_wait)
        else:
          self.log.info("Stream: Sleeping for %i seconds (max)" \
	             % self.max_reconnect_wait)
          time.sleep(self.max_reconnect_wait)

class Stream:
  def __init__(self, config, callback, log):
    log.debug("Stream: Setting up...")

    self.config = config
    self.callback = callback
    self.log = log

  def start(self):
    self.log.debug("Stream: Starting...")
    DaemonThread(self.log, target=self.main).start()

  def main(self):
    self.log.debug("Stream: Running!")

    s = self.config
    with ReconnectingTrackStream(self.log, s.username, s.password, \
                                 s.keywords, s.max_reconnect_wait) as stream:
      for tweet in stream:
        for f in [ format_tweet, crush_whitespace, fix_entities, fix_unicode ]:
          tweet = f(tweet)

        self.log.debug("Stream: Pushing Tweet %s" % tweet)
        self.callback(tweet)

