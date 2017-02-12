#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ___        InstaBot V 1.0.1 by nickpettican           ___
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

from lxml import etree
import json, itertools, socket, random, time

# === INSTAGRAM FUNCTIONS ===

def refill(user_id, data, bucket, friends, tags_to_avoid, enabled, mode):
	
	# --- refill the bucket - returns dict with ---

	if mode == 'feed' and data:
	
		if enabled['like_feed']:
	
			bucket['feed']['like'].extend([[i['media_id'], i['username'], i['user_fullname']] for i in data 
											if any(n.lower() == i['username'].lower() for n in friends) 
											if not user_id == i['user_id']
											if not any(n == i['media_id'] for n in bucket['feed']['done'])
											if not any(n in i['caption'] for n in tags_to_avoid)])
	
	if mode == 'explore' and data['posts']:

		tmp = [['like', 'media_id'], ['follow', 'user_id'], ['comment', 'media_id']]
		params = [param for param in tmp if enabled[param[0]]]

		for param in params:
			if param:
	
				bucket[mode][param[0]].update([i[param[1]] for i in data['posts'] if not user_id == i['user_id']
											if not any(i[param[1]] in n for n in bucket[mode]['done'][param[0]]) 
											if not any(n in i['caption'] for n in tags_to_avoid)])

	elif mode == 'explore' and not data['posts']:
		raise Exception('No posts found')

	return bucket

def media_by_tag(pull, tag_url, tag, media_max_likes, media_min_likes):
	
	# --- returns list with the 14 'nodes' (posts) for the tag page ---
	
	result = {'posts': False, 'tag': tag}
	
	try:
	
		explore_site = pull.get(tag_url %(tag))
		tree = etree.HTML(explore_site.text)
		identifier = 'window._sharedData = '
	
		for a in tree.findall('.//script'):
	
			try:
				if a.text.startswith(identifier):

					nodes = json.loads(a.text.replace(identifier, '')[:-1])['entry_data']['TagPage'][0]['tag']['media']['nodes']
					result['posts'] = [{'user_id': n['owner']['id'], 'likes': n['likes']['count'], 'caption': n['caption'], 'media_id': n['id']} 
										for n in nodes if media_min_likes <= n['likes']['count'] <= media_max_likes if not n['comments_disabled']]
					break
	
			except:
				continue
	except:
		print '\nERROR in obtaining media by tag'
			
	return result

def news_feed_media(pull, url, user_id):
	
	# --- returns the latest media on the news feed ---
	
	posts = False
	
	try:
		news_feed = pull.get(url)
		tree = etree.HTML(news_feed.text)
		identifier = 'window._sharedData = '
		
		for a in tree.findall('.//script'):

			try:
				if a.text.startswith(identifier):
					nodes = json.loads(a.text.replace(identifier, '')[:-1])['entry_data']['FeedPage'][0]['feed']['media']['nodes']
					break

			except:
				continue

		if nodes:

			posts = []

			for n in nodes:
				if not n['owner']['id'] == user_id:

					try:
						post = {'user_id': n['owner']['id'], 
								'username': n['owner']['username'], 
								'likes': n['likes']['count'], 
								'caption': n['caption'], 
								'media_id': n['id'], 
								'user_fullname': n['owner']['full_name']}
						posts.append(post)
					except:
						continue

	except:
		print '\nERROR getting news feed media.'
	
	return posts

def check_user(pull, url, user):

	# --- checks the users profile to assess if it's fake ---

	result = {
	'fake': False, 'active': False, 'follower': False, 'data': {
		'username': '', 'user_id': '', 'media': '', 'follows': 0, 'followers': 0
	}}

	try:
		site = pull.get(url %(user))
		tree = etree.HTML(site.text)
		identifier = 'window._sharedData = '
		data = False
		
		for a in tree.findall('.//script'):
			try:
				if a.text.startswith(identifier):
					data = json.loads(a.text.replace(identifier, '')[:-1])['entry_data']['ProfilePage'][0]['user']
					break

			except:
				continue

		if data:
			if data['follows_viewer'] or data['has_requested_viewer']:
				result['follower'] = True

			if data['followed_by']['count'] > 0:
				if data['follows']['count'] / data['followed_by']['count'] > 2 and data['followed_by'] < 10:
					result['fake'] = True
			else:
				result['fake'] = True

			if data['followed_by']['count'] > 0:
				if data['follows']['count'] / data['media']['count'] < 10 and data['followed_by']['count'] / data['media']['count'] < 10:
					result['active'] = True

			result['data'] = {
				'username': data['username'],
				'user_id': data['id'],
				'media': data['media']['count'],
				'follows': data['follows']['count'],
				'followers': data['followed_by']['count']
			}

	except:
		print '\nERROR getting user data.'

	time.sleep(5*random.random())
	return result
	
def generate_comment():
	
	# --- returns a randomly generated generic comment ---

	batch = list(itertools.product(

			['Cool', 'Sweet', 'Awesome', 'Great'], 
			['😄', '🙌', '👍', '👌', '😊'], 
			['.', '!', '!!', '!!!']))
	
	return ' '.join(random.choice(batch))

def post_data(pull, url, identifier, comment):

	# --- sends post request ---

	result = {'response': False, 'identifier': identifier}

	try:

		if comment:
			response = pull.post(url %(identifier), data= {'comment_text': comment})

		else:
			response = pull.post(url %(identifier))

		result['response'] = response

	except:
		pass

	return result	