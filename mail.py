#!/usr/bin/env python

# Copyright 2010 Daniel Richman and Simrun Basuita

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from daemon import DaemonThread

class Mail:
  def __init__(self, config, callback, debug):
    debug("Mail: Setting up...")
    self.config = config
    self.callback = callback
    self.debug = debug

  def start(self):
    self.debug("Mail: Starting...")
    DaemonThread(target=self.main).start()

  def main(self):
    self.debug("Mail: Running!")
