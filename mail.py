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
import traceback
import socket

import imaplib2

import time

class SrsError(Exception):
  pass

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

  def process_mail(self, response):
    self.debug("Mail: Processing email...")

    try:
      # Unpack the monstrosity that was given to us...
      data = str(response[1][0][1])
    except:
      self.debug("Mail: Unpack failed.")
      return

    mail = email.message_from_string(data)

    message = "Email from %s: \"%s\"" % (mail['From'], mail['Subject'])
    self.debug("Mail: Parsed email: %s" % message)

    if self.config.match(mail):
      self.debug("Mail: Email matched.")
      self.callback(message)
    else:
      self.debug("Mail: Email didn't match.")

  def main(self):
    self.debug("Mail: Running!")

    while True:
      try:
        self.debug("Mail: Connecting to IMAP server...")
        self.imap = imaplib2.IMAP4_SSL(self.config.imap_server)

        self.debug("Mail: Logging in...")

        try:
          self.imap.login(self.config.username, self.config.password)
        except imaplib2.IMAP4.abort:
          # Don't catch errors for this stage >_<
          self.debug("".join(traceback.format_exc()))
          raise SrsError()

        self.debug("Mail: Success")
        self.reconnects = 0

        self.debug("Mail: Selecting INBOX")
        self.imap.select("INBOX")

        waited = False
        self.reconnects = 0

        while True:
          self.debug("Mail: Fetching emails...")
          type, emails = self.imap.search(None, "ALL")

          for num in emails[0].split(" "):
            if num:
              self.debug("Mail: Retrieving message %s..." % num)
              response = self.imap.fetch(num, "(RFC822)")

              if waited:
                # Don't dump our entire INBOX into callback().
                # We only post messages after having imap.idle()d once
                self.process_mail(response)

              self.debug("Mail: Flagging %s for deletion..." % num)
              self.imap.store(num, '+FLAGS', '\\Deleted')

          self.debug("Mail: Now calling imap.expunge()...")
          self.imap.expunge()

          self.debug("Mail: Now calling imap.idle() ... ")
          self.imap.idle()

          self.debug("Mail: Wait finished; now looping - searching for msgs...")
          waited = True

      except SrsError:
        raise

      except (imaplib2.IMAP4.abort, socket.error):
        self.debug("Mail: Error caught:")
        self.debug("".join(traceback.format_exc()))

        self.reconnects += 1
        self.debug("Mail: Reconnects is %i" % self.reconnects)

        proposed_wait = 2 ** self.reconnects
        if proposed_wait < self.config.max_reconnect_wait:
          self.debug("Mail: Sleeping for %i seconds" % proposed_wait)
          time.sleep(proposed_wait)
        else:
          self.debug("Mail: Sleeping for %i seconds (max)" \
	             % self.config.max_reconnect_wait)
          time.sleep(self.config.max_reconnect_wait)
