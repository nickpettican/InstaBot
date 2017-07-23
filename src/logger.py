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

import arrow
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
        self.today = arrow.now().format('DD_MM_YYYY')
        
        if not path.isdir(self.path):
            makedirs(self.path)

        self.init_log_name()

        print header

    def init_log_name(self):
        # change log file name

        self.today = arrow.now().format('DD_MM_YYYY')
        self.log_main = []
        self.log_file = self.path + 'activity_log_' + self.today + '.csv'

    def log(self, string):
        # write to log file

        try:
            if self.today != arrow.now().format('DD_MM_YYYY'):
                self.init_log_name()

            self.backup()

            if string.endswith('\,'):
                log = string.replace('\,', '')
                
                if self.new_line or log.startswith('\n'):
                    if log.startswith('\n'):
                        log = log.replace('\n', '')
                        print '\n',
                    log = arrow.now().format('[ YYYY-MM-DD HH:mm:ss ] ') + log
                print log,

                self.new_line = False
                if self.log_temp:
                    try:
                        self.log_temp += log
                    except:
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
            print 'Error while logging: %s' %(e)

    def backup(self):
        # backs up the log

        self.backupUnfollows()

        try:
            with open(self.log_file, 'wb') as log:
                w = writer(log)
                w.writerows(self.log_main)

        except Exception as e:
            print 'Error backing up: %s' %(e)

        try:
            with open('cache/followlist.csv', 'wb') as backup:
                w = writer(backup)
                w.writerows(self.bucketUnfollow)
        except Exception as e:
            print 'Error while saving backup follow list: %s' %(e)
