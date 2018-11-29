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

import json
import os
import csv

# === Instagram Profile ===

def profile_template():
    # returns template of profile object

    return {
        'user': {
            'username': '',
            'user_id': '',
            'media': 0,
            'follows': 0,
            'followers': 0
        },
        'followers': [],
        'follows': []
    }

class InstaProfile:
    # This object will contain the followers and followed users that
    # InstaBot picks up along the way in order to operate efficiently

    def __init__(self, path='cache/', params=''):

        self.prof_path = path + params['username'] + '.json'
        self.unf_list_path = path + 'unfollowlist.csv'
        self.params = params
        self.import_unfollow_list()

    def import_unfollow_list(self):
        # imports the master unfollow list

        self.master_unfollow_list = [
            line for line in open(
                self.unf_list_path, 'r')]

    def save_unfollow_list(self):
        # saves the master unfollow list

        with open(self.unf_list_path, 'wb') as outfile:
            w = csv.writer(outfile)
            w.writerows([[user] for user in self.master_unfollow_list])

    def import_profile(self, user):
        # imports the profile file with all the data

        if os.path.isfile(self.prof_path):
            with open(self.prof_path) as data_file:
                self.profile = json.load(data_file)

        else:
            self.profile = profile_template()
            self.populate_profile(user)

    def save_profile(self):
        # saves the profile to file

        with open(self.prof_path, 'wb') as outfile:
            json.dump(self.profile, outfile)

    def populate_profile(self, user):
        # builds the profile if it's the first time

        self.profile['user'] = {
            'username': self.params['username'],
            'user_id': user['data']['user_id'],
            'media': user['data']['media'],
            'follows': user['data']['follows'],
            'followers': user['data']['followers']
        }

    def add_follower(self, data):
        # adds user to the follower list

        self.profile['followers'].append(data)
        self.save_profile()

    def add_follow(self, data):
        # adds user to the follows list

        self.profile['follows'].append(data)
        self.save_profile()

    def remove_follow(self, user_id):
        # removes follow from follows list

        for i, node in enumerate(self.profile['follows']):
            if node['user_id'] == user_id:
                del self.profile['follows'][i]
                break

    def update_user(self, data, op):
        # updates current follower data

        for i, node in enumerate(self.profile[op]):
            if node['user_id'] == data['user_id']:
                self.profile[op][i] = data
                break

        self.save_profile()
