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

from src.instabot import InstaBot
from src.instaprofile import InstaProfile
import json


def parse_config(path):
    # parses config file to load parameters

    try:
        raw = [line.strip() for line in open(path, 'r')]
        return json.loads(''.join(raw))
    except BaseException:
        print 'Could not open config file, check parameters.'


def main():
    # main operations

    data = parse_config('config.json')
    profile = InstaProfile(path='cache/', params=data)
    instabot = InstaBot(profile, data=data)
    instabot.main()


if __name__ == '__main__':
    main()
