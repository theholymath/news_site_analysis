# news_site_analysis

The aim of this project is to accumulate a database of various news site's headlines and summaries for sentiment analysis. I use the package `feedparser` to pull and parse the data for ingestion into the database. The file `news_feed_dict.json` has approximately 30 news site's RSS feeds to build a local `sqlite3` database. 

The goal is to look at both conservative, liberal, and moderate news sources, along with Russia Today, and to analyze the tone of the writing, the stories covered and the biases therein. 

The core of the code is in `fill_news_Site_db.py` and includes code to make the database and pull data to fill it. Since it was agonizingly slow I added an asynchronous method, `add_headlineText_to_DB_async_concurrent()` that uses threading and the package `asyncio` to give it about a 5x speedup.  
