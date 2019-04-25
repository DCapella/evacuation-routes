from app import db

from app import KeysAPI

from flask import send_file

import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup

import pandas as pd

import tweepy

from io import BytesIO
from PIL import Image
from urllib import request



class Address(db.Model):
    address = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    address_from = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)

    def __repr__(self):
        return f'<Address: {self.address}>'


                         ########################################################################
                         ############################# !!! News !!! #############################
                         ########################################################################

class NewsAPI():


    def __init__(self):
        self.key = KeysAPI.newsapi

    def main(self, city_name='Austin'):
        """Engine to gather all texts from different news and blogs for road closure.
        
        Parameters
        ----------
        city_name : string
            Contains the city that you are in; if none given, default is Austin.
            
        Returns
        -------
        texts : list
            Contains a list of all texts that have road closure in it.
        
        """
        date = datetime.now()
        date_format = f"{date.year}-{date.month}-{date.day}"
        
        BASE_URL = "https://newsapi.org/v2/everything/"

        params = {
            'q': city_name,
            'apiKey': self.key,
            'from': date_format,
            'to': date_format,
        }

        response = requests.get(BASE_URL, params)

        articles = response.json()['articles']
        urls = self.get_urls(articles)
        texts = self.use_urls(urls)
        return texts

    def get_urls(self, articles):
        """Simply extracts the urls.
        
        Paramters
        ---------
        articles : list
            List of objects that contain an attribute url.
        
        Returns
        -------
        urls : list
            List of extracted urls.
        
        """
        urls = []
        for article in articles:
            urls.append(article['url'])
        return urls

    def use_urls(self, urls):
        """Extracts text from each website.
        
        Paramters
        ---------
        urls : list
            A list of urls.
        
        Returns
        -------
        texts : list
            A list of extracted texts from given urls.
        
        """
        count = 0
        texts = []
        for url in urls:
            response = requests.get(url)

            if response.status_code == 200:
                text = self.get_texts(response)
                if len(text) != 0:
                    texts.append(text)
            else:
                count = count + 1
        print(f"There was {count} error(s).")
        return texts

    def get_texts(self, response):
        """Extracts the text from the p element.
        
        Paramters
        ---------
        response : Response object
            e.g. response = requests.get(url)
        
        Returns
        -------
        texts : list
        
        """
        soup = BeautifulSoup(response.content, 'lxml')
        paragraphs = soup.find_all('p')
        texts = []
        for p in paragraphs:
            text = p.text
            text = self.process(text)
            if text != '':
                texts.append(text)
        
        return texts

    def process(self, text):
        """Grabs everything after road closure, inclusively.
        
        Paramters
        ---------
        text : string
            A single string of text.
        
        Returns
        -------
        matches[0] : string
            If there is a match, then it will return the string begining with road closure.
        '' : string
            Returns empty string if there is not a match.
        
        """
        
        regex = r"road .*"
        matches = re.search(regex, text, re.MULTILINE | re.IGNORECASE)
        if matches is not None:
            return matches[0]
        
        return ''

                         ########################################################################
                         ############################# !!! HERE !!! #############################
                         ########################################################################

class HereAPI:
    """Interacts with the HereAPI specifically for evacuation-routes"""
    address_1 = None
    address_2 = None
    lat_1 = None
    long_1 = None
    lat_2 = None
    long_2 = None
    geo = None
    alt_lat = None
    alt_long = None
    summary = None
    flags = None
    set_map = None
    instructions = None
    testing = None
    
    def __init__(self):
        self.APP_ID = KeysAPI.here_id
        self.APP_CODE = KeysAPI.here_code
        
    def main(self, a, b='Austin, TX', alt=0, input_self=False):
        """Gets travel summary"""
        if input_self:
            search = input("Address 1\n>>>> ")
            search_2 = input("Address 2\n>>>> ")
        else:
            search = a
            search_2 = b

        lat, long, lat_2, long_2 = self.get_geo(search, search_2)
        
        self.lat_1, self.long_1, self.lat_2, self.long_2 = lat, long, lat_2, long_2
        self.address_1 = a
        self.address_2 = b
        
        return self.get_route(lat, long, lat_2, long_2, alt=alt)
    
    def get_geo(self, search_text_1, search_text_2='Austin, TX'):
        """Calculates route

        Parameters
        ----------
        search_text_1 : string
            Address in format [number street, city, state zipcode]

        search_text_2 : string
            Address in format [number street, city, state zipcode]

        Returns
        -------
        lat : float
            First geographic latitude location.

        long : float
            First geographic longitude location.

        lat_2 : float
            Second geographic latitude location.

        long_2 : float
            Second geographic longitude location.

        Note
        ----
        If you only need one set of cordinates then do: get_get()[:2]

        """

        BASE_GEO = "https://geocoder.api.here.com/6.2/geocode.json"

        params_geo = {
            "app_id": self.APP_ID,
            "app_code": self.APP_CODE,
            "searchtext": search_text_1,
        }

        req = requests.get(BASE_GEO, params=params_geo)
        info = req.json()["Response"]

        lat, long = info['View'][0]["Result"][0]["Location"]["DisplayPosition"].values()

        params_geo['searchtext'] = search_text_2

        req = requests.get(BASE_GEO, params=params_geo)
        info = req.json()["Response"]

        lat_2, long_2 = info['View'][0]["Result"][0]["Location"]["DisplayPosition"].values()

        return (lat, long, lat_2, long_2)
    
    def get_route(self, lat, long, lat_2, long_2, alt=0):
        """Calculates route

        Parameters
        ----------
        lat : float
            First geographic latitude location.

        long : float
            First geographic longitude location.

        lat_2 : float
            Second geographic latitude location.

        long_2 : float
            Second geographic longitude location.

        Returns
        -------
        info : dict

        """
        BASE_ROUTING = "https://route.api.here.com/routing/7.2/calculateroute.json"

        params_routing = {
            "app_id": self.APP_ID,
            "app_code": self.APP_CODE,
            "waypoint0": "geo!" + str(lat) + "," + str(long),
            "waypoint1": "geo!" + str(lat_2) + "," + str(long_2),
            "mode": "fastest;car;traffic:enabled",
            "alternatives": alt
        }

        req = requests.get(BASE_ROUTING, params=params_routing)

        info = req.json()['response']

        return info
    
    def get_alt_routes(self, results, save_df=False, df_as='lat_long_routes.csv'):
        """Grabs all the geo locations for all the routes

        Parameters
        ----------
            results : dictionary
                From request.
            save_df : boolean, optional, default True
            df_as : string, optional, default 'routes.csv'

        Returns
        -------
            df : Pandas DataFrame
                Contains latitude and longitude from routes.

        """
        regex = r"(.*?)\<.*?\>"
        
        lat_long = []
        instructions = []
        self.testing = results['route']

        for count, j in enumerate(results['route']):
            for i in j['leg'][0]['maneuver']:
                instruction = i['instruction']
                
                lat_long.append([i['position']['latitude'], i['position']['longitude'], count])
                
                mystring = instruction
                result = re.findall(regex, mystring)
                instruction = ''.join(result)
                
                instructions.append([instruction, count])

        df = pd.DataFrame(lat_long, columns=['lat', 'long', 'route'])
        df_instruction = pd.DataFrame(instructions, columns=['instruction', 'route'])

        if save_df:
            df.to_csv(df_as, index=False)
            df_instruction.to_csv('instructions.csv', index=False)

        return df, df_instruction
    
    def get_summary(self, results, save_df=False, df_as='summary_routes.csv', only_flags=False):
        """Grabs the summary from each route

        Parameters
        ----------
            results : dictionary
                From request
            save_df : boolean, optional, default True
            df_as : string, optional, default 'routes.csv'

        Returns
        -------
            Pandas DataFrame

        """
        temp = []
        # flags = []
        for i, route in enumerate(results['route']):
            traffic_time = (route['summary']['trafficTime'] - route['summary']['baseTime']) / 60
            total_time = route['summary']['travelTime'] / 60
            flags = ', '.join(route['summary']['flags'])

            temp.append([i, traffic_time, total_time, flags])
            # flags.append(flags)

        df =  pd.DataFrame(temp, columns=['route', 'traffic_time', 'total_time', 'flags']).sort_values(by='total_time')

        if save_df:
            df.to_csv(df_as, index=False)

        # if only_flags:
        #     return flags
        return df
    
    def get_map(self):
        """UNAUTHORIZED"""
        # https://image.maps.api.here.com/mia/1.6/routing?c=1652B4&lw=6&t=0&ppi=320&w=400&h=600
        # BASE = 'https://image.maps.api.here.com/mia/1.6/routing'
        
        # params = {
            # "app_id": self.keys.APP_ID,
            # "app_code": self.keys.APP_CODE,
            # "waypoint0": [self.lat_1, self.long_1],
            # "waypoint1": [self.lat_2, self.long_2],
            # "c": "1652B4",
            # "lw": 6,
            # "t": 0,
            # "ppi": 320,
            # "w": 400,
            # "h": 600,
        # }
        
        # response = requests.get(BASE, params)
        # return response
    
    def fit(self, address_1, address_2, alt=0):
        """Grabs both dataframes

        Parameters
        ----------
            address_1 : string
            address_2 : string
            alt : int, optional, default = 0
                Alternate routes

        Returns
        -------
            geo : Pandas DataFrame
            summary : Pandas DataFrame

        """
        results = self.main(address_1, address_2, alt=alt)
        geo, instructions = self.get_alt_routes(results)
        summary = self.get_summary(results)
        
        self.geo = geo
        self.alt_lat = self.geo['lat']
        self.alt_long = self.geo['long']
        self.summary = summary
        self.flags = self.summary['flags']
        self.instructions = instructions
        # self.set_map = self.get_map()


                         ######################################################################
                         ########################### !!! Tweets !!! ###########################
                         ######################################################################

class LiveTrafficTweets:
    auth = tweepy.OAuthHandler(KeysAPI.tweet_1, KeysAPI.tweet_2)
    auth.set_access_token(KeysAPI.tweet_3, KeysAPI.tweet_4)
    
    api = tweepy.API(auth, wait_on_rate_limit=True) 
    
    def __init__(self):
        # self.api = api
        pass

    
    def gather_tweets(self, handle:str, n=300):
        """
        Returns the most recent tweets (up to 200), from the selected Twitter username (handle)
        
        Parameters:
        -----------
        handle: name of the Twitter user page
        n: how many tweets you want. can't get more than 200 
        retrieves only recent tweets
        """
        tweets_everything = self.api.user_timeline(handle, count = n)
        df = pd.DataFrame(columns = ['id', 'tweets', 'date', 'location'])
        
        for i in tweets_everything:
            tweets = i.text
            try: 
                date = i.formatted_date
            except: 
                date = i.created_at
            
            try:
                location = i.geo['coordinates']
            except: 
                try: 
                    location = i.coordinates
                except: 
                    location = 'NaN'
                    
            tweet_id = i.id # by the way, tweet_id is included in the permalink
                    
            df.loc[len(df)] = [tweet_id, tweets, date, location] # inside the loop, building the df row by row
            
        return df
    
    # def get_twitter_user_names(self, city_name, df = data_f):
    #     """
    #     Returns the Twitter user names that you can plug later in the function: traffic, that get twitter updates.
        
    #     Parameters:
    #     ----------
    #     city_name: Enter the city name, state. All small letters, in this format. Example: "round rock, texas".
    #     df: the dataframe of city names and their traffic Twitter user names.
    #     """

    #     temp_df = data_f
    #     temp_df.columns = [col.lower() for col in temp_df.columns]
    #     try: 
    #         mask = temp_df[city_name].notna()
    #         return list(temp_df.loc[mask, city_name])
    #     except KeyError: 
    #         print(f'This City Does Not Have Twitter User Names Yet. Try From This List: {temp_df.columns}')

        
    def traffic(self, s, users = ["TotalTrafficHOU", "houstontranstar"]):
        """
        This function takes an input a street name, and return the most live recent tweets from the traffic data frame.
        Enter street name in all any case you like, upper, lower, mix..

        Parameters:
        -----------
        users: a list of actual Twitter user names (found after the @ in their homepage on Twitter)

        """
        print('WARNING: If no users were passed, it will search Houston, TX traffic by default')

        if users == []:
            users = ["TotalTrafficHOU", "houstontranstar"]
            print("Empty users list passed; changed to default: Houston, TX traffic")

        # s = input('What street you want to find? ')

        # getting the df, in case there's more than 2 users: 
        lst = []
        for u in users: 
            lst.append(self.gather_tweets(u))

        df = pd.concat(lst, 
                  axis = 0, sort = False)

        # mask = df['tweets'].str.contains(s, case = False) # case = False makes it not case sensitive!


        # return df.loc[mask, 'tweets'].values[:15]
        # result = df[['tweets', 'location']].values[:15]
        tweets = list(df['tweets'])[:15]
        location = list(df['location'])[:15]
        return tweets, location
        # the tweets are ordered most recent first by nature; the first 15 tweets are the most recent. 
        # since the resutls are not perfect, one will have information about other streets too
