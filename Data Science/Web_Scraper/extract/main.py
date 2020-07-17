import argparse
import csv
import datetime
import re
import logging
import web_pages as pages
from config_model import Config, QueryWebScraper, PaginationOption, Query
from common import config

PATH_YAML= r'C:\Users\Usuario\Desktop\Capacitacion\Data Science\Web_Scraper\extract\config.yaml'
__config = config(PATH_YAML)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _news_scraper(news_site_uid):
    config = _build_yaml_config( news_site_uid = news_site_uid )

    logging.info('Beginning scraper for {}'.format(config.url))
    try:
        homepage = pages.HomePage(config)
    
        items= []
        
        for url in homepage.items_links:
            logger.info('Start fetching article at {}'.format(url))
            try:
                itemPage = pages.ItemPage(config, url)
                _item = itemPage.item_data
                
                if _item :
                    _item['url'] = url
                    items.append(_item)
                    logger.info(_item['brank'])
                    logger.info('{} Items has been fetch'.format(len(items)))
                else:
                    logger.warning('Invalid item not fetch')
            
            except:
                logger.warning('Error while feching the article', exc_info=False)
        _save_articles(news_site_uid, items)
    except:
        logger.warning('Error while feching page {}'.format(news_site_uid), exc_info = False)
    
def _save_articles(news_site_uid, items: list):
    now = datetime.datetime.now().strftime("%m_%d_%Y")
    csv_headers = list(items[0].keys())
    out_file_name =f'{news_site_uid}_{now}_items.csv'
     # csv_headers=['body', 'title']

    with open(out_file_name, mode='w+', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        writer.writerow(csv_headers)

        for item in items:
            row = list(item.values())
            
            try:
                writer.writerow(row)
            except:
                logger.error('Error write row: {}'.format(row))
            

def _build_yaml_config(news_site_uid: str):
    site_yaml = __config['sites'][news_site_uid]
    site_pagination = site_yaml['pagination']
    site_queries = site_yaml['queries']
    
    queries_options = QueryWebScraper(
        items = site_queries['items'] ,
        fields= [Query(**i) for i in site_queries['fields']]
    )

    pagination_options = PaginationOption(
        active = site_pagination['active'], 
        link = site_pagination['link'], 
        parametes_link = site_pagination['parametes_link'],
        max_page = site_pagination['max_page'],
        min_page = site_pagination['min_page'],
        step_page= site_pagination['step']
    )

    config = Config(
        url = site_yaml['url'],
        max_items= site_yaml['max_items'],
        paginationConfig = pagination_options, 
        queries = queries_options
    )  
    return config

if __name__ == '__main__':
    
    #_news_scraper('Linio')
    #_news_scraper('MercadoLibre')
    #_news_scraper('Alkosto')
    
    parser = argparse.ArgumentParser()

    news_site_choices = list(__config['sites'])
    
    parser.add_argument('news_site',
                        help='The news site that you want to scrape',
                        type=str,
                        choices=news_site_choices)

    args = parser.parse_args()
    _news_scraper(args.news_site)
    
