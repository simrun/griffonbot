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
from daemon import DaemonThread

class Stdin:
  def __init__(self, config, callback, log):
    log.debug("Stdin: Setting up...")

    self.config = config
    self.callback = callback
    self.log = log

  def start(self):
    self.log.debug("Stdin: Starting...")
    DaemonThread(self.log, target=self.main).start()

  def main(self):
    self.log.debug("Stdin: Running!")

    while 1:
      line = sys.stdin.readline()
 
      if not line:
        self.log.error("Stdin: sys.stdin.readline() returned false")

      line = line.strip()

      if len(line) > 0: 
        self.callback(line)
