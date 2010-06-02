# Copyright (c) Daniel Richman 2010

from threading import Thread
import sys

class Stream:
  def __init__(self, config, msgqueue, debug):
    debug("Dummy Stream: Setting up...")

    self.config = config
    self.msgqueue = msgqueue
    self.debug = debug

  def start(self):
    Thread(target=self.main).start()

  def main(self):
    self.debug("Dummy Stream: Running")

    while True:
      line = sys.stdin.readline()
      self.debug("Dummy Stream: Got line %s" % line)
      self.msgqueue.put(line)
