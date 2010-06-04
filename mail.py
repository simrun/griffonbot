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
import email

import imaplib2

import time

class Mail:
  def __init__(self, config, callback, debug):
    debug("Mail: Setting up...")

    self.config = config
    self.callback = callback
    self.debug = debug

    self.reconnects = 0

  def start(self):
    self.debug("Mail: Starting...")
    DaemonThread(target=self.main).start()

  def announce_mail(self, mail):
    message = "Email from %s: \"%s\"" % (mail['From'], mail['Subject'])
    self.callback(message)

  def process_mail(self, response):
    self.debug("Mail: Processing email...")

    try:
      # Unpack the monstrosity that was given to us...
      ((type, data), cb_arg, error) = response
      data = str(data[0][1])
    except:
      self.debug("Mail: Unpack failed.")
      return

    #XXX First message is fine. Why does this happen?
    # (Pdb) print mail
    # (None, None, (<class 'imaplib2.error'>, 
    # "program error: <type 'exceptions.TypeError'> - 
    # 'bool' object is not callable"))

    # Only parse headers
    #pdb.set_trace()
    mail = email.message_from_string(data, True)
    time.sleep(0.1)
    #pdb.set_trace()
    return

    if self.config.match(mail):
      self.debug("Mail: Email matched.")
      self.announce_mail(mail)
    else:
      self.debug("Mail: Email didn't match.")

      if self.config.forward_nonmatching:
        #TODO Forward it
        pass

    #TODO Delete it

  def main(self):
    self.debug("Mail: Running!")

    while True:
      self.debug("Mail: Connecting to IMAP server...")
      self.imap = imaplib2.IMAP4_SSL(self.config.imap_server)

      self.debug("Mail: Logging in...")
      self.imap.login(self.config.username, self.config.password)

      self.debug("Mail: Success")
      self.reconnects = 0

      self.debug("Mail: Selecting INBOX")
      self.imap.examine("INBOX")

      while True:
        self.debug("Mail: Fetching emails...")
        type, emails = self.imap.search(None, "ALL")

        for num in emails[0].split(" "):
          self.debug("Mail: Retrieving message %s..." % num)
          self.imap.fetch(num, "(RFC822)", callback=self.process_mail, 
                                           cb_arg=num)

        self.debug("Mail: Now calling imap.idle() ... ")
        self.imap.idle()

        self.debug("Mail: Wait over: looping - searching for messages...")

      #TODO Wrap this stuff in a try: and implement reconnection
