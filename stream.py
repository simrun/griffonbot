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
import re
from threading import Thread
import unicodedata

import tweetstream

crush_whitespace_re = re.compile(r"\s+")
def crush_whitespace(s):
  return crush_whitespace_re.sub(" ", s)

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
    with tweetstream.TrackStream(s.username, s.password, s.keywords) as stream:
      for tweet in stream:
        screenname = tweet["user"]["screen_name"]
        content =  "@%s: %s" % (screenname, tweet["text"])
        url = "http://twitter.com/%s/status/%d" % (screenname, tweet["id"])
        formatted = "%s (%s)" % (content, url)

        # Obliterate Unicode
        # formatted_uni = unicode(formatted) # formatted.decode('utf-8')
        # formatted_uni_n = unicodedata.normalize('NFKD', formatted_uni)
        # formatted_safe = formatted_uni_n.encode('ascii', 'ignore')

        # Remove tabs and newlines, encode nicely.
        formatted_safe = crush_whitespace(unicode(formatted)).encode('utf-8')

        self.debug("Stream: Pushing Tweet %s" % formatted_safe)
        self.callback(formatted_safe)

