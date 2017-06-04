#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ___        InstaBot V 1.0.3 by nickpettican           ___
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

import requests, os, random, time, csv, arrow
from requests.exceptions import ConnectionError
from operator import itemgetter
from datetime import datetime
from sys import platform

from src.miscellaneous import *
from src.instafunctions import *

# === INSTABOT ===

class InstaBot:

	# --- default values ---

	def __init__(self, profile, data = {	
		'username': 'user', 
		'password': 'pwd', 
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
		'bot_start_at': '07:00', 
		'bot_stop_at': '23:00'
	}):

		self.today = arrow.now().format('DD_MM_YYYY')
		self.users_checked_today = []

		self.header = '\n--- InstaBot V 1.0.3 by nickpettican ---\
					   \n--- Automate your Instagram activity ---\n'

		self.console_log('START')

		# === INITIALISE VARIABLES ===

		self.params = data
		self.profile = profile

		if data['unfollow']:
			self.params['total_operations'] = data['likes_in_day'] + data['follow_in_day']*2 + data['comments_in_day']
		else:
			self.params['total_operations'] = data['likes_in_day'] + data['follow_in_day'] + data['comments_in_day']

		self.params['follow_time'] = data['follow_time_hours']*60*60
		self.ERROR = {'mkdir': False, 'importing': False, 'cache': False}
		self.op_tmp = {'like': False, 'comment': False}
		self.banned = {'banned': False, '400': 0}
		self.activity_log = []
		self.cache = {}

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
			'feed':	{
				'like': [],
				'media_ids': [],
				'done': []
			},
			'codes': {}
		}

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

		# --- counters ---

		self.total_counters = {'like_feed': 0, 'like': 0, 'follow': 0, 'unfollow': 0, 'comment': 0}
		self.day_counters = {'all':0, 'like_feed': 0, 'like': 0, 'follow': 0, 'unfollow': 0, 'comment': 0}

		# --- initialise links and other parameters ---

		self.mkdir_cache()
	
		self.sort_enabling()

		self.starting_operations()

		self.catch_up_operations()

		self.init_requests()

		self.init_profile()

	# === INITIAL OPERATIONS ===

	def starting_operations(self):

		# --- starting operations ---

		self.user_input()
		self.create_delays()
		self.set_operation_sequence()

	def mkdir_cache(self):
		
		# --- creates the cache folder ---
		
		if not os.path.isdir('cache'):
			try:
				os.makedirs('cache')

			except:
				self.console_log('\nERROR creating cache.\n')
				self.ERROR['mkdir'] = True

	def user_input(self):

		# --- imports friend list so that the bot likes their new media ---

		try:
			if type(self.params['friends']) is list:
				self.cache['friends'] = self.params['friends']
			else:	
				self.cache['friends'] = [line.strip() for line in open(self.params['friends'], 'r')]
			
			if type(self.params['tags']) is list:
				self.cache['tags'] = self.params['tags']
			else:
				self.cache['tags'] = [line.strip() for line in open(self.params['tags'], 'r')]
			
			if type(self.params['tags_to_avoid']) is list:
				self.cache['tags_to_avoid'] = self.params['tags_to_avoid']
			else:
				self.cache['tags_to_avoid'] = [line.strip() for line in open(self.params['tags_to_avoid'], 'r')]

		except:
			self.ERROR['importing'] = True
			self.console_log('\nERROR importing cached lists')
		
		self.cache['unfollow'] = False

		try:
			if os.path.isfile('cache/followlist.csv'):
				self.cache['unfollow'] = [line.strip().split(',') for line in open('cache/followlist.csv', 'r')]

		except:
			self.console_log('\nERROR importing cached follow list')

	def sort_enabling(self):
		
		# --- define which operations are enabled ---
		
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

			self.enabled['unfollow'] = self.params['unfollow']

		except:
			self.console_log('ERROR while sorting parameters. Check you entered the right formats.')
			exit()

	def init_profile(self):

		# --- returns data for InstaProfile ---

		self.profile.import_profile(check_user(self.pull, self.insta_urls['user'], self.params['username']))

	# === END INITIAL OPERATIONS ===

	# === TIME OPERATIONS ===

	def time_now(self):

		# --- returns current timestamp ---

		return float(arrow.now().timestamp)

	def create_delays(self):

		# --- creates the necessary times ---

		if self.params['bot_start_at'] == self.params['bot_stop_at']:
			self.run_all_day = True
			self.params['time_in_day'] = 24*60*60

		else:
			self.run_all_day = False
			self.times = self.today_times()
			self.params['time_in_day'] = int(self.times['stop_bot'] - self.times['start_bot'])
			self.params['total_operations'] += self.params['time_in_day']/60/60

		follow_delays = return_random_sequence(self.params['follow_in_day'], self.params['time_in_day'])
		self.delays = { 
			'like': return_random_sequence(self.params['likes_in_day'], self.params['time_in_day']), 
			'follow': follow_delays, 
			'comment': return_random_sequence(self.params['comments_in_day'], self.params['time_in_day']), 
			'unfollow': follow_delays,
			'like_feed': [60*60 for i in range(0, int(self.params['time_in_day']/60/60))]	
		}

	def today_times(self):

		# --- creates the times for the day ---

		if not self.run_all_day:
		
			if float(self.params['bot_stop_at'].replace(':', '.')) - float(self.params['bot_start_at'].replace(':', '.')) < 0:
				self.params['bot_stop_at'] = str(float(self.params['bot_stop_at'].replace(':', '.')) + 12).replace('.', ':')
			time_tomorrow = float(arrow.get(str(arrow.utcnow().replace(days=1)).split('T').pop(0) + 'T' + \
							str(self.params['bot_start_at']).replace('.', ':')).timestamp)

			return {	
					'start_bot': float(arrow.get(arrow.now().format('YYYY-MM-DD') + 'T' + str(self.params['bot_start_at']).replace('.', ':')).timestamp), 
					'stop_bot': float(arrow.get(arrow.now().format('YYYY-MM-DD') + 'T' + str(self.params['bot_stop_at']).replace('.', ':')).timestamp),
					'tomorrow_start': time_tomorrow
			}

	def set_operation_sequence(self):

		# --- set the operation times to iterate ---
		
		self.next_operation = {	

			'like': self.time_now() + 40, 
			'follow': self.time_now() + 60, 
			'comment': self.time_now() + 40, 
			'unfollow': self.time_now() + self.params['follow_time'],
			'like_feed': self.time_now()
		}

		if self.bucket['explore']['unfollow']:
			self.next_operation['unfollow'] = min(i[1] for i in self.bucket['explore']['unfollow'])

		self.next_check_feed = self.time_now()

		self.max_operation = {	

			'like': self.params['likes_in_day'], 
			'follow': self.params['follow_in_day'], 
			'comment': self.params['comments_in_day'], 
			'unfollow': self.params['follow_in_day'],
			'like_feed': self.params['time_in_day']/60/60, 
			'all': self.params['total_operations']
		}

	def reset_day_counters(self):

		# --- resets the day counters ---

		unfollow_counter_tmp = self.day_counters['unfollow']
		self.day_counters = {'all':0, 'like_feed': 0, 'like': 0, 'follow': 0, 'comment': 0, 'unfollow': unfollow_counter_tmp}

	def catch_up_operations(self):

		# --- organises the operations for the day ---

		if not self.run_all_day:
			if self.times['start_bot'] < self.time_now() < self.times['stop_bot']:
				
				for action, enabled in self.enabled.items():
					if enabled:
						tmp_time = self.times['start_bot']
						
						while tmp_time < self.time_now():
							if self.day_counters[action] < self.max_operation[action]:
								tmp_time = tmp_time + self.delays[action][self.day_counters[action]]
								self.day_counters[action] += 1
								self.day_counters['all'] += 1
						
							else: 
								break

				self.day_counters['unfollow'] = self.day_counters['follow']

	def banned_sleep(self):
		
		# --- sleep for x minutes and try again ---
		
		if self.banned['400'] < 3:
			sleep_time = 5*60

		else:
			sleep_time = 60*60
			self.banned['banned'] = True
			self.banned['400'] = 0
			
		self.console_log('\tSleeping for %s minutes... '%(sleep_time/60))

		self.next_operation['like'] += sleep_time
		self.next_operation['follow'] += sleep_time
		self.next_operation['comment'] += sleep_time
		self.next_operation['like_feed'] += sleep_time
		self.next_check_feed += sleep_time

		time.sleep(sleep_time)

	# === END TIME OPERATIONS ===

	# === MAIN REQUESTS OPERATIONS ===

	def init_requests(self):

		# --- starting requests operations ---

		self.start_requests()
		self.log_in()
	
	def start_requests(self):
		
		# --- starts requests session ---

		user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
		
		self.pull = requests.Session()
		self.pull.cookies.update({

			'sessionid' : '', 'mid' : '', 'ig_pr' : '1', 'ig_vw' : '1920', 
			'csrftoken' : '', 's_network' : '', 'ds_user_id' : ''
		})
		self.pull.headers.update({

			'Accept-Encoding' : 'gzip, deflate',
			'Accept-Language' : 'en-US;q=0.6,en;q=0.4',
			'Connection' : 'keep-alive',
			'Content-Length' : '0',
			'Host' : 'www.instagram.com',
			'Origin' : 'https://www.instagram.com',
			'Referer' : 'https://www.instagram.com/',
			'User-Agent' : user_agent,
			'X-Instagram-AJAX' : '1',
			'X-Requested-With' : 'XMLHttpRequest'
		})

	def log_in(self):
		
		# --- signs the user into instagram ---

		self.logged_in = False
		
		try:	 
			self.console_log('\nTrying to sign in as %s... \,' %(self.params['username']))
			
			# extract cookies from Instagram main page

			extract = self.pull.get(self.insta_urls['domain'])
			self.pull.headers.update({'X-CSRFToken': extract.cookies['csrftoken']})
			time.sleep(2)
		
			# extract csrf token from login requests post
		
			extract_login = self.pull.post(self.insta_urls['login'], data = {'username': self.params['username'], 'password': self.params['password']}, allow_redirects = True)
			self.csrf_token = extract_login.cookies['csrftoken']
			self.pull.headers.update({'X-CSRFToken': self.csrf_token})
			time.sleep(2)
		
			# check if login successful
		
			if extract_login.ok:
				if self.check_login():
					self.console_log('successfully signed in!')
					self.logged_in = True
					time.sleep(2)

				else:
					self.console_log('ERROR, could not sign in.')
					exit('\nCheck you entered the correct details!\n')

			else:
				self.console_log('ERROR, could not sign in.')
				exit('\nCheck you entered the correct details!\n')

		except:
			self.console_log('\nERROR while attempting sign in\n')

	def check_login(self):

		# --- checks if user is logged in ---

		try:
			main_page = self.pull.get(self.insta_urls['domain'])
			if self.params['username'] in main_page.text:
				return True

			else:
				return False

		except Exception as e:
			self.console_log('ERROR checking if logged in: %s' %(e))
			return False
			
	def log_out(self):
		
		# --- logs the user out ---
		
		try:
			log_out_post = self.pull.post(self.insta_urls['logout'], data = {'csrfmiddlewaretoken': self.csrf_token})
			main_page = self.pull.get(self.insta_urls['domain'])
			self.console_log('\nSuccessfully logged out!')
			self.logged_in = False

		except:
			self.console_log('\nERROR while attempting logout')
			
		self.back_up()
				
		exit('\nThank you for using InstaBot!\n')

	def clean_up(self, on_exit, statement):

		# --- unfollows from list if user wants to log out or if day is over ---

		self.console_log(statement)

		try:
			if on_exit:
				while len(self.bucket['explore']['unfollow']) > 0:
					for user in sorted(self.bucket['explore']['unfollow'], key=itemgetter(1)):

						user_id = user[0]
						self.console_log('\n * Trying to unfollow %s... \,' %(user_id))
						
						response = self.explore_operation('unfollow', user)

						if not response[0]:
							if response[1].status_code == 400:
								self.banned_sleep()

						if response[0]:
							self.profile.remove_follow(user_id)
							self.banned['400'] = 0

						sleep_time = random.randint(30, 60)
						print '\tWaiting %s seconds' %(sleep_time)
						time.sleep(sleep_time)

			else:

				while self.max_operation['unfollow'] > self.day_counters['unfollow']:
					self.next_operation['unfollow'] += self.delays['unfollow'][self.day_counters['unfollow']]
					self.day_counters['all'] += 1
					self.day_counters['unfollow'] += 1

					response = self.insta_operation('unfollow')

					if not response[0]:
						if response[1].status_code == 400:
							self.banned_sleep()

					if response[0]:
						self.banned['400'] = 0

					if self.time_now() > self.times['tomorrow_start']:
						break

					time.sleep(self.delays['unfollow'][self.day_counters['unfollow']])

		except KeyboardInterrupt:
			if len(self.bucket['explore']['unfollow']):
				self.console_log('\nList of followers will be created and unfollowed when InstaBot is next started.')

			self.log_out()

		except Exception as e:
			 self.console_log('Error cleaning up: %s' %(e))
			 if on_exit:
				 self.log_out()

	# === END REQUESTS OPERATIONS ===

	# === BACKUPS ===

	def back_up(self):

		# --- saves a back-up of follow lists ---

		self.profile.save_unfollow_list()

		if self.today != arrow.now().format('DD_MM_YYYY'):
			self.activity_log = []
			self.users_checked_today = []
			self.today = arrow.now().format('DD_MM_YYYY')

		if not self.ERROR['cache']:
		
		# --- saves activity log ---
		
			try:
				with open('cache/activity_log_'+ self.today +'.csv', 'wb') as log:
					w = csv.writer(log)
					w.writerows(self.activity_log)
			
			except:
				self.console_log('\nERROR while backing up activity log.\n')
			
		# --- saves backup of followed users that haven't been unfollowed ---
		
			try:
				with open('cache/followlist.csv', 'wb') as backup:
					w = csv.writer(backup)
					w.writerows(self.bucket['explore']['unfollow'])
			
			except:
				self.console_log('\nERROR while saving backup follow list.\n')

	# === END BACKUPS ===

	# === MAIN LOOP ===

	def main(self):

		# --- main ---

		if self.cache['unfollow']:
			if len(self.cache['unfollow']) >= 1:
				add = [self.bucket['explore']['unfollow'].append([user[0], i]) for i, user in enumerate(self.cache['unfollow'])]
				self.clean_up(on_exit=True, statement='\nCleaning up last sessions follows...')

		self.console_log('\nStarting operations - %s' %(arrow.now().format('HH:mm:ss DD/MM/YYYY')))

		self.loop_count = 0

		time.sleep(2*random.random())

		if self.times['start_bot'] > self.time_now():
			self.console_log('\nOut of hours... sleeping until %s' %(self.params['bot_start_at']))
			print self.times['start_bot'], self.time_now(), self.times['tomorrow_start']
			time.sleep(int(self.times['start_bot'] - self.time_now()))

		while True:
			dc = self.day_counters
			self.back_up()
			self.console_log('\nCurrent daily count:\n - All operations: %s\n - Like news feed: %s\n - Likes: %s\n - Follows: %s\n - Unfollows: %s\n - Comments: %s' 
								%(dc['all'], dc['like_feed'], dc['like'], dc['follow'], dc['unfollow'], dc['comment']))

			try:
				if self.run_all_day:

					while internet_connection():
						self.main_loop()
						if all(self.max_operation[op] == self.day_counters[op] for op in self.day_counters 
								if op != 'unfollow' if op != 'all'):
							self.reset_day_counters()
							self.starting_operations()

				else:
					while self.times['start_bot'] < self.time_now() < self.times['stop_bot']:
						self.main_loop()

					self.clean_up(on_exit=False, statement='\nFinishing operations...')
					time.sleep(10)
					self.console_log('\nSleeping until %s' %(self.params['bot_start_at']))

					time.sleep(int(self.times['start_bot'] - self.time_now()))

					if self.time_now() > self.times['tomorrow_start']:
						self.reset_day_counters()
						self.starting_operations()

			except ConnectionError:
				self.console_log('connection error')

				while not internet_connection():
					self.console_log('NO INTERNET - re-establish connection to continue')
					time.sleep(60)

				self.reset_day_counters()
				self.starting_operations()
				self.catch_up_operations()
				if not self.check_login():
					self.init_requests()

				continue

			except Exception as e:

				self.console_log('Error: %s' %(e))
				continue

			except KeyboardInterrupt:
				self.clean_up(on_exit=True, statement='\nCleaning up...')
				self.log_out()

		exit('\nBye!\n')

	def main_loop(self):

		# --- main loop of operations ---

		self.refill_bucket()
		self.loop_count += 1

		# --- run operations ---

		for operation, enabled in self.enabled.items():
			if enabled:
				if self.next_operation[operation] < self.time_now() \
					and self.max_operation[operation] > self.day_counters[operation] \
					and self.max_operation['all'] > self.day_counters['all']:

					if operation == 'unfollow':
						if self.bucket['explore']['unfollow']:
							self.next_operation[operation] = min(i[1] for i in self.bucket['explore']['unfollow'])	
					
					self.next_operation[operation] += self.delays[operation][self.day_counters[operation]]
					self.day_counters['all'] += 1
					self.day_counters[operation] += 1
					if self.day_counters['unfollow'] == self.max_operation['unfollow']:
						self.day_counters['unfollow'] = 0

					response = self.insta_operation(operation)
					
					if not response[0]:
						if response[1].status_code == 400:
							self.banned_sleep()

					if response[0]:
						self.banned['400'] = 0

			minim = min(value for key, value in self.next_operation.items() if self.enabled[key])
			sleep_time = minim - self.time_now()
			if sleep_time > 0:
				print '\tWaiting %s seconds' %(sleep_time)
				time.sleep(sleep_time)

		if not internet_connection():
			raise ConnectionError

		if self.loop_count > 100:
			print '\tWaiting 60 seconds'
			time.sleep(60)

	def refill_bucket(self):

		# --- refill bucket with media and user ids ---

		if self.logged_in:
			tag = random.choice(self.cache['tags'])
			if (len(self.bucket['explore']['like']) < 5 and self.enabled['like']) or \
				(len(self.bucket['explore']['follow']) < 5 and self.enabled['follow']):
				self.console_log('\nRefilling bucket - looking for "%s" posts... \,' %(tag))
				bucket_len = len(self.bucket['explore']['like'])
				
				try:
					self.bucket = refill(self.profile.profile['user']['user_id'], media_by_tag(self.pull, self.insta_urls['explore'], tag, self.params['media_max_likes'], 
								self.params['media_min_likes']), self.bucket, self.cache['friends'], self.cache['tags_to_avoid'], self.enabled, 'explore')
				
				except Exception as e:
					tag = random.choice(self.cache['tags'])
					self.console_log('Error: %s. Trying again with %s... \,' %(e, tag))
					self.bucket = refill(self.profile.profile['user']['user_id'], media_by_tag(self.pull, self.insta_urls['explore'], tag, self.params['media_max_likes'], 
								self.params['media_min_likes']), self.bucket, self.cache['friends'], self.cache['tags_to_avoid'], self.enabled, 'explore')
				
				self.console_log('found %s new.' %(len(self.bucket['explore']['like']) - bucket_len))

			if len(self.bucket['feed']['like']) < 5:
				if self.time_now() > self.next_check_feed:
					self.next_check_feed += 5*60
					self.console_log("\nScrolling through feed for friend's posts... \,")
					
					bucket_feed_len = len(self.bucket['feed']['like'])
					feed_data = news_feed_media(self.pull, self.insta_urls['domain'], self.profile.profile['user']['user_id'])
					self.bucket = refill(self.profile.profile['user']['user_id'], feed_data, self.bucket, self.cache['friends'], self.cache['tags_to_avoid'], self.enabled, 'feed')
					self.console_log('found %s, %s from friends.' %(len(feed_data), len(self.bucket['feed']['like']) - bucket_feed_len))
					
					self.organise_profile(feed_data)

			minim = min(value for key, value in self.next_operation.items() if self.enabled[key])
			sleep_time = minim - self.time_now()
			if sleep_time > 0:
				print '\tWaiting %s seconds' %(sleep_time)
				time.sleep(sleep_time)

		else:
			self.console_log("\nYou're not logged in!\n")
			raise ConnectionError

	def insta_operation(self, op):

		# --- runs the instagram operation ---

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

	def follow_user(self):

		# --- follows random user ---

		user_id = random.choice(list(self.bucket['explore']['follow']))

		self.console_log('\n * Trying to follow %s... \,' %(user_id))

		if not any(user_id == user for user in self.profile.master_unfollow_list):

			return self.explore_operation('follow', user_id)

		else:

			self.console_log('user has already been unfollowed before!')
			return [True]

	def unfollow_user(self):

		# --- unfollows user ---

		for user in self.bucket['explore']['unfollow']:
			
			if self.time_now() > user[1]:
			
				user_id = user[0]

				self.console_log('\n * Trying to unfollow %s... \,' %(user_id))

				self.profile.remove_follow(user_id)

				return self.explore_operation('unfollow', user)

		return [True]

	def like_media(self, media):

		# --- likes media ---

		if media:
			media_id = media
		
		else:
			media_id = random.choice(list(self.bucket['explore']['like']))

		self.console_log('\n * Trying to like %s... \,' %(self.insta_urls['media'] %(self.bucket['codes'][media_id])))

		try:
			response = self.explore_operation('like', media_id)

			if self.enabled['comment'] and self.time_now() > self.next_operation['comment'] \
					and self.max_operation['comment'] > self.day_counters['comment']:

				self.next_operation['comment'] = self.next_operation['comment'] + self.delays['comment'][self.day_counters['comment']]
				self.day_counters['all'] += 1
				self.day_counters['comment'] += 1

				comment = self.comment_media(media_id)

			else:
				self.bucket['explore']['comment'].discard(media_id)

			return response

		except:
			raise Exception('while liking - debugging needed.')

	def comment_media(self, media):

		# --- comments media ---

		if media:
			media_id = media
		
		else:
			media_id = random.choice(list(self.bucket['explore']['like']))

		self.console_log('\n * Trying to comment %s... \,' %(self.insta_urls['media'] %(self.bucket['codes'][media_id])))

		try:
			response = self.explore_operation('comment', media_id)

			if self.enabled['like'] and self.max_operation['like'] > self.day_counters['like']:

				self.next_operation['like'] = self.next_operation['like'] + self.delays['like'][self.day_counters['like']]
				self.day_counters['all'] += 1
				self.day_counters['like'] += 1

				like = self.like_media(media_id)

			else:
				self.bucket['explore']['like'].discard(media_id)

			return response

		except:
			raise Exception('while commenting - debugging needed.')

	def explore_operation(self, operation, identifier):

		# --- sends requests post and checks response ---

		try:
			comment = False
			result = [True]
			
			if operation == 'comment':
				comment = generate_comment()
				self.console_log(comment + '\,')

			if operation == 'unfollow':
				response = post_data(self.pull, self.insta_urls[operation], identifier[0], comment)

			else:
				response = post_data(self.pull, self.insta_urls[operation], identifier, comment)

			if response['response'].ok:
				self.total_counters[operation] += 1
				self.console_log('success')

			elif response['response'].status_code == 400:
				self.console_log('ERROR 400 - failed')
				self.banned['400'] += 1
				result = [False, response['response']]

			else:
				self.console_log('ERROR %s - failed' %(response['response'].status_code))
				
			if not operation == 'unfollow':
				self.bucket['explore'][operation].discard(identifier)
				self.bucket['explore']['done'][operation].add(identifier)
				
			else:
				self.bucket['explore'][operation].remove(identifier)
				self.bucket['explore']['done'][operation].append(identifier)
				
			if operation == 'follow':
				self.bucket['explore']['unfollow'].append([identifier, self.time_now() + self.params['follow_time']])

			return result

		except:
			raise Exception('in explore operation - debugging needed.')

	def like_feed(self):

		# --- like news feed ---

		post_ids = self.bucket['feed']['like']

		if len(post_ids) == 0:
			self.console_log('\nNo new posts from your friends to like')
			return [True]

		elif len(post_ids) > 5:
			until = 5

		else:
			until = len(post_ids)

		self.console_log('\nLiking news feed...')

		ban_counter = 0

		for i in range(0, until):

			try:
				post = self.bucket['feed']['like'][0]

				liked = post_data(self.pull, self.insta_urls['like'], post[0], False)
					
				if liked['response'].ok:
					self.console_log(" * Liked %s's post %s" %(post[1], self.insta_urls['media'] %(self.bucket['codes'][post[0]])))
					
				elif liked['response'].status_code == 400:
					ban_counter += 1
					if ban_counter > 2:
						self.bucket['feed']['done'].append(post)
						self.bucket['feed']['like'].remove(post)
						return [False, liked['response']]
					
				else:
					raise Exception("%s could not like %s's media" %(liked['response'].status_code, post_ids[i][2]))
				
			except Exception as e:
				self.console_log(' * Error: %s' %(e))

			self.bucket['feed']['done'].append(post)
			self.bucket['feed']['like'].remove(post)

			time.sleep(10*random.random())

		self.total_counters['like_feed'] += 1

		return [True]

	def organise_profile(self, data):

		# --- checks news feed for users and adds them to profile object ---

		#print json.dumps(self.profile.profile, indent=3)

		self.console_log('Checking the profiles of those you follow:\n + Checked users:\,')

		user_names = list(set([post['username'] for post in data if post['username'] not in self.users_checked_today]))
		if len(user_names) > 1:
			users_data = [check_user(self.pull, self.insta_urls['user'], user) for user in user_names]
			for user in users_data[:-1]:
				self.console_log('%s, \,' %(user['data']['username']))
			self.console_log('%s.' %(users_data[-1]['data']['username']))

			for user in users_data:
				self.users_checked_today.append(user['data']['username'])
				if user['follower'] and not user['fake']:

					# --- add user to your followers list in profile ---

					if not any(user['data']['user_id'] == node['user_id'] for node in self.profile.profile['followers']):
						self.profile.add_follower(user['data'])

					else:
						self.profile.update_user(user['data'], 'followers')

					# --- remove from bucket if they are going to be unfollowed --- 
					
					if any(user['data']['user_id'] == user_id[0] for user_id in self.bucket['explore']['unfollow']):
						for i, user_id in enumerate(self.bucket['explore']['unfollow']):
							if user['data']['user_id'] == user_id[0]:
								self.console_log(' - %s followed you back - \,' %(user['data']['username']))
								del self.bucket['explore']['unfollow'][i]
								self.console_log('removed from unfollow list')
								break

					# --- if user has been unfollowed, follow back ---

					if any(user['data']['user_id'] == user_id[0] for user_id in self.bucket['explore']['done']['unfollow']):
						for i, user_id in enumerate(self.bucket['explore']['done']['unfollow']):
							if user['data']['user_id'] == user_id[0]:
								self.console_log(' - %s followed you back but was unfollowed - \,' %(user['data']['username']))
								del self.bucket['explore']['done']['unfollow'][i]
								try:
									response = post_data(self.pull, self.insta_urls['follow'], user['data']['user_id'], False)
									if response['response'].ok:
										self.console_log('followed back!')

									else:
										self.console_log('ERROR %s while following back' %(response['response'].status_code))
								
								except:
									self.console_log('ERROR while following back')
								break

				# --- unfollow if user is fake ---

				elif user['fake']:
					self.console_log(' - %s is a fake account - \,' %(user['data']['username']))
					for i, user_id in enumerate(self.bucket['explore']['unfollow']):
						if user['data']['user_id'] == user_id[0]:
							response = self.explore_operation('unfollow', user_id)
							if response[0]:
								self.console_log('unfollowed!')
							
							else:
								self.console_log('ERROR %s while unfollowing' %(response[1]))
							break

				# --- add user to follow list in profile ---

				if not any(user['data']['user_id'] == node['user_id'] for node in self.profile.profile['follows']):
					self.console_log(' - %s will be added to follow list in profile' %(user['data']['username']))
					self.profile.add_follow(user['data'])

				else:
					self.profile.update_user(user['data'], 'follows')

		else:
			self.console_log('all users have already been checked for today.')
		
	# === END MAIN LOOP

	# === CONSOLE LOG ===

	def console_log(self, statement):

		# --- logs all bot activity and prints to terminal ---

		if statement == 'START':
		
			print self.header
			self.console_tmp = ''
			return

		if statement.endswith('\,'):
		
			log = statement.replace('\,', '')
		
			if self.console_tmp:
				try:
					self.console_tmp += log
				except:
					pass
		
			else:
				self.console_tmp = log

			print log,

		else:
		
			log = statement
		
			if self.console_tmp:
				statement = self.console_tmp + statement
				self.console_tmp = ''

			self.activity_log.append([statement.strip()])

			print log

		self.back_up()

# === END ===