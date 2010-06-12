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
  def __init__(self, config, callback, log):
    log.debug("Mail: Setting up...")

    self.config = config
    self.callback = callback
    self.log = log

    self.reconnects = 0

  def start(self):
    self.log.debug("Mail: Starting...")
    DaemonThread(self.log, target=self.main).start()

  def process_mail(self, response):
    self.log.debug("Mail: Processing email...")

    try:
      # Unpack the monstrosity that was given to us...
      data = str(response[1][0][1])
    except:
      self.log.notice("Mail: Unpack failed.")
      return

    mail = email.message_from_string(data)

    message = "Email from %s: \"%s\"" % (mail['From'], mail['Subject'])
    self.log.debug("Mail: Parsed email: %s" % message)

    if self.config.match(mail):
      self.log.debug("Mail: Email matched.")
      self.callback(message)
    else:
      self.log.notice("Mail: Email didn't match.")

  def main(self):
    self.log.debug("Mail: Running!")

    while True:
      try:
        self.log.debug("Mail: Connecting to IMAP server...")
        self.imap = imaplib2.IMAP4_SSL(self.config.imap_server)

        self.log.debug("Mail: Logging in...")

        try:
          self.imap.login(self.config.username, self.config.password)
        except imaplib2.IMAP4.abort:
          # Don't catch errors for this stage >_<
          self.log.error("".join(traceback.format_exc()))
          raise SrsError()

        self.log.debug("Mail: Success")
        self.reconnects = 0

        self.log.debug("Mail: Selecting INBOX")
        self.imap.select("INBOX")

        waited = False
        self.reconnects = 0

        while True:
          self.log.debug("Mail: Fetching emails...")
          type, emails = self.imap.search(None, "ALL")

          for num in emails[0].split(" "):
            if num:
              self.log.debug("Mail: Retrieving message %s..." % num)
              response = self.imap.fetch(num, "(RFC822)")

              if waited:
                # Don't dump our entire INBOX into callback().
                # We only post messages after having imap.idle()d once
                self.process_mail(response)

              self.log.debug("Mail: Flagging %s for deletion..." % num)
              self.imap.store(num, '+FLAGS', '\\Deleted')

          self.log.debug("Mail: Now calling imap.expunge()...")
          self.imap.expunge()

          self.log.debug("Mail: Now calling imap.idle() ... ")
          self.imap.idle()

          self.log.debug("Mail: Wait finished; now looping - " \
                         "searching for msgs...")
          waited = True

      except SrsError:
        raise

      except (imaplib2.IMAP4.abort, socket.error):
        self.log.notice("Mail: Error caught:")
        self.log.info("".join(traceback.format_exc()))

        self.reconnects += 1
        self.log.info("Mail: Reconnects is %i" % self.reconnects)

        proposed_wait = 2 ** self.reconnects
        if proposed_wait < self.config.max_reconnect_wait:
          self.log.info("Mail: Sleeping for %i seconds" % proposed_wait)
          time.sleep(proposed_wait)
        else:
          self.log.info("Mail: Sleeping for %i seconds (max)" \
	             % self.config.max_reconnect_wait)
          time.sleep(self.config.max_reconnect_wait)
