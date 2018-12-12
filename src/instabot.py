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

from datetime import datetime, timedelta
from json import loads as toJSON
from emoji import emojize
from requests import Session
from os import path, makedirs
from time import sleep, time, mktime
from random import random as aleatory, randint, choice
from requests.exceptions import ConnectionError
from operator import itemgetter
import traceback, re

from logger import Logger
from src.miscellaneous import *
from src.instafunctions import *

# === INSTABOT ===

# after doing some web development I kinda liked having the code more packed together
# which is why the code is a bit more minimised now
# also I thought of leaving more comments for my (and your) convenience
# and I also got rid of some "else"s to make it cleaner


class InstaBot:

    def __init__(self, profile, data={
        'username': 'user',
        'password': 'pwd',
        'timezone': 0,
        'friends': 'input/friends.csv',
        'tags': 'input/tags.csv',
        'tags_to_avoid': 'input/tags_to_avoid.csv',
        'like_news_feed': True,
        'likes_in_day': 500,
        'media_max_likes': 50,
        'media_min_likes': 0,
        'follow_in_day': 0,
        'unfollow': True,
        'follow_time_hours': 5,
        'comments_in_day': 0,
        "comments_list": [["Cool", "Sweet", "Awesome", "Great"],
                          ["ðŸ˜„", "ðŸ™Œ", "ðŸ‘", "ðŸ‘Œ", "ðŸ˜Š"],
                          [".", "!", "!!", "!!!"]],
        'bot_start_at': '07:00',
        'bot_stop_at': '23:00'
    }):
        # default values
        self.today = datetime.today().strftime('%d-%m-%Y')
        self.users_checked_today = []
        self.header = '\n\tInstaBot 1.3.0 by nickpettican\
                       \n\tAutomate your Instagram activity\n\
                       \n\tNew features:\
                       \n\t- Added timezone as config parameter\
                       \n\t- Removed arrow as dependency'

        # INITIALISE VARIABLES

        self.params = data
        self.profile = profile
        self.params['total_operations'] = data['likes_in_day'] + \
            (data['follow_in_day'] * 2 if data['unfollow'] else data['follow_in_day']) + data['comments_in_day']
        self.params['follow_time'] = data['follow_time_hours'] * 60 * 60
        self.ERROR = {'mkdir': False, 'importing': False, 'cache': False}
        self.op_tmp = {'like': False, 'comment': False}
        self.banned = {'banned': False, '400': 0}
        self.cache = {}
        # define the bucket
        self.bucket = {
            'explore': {
                'follow': set(),
                'unfollow': [],
                'like': set(),
                'unlike': set(),
                'comment': set(),
                'done': {
                    'follow': set(),
                    'unfollow': [],
                    'like': set(),
                    'comment': set()
                },
            },
            'feed': {
                'like': [],
                'media_ids': [],
                'done': []
            },
            'codes': {},
            'user_ids': {}
        }
        # initialise the logger
        self.logger = Logger(
            self.header,
            self.profile.save_unfollow_list,
            self.bucket['explore']['unfollow'])
        # instagram urls
        url = 'https://www.instagram.com/'
        self.insta_urls = {
            'domain': url,
            'user': url + '%s/',
            'login': url + 'accounts/login/ajax/',
            'logout': url + 'accounts/logout/',
            'explore': url + 'explore/tags/%s/',
            'like': url + 'web/likes/%s/like/',
            'unlike': url + 'web/likes/%s/unlike/',
            'comment': url + 'web/comments/%s/add/',
            'follow': url + 'web/friendships/%s/follow/',
            'unfollow': url + 'web/friendships/%s/unfollow/',
            'media': url + 'p/%s/'
        }
        # counters
        self.total_counters = {
            'like_feed': 0,
            'like': 0,
            'follow': 0,
            'unfollow': 0,
            'comment': 0}
        self.day_counters = {
            'all': 0,
            'like_feed': 0,
            'like': 0,
            'follow': 0,
            'unfollow': 0,
            'comment': 0}
        # initialise links and other parameters
        self.mkdir_cache()
        self.sort_enabling()
        self.starting_operations()
        self.catch_up_operations()
        self.init_requests()
        self.init_profile()

    # === INITIAL OPERATIONS ===

    def starting_operations(self):
        # starting operations

        self.user_input()
        self.create_delays()
        self.set_operation_sequence()

    def mkdir_cache(self):
        # creates the cache folder

        if not path.isdir('cache'):
            try:
                makedirs('cache')
            except BaseException:
                self.logger.log('\nERROR creating cache.\n')
                self.ERROR['mkdir'] = True

    def user_input(self):
        # imports friend list so that the bot likes their new media

        try:
            for key in ['friends', 'tags', 'tags_to_avoid']:
                if isinstance(self.params[key], list):
                    self.cache[key] = self.params[key]
                    continue
                self.cache[key] = [
                    line.strip() for line in open(
                        self.params[key], 'r')]
        except BaseException:
            self.ERROR['importing'] = True
            self.logger.log('\nERROR importing cached lists')

        self.cache['unfollow'] = False

        try:
            if path.isfile('cache/followlist.csv'):
                self.cache['unfollow'] = [line.strip().split(',')
                                          for line in open('cache/followlist.csv', 'r')]
        except BaseException:
            self.logger.log('\nERROR importing cached follow list')

    def sort_enabling(self):
        # define which operations are enabled

        self.enabled = {
            'like_feed': False,
            'like': False,
            'follow': False,
            'comment': False,
            'unfollow': False
        }
        try:
            if self.params['like_news_feed']:
                self.enabled['like_feed'] = True

            if self.params['likes_in_day'] > 0:
                self.enabled['like'] = True

            if self.params['follow_in_day'] > 0:
                self.enabled['follow'] = True

            if self.params['comments_in_day'] > 0:
                self.enabled['comment'] = True

            if self.enabled['follow']:
                self.enabled['unfollow'] = self.params['unfollow']
        except BaseException:
            self.logger.log(
                'ERROR while sorting parameters. Check you entered the right formats.')
            exit()

    def init_profile(self):
        # returns data for InstaProfile

        self.profile.import_profile(
            check_user(
                self.browser,
                self.insta_urls['user'],
                self.params['username']))

    # === TIME OPERATIONS ===

    def time_now(self):
        # returns current timestamp

        try:
            return float(time() + (self.params["timezone"] * 60 * 60))
        except BaseException:
            return float(time())

    def create_delays(self):
        # creates the necessary times

        if self.params['bot_start_at'] == self.params['bot_stop_at']:
            self.run_all_day = True
            self.params['time_in_day'] = 24 * 60 * 60
        else:
            self.run_all_day = False
            self.times = self.today_times()
            self.params['time_in_day'] = int(
                self.times['stop_bot'] - self.times['start_bot'])
            self.params['total_operations'] += self.params['time_in_day'] / 60 / 60
        follow_delays = return_random_sequence(
            self.params['follow_in_day'], self.params['time_in_day'])
        self.delays = {
            'like': return_random_sequence(
                self.params['likes_in_day'],
                self.params['time_in_day']),
            'follow': follow_delays,
            'comment': return_random_sequence(
                self.params['comments_in_day'],
                self.params['time_in_day']),
            'unfollow': follow_delays,
            'like_feed': [
                60 *
                60 for i in range(
                    0,
                    int(
                        self.params['time_in_day'] /
                        60 /
                        60))]}

    def today_times(self):
        # creates the times for the day

        if not self.run_all_day:
            if float(self.params['bot_stop_at'].replace(
                    ':', '.')) - float(self.params['bot_start_at'].replace(':', '.')) < 0:
                self.params['bot_stop_at'] = str(
                    float(
                        self.params['bot_stop_at'].replace(
                            ':',
                            '.')) +
                    12).replace(
                    '.',
                    ':')
            time_tomorrow = float(
                mktime(
                    datetime.strptime(
                        (datetime.now() + timedelta(
                            days=1)).strftime("%Y-%m-%d ") + str(
                            self.params['bot_start_at']).replace(
                            '.',
                            ':'),
                        '%Y-%m-%d %H:%M').timetuple())) + (
                self.params["timezone"] * 60 * 60)
            return {
                'start_bot': float(mktime(
                    datetime.strptime(
                        datetime.today().strftime("%Y-%m-%d ") + str(self.params['bot_start_at']).replace('.', ':'), '%Y-%m-%d %H:%M'
                    ).timetuple())) + (self.params["timezone"] * 60 * 60),
                'stop_bot': float(mktime(
                    datetime.strptime(
                        datetime.today().strftime("%Y-%m-%d ") + str(self.params['bot_stop_at']).replace('.', ':'), '%Y-%m-%d %H:%M'
                    ).timetuple())) + (self.params["timezone"] * 60 * 60),
                'tomorrow_start': time_tomorrow
            }

    def set_operation_sequence(self):
        # set the operation times to iterate

        self.next_operation = {
            'like': (
                datetime.now() -
                datetime(
                    1970,
                    1,
                    1)).total_seconds() +
            40,
            'follow': (
                datetime.now() -
                datetime(
                    1970,
                    1,
                    1)).total_seconds() +
            60,
            'comment': (
                        datetime.now() -
                        datetime(
                            1970,
                            1,
                            1)).total_seconds() +
            40,
            'unfollow': (
                                datetime.now() -
                                datetime(
                                    1970,
                                    1,
                                    1)).total_seconds() +
            self.params['follow_time'],
            'like_feed': (
                                        datetime.now() -
                                        datetime(
                                            1970,
                                            1,
                                            1)).total_seconds()}
        if self.bucket['explore']['unfollow']:
            self.next_operation['unfollow'] = min(
                i[1] for i in self.bucket['explore']['unfollow'])
        self.next_check_feed = (
            datetime.now() -
            datetime(
                1970,
                1,
                1)).total_seconds()
        self.max_operation = {
            'like': self.params['likes_in_day'],
            'follow': self.params['follow_in_day'],
            'comment': self.params['comments_in_day'],
            'unfollow': self.params['follow_in_day'],
            'like_feed': self.params['time_in_day'] / 60 / 60,
            'all': self.params['total_operations']
        }

    def reset_day_counters(self):
        # resets the day counters

        unfollow_counter_tmp = self.day_counters['unfollow']
        self.day_counters = {
            'all': 0,
            'like_feed': 0,
            'like': 0,
            'follow': 0,
            'comment': 0,
            'unfollow': unfollow_counter_tmp}

    def catch_up_operations(self):
        # organises the operations for the day

        if not self.run_all_day:
            if self.times['start_bot'] < (
                datetime.now() -
                datetime(
                    1970,
                    1,
                    1)).total_seconds() < self.times['stop_bot']:
                for action, enabled in self.enabled.items():
                    if enabled:
                        tmp_time = self.times['start_bot']
                        while tmp_time < (
                            datetime.now() -
                            datetime(
                                1970,
                                1,
                                1)).total_seconds():
                            if self.day_counters[action] < self.max_operation[action]:
                                tmp_time = tmp_time + \
                                    self.delays[action][self.day_counters[action]]
                                self.day_counters[action] += 1
                                self.day_counters['all'] += 1
                                continue
                            break

                self.day_counters['unfollow'] = self.day_counters['follow']

    def banned_sleep(self):
        # sleep for x minutes and try again

        if self.banned['400'] < 3:
            sleep_time = 5 * 60

        else:
            sleep_time = 60 * 60
            self.banned['banned'] = True
            self.banned['400'] = 0
        self.logger.log(
            '\n\t--- Sleeping for %s minutes ---' %
            (sleep_time / 60))
        self.next_operation['like'] += sleep_time
        self.next_operation['follow'] += sleep_time
        self.next_operation['comment'] += sleep_time
        self.next_operation['like_feed'] += sleep_time
        self.next_check_feed += sleep_time
        sleep(sleep_time)

    # === MAIN REQUESTS OPERATIONS ===

    def init_requests(self):
        # starting requests operations

        self.start_requests()
        self.log_in()

    def start_requests(self):
        # starts requests session

        user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'

        self.browser = Session()
        self.browser.cookies.update({
            'sessionid': '', 'mid': '', 'ig_pr': '1', 'ig_vw': '1920',
            'csrftoken': '', 's_network': '', 'ds_user_id': ''
        })
        self.browser.headers.update({
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US;q=0.6,en;q=0.4',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Host': 'www.instagram.com',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'User-Agent': user_agent,
            'X-Instagram-AJAX': '1',
            'X-Requested-With': 'XMLHttpRequest'

        })

    def log_in(self):
        # signs the user into instagram

        self.logged_in = False
        try:
            self.logger.log(
                '\nTrying to sign in as %s: \,' %
                (self.params['username']))
            # extract cookies from Instagram main page
            extract = self.browser.get(self.insta_urls['domain'])
            csrftoken = re.search(
                '(?<=\"csrf_token\":\")\w+', extract.text).group(0)
            self.browser.headers.update(
                {'X-CSRFToken': csrftoken})
            sleep(2)
            # extract csrf token from login requests post
            extract_login = self.browser.post(
                self.insta_urls['login'],
                data={
                    'username': self.params['username'],
                    'password': self.params['password']},
                allow_redirects=True)
            self.csrf_token = extract_login.cookies['csrftoken']
            self.browser.headers.update({'X-CSRFToken': self.csrf_token})
            self.browser.cookies['ig_vw'] = '1536'
            self.browser.cookies['ig_pr'] = '1.25'
            self.browser.cookies['ig_vh'] = '772'
            self.browser.cookies['ig_or'] = 'landscape-primary'
            sleep(2)
            # check if login successful
            if extract_login.ok:
                if self.check_login():
                    self.logger.log('Success')
                    self.logged_in = True
                    sleep(2)
                else:

                    self.logger.log('\nError signing in.\,')
                    self.logger.log(
                        'Request returns %s but it seems it didn\'t work.' %
                        (extract_login.status_code))

                    response_data = toJSON(extract_login.text)
                    self.logger.log(
                        '\nInstagram error message: %s' %
                        (response_data.get('message')))
                    if response_data.get('error_type'):
                        self.logger.log(
                            '\nError type: %s' %
                            (response_data.get('error_type')))

                    exit('\nCheck you entered the correct details!\n')

            else:

                self.logger.log('\nError signing in.\,')
                self.logger.log(
                    'Request returns %s error.' %
                    (extract_login.status_code))

                response_data = toJSON(extract_login.text)
                self.logger.log(
                    '\nInstagram error message: %s' %
                    (response_data.get('message')))
                if (response_data.get('message') == 'checkpoint_required'):
                    self.logger.log(
                        '\nCheckpoint_url: %s' %
                        (response_data.get('checkpoint_url')))
                    self.logger.log(
                        '\nOpen Instagram on your desktop browser and confirm that it is you trying to log in!')
                    self.logger.log('You have 30 seconds...')
                    sleep(30)
                elif response_data.get('error_type'):
                    self.logger.log(
                        '\nError type: %s' %
                        (response_data.get('error_type')))
                    exit('\nCheck you entered the correct details!\n')
                else:
                    exit('\nCheck you entered the correct details!\n')

        except KeyError as e:
            self.logger.log('\nERROR signing in, InstaBot probably failed to obtain Instagram\'s cookies')
            self.logger.log(traceback.format_exc())
            exit('\nApologies, I could not sign you in.\n')

        except Exception as e:
            self.logger.log('\nERROR while attempting sign in: %s\n' % e)
            self.logger.log(traceback.format_exc())
            exit('\nApologies, I could not sign you in.\n')

    def check_login(self):
        # checks if user is logged in

        try:
            main_page = self.browser.get(self.insta_urls['domain'])
            if self.params['username'] in main_page.text:
                return True
        except Exception as e:
            self.logger.log('ERROR while checking if logged in: %s' % (e))
        return False

    def log_out(self):
        # logs the user out

        try:
            self.browser.post(
                self.insta_urls['logout'], data={
                    'csrfmiddlewaretoken': self.csrf_token})
            self.browser.get(self.insta_urls['domain'])
            self.logger.log('\nSuccessfully logged out!')
            self.logged_in = False
        except Exception as err:
            self.logger.log('\nError while attempting logout: %s' % err)

        self.logger.backup()
        exit('\nThank you for using InstaBot!\n')

    def clean_up(self, on_exit, statement):
        # unfollows from list if user wants to log out or if day is over

        self.logger.log(statement)
        try:
            if on_exit:
                # unfollows between 30-60 second breaks
                while len(self.bucket['explore']['unfollow']) > 0:
                    self.clean_up_loop_count += 1
                    # sort the users by the time they were followed
                    for user in sorted(
                            self.bucket['explore']['unfollow'],
                            key=itemgetter(1)):
                        user_id = user[0]
                        # try to find the username
                        try:
                            username = self.bucket['user_ids'][user_id]
                        except BaseException:
                            username = False
                        # if available, print the username
                        if username:
                            check = self.user_following_back(username)
                            if check[0]:
                                self.logger.log(
                                    '\n * "%s" followed you back' % (username))
                                self.bucket['explore']['unfollow'].remove(user)
                                self.profile.add_follower(check[1])
                                continue
                        else:
                            username = user_id
                        self.logger.log(
                            '\n * Trying to unfollow "%s": \,' %
                            (username))
                        # unfollow
                        response = self.explore_operation('unfollow', user)
                        if not response[0]:
                            if response[1].status_code == 400:
                                self.banned_sleep()
                        if response[0]:
                            self.profile.remove_follow(user_id)
                            self.banned['400'] = 0
                        # small break
                        sleep_time = randint(20, 50)
                        print '\n\t--- Delaying %s seconds ---' % (sleep_time)
                        sleep(sleep_time)
                    # in case there's an error and it keeps looping
                    if self.clean_up_loop_count > 1000:
                        self.clean_up_loop_count = 0
                        self.logger.log(
                            '\nThe clean_up function is stuck in a loop. Breaking it...')
                        break
                return

            # normal unfollow
            while self.max_operation['unfollow'] > self.day_counters['unfollow']:
                self.clean_up_loop_count += 1
                self.next_operation['unfollow'] += self.delays['unfollow'][self.day_counters['unfollow']]
                self.day_counters['all'] += 1
                self.day_counters['unfollow'] += 1
                # normal unfollow operation
                response = self.insta_operation('unfollow')
                if not response[0]:
                    if response[1].status_code == 400:
                        self.banned_sleep()
                if response[0]:
                    self.banned['400'] = 0
                if (datetime.now() - datetime(1970, 1, 1)
                    ).total_seconds() > self.times['tomorrow_start']:
                    break
                # just to log the time
                sleep_time = self.delays['unfollow'][self.day_counters['unfollow']]
                print '\n\t--- Delaying %s seconds ---' % (sleep_time)
                sleep(sleep_time)
                # in case there's an error and it keeps looping
                if self.clean_up_loop_count > 1000:
                    self.clean_up_loop_count = 0
                    self.logger.log(
                        '\nThe clean_up function is stuck in a loop. Breaking it...')
                    break

        except KeyboardInterrupt:
            if len(self.bucket['explore']['unfollow']):
                self.logger.log(
                    '\nList of followers will be created and unfollowed when InstaBot is next started.')
            self.log_out()

        except Exception as e:
            self.logger.log('\nError cleaning up: %s' % (e))
            self.logger.log(traceback.format_exc())
            if on_exit:
                self.log_out()

    # === MAIN LOOP ===

    def main(self):

        # --- main ---

        self.loop_count = 0
        self.clean_up_loop_count = 0
        # unfollow previous session's follows
        if self.cache['unfollow']:
            if len(self.cache['unfollow']) >= 1:
                [self.bucket['explore']['unfollow'].append(
                    [user[0], i]) for i, user in enumerate(self.cache['unfollow'])]
                self.clean_up(
                    on_exit=True,
                    statement='\nCleaning up last sessions follows...')
        # start
        self.logger.log('\n\tStarting Bot at %s' %
                        (datetime.today().strftime('%H:%m %Y-%m-%d')))
        sleep(1 * aleatory())
        # check if out of hours
        if not self.run_all_day:
            if self.times['start_bot'] > (
                datetime.now() -
                datetime(
                    1970,
                    1,
                    1)).total_seconds():
                self.logger.log(
                    '\n%s => Stopping time reached. Pausing Bot until %s' %
                    (self.params['bot_stop_at'], self.params['bot_start_at']))
                # print self.times['start_bot'], (datetime.now() -
                # datetime(1970, 1, 1)).total_seconds(),
                # self.times['tomorrow_start']
                sleep(int(self.times['start_bot'] -
                          (datetime.now() -
                           datetime(1970, 1, 1)).total_seconds()))
        # main while loop
        while True:
            dc = self.day_counters
            self.logger.backup()
            self.logger.log(
                '\n\tCurrent daily count:\n\t - All operations: %s\n\t - Like news feed: %s\n\t - Likes: %s\n\t - Follows: %s\n\t - Unfollows: %s\n\t - Comments: %s' %
                (dc['all'], dc['like_feed'], dc['like'], dc['follow'], dc['unfollow'], dc['comment']))
            # here we go
            try:
                if self.run_all_day:
                    # all day mode
                    while internet_connection():
                        self.main_loop()
                        if all(self.max_operation[op] == self.day_counters[op]
                               for op in self.day_counters if op != 'unfollow' if op != 'all'):
                            self.reset_day_counters()
                            self.starting_operations()
                    continue
                # hour to hour mode
                while self.times['start_bot'] < (
                    datetime.now() -
                    datetime(
                        1970,
                        1,
                        1)).total_seconds() < self.times['stop_bot']:
                    # where the magic happens
                    self.main_loop()
                # if the loop is broken, finish up
                self.clean_up(on_exit=False,
                              statement='\nFinishing operations...')
                sleep(10)
                self.logger.log(
                    '\nSleeping until %s' %
                    (self.params['bot_start_at']))
                sleep_time = int(
                    self.times['tomorrow_start'] - (datetime.now() - datetime(1970, 1, 1)).total_seconds())
                if sleep_time > 0:
                    sleep(sleep_time)
                # check if it's the next day
                if (datetime.now() - datetime(1970, 1, 1)
                    ).total_seconds() > self.times['tomorrow_start']:
                    self.reset_day_counters()
                    self.starting_operations()

            except ConnectionError:
                self.logger.log('Connection error!')
                if not internet_connection():
                    while not internet_connection():
                        self.logger.log(
                            'NO INTERNET - re-establish connection to continue')
                        sleep(60)
                self.reset_day_counters()
                self.starting_operations()
                self.catch_up_operations()
                if not self.check_login():
                    self.init_requests()

            except Exception as e:
                self.logger.log('Error: %s' % (e))
                self.logger.log(traceback.format_exc())

            except KeyboardInterrupt:
                self.clean_up(
                    on_exit=True,
                    statement='\n\nStopping Bot. Please wait for cleaning follows...')
                self.logger.log('\nCleanup Done. Logging out...')
                self.log_out()

        exit('\nBye!\n')

    def main_loop(self):
        # main loop of operations

        self.refill_bucket()
        self.loop_count += 1
        # run operations
        for operation, enabled in self.enabled.items():
            if enabled:
                if self.next_operation[operation] < (datetime.now() - datetime(1970, 1, 1)).total_seconds() \
                        and self.max_operation[operation] > self.day_counters[operation] \
                        and self.max_operation['all'] > self.day_counters['all']:
                    # if unfollow, pick the user that was followed the soonest
                    if operation == 'unfollow':
                        if self.bucket['explore']['unfollow']:
                            self.next_operation[operation] = min(
                                i[1] for i in self.bucket['explore']['unfollow'])
                    # add to counter and create delay
                    self.next_operation[operation] += self.delays[operation][self.day_counters[operation]]
                    self.day_counters['all'] += 1
                    self.day_counters[operation] += 1
                    if self.day_counters['unfollow'] == self.max_operation['unfollow']:
                        self.day_counters['unfollow'] = 0
                    # normal operation
                    response = self.insta_operation(operation)
                    # handle error
                    if not response[0]:
                        if response[1].status_code == 400:
                            self.banned_sleep()
                    else:
                        self.banned['400'] = 0
            # add sleep time
            minim = min(
                value for key,
                value in self.next_operation.items() if self.enabled[key])
            sleep_time = minim - \
                (datetime.now() - datetime(1970, 1, 1)).total_seconds()
            if sleep_time > 0:
                print '\n\t--- Delaying %s seconds ---' % (sleep_time)
                sleep(sleep_time)

        if not internet_connection():
            raise ConnectionError
        # in case there's an error and it keeps looping
        if self.loop_count > 100:
            print '\tDelaying 60 seconds'
            sleep(60)

    def refill_bucket(self):
        # refill bucket with media and user ids

        if self.logged_in:
            tag = choice(self.cache['tags'])
            if (len(self.bucket['explore']['like']) < 5 and self.enabled['like']) or (
                    len(self.bucket['explore']['follow']) < 5 and self.enabled['follow']):
                self.logger.log(
                    '\nRefilling bucket - looking for "%s" posts: \,' %
                    (tag))
                bucket_len = len(self.bucket['explore']['like'])
                # refill the bucket
                try:
                    self.bucket = refill(
                        self.profile.profile['user']['user_id'],
                        media_by_tag(
                            self.browser,
                            self.insta_urls['explore'],
                            self.insta_urls['media'],
                            tag,
                            self.params['media_max_likes'],
                            self.params['media_min_likes']),
                        self.bucket,
                        self.cache['friends'],
                        self.cache['tags_to_avoid'],
                        self.enabled,
                        'explore')

                except Exception as e:
                    tag = choice(self.cache['tags'])
                    self.logger.log(
                        '\nError: %s. Trying again with %s: \,' %
                        (e, tag))
                    self.bucket = refill(
                        self.profile.profile['user']['user_id'],
                        media_by_tag(
                            self.browser,
                            self.insta_urls['explore'],
                            self.insta_urls['media'],
                            tag,
                            self.params['media_max_likes'],
                            self.params['media_min_likes']),
                        self.bucket,
                        self.cache['friends'],
                        self.cache['tags_to_avoid'],
                        self.enabled,
                        'explore')

                self.logger.log('found %s new.' %
                                (len(self.bucket['explore']['like']) - bucket_len))
            # refill if the bucket is low
            if len(self.bucket['feed']['like']) < 5:
                if (datetime.now() - datetime(1970, 1, 1)
                    ).total_seconds() > self.next_check_feed:
                    self.next_check_feed += 5 * 60
                    self.logger.log(
                        "\nScrolling through feed for friend's posts: \,")
                    # new feed posts
                    bucket_feed_len = len(self.bucket['feed']['like'])
                    feed_data = news_feed_media(
                        self.browser,
                        self.insta_urls['domain'],
                        self.profile.profile['user']['user_id'])
                    self.bucket = refill(
                        self.profile.profile['user']['user_id'],
                        feed_data,
                        self.bucket,
                        self.cache['friends'],
                        self.cache['tags_to_avoid'],
                        self.enabled,
                        'feed')
                    self.logger.log(
                        'found %s, %s from friends. \n' %
                        (len(feed_data), len(
                            self.bucket['feed']['like']) - bucket_feed_len))
                    # organise this data please
                    self.organise_profile(feed_data)
            # give it some sleep time
            minim = min(
                value for key,
                value in self.next_operation.items() if self.enabled[key])
            sleep_time = minim - \
                (datetime.now() - datetime(1970, 1, 1)).total_seconds()
            if sleep_time > 0:
                print '\n\t--- Delaying %s seconds ---' % (sleep_time)
                sleep(sleep_time)
            return

        self.logger.log("\nYou're not logged in!\n")
        raise ConnectionError

    def insta_operation(self, op):
        # runs the instagram operation

        self.loop_count = 0
        if op == 'like_feed':
            return self.like_feed()
        elif op == 'like':
            return self.like_media(False)
        elif op == 'comment':
            return self.comment_media(False)
        elif op == 'follow':
            return self.follow_user()
        elif op == 'unfollow':
            return self.unfollow_user()
        # there are no other options

    def follow_user(self):
        # follows random user

        user_id = choice(list(self.bucket['explore']['follow']))
        username = self.bucket['user_ids'][user_id]
        if not username:
            username = user_id
        self.logger.log('\n * Trying to follow "%s": \,' % (username))
        if not any(
                user_id == user for user in self.profile.master_unfollow_list):
            return self.explore_operation('follow', user_id)
        self.logger.log('\nuser has already been unfollowed before!')
        return [True]

    def unfollow_user(self):
        # unfollows user

        for user in self.bucket['explore']['unfollow']:
            if (datetime.now() - datetime(1970, 1, 1)
                ).total_seconds() > user[1]:
                user_id = user[0]
                username = self.bucket['user_ids'][user[0]]
                if username:
                    check = self.user_following_back(username)
                    if check[0]:
                        self.logger.log(
                            '\n * "%s" followed you back' %
                            (username))
                        self.bucket['explore']['unfollow'].remove(user)
                        self.profile.add_follower(check[1])
                        return [True]
                else:
                    username = user_id
                self.logger.log(
                    '\n * Trying to unfollow "%s": \,' %
                    (username))
                self.profile.remove_follow(user_id)
                return self.explore_operation('unfollow', user)
        return [True]

    def user_following_back(self, username):
        # check if the user is following back

        user_data = check_user(self.browser, self.insta_urls['user'], username)
        if user_data['follower']:
            return [True, user_data['data']]
        return [False]

    def like_media(self, media):
        # likes media, or does it?
        # yeah, it does...

        media_id = media if media else choice(
            list(self.bucket['explore']['like']))
        self.logger.log(
            '\n * Trying to like "%s": \,' %
            (self.insta_urls['media'] %
             (self.bucket['codes'][media_id])))
        try:
            response = self.explore_operation('like', media_id)
            del self.bucket['codes'][media_id]
            if self.enabled['comment'] and (datetime.now() - datetime(1970, 1, 1)).total_seconds(
            ) > self.next_operation['comment'] and self.max_operation['comment'] > self.day_counters['comment']:
                self.next_operation['comment'] = self.next_operation['comment'] + \
                    self.delays['comment'][self.day_counters['comment']]
                self.day_counters['all'] += 1
                self.day_counters['comment'] += 1
                self.comment_media(media_id)
            else:
                self.bucket['explore']['comment'].discard(media_id)
            return response
        except Exception as e:
            raise Exception(' while liking - debugging needed: %s' % (e))
        return [True]

    def comment_media(self, media):
        # comments media

        media_id = media if media else choice(
            list(self.bucket['explore']['like']))
        self.logger.log(
            '\n * Trying to comment "%s": \,' %
            (self.insta_urls['media'] %
             (self.bucket['codes'][media_id])))
        try:
            response = self.explore_operation('comment', media_id)
            if self.enabled['like'] and self.max_operation['like'] > self.day_counters['like']:
                self.next_operation['like'] = self.next_operation['like'] + \
                    self.delays['like'][self.day_counters['like']]
                self.day_counters['all'] += 1
                self.day_counters['like'] += 1
                self.like_media(media_id)
            else:
                self.bucket['explore']['like'].discard(media_id)
            return response
        except Exception as e:
            raise Exception('\nwhile commenting - debugging needed: %s' % (e))
        return [True]

    def explore_operation(self, operation, identifier):
        # sends requests post and checks response

        self.clean_up_loop_count = 0
        result = [True]
        try:
            comment = False
            # comment
            if operation == 'comment':
                commentString = generate_comment(self.params['comments_list'])
                self.logger.log('\n\n\tComment: "' + commentString + '" \n')
                comment = emojize((commentString), use_aliases=True)
            # unfollow
            if operation == 'unfollow':
                self.profile.master_unfollow_list.append(identifier[0])
                response = post_data(
                    self.browser,
                    self.insta_urls[operation],
                    identifier[0],
                    comment)
            else:
                response = post_data(
                    self.browser,
                    self.insta_urls[operation],
                    identifier,
                    comment)
            # check if it worked
            if response['response'].ok:
                self.total_counters[operation] += 1
                self.logger.log('Success')
            # error
            elif response['response'].status_code == 400:
                self.logger.log('Error 400 - failed')
                self.banned['400'] += 1
                result = [False, response['response']]
            else:
                self.logger.log(
                    'Error %s - failed' %
                    (response['response'].status_code))
            # remove from bucket
            if not operation == 'unfollow':
                self.bucket['explore'][operation].discard(identifier)
                self.bucket['explore']['done'][operation].add(identifier)
            else:
                self.bucket['explore'][operation].remove(identifier)
                self.bucket['explore']['done'][operation].append(identifier)
            if operation == 'follow':
                # add with time to unfollow
                self.bucket['explore']['unfollow'].append([identifier, (datetime.now(
                ) - datetime(1970, 1, 1)).total_seconds() + self.params['follow_time']])
        except Exception as e:
            raise Exception(
                '\nin explore operation: %s - debugging needed: %s' %
                (e, traceback.format_exc()))
        return result

    def like_feed(self):
        # like news feed

        post_ids = self.bucket['feed']['like']
        if len(post_ids) == 0:
            self.logger.log('\nNo new posts from your friends to like')
            return [True]
        elif len(post_ids) > 5:
            until = 5
        else:
            until = len(post_ids)
        self.logger.log('\nLiking news feed...')
        ban_counter = 0
        for i in range(0, until):
            try:
                post = self.bucket['feed']['like'][0]
                liked = post_data(
                    self.browser,
                    self.insta_urls['like'],
                    post[0],
                    False)
                if liked['response'].ok:
                    self.logger.log(" * Liked %s's post %s" %
                                    (post[1], self.insta_urls['media'] %
                                     (self.bucket['codes'][post[0]])))
                elif liked['response'].status_code == 400:
                    ban_counter += 1
                    if ban_counter > 2:
                        self.bucket['feed']['done'].append(post)
                        self.bucket['feed']['like'].remove(post)
                        return [False, liked['response']]
                else:
                    raise Exception(
                        "%s could not like %s's media" %
                        (liked['response'].status_code, post_ids[i][2]))
            except Exception as e:
                self.logger.log(' * Error: %s' % (e))
            self.bucket['feed']['done'].append(post)
            self.bucket['feed']['like'].remove(post)
            sleep(10 * aleatory())
        self.total_counters['like_feed'] += 1
        return [True]

    def organise_profile(self, data):
        # checks news feed for users and adds them to profile object

        self.logger.log(
            'Checking the profiles of those you follow:\nChecked users:\,')
        user_names = list(set(
            [post['username'] for post in data if post['username'] not in self.users_checked_today]))
        if len(user_names) > 1:
            users_data = [
                check_user(
                    self.browser,
                    self.insta_urls['user'],
                    user) for user in user_names]
            for user in users_data[:-1]:
                self.logger.log('%s, \,' % (user['data']['username']))
            self.logger.log('%s.' % (users_data[-1]['data']['username']))
            for user in users_data:
                self.users_checked_today.append(user['data']['username'])
                if user['follower'] and not user['fake']:
                    # add user to your followers list in profile
                    if not any(user['data']['user_id'] == node['user_id']
                               for node in self.profile.profile['followers']):
                        self.profile.add_follower(user['data'])
                    else:
                        self.profile.update_user(user['data'], 'followers')
                    # remove from bucket if they are going to be unfollowed
                    if any(user['data']['user_id'] == user_id[0]
                           for user_id in self.bucket['explore']['unfollow']):
                        for i, user_id in enumerate(
                                self.bucket['explore']['unfollow']):
                            if user['data']['user_id'] == user_id[0]:
                                self.logger.log(
                                    ' - %s followed you back - \,' %
                                    (user['data']['username']))
                                del self.bucket['explore']['unfollow'][i]
                                self.logger.log('removed from unfollow list')
                                break
                    # if user has been unfollowed, follow back
                    if any(user['data']['user_id'] == user_id[0]
                           for user_id in self.bucket['explore']['done']['unfollow']):
                        for i, user_id in enumerate(
                                self.bucket['explore']['done']['unfollow']):
                            if user['data']['user_id'] == user_id[0]:
                                self.logger.log(
                                    ' - %s followed you back but was unfollowed - \,' %
                                    (user['data']['username']))
                                del self.bucket['explore']['done']['unfollow'][i]
                                try:
                                    response = post_data(
                                        self.browser, self.insta_urls['follow'], user['data']['user_id'], False)
                                    if response['response'].ok:
                                        self.logger.log('followed back!')
                                    else:
                                        self.logger.log(
                                            'Error %s while following back' %
                                            (response['response'].status_code))
                                except BaseException:
                                    self.logger.log(
                                        'Error while following back')
                                break
                # unfollow if user is fake
                elif user['fake']:
                    self.logger.log(
                        ' - %s is a fake account - \,' %
                        (user['data']['username']))
                    for i, user_id in enumerate(
                            self.bucket['explore']['unfollow']):
                        if user['data']['user_id'] == user_id[0]:
                            response = self.explore_operation(
                                'unfollow', user_id)
                            if response[0]:
                                self.logger.log('unfollowed!')

                            else:
                                self.logger.log(
                                    '\nError %s while unfollowing' % (response[1]))
                            break
                # add user to follow list in profile
                if not any(user['data']['user_id'] == node['user_id']
                           for node in self.profile.profile['follows']):
                    self.logger.log(
                        ' - %s will be added to follow list in profile' %
                        (user['data']['username']))
                    self.profile.add_follow(user['data'])

                else:
                    self.profile.update_user(user['data'], 'follows')
        else:
            self.logger.log('all users have already been checked for today.')
