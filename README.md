# news_site_analysis

The aim of this project is to accumulate a database of various news site's headlines and stories for sentiment analysis. The file `news_feed_dict.json` has approximately 30 news site's RSS feeds to build a local `sqlite3` database. 

The core of the code is in `fill_news_Site_db.py` and includes code to make the database and pull data to fill it. Since it was agonizingly slow I added an asynchronous method, `add_headlineText_to_DB_async_concurrent()` that uses threading and the package `asyncio` to give it about a 5x speedup.  
