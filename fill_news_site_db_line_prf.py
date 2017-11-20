import pandas as pd
import feedparser
import requests
#import asyncio
#import aiohttp
import sqlite3
import json
import sys
#import concurrent.futures

import pprint
pp = pprint.PrettyPrinter(indent = 4)

import time
import datetime
form = '%Y-%m-%d %H:%M:%S'

import warnings
warnings.filterwarnings('ignore')

def _create_db_and_initialize_tables():
    # create db
    db = sqlite3.connect('data/NewsSiteRSSFeeds.db')

    # Get a cursor object
    cursor = db.cursor()

    # Note to self - never use python's string operations for db interface: insecure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sources(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, ideology TEXT,
                             url TEXT, rss_feed_url TEXT unique)
                   ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sources_data(id INTEGER PRIMARY KEY AUTOINCREMENT,sources_id INTEGER, date TEXT, title TEXT, summary TEXT)
                   ''')
    db.commit()
    db.close()

def _fill_sources_table(filename):
    # open connection
    db = sqlite3.connect('data/NewsSiteRSSFeeds.db')
    cursor = db.cursor()

    # grab dictionary from json file
    with open(filename) as json_data:
        data = json.load(json_data)

    list_to_commit = []

    # write to database - can't use zip here
    keys = ["C","L","O"]

    for ideology in keys:
        names = data[ideology]

        for name in names:
            tup = (name,ideology,data[ideology][name]["url"],data[ideology][name]["feed_url"])
            list_to_commit.append(tup)

    cursor.executemany('INSERT OR IGNORE INTO sources(name,ideology,url,rss_feed_url) VALUES (?,?,?,?)',list_to_commit)
    db.commit()
    db.close()

def _fill_sources_data_table(filename):
    # open connection
    db = sqlite3.connect('data/NewsSiteRSSFeeds.db')
    cursor = db.cursor()

    list_to_commit = []

    tup = (name,ideology,data[ideology][name]["url"],data[ideology][name]["feed_url"])
    list_to_commit.append(tup)

    cursor.executemany('INSERT OR IGNORE INTO sources_data(sources_id,date,title,summary) VALUES (?,?,?,?)',list_to_commit)
    db.commit()
    db.close()

@profile
def _get_rss_feed_list():
    db = sqlite3.connect('data/NewsSiteRSSFeeds.db')
    cursor = db.cursor()
    rss_feed_list = [url for url in cursor.execute('SELECT rss_feed_url FROM sources')]
    db.close()

    return rss_feed_list

def _get_feedparsed_site(url):
    return feedparser.parse(url)

# old synchronous way to fill db table
@profile
def add_headlineText_to_DB(rss_feed_list):
    # open connection
    db = sqlite3.connect('data/NewsSiteRSSFeeds_test.db')
    cursor = db.cursor()

    now = datetime.datetime.now()
    time_to_enter = now.strftime(form)

    for site in rss_feed_list:
        # get source_id from table of news sources
        sources_id = cursor.execute('SELECT id FROM sources WHERE rss_feed_url = ?',(site)).fetchone()[0]
        d = feedparser.parse(site[0])
        list_to_commit = []
        for entry in d['entries']:
            title   = entry['title'].encode('utf-8')
            summary = entry['summary'].encode('utf-8')
            try:
                published = entry['published']
            except KeyError:
                published = time_to_enter
            tup     = (int(sources_id),published.encode('utf-8'),str(title),str(summary))
            list_to_commit.append(tup)

        #cursor.executemany('INSERT INTO sources_data(sources_id,date,title,summary) VALUES (?,?,?,?)',list_to_commit)

        db.commit()
    db.close()

# async def add_headlineText_to_DB_async(rss_feed_list):
#     now = datetime.datetime.now()
#     time_to_enter = now.strftime(form)
#
#     db = sqlite3.connect('data/NewsSiteRSSFeeds_test.db')
#     cursor = db.cursor()
#
#     async with aiohttp.ClientSession() as session:
#         for site in rss_feed_list:
#
#             if type(site) == tuple:
#                 sources_id = cursor.execute('SELECT id FROM sources WHERE rss_feed_url = ?',(site)).fetchone()[0]
#                 site = site[0]
#
#             list_to_commit = []
#
#             async with session.get(site) as resp:
#                 text = await resp.text()
#                 feed = feedparser.parse(text)
#
#                 for entry in feed['entries']:
#                     title   = entry['title']
#                     summary = entry['summary'].encode('utf-8')
#
#                     try:
#                         published = entry['published']
#                     except KeyError:
#                         published = time_to_enter
#                     tup     = (int(sources_id),published,str(title),str(summary))
#                     list_to_commit.append(tup)
#
#             cursor.executemany('INSERT INTO sources_data(sources_id,date,title,summary) VALUES (?,?,?,?)',list_to_commit)
#             db.commit()
#     db.close()
#
# async def add_headlineText_to_DB_async_concurrent(rss_feed_list):
#     now = datetime.datetime.now()
#     time_to_enter = now.strftime(form)
#     db = sqlite3.connect('data/NewsSiteRSSFeeds_test.db')
#     cursor = db.cursor()
#
#     with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
#
#         loop = asyncio.get_event_loop()
#         futures = []
#         #for site in rss_feed_list:
#         for site in rss_feed_list:
#             sources_id = cursor.execute('SELECT id FROM sources WHERE rss_feed_url = ?',(site)).fetchone()[0]
#             futures.append(loop.run_in_executor(
#                     executor,
#                     requests.get,
#                     site[0])
#                           )
#         for response in await asyncio.gather(*futures):
#             feed = feedparser.parse(response.text)
#             list_to_commit = []
#
#             for entry in feed['entries']:
#                 title   = entry['title']
#                 summary = entry['summary'].encode('utf-8')
#
#                 try:
#                     published = entry['published']
#                 except KeyError:
#                     published = time_to_enter
#                 tup     = (int(sources_id),published,str(title),str(summary))
#                 list_to_commit.append(tup)
#             cursor.executemany('INSERT INTO sources_data(sources_id,date,title,summary) VALUES (?,?,?,?)',list_to_commit)
#             db.commit()
#     db.close()

_create_db_and_initialize_tables()
_fill_sources_table('news_feed_dict.json')
rss_feed_list = _get_rss_feed_list()
add_headlineText_to_DB(rss_feed_list)

# startTime = int(round(time.time() * 1000))
#
# asyncio.set_event_loop(asyncio.new_event_loop()) # need to have global loop open
# loop = asyncio.get_event_loop()
# #loop.run_until_complete(test_get_function(rss_feed_list))
# try:
#     loop.run_until_complete(add_headlineText_to_DB_async_concurrent(rss_feed_list))
# finally:
#     loop.close()
# endTime = int(round(time.time() * 1000))
#
# #print(endTime - startTime,'ms')
