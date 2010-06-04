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

import imaplib2
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

  def form_message(self, data):
    body = data[0][1]
    self.callback(body)

  def process_mail(self, email, num, error):
    type, data = email
    form_message(self, data)

  def main(self):
    self.debug("Mail: Running!")

    while True:
      self.imap = imaplib2.IMAP4_SSL(self.config.imap_server)
      self.reconnects = 0

      self.imap.login(self.config.username, self.config.password)
      self.imap.examine("INBOX")

      while True:
        self.event.clear()
        self.imap.idle(callback=self.event.set)
        self.event.wait()

        type, emails = imap.search(None, "ALL")
        for num in emails:
            imap.fetch(num, "(RFC822)", callback=self.process_mail, cb_arg=num)
