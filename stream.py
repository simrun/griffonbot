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
from threading import Thread
import unicodedata
from xml.sax import saxutils

import tweetstream

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

class ReconnectingTrackStream(tweetstream.ReconnectingTweetStream, \
                              tweetstream.TrackStream):
  def __init__(self, debug, username, password, keywords, url="track", \
               max_reconnect_wait=60):
    self.max_reconnect_wait = max_reconnect_wait
    self._reconnects = 0

    self.keywords = keywords

    self.debug = debug

    tweetstream.TweetStream.__init__(self, username, password, url=url)

  def next(self):
    while True:
      try:
        return tweetstream.TweetStream.next(self)
      except tweetstream.ConnectionError, e:
        self._reconnects += 1
        self.debug("Stream: Connection error; self._reconnects = %i" % self._reconnects)

        proposed_wait = 2 * self._reconnects
        if proposed_wait < self.max_reconnect_wait:
          self.debug("Stream: Sleeping for %i seconds" % proposed_wait)
          time.sleep(proposed_wait)
        else:
          self.debug("Stream: Sleeping for %i seconds" % self.max_reconnect_wait)
          time.sleep(self.max_reconnect_wait)

class Stream:
  def __init__(self, config, callback, debug):
    debug("Stream: Setting up...")

    self.config = config
    self.callback = callback
    self.debug = debug

  def start(self):
    self.debug("Stream: Starting...")
    Thread(target=self.main).start()

  def main(self):
    self.debug("Stream: Running!")

    s = self.config
    with ReconnectingTrackStream(self.debug, s.username, s.password, s.keywords) as stream:
      for tweet in stream:
        for f in [ format_tweet, crush_whitespace, fix_entities, fix_unicode ]:
          tweet = f(tweet)

        self.debug("Stream: Pushing Tweet %s" % tweet)
        self.callback(tweet)

