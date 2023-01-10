import pandas as pd
from newsapi.newsapi_client import NewsApiClient
from datetime import datetime, timedelta
from db.db_handler import DB
from model.model import Predictor
from time import sleep as wait
import logging

formatter = logging.Formatter(
    fmt=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')
handler = logging.FileHandler('scrapper_logs.log')

handler.setFormatter(formatter)
logger = logging.getLogger('default_logger')
logger.setLevel(logging.INFO)

logger.addHandler(handler)


def scrap_manual(start_time):
    try:
        sources = db.get_from_db("SELECT id FROM data_sources WHERE used=1 AND source='scrapping'")
    except Exception as e:
        logger.error(
            f'exception occurred while getting ids::{e.__traceback__.tb_lineno}, {e.__class__.__name__}: {str(e)}')
        return 0


def scrap_newsapi(newsapi, start_time):
    db = DB()
    try:
        sources = db.get_from_db("SELECT id FROM data_sources WHERE used=1 AND source='newsapi'")
    except Exception as e:
        db.connection.close()
        logger.error(
            f'exception occurred while getting ids::{e.__traceback__.tb_lineno}, {e.__class__.__name__}: {str(e)}')
        return 0

    try:
        page = 1
        df = pd.DataFrame()
        while True:
            response = newsapi.get_everything(sources=','.join([i[0] for i in sources.values]),
                                              from_param=start_time,
                                              language='en',
                                              page=page)
            page += 1
            new_df = pd.json_normalize(response['articles'])
            df = pd.concat([df, new_df])
            if len(new_df) < 100:
                break

        if len(df) == 0:
            return 0
    except Exception as e:
        db.connection.close()
        logger.error(
            f'exception occurred while scrapping::{e.__traceback__.tb_lineno}, {e.__class__.__name__}: {str(e)}')
        return 0

    try:
        df['category'] = Predictor().predict(df['title'] + ' ' + df['description'])
        df = df[['title', 'description', 'url', 'publishedAt', 'source.id', 'source.name', 'category']]
        df['publishedAt'] = pd.to_datetime(df['publishedAt'])
    except Exception as e:
        db.connection.close()
        logger.error(
            f'exception occurred while predicting::{e.__traceback__.tb_lineno}, {e.__class__.__name__}: {str(e)}')
        return 0

    try:
        db.write_to_db(df.values.tolist(), 'news')
    except Exception as e:
        db.connection.close()
        logger.error(
            f'exception occurred while writing to db::{e.__traceback__.tb_lineno}, {e.__class__.__name__}: {str(e)}')
        return 0
    db.connection.close()
    return len(df)


if __name__ == '__main__':
    # Init
    newsapi = NewsApiClient(api_key='6555c4db1c924c30afd9ec5bf5c88dcd')
    period = 15  # minutes
    start_time = (datetime.now() - timedelta(minutes=period)).strftime("%Y-%m-%dT%H:%M:%S")
    while True:
        new_start_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        rows = scrap_newsapi(newsapi, start_time)
        logger.info(f"Inserted {rows} rows to db")
        start_time = new_start_time
        wait(period * 60)
