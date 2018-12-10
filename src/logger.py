#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ___        InstaBot V 1.2.0 by nickpettican           ___
# ___        Automate your Instagram activity           ___

# ___        Copyright 2017 Nicolas Pettican            ___

# ___   This software is licensed under the Apache 2    ___
# ___   license. You may not use this file except in    ___
# ___   compliance with the License.                    ___

# ___                   DISCLAIMER                      ___

# ___ InstaBot was created for educational purposes and ___
# ___ the end-user assumes sole responsibility of any   ___
# ___ consequences of it's misuse. Please be advised of ___
# ___ Instagram's monitoring, 1000 likes a day is the   ___
# ___ maximum you will get or you risk a temporary ban. ___
# ___ Choose your tags wisely or you may risk liking    ___
# ___ and commenting on undesirable media or spam.      ___

import datetime
from csv import writer
from os import makedirs, path


class Logger:

    def __init__(self, header, backupUnfollows, bucketUnfollow):
        # initialise the logger variables

        self.path = 'cache/log/'
        self.log_temp = ''
        self.new_line = True
        self.backupUnfollows = backupUnfollows
        self.bucketUnfollow = bucketUnfollow
        self.today = datetime.datetime.today().strftime('%d-%m-%Y')

        if not path.isdir(self.path):
            makedirs(self.path)

        self.init_log_name()

        print header

    def init_log_name(self):
        # change log file name

        self.today = datetime.datetime.today().strftime('%d-%m-%Y')
        self.log_main = []
        self.log_file = self.path + 'activity_log_' + self.today + '.txt'

    def log(self, string):
        # write to log file

        try:
            if self.today != datetime.datetime.today().strftime('%d-%m-%Y'):
                self.init_log_name()

            self.backup()

            if string.endswith('\,'):
                log = string.replace('\,', '')

                if self.new_line or log.startswith('\n'):
                    if log.startswith('\n'):
                        log = log.replace('\n', '')
                        print '\n',
                    log = datetime.datetime.today().strftime(
                        '[ %Y-%m-%d %H:%m:%S ] ') + log
                print log,

                self.new_line = False
                if self.log_temp:
                    try:
                        self.log_temp += log
                    except BaseException:
                        pass
                else:
                    self.log_temp = log
                return

            log = string
            print log
            if self.log_temp:
                string = self.log_temp + string
                self.log_temp = ''
                self.new_line = True

            self.log_main.append([string.strip()])

        except Exception as e:
            print 'Error while logging: %s' % (e)

    def backup(self):
        # backs up the log

        self.backupUnfollows()

        try:
            with open(self.log_file, 'w') as log:
                for line in self.log_main:
                    log.writelines(line if isinstance(line, list) else [line])
                    log.write('\n')

        except Exception as e:
            print 'Error backing up: %s' % (e)

        try:
            with open('cache/followlist.csv', 'wb') as backup:
                w = writer(backup)
                w.writerows(self.bucketUnfollow)
        except Exception as e:
            print 'Error while saving backup follow list: %s' % (e)
