# Copyright (c) Daniel Richman 2010

from threading import Thread
import sys

class Stream:
  def __init__(self, callback):
    self.callback = callback

  def start(self):
    Thread(target=self.main).start()

  def main(self):
    with tweetstream.TrackStream(username, password, words) as stream:
      for tweet in stream:
        screenname = tweet["user"]["screen_name"]
        content =  "@%s: %s" % (screenname, tweet["text"])
        url = "http://twitter.com/%s/status/%d" % (screenname, tweet["id"])
	formatted = "%s (%s)" % (content, url)
        
	self.callback(formatted)

    while True:
      self.callback(line)
