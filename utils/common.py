import logging
import requests

from .database import MariaDBManager
from tenacity import retry, stop_after_attempt, wait_exponential

log = logging.getLogger('common')


def push_to_database(shop, products_list):
    db_manager = MariaDBManager()
    db_manager.connect()
    
    added, updated = 0, 0
        
    for product in products_list:
        
        # DixiePomerania has really oldschool site with all products on single site
        if 'Dixie' in shop:
            existing_products = db_manager.check_for_duplicates_dixie()
            if product['product_name'] in existing_products:
                db_manager.update_data(product['shop'], 
                                    product['price'], 
                                    product['available'], 
                                    'product_name', 
                                    product['product_name'])
                updated += 1
            else:
                log.debug("New product -> %s", product)
                db_manager.insert_data(product)   
                added += 1
                
        else:
            existing_products = db_manager.check_for_duplicates()
            if product['link'] in existing_products:
                db_manager.update_data(product['shop'], 
                                    product['price'], 
                                    product['available'],
                                    'link', 
                                    product['link'])
                updated += 1
            else:
                log.debug("New product -> %s", product)
                db_manager.insert_data(product)
                added += 1
            
    db_manager.disconnect()
    
    return added, updated

def log_retry_attempt(retry_state):
    log.info(f"Retry {retry_state.attempt_number} for URL: {retry_state.args[0]}...")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), after=log_retry_attempt)
def fetch_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response
