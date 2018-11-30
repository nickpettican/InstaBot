<img src="http://www.nicolaspettican.com/css/img/instabot.png" title="Instabot logo" alt="Instabot logo" width="30%">

# InstaBot 1.3.0

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4c7690e086f54631b169eaa2375d9c31)](https://www.codacy.com/app/nickpettican/InstaBot?utm_source=github.com&utm_medium=referral&utm_content=nickpettican/InstaBot&utm_campaign=Badge_Grade)

-   [InstaBot 1.3.0](#instabot-130)
    -   [Requirements](#requirements)

    -   [In a nutshell](#in-a-nutshell)
        -   [InstaBot will](#instabot-will)
        -   [Instabot runs in two modes](#instabot-runs-in-two-modes)

    -   [How to install](#how-to-install)

    -   [Your input](#your-input)
        -   [Set likes](#set-likes)
        -   [Set comments](#set-comments)
        -   [Follow and unfollow](#follow-and-unfollow)

    -   [Set Instabot to run during the day](#set-instabot-to-run-during-the-day)

    -   [Instabot is smart](#instabot-is-smart)

    -   [Motivation](#motivation)

    -   [Server](#server)

    -   [Future of InstaBot](#future-of-instabot)

    -   [Warnings](#warnings)

Automate your Instagram activity with InstaBot - a customisable bot that likes, follows and comments

InstaBot is a Python-based automated Instagram bot made for **Social Media Marketing Campaigns** in order to reach the desired audience while saving time and money.

All you need is your username and password and other parameters - no API signup is needed.

## Requirements

`Python 2.7` and a server (a Raspberry Pi works great). See installation bellow to install libraries.

## In a nutshell

### InstaBot will

-   [x] **Like** posts of users you want to reach
-   [x] **Comment** on these posts
-   [x] **Follow** users you want to reach
-   [x] **Unfollow** users who don't follow you back within x hours
-   [x] **Like** posts in your news feed - only those you want to
-   [x] **Build a `profile` object** with all your followers and users you follow

### Instabot runs in two modes

-   From XX:XX to YY:YY
-   All day (24/7)

_The bot works on 24-hour military time_, so you should input 09:00 to have it start at 9am.

## How to install

1.  Download and install Python on your computer (a Raspberry Pi will have it pre-installed)
2.  Install dependencies running `pip install -r requirements.txt`. 
3.  [Install lxml](http://lxml.de/installation.html)
4.  `Git clone` this repo or download as a ZIP and extract
5.  Add your input (see bellow)
6.  Run `python run.py`

## Your input

Open the `config` file and insert your credentials and preferences:

    {
    	"username": "username",
    	"password": "password",
    	"timezone": 0,
    	"tags": "input/tags.csv",
    	"tags_to_avoid": "input/tags_to_avoid.csv",
    	"friends": "input/friends.csv",
    	"like_news_feed": true,
    	"likes_in_day": 500,
    	"media_max_likes": 50,
    	"media_min_likes": 0,
    	"follow_in_day": 50,
    	"unfollow": true,
    	"follow_time_hours": 6,
    	"comments_in_day": 0,
    	"comments_list": [["Cool", "Sweet", "Awesome", "Great"],
                      ["😄", "🙌", "👍", "👌", "😊"], 
                      [".", "!", "!!", "!!!"]],
    	"bot_start_at": "07:00",
    	"bot_stop_at": "23:00"
    }

|     Variables     |                                        Defaults                                       | Explanation                                                                                                  |
| :---------------: | :-----------------------------------------------------------------------------------: | :----------------------------------------------------------------------------------------------------------- |
|      username     |                                        username                                       | Your Instagram username                                                                                      |
|      password     |                                        password                                       | Your Instagram password                                                                                      |
|      timezone     |                                           0                                           | Your timezone code, in order to run it at your local time                                                    |
|        tags       |                                     input/tags.csv                                    | Tags file - alternatively you can use \['tag1', 'tag2', 'tag3',...]                                          |
|   tags_to_avoid   |                                input/tags_to_avoid.csv                                | Tags to avoid file - you can also use \['tagx', 'tagy',...]                                                  |
|      friends      |                                   input/friends.csv                                   | Friends file, containing usernames all in one column - alternatively you can use \['friend1', 'friend2',...] |
|   like_news_feed  |                                          true                                         | `true` or `false` whether you want to like your friends' posts                                               |
|    likes_in_day   |                                          500                                          | Number of likes InstaBot will do in a day                                                                    |
|  media_max_likes  |                                           50                                          | Maximum number of likes a post will have for InstaBot to like it                                             |
|  media_min_likes  |                                           0                                           | Minimum number of likes a post will have for InstaBot to like it                                             |
|   follow_in_day   |                                           50                                          | Number of users it will follow per day                                                                       |
|      unfollow     |                                          true                                         | `true` or `false` whether you want to unfollow users                                                         |
| follow_time_hours |                                           6                                           | Time (in hours) it will follow these users for                                                               |
|  comments_in_day  |                                           0                                           | Number of comments it will leave per day                                                                     |
|   comments_list   | \[\["Cool", "Awesome", "Great"], \["😄", "🙌", "👍", "😊"], \[".", "!", "!!", "!!!"]] | What words you want shuffled to post comments                                                                |
|    bot_start_at   |                                         07:00                                         | Time when InstaBot will start                                                                                |
|    bot_stop_at    |                                         23:00                                         | Time when InstaBot will stop                                                                                 |

### Set likes

Tell Instabot how **many posts you want to like per day**. The **maximum** you will get to do before you get **banned** is **1000**, but the default is set at 500 to keep it safe, especially if you're doing a daytime run (7am to 11pm). Instabot will take random time breaks between likes, to make it look more like a real person and not an automated bot. 

    "likes_in_day": 500

Set Instabot to **like your friends posts** so you don't have to. Only the friends usernames you included in the friends list will have their posts liked.

    "friends": "input/friends.csv"
    "like_news_feed": true

You can tell Instabot not to like posts with less than a **minimum like number** or more than a **maximum like number**. This property is useful because you will get **more feedback** from posts with a lower number of likes.

    "media_max_likes": 50
    "media_min_likes": 0

Give Instabot a list of **hashtags** to look for posts to like. I recommend you read [this article](http://www.socialmediaexaminer.com/how-to-use-hashtags-on-instagram-to-grow-your-reach/) for tips on using hashtags. You can either put the tags into `input/tags.csv`, as it is currently the case in the default values:

    "tags": "input/tags.csv"

Or you can insert the tags straight into the config file like this:

    "tags": ['tag1', 'tag2']

You can do the same with your friends list: either leave it as the default and include your friends' usernames in the `friends.csv` file or insert the usernames straight into the config file.

    "friends": "input/friends.csv"

And finally, **negative keywords** are very important. These will help you avoid liking posts you don't want to like. These can be inserted the same way as the tags. The default is for them to be in a file.

    "tags_to_avoid": "input/tags_to_avoid.csv"

### Set comments

Instabot will comment randomly on posts that it liked. The comments are generated through a list of lists that gets shuffled to make a comment. You can add extra lists to increase the comment, or just reduce it to a single list of list e.g. `[['I just want this comment']]`.

    "comments_in_day": 0
    "comments_list": [["Cool", "Sweet", "Awesome", "Great"],
                      ["😄", "🙌", "👍", "👌", "😊"], 
                      [".", "!", "!!", "!!!"]]

### Follow and unfollow

Follow users of posts you liked:

    "follow_in_day": 50

Set the amount of time you want to follow users:

    "follow_time_hours": 6

Set Instabot to unfollow them if they haven't followed you back:

    "unfollow": true

## Set Instabot to run during the day

To make Instabot's activities look more real, you can set the bot to run between set times such as the default 7am to 11pm. Between those times the bot will either sleep or carry on unfollowing users it followed during the day.

    "bot_start_at": "07:00"
    "bot_stop_at": "23:00"

Make sure you use military time.

## Instabot is smart

-   **Before unfollowing** a user, Instabot will **check if that user followed you back**. If that person followed you back, Instabot won't unfollow them. I mean it's only fair. It will also check if users are potentially fake accounts and will unfollow them. If a user was unfollowed recently but followed you back, he/she will be followed back again.
-   **Internet connection breaks?** No problem. InstaBot will wait until your internet connection is back in order to continue.
-   **Need to shut it down quickly but you're still following lots of people?** No problem. Instabot will save a list of the users it followed and will unfollow them next time it's turned on.

## Motivation

Digital Marketing is becoming more and more complicated, with new platforms coming out and newer and better competitors appearing left right and center. InstaBot was created in order to save the time of having to reach out to the potential audience by liking posts and following those that will be interested in your service. Not everyone on Instagram is actively seeking out interesting profiles on the 'explore' tab, so in order to reach them, a like and a follow might be enough to spark that extra interest for them to visit your profile.

## Server

If you haven't got a server I find a Raspberry Pi works just fine. All you need to do is follow the installation guide above and run the bot.

## Future of InstaBot

Instabot is written in Python2, meaning it would need to be translated to Python3. Feel free to fork it and do this yourself.

The stats functionality is something I would also like to work on, but feel free to collaborate to make it happen sooner.

## Warnings

-   Instagram does not like spam or bulk liking and following, so:

> _Keep the likes per day bellow 1000 in a 24 hour period_, meaning if you use the bot for 12 hours a day, I would suggest only setting the likes to 500 or you might risk a ban. 

-   Don't bulk unfollow: 

> You only get 15 unfollows in a short time period, so if you do a bulk unfollowing on your own, you risk InstaBot not being able to unfollow for a couple of hours.

-   Choose your tags wisely, and monitor the posts you are liking:

> In case InstaBot likes unappropriate posts.

-   Don't rely on InstaBot as your only Social Media Digital Marketeer, Social Media is a two-way conversation, it's a way to gain an audience and talk to them, not a means to sell.
