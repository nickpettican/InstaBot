# InstaBot 1.0.3
Automate your Instagram activity with InstaBot - a customisable bot that likes, follows and comments

## Synopsis

InstaBot is a Python-based automated Instagram bot made for **Social Media Marketing Campaigns** in order to reach the desired audience while saving time and money. 

InstaBot will:

* **Like**, **comment** and **follow** (and **unfollow**) those users you want to reach. 
* It does so by seeking out **media tagged with the hashtags you want** while **excluding those you don't want**. To do so you will need to fill out `input/tags.csv` and `input/tags_to_avoid.csv`. 
* Additionally, every hour it will **like** 5 of **your friend's posts on your news feed** (contact me if you want to change this amount). You will need to tell InstaBot who your friends are by filling out `input/friends.csv`. 
* InstaBot also **builds a `profile`** from the media in your feed in order to **map out your "followers" and "following"** as well as to **calculate which profiles you followed are fake** and **which profiles you followed are now following you back**. Those that are fake will be unfollowed. Those that followed you back will be removed from the "unfollow list", and will not be unfollowed. Alternatively, if they were unfollowed recently, they will be followed back. 

You can:

* Set the bot to run all day
* Set to start and stop at set times e.g. 07:00 to 23:00.

*Please be aware that the bot works on 24-hour military time*, so you should input 09:00 to have it start at 9am. If you switch it on halfway through the day and have it on for just 12 hours a day, it will calculate how many operations it would have completed by then and finish off. This is to avoid doing 12 hours worth of operations in just 5.

If you need to shut it down: 

* If you are still following people, it will unfollow them as quickly as it can.

> Unfollowing very quickly will risk a ban, so InstaBot takes 30-60 second breaks. 
* If you can't wait, InstaBot will save the current following to a backup file, and next time you switch it on it will unfollow them first.

Internet connection breaks? 
* No problem. InstaBot will wait until your internet connection is back in order to continue.

## Motivation

Digital Marketing is becoming more and more complicated, with new platforms coming out and newer and better competitors appearing left right and center. InstaBot was created in order to save the time of having to reach out to the potential audience by liking posts and following those that will be interested in your service. Not everyone on Instagram is actively seeking out interesting profiles on the 'explore' tab, so in order to reach them, a like and a follow might be enough to spark that extra interest for them to visit your profile.

## Installation

To get you started, first clone or download the repository. Make sure you have all the libraries installed:

* Requests 
* Arrow
* lxml

`pip install name_of_library` or `sudo pip install name_of_library` will do the trick.

Once that's done, open the `config` file and insert your credentials and preferences:

|	Variables   		|	Defaults   				|	Explanation 															|
|:---------------------:|:-------------------------:|:------------------------------------------------------------------------	|
|	username			|	username				|	Your Instagram username													|
|	password			|	password	 			|	Your Instagram password													|
|	friends				|	input/friends.csv		|	Friends file - alternatively you can use ['friend1', 'friend2',...]		|
|	tags 		 		|	input/tags.csv			|	Tags file - alternatively you can use ['tag1', 'tag2', 'tag3',...]		|
|	tags_to_avoid		|	input/tags_to_avoid.csv	|	Tags to avoid file - you can also use ['tagx', 'tagy',...]				|
|	like_news_feed		|	true 					|	`true` or `false` whether you want to like your friends' posts			|
|	likes_in_day	 	|	500						|	Number of likes InstaBot will do in a day 								|
|	media_max_likes		|	50 						|	Maximum number of likes a post will have for InstaBot to like it 		|
|	media_min_likes		|	0	 					|	Minimum number of likes a post will have for InstaBot to like it 		|
|	follow_in_day		|	50						|	Number of users it will follow per day 							 		|
|	unfollow 			|	true					|	`true` or `false` whether you want to unfollow users					|
|	follow_time_hours	|	6			 			|	Time (in hours) it will follow these users for 				 			|
|	comments_in_day		|	0						|	Number of comments it will leave per day								|
|	bot_start_at 		|	07:00 					|	Time when InstaBot will start 											|
|	bot_stop_at 		|	23:00 					|	Time when InstaBot will stop 										 	|

Now all you have to do is go to the parent directory and type in the terminal `python run.py`

## Server

If you haven't got a server I find a Raspberry Pi works just fine. All you need is to download the files into the Pi, install the libraries and run the bot.

## Warnings

> Instagram does not like spam or bulk liking and following, so *keep the likes per day bellow 1000 in a 24 hour period*, meaning if you use the bot for 12 hours a day, I would suggest only setting the likes to 500 or you might risk a ban. When bulk unfollowing you only get 15 unfollows in a short time period, so if you yourself do a bulk unfollowing on your own, you risk InstaBot not being able to unfollow for a couple of hours.

> Choose your tags wisely, and monitor the posts you are liking in case InstaBot likes unappropriate posts.

> Don't rely on InstaBot as your only Social Media Digital Marketeer, Social Media is a two-way conversation, it's a way to gain an audience and talk to them, not a means to sell.