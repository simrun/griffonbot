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
import threading

class Mail:
  def __init__(self, config, callback, debug):
    debug("Mail: Setting up...")

    self.config = config
    self.callback = callback
    self.debug = debug

    self.event = threading.Event()

    self.reconnects = 0

  def start(self):
    self.debug("Mail: Starting...")
    DaemonThread(target=self.main).start()

  def main(self):
    self.debug("Mail: Running!")

    while True:
      try:
        self.imap.setupandlogink()

        while True:
          self.event.clear()
          self.imap.idle(callback=self.event.set)
          self.event.wait()

          for email in self.imap.fetch_email():
            if self.config.match(email):
              make_a_message
              self.callback(message)
            else if self.config.forward:
              forward_message_to(self.config.forward)
      except SomeSortOfImapError:
        exponential_waiting_from_stream.py. Also add a self.reconnects reset somewhere.
