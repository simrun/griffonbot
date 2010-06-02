# Copyright (c) Daniel Richman 2010

from threading import Thread
import sys

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
    with tweetstream.TrackStream(s.username, s.password, s.words) as stream:
      for tweet in stream:
        screenname = tweet["user"]["screen_name"]
        content =  "@%s: %s" % (screenname, tweet["text"])
        url = "http://twitter.com/%s/status/%d" % (screenname, tweet["id"])
	formatted = "%s (%s)" % (content, url)

        self.debug("Stream: Pushing Tweet %s" % formatted)
	self.callback(formatted)

