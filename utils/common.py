import logging

from .database import MariaDBManager

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