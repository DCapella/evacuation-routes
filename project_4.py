## Haya Toumy - https://hayatoumy.github.io/hayatoumy/ 

## Action Plan: 
# 1. Get traffic updates during hurricane Harvey. 
# 2. Get recent traffic updates from Houston area
# 3. Get random tweets from various topics other than traffic 

import requests
import json 
import pandas as pd
from time import sleep

# !pip install tweepy

# inserting authentication keys for the twitter API
with open('./consumer_key.txt') as f1:
    consumer_key = f1.read().strip()
with open('./consumer_secret.txt') as f2:
    consumer_secret = f2.read().strip()
with open('./access_token.txt') as f3:
    access_token = f3.read().strip()
with open('./access_token_secret.txt') as f4:
    access_token_secret = f4.read().strip()

# setting up the library, and autherizations
import tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# using GetOldTweets-python library by Jefferson Henrique, found on GitHub
# !pip install -r requirements.txt
import got3 # it's got for python 2, which is more stable, according to the author. But got3 works just fine for me

# requesting the traffic updates tweets during Harvey
harveyCriteria = got3.manager.TweetCriteria().setUsername("houstontranstar").setSince("2017-08-17").setUntil("2017-09-03").setMaxTweets(9999)
harvey_tweet = got3.manager.TweetManager.getTweets(harveyCriteria)

# making a data frame:
def make_dataframe(tweet_object):
    """
    Takes one argument: tweet_object, and returns a dataframe with most important info from tweets.
    The tweet_object is collected using GetOldTweets-python library, by Jefferson Henrique.  
    """
    df = pd.DataFrame(columns = ['id', 'tweets', 'date', 'location'])
    
    for i in range(len(tweet_object)-1):
        # get tweets text
        tweets = i.text
        # collect dates of tweets
        try: 
            date = i.formatted_date
        except: 
            date = i.created_at
        # collect location if possible. Most tweets don't have location.
        try:
            location = i.geo['coordinates']
        except: 
            try: 
                location = i.coordinates
            except: 
                location = 'NaN'
        # get tweet id        
        tweet_id = i.id # by the way, tweet_id is included in the permalink

        # make the df        
        df.loc[len(df)] = [tweet_id, tweets, date, location] # inside the loop, building the df row by row
        
    return df
    
harvey = make_dataframe(harvey_tweet)
# saving the data frame to csv
harvey.to_csv('harvey_tweets.csv', index = False)
#==============================================================================================

# collect other random recent tweets from Houston and Austin, and produce a data frame: 
def gather_tweets(handle:str, n=300):
    """
    handle: name of the Twitter user page, passed as string!
    n: how many tweets you want. can't get more than 200 
    retrieves only recent tweets
    """
    tweets_everything = api.user_timeline(handle, count = n)
    df = pd.DataFrame(columns = ['id', 'tweets', 'date', 'location'])
    
    for i in tweets_everything:
        # get tweets text
        tweets = i.text
        # get the dates
        try: 
            date = i.formatted_date
        except: 
            date = i.created_at
        # get the location. Most tweets don't have a location.
        try:
            location = i.geo['coordinates']
        except: 
            try: 
                location = i.coordinates
            except: 
                location = 'NaN'
        # get tweet id        
        tweet_id = i.id # by the way, tweet_id is included in the permalink

        # build the df row by row        
        df.loc[len(df)] = [tweet_id, tweets, date, location] # inside the loop, building the df row by row
        
    return df
#----------------------------------------------------------------------------------------
midtown_houston = gather_tweets("midtownHOU")

houston_public_media = gather_tweets("HoustonPubMedia")
 
houston_biz_journal = gather_tweets("HOUBizJournal")
 
houston_press = gather_tweets("HPStreet")

houston_oem = gather_tweets("HoustonOEM") # office of emergency management

houston_downtown = gather_tweets("DowntownHouston")

houston_visit = gather_tweets("VisitHouston")

houston_link = gather_tweets("LINK_Houston")

houston_rockets = gather_tweets("HoustonRockets")

houston_library = gather_tweets("houstonlibrary")

houston_fashionx = gather_tweets("fashionxhouston")

fashion = gather_tweets("TwitterFashion")

nyt_fashion = gather_tweets("NYTFashion")

music_austin = gather_tweets("musicaustin")

music_foundation_austin = gather_tweets("austinmusic")

apple_music_austin = gather_tweets("austinmusicppl")

austin_tech = gather_tweets("ATXTechEvents")

austin_tech_alliance = gather_tweets("AustinTechAll")

austin_capital_factory = gather_tweets("AustinTechLive")

austin_built_in = gather_tweets("BuiltInAustin")

austin_girls_tech = gather_tweets("GirlsinTechATX")

# combining all non-traffic frames into one:
recent_non_traffic = pd.concat([midtown_houston , houston_public_media, houston_biz_journal, houston_press, 
                                houston_oem, houston_downtown, houston_visit, houston_link, houston_rockets, 
                                houston_library, houston_fashionx, 
                               fashion, nyt_fashion, music_austin, music_foundation_austin, apple_music_austin, 
                               austin_tech, austin_tech_alliance, austin_capital_factory, austin_built_in,
                               austin_girls_tech],
         sort = False).reset_index(drop = True)

# create a new column specifiying the class as "non-traffic". So I can train my model on
recent_non_traffic['tag'] = 'non-traffic' # for later classification purposes

# saving it to csv to easily retrieve:
recent_non_traffic.to_csv("recent_non_traffic.csv", index = False)
#======================================================================================================

# Collecting recent_traffic tweets, from TotalTrafficHOU (similar to houstontranstar)
traffic_tth_Criteria = got3.manager.TweetCriteria().setUsername("TotalTrafficHOU").setSince("2019-03-01").setUntil("2019-04-16").setMaxTweets(9999)
traffic_tth_tweet = got3.manager.TweetManager.getTweets(traffic_tth_Criteria)

# making the data frame, adding a tag column, and saving it to csv
total_traffic_houston = make_dataframe(traffic_tth_tweet)
total_traffic_houston['tag'] = 'traffic'
total_traffic_houston.to_csv("total_recent_traffic_houston.csv", index = False) 
#=============================================================================================================
#=============================================================================================================
#### Building the function: Goal 2:
#-----------------------------------
# Searching the live tweets from two major traffic Twitter users in Houston 
def traffic(users = ["TotalTrafficHOU", "houstontranstar"]):
    """
    This function takes an input a street name, and return the most live recent tweets from the traffic data frame.
    Enter street name in all any case you like, upper, lower, mix..
    
    parameters: 
    users: a list of actual Twitter user names (found after the @ in their homepage on Twitter)
    
    """
    print('WARNING: If no users were passed, it will search Houston, TX traffic by default')
    
    if users == []:
        users = ["TotalTrafficHOU", "houstontranstar"]
        print("Empty users list passed; changed to default: Houston, TX traffic")
        
    s = input('What street you want to find? ')
    
    # getting the df, in case there's more than 2 users: 
    lst = []
    for u in users: 
        lst.append(gather_tweets(u))
        
    df = pd.concat(lst, 
              axis = 0, sort = False)
    
    mask = df['tweets'].str.contains(s, case = False) # case = False makes it not case sensitive!

    
    return df.loc[mask, 'tweets'].values[:15]
# the tweets are ordered most recent first by nature; the first 15 tweets are the most recent. 
# since the resutls are not perfect, one will have information about other streets too