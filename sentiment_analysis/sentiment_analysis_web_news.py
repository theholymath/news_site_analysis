# class for parsing news site data

import pandas as pd
import numpy as np
import urllib.request
import datetime
import json
import feedparser
import newsite_db_class as db_conn
from bs4 import BeautifulSoup
from html.parser import HTMLParser

import nltk
from nltk import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import re

# establish connection
DB_instance = db_conn.databaseInterface()

# load the names, url, rss feeds of news sites
with open('contraction_for_NLTK.json', 'r') as fp:
    contractions = json.load(fp)


def _load_happy_text():
    '''
    http://hedonometer.org/words.html
    The scale we use is 1 to 9, with 1 meaning extremely negative,
    5 neutral, and 9 extremely positive.
    How to calculate text score: https://www.uvm.edu/storylab/2014/10/06/hedonometer-2-0-measuring-happiness-and-using-word-shifts/

    '''#
    try:
        df = pd.read_csv('hedonemeter_happy_sad_words.txt',delim_whitespace=True)
    except FileNotFoundError:
        url = 'https://arxiv.org/src/1101.5120v5/anc/labMT-1.0.txt'
        response = urllib.request.urlopen(url)
        data = response.read()
        text = data.decode('utf-8')
        with open('hedonemeter_happy_sad_words.txt','w') as f:
            f.write(text)

        df = pd.read_csv('hedonemeter_happy_sad_words.txt',delim_whitespace=True)
    return df

df_happiness = _load_happy_text()
def happiness_score(text):
    # tokenization
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)

    text_nltk = nltk.Text(tokens)
    one_grams = nltk.FreqDist(text_nltk)
    #text_nltk.collocations()

    denominator = 0.0
    total_happy_score = 0.0

    numerator = 0
    for word in one_grams.most_common():
        # does the word appear in pos_neg?
        if word[0] in df_happiness['word'].values:
            val = df_happiness[df_happiness['word'] == word[0]]['happiness_average']
            numerator += float(val)*float(word[1])
            total_happy_score += float(val)
            denominator +=  float(word[1])

    #print("Happy socre: ",numerator/denominator)
    if denominator == 0:
        return -1

    return numerator/denominator
    #print("Neutral score: ",len(one_grams) - (positive_score + positive_score))
