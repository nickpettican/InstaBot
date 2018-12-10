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

from lxml.etree import HTML
from json import loads as toJSON
from random import random, choice
from time import sleep
import itertools

# === INSTAGRAM FUNCTIONS ===


def refill(user_id, data, bucket, friends, tags_to_avoid, enabled, mode):
    # refill the bucket - returns dict with modified bucket

    if mode == 'feed' and data:
        for _post in data:
            bucket['codes'][_post['media_id']] = _post['url_code']
        # add feed posts to bucket
        if enabled['like_feed']:
            bucket['feed']['like'].extend([[_post['media_id'], _post['username']] for _post in data
                                           if any(n.lower() == _post['username'].lower() for n in friends)
                                           if not user_id == _post['user_id']
                                           if not any(n == _post['media_id'] for n in bucket['feed']['media_ids'])
                                           if not any(n[0] == _post['media_id'] for n in bucket['feed']['done'])
                                           if not any(n in _post['caption'] for n in tags_to_avoid)])
            bucket['feed']['media_ids'].extend([_post['media_id'] for _post in data])
    # add explored posts to bucket
    if mode == 'explore' and data['posts']:
        for _post in data['posts']:
            bucket['codes'][_post['media_id']] = _post['url_code']
            bucket['user_ids'][_post['user_id']] = _post['username']
        # just to get the keys right
        tmp = [['like', 'media_id'], [
            'follow', 'user_id'], ['comment', 'media_id']]
        params = [param for param in tmp if enabled[param[0]]]
        # check if posts obbey the rules
        for param in params:
            if param:
                bucket[mode][param[0]].update([_post[param[1]] for _post in data['posts'] if not user_id == _post['user_id']
                                               if not any(_post[param[1]] in n for n in bucket[mode]['done'][param[0]])
                                               if not any(n in _post['caption'] for n in tags_to_avoid)])
    elif mode == 'explore' and not data['posts']:
        raise Exception('No posts found')
    return bucket


def get_node_post_data(
        node,
        media_min_likes,
        media_max_likes,
        browser,
        media_url):
    try:
        if media_min_likes <= node['edge_liked_by']['count'] <= media_max_likes and not node['comments_disabled']:
            return dict(
                user_id=node['owner']['id'],
                username=return_username(
                    browser,
                    media_url,
                    node['shortcode']),
                likes=node['edge_liked_by']['count'],
                caption=node['edge_media_to_caption']['edges'][0]['node']['text'],
                media_id=node['id'],
                url_code=node['shortcode'])
    except BaseException:
        return None


def media_by_tag(
        browser,
        tag_url,
        media_url,
        tag,
        media_max_likes,
        media_min_likes):
    # returns list with the 14 'nodes' (posts) for the tag page

    result = {'posts': False, 'tag': tag}
    try:
        explore_site = browser.get(tag_url % (tag))
        tree = HTML(explore_site.text)
        data = return_sharedData(tree)
        if data:
            nodes = data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
            posts = [get_node_post_data(
                n['node'], media_min_likes, media_max_likes, browser, media_url) for n in nodes]
            result['posts'] = [p for p in posts if p is not None]
    except Exception as e:
        print '\nError in obtaining media by tag: %s' % (e)
    return result


def return_sharedData(tree):
    # returns the sharedData JSON object

    identifier = 'window._sharedData = '
    for a in tree.findall('.//script'):
        try:
            if a.text.startswith(identifier):
                try:
                    return toJSON(a.text.replace(identifier, '')[:-1])
                except Exception as e:
                    print '\nError returning sharedData JSON: %s' % (e)
        except Exception as e:
            continue
    return None


def return_username(browser, media_url, code):
    # returns the username from an image

    try:
        media_page = browser.get(media_url % (code))
        tree = HTML(media_page.text)
        data = return_sharedData(tree)
        if data is not None:
            return data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['owner']['username']
    except Exception as e:
        print '\nError obtaining username: %s' % (e)
    return None


def get_feed_node_post_data(node, user_id):

    try:
        if not node['owner']['id'] == user_id and not node['viewer_has_liked']:
            return dict(
                user_id=node['owner']['id'],
                username=node['owner']['username'],
                likes=node['edge_media_preview_like']['count'],
                caption=node['edge_media_to_caption']['edges'][0]['node']['text'],
                media_id=node['id'],
                url_code=node['shortcode'])
    except BaseException:
        return None


def return_feedData(tree):

    identifier = "window.__additionalDataLoaded('feed',"
    for a in tree.findall('.//script'):
        try:
            if a.text.startswith(identifier):
                try:
                    return toJSON(a.text.replace(identifier, '')[:-2])
                except Exception as e:
                    print '\nError returning sharedData JSON: %s' % (e)
        except Exception as e:
            continue
    return None


def news_feed_media(browser, url, user_id):
    # returns the latest media on the news feed

    try:
        news_feed = browser.get(url)
        tree = HTML(news_feed.text)
        data = return_feedData(tree)
        if data:
            nodes = data['user']['edge_web_feed_timeline']['edges']
            if nodes:
                posts = [get_feed_node_post_data(n['node'], user_id) for n in nodes]
                return [p for p in posts if p is not None]
    except Exception as e:
        print '\nError getting new feed data: %s.' % (e)
    return []


def check_user(browser, url, user):
    # checks the users profile to assess if it's fake

    result = {
        'fake': False,
        'active': False,
        'follower': False,
        'data': {
            'username': '',
            'user_id': '',
            'media': '',
            'follows': 0,
            'followers': 0}}
    try:
        site = browser.get(url % (user))
        tree = HTML(site.text)
        data = return_sharedData(tree)
        user_data = data['entry_data']['ProfilePage'][0]['graphql']['user']
        if user_data:
            if user_data['follows_viewer'] or user_data['has_requested_viewer']:
                result['follower'] = True
            if user_data['edge_followed_by']['count'] > 0:
                try:
                    if user_data['edge_follow']['count'] / user_data['edge_followed_by']['count'] > 2 \
                            and user_data['edge_followed_by']['count'] < 10:
                        result['fake'] = True
                except ZeroDivisionError:
                    result['fake'] = True
                try:
                    if user_data['edge_follow']['count'] / user_data['edge_owner_to_timeline_media']['count'] < 10 \
                            and user_data['edge_followed_by']['count'] / user_data['edge_owner_to_timeline_media']['count'] < 10:
                        result['active'] = True
                except ZeroDivisionError:
                    pass
            else:
                result['fake'] = True
            result['data'] = {
                'username': user_data['username'],
                'user_id': user_data['id'],
                'media': user_data['edge_owner_to_timeline_media']['count'],
                'follows': user_data['edge_follow']['count'],
                'followers': user_data['edge_followed_by']['count']
            }

    except Exception as e:
        print '\nError checking user: %s.' % (e)

    sleep(5 * random())
    return result


def generate_comment(comments_list):
    # returns a randomly generated generic comment

    batch = list(itertools.product(*comments_list))
    return ' '.join(choice(batch))


def post_data(browser, url, identifier, comment):
    # sends post request

    result = {'response': False, 'identifier': identifier}

    try:
        if comment:
            response = browser.post(
                url %
                (identifier), data={
                    'comment_text': comment})
        else:
            response = browser.post(url % (identifier))
        result['response'] = response
    except BaseException:
        pass
    return result
