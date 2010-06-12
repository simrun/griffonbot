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

DEBUG  = (0, "Debug ")
INFO   = (1, "Info  ")
NOTICE = (2, "Notice")
ERROR  = (3, "Error ")

class Log:
  def __init__(self, config):
    self.config = config
    self.file = open(self.config.filename, "a", 1)

  def msg(self, level, str):
    str = str.strip()

    header = "%s %s" % (time.strftime("%H:%M:%S"), level[1])

    for line in str.splitlines():
      message = "%s %s\n" % (header, line)

      if level[0] >= self.config.file[0]:
        self.file.write(message)

      if level[0] >= self.config.stderr[0]:
        sys.stderr.write(message)

  # Shortcuts
  def debug(self, str):
    self.msg(DEBUG, str)

  def info(self, str):
    self.msg(INFO, str)

  def notice(self, str):
    self.msg(NOTICE, str)

  def error(self, str):
    self.msg(ERROR, str)
