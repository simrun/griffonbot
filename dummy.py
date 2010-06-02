# Copyright (c) Daniel Richman 2010

from threading import Thread
import sys

class Stream:
  def __init__(self, config, callback, debug):
    debug("Dummy Stream: Setting up...")

    self.config = config
    self.callback = callback
    self.debug = debug

  def start(self):
    self.debug("Dummy Stream: Starting...")
    Thread(target=self.main).start()

  def main(self):
    self.debug("Dummy Stream: Running!")

    while True:
      line = sys.stdin.readline()
      self.debug("Dummy Stream: Got line %s" % line)
      self.callback(line)
