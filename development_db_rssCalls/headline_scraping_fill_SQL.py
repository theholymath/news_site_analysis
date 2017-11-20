#!/usr/bin/env python
import json
import pymysql
import datetime
import feedparser
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import pprint as pprint
#import matplotlib.pyplot as plt 
import newsite_db_class as db_conn

from os import path
from PIL import Image
from bs4 import BeautifulSoup  
from wordcloud import WordCloud, STOPWORDS

# encoding: utf-8

f = '%Y-%m-%d %H:%M:%S'
#now = datetime.datetime.now()
#now.strftime(f) 

## script
## open news feed dictionary - contains url's, etc.
with open('news_feed_dict.json', 'r') as fp:
    news_feed_dict = json.load(fp)

    # http://guides.lib.umich.edu/c.php?g=637508&p=4462444
    
    
# from https://stackoverflow.com/questions/6327146/how-to-find-rss-feed-of-a-particular-website
def get_rss_feed(website_url):
    if website_url is None:
        print("URL should not be null")
    else:
        source_code = requests.get(website_url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text)
        for link in soup.find_all("link", {"type" : "application/rss+xml"}):
            href = link.get('href')
            print("RSS feed for " + website_url + "is -->" + str(href))
            return 
        print("Nothing found")
# get_rss_feed("http://www.breitbart.com/") 

from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# fill database with source reference
def fill_source_table_DB():
    DB_instance = db_conn.databaseInterface()
    
    for politics in news_feed_dict.keys():
        for name in news_feed_dict[politics]:
            sql_info = [politics,
                        news_feed_dict[politics][name]["url"],
                        name,
                        news_feed_dict[politics][name]["feed_url"]
                       ]
            DB_instance.insert_into_sources(sql_info)
    return True

def add_headlineText_to_DB(rss_feed_list,DB_instance):
    for site in rss_feed_list:
        #print(site)
        d = feedparser.parse(site)
        now = datetime.datetime.now()
        time_to_enter = now.strftime(f)

        for k in range(len(d.entries)):
            title_text = d.entries[k]['title']
            summary_text = d.entries[k]['summary']
            summary_text = summary_text.encode()

            sql_info = [time_to_enter,
                        title_text,
                        summary_text,
                        str(site)]

            DB_instance.insert_into_source_data(sql_info)
      

# start parsing
test_feeds = []
conservative_rss_feeds = [str(news_feed_dict['C'][key]['feed_url']) for key in news_feed_dict['C'].keys()]
liberal_rss_feeds = [str(news_feed_dict['L'][key]['feed_url']) for key in news_feed_dict['L'].keys()]
russia_today = ['https://www.rt.com/rss/'] 

# fill another snapshot of headlines and summaries for all sites
DB_instance = db_conn.databaseInterface()
feed_lists = [conservative_rss_feeds,liberal_rss_feeds,russia_today]

for feed_list in feed_lists:
    add_headlineText_to_DB(feed_list,DB_instance)
