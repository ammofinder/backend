import requests
import logging
from bs4 import BeautifulSoup

from utils.common import push_to_database

log = logging.getLogger('Arel')


def get_number_of_pages(soup):
    pagination = soup.find('ul', class_='paginator')
    if pagination:
        li_elements = pagination.find_all('li', string=None)
        result = []
        for li in li_elements:
            a_tag = li.find('a', title=True)
            if a_tag:
                result.append(li)
        return len(result)
    return 1

def scrapper():
    base_url = 'https://dharel.pl/pl/c/AMUNICJA/18'
    products = []
    
    accepted_calibers = ['9x19', '.223', '22LR', '22 lr', '.22 LR', 'kal.22', '7,62x39']
    
    response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        number_of_pages = get_number_of_pages(soup)
        log.info("Number of pages: %d", number_of_pages)

    for page in range(1, number_of_pages + 1):
        url = f'{base_url}/{page}'
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            product_elements = soup.find_all('div', class_='product product_view-extended s-grid-3 product-main-wrap product_with-lowest-price')
            
            log.info('Items found: %s page %s', len(product_elements), page)

            for product in product_elements:
                name_tag = product.find('a', class_='prodname')
                product_name = name_tag.get('title') if name_tag else None
                
                product_link = 'https://dharel.pl'+name_tag.get('href') if name_tag else None

                price_tag = product.find('div', class_='price').find('em')
                product_price = price_tag.get_text(strip=True) if price_tag else None
                product_price = product_price.replace(',', '.').replace('zł', '').strip()
                
                available = 'tak' # assume, that if product is on website, it is available
                
                log.debug('%s %s', product_name, product_price)

                matching_caliber = [caliber for caliber in accepted_calibers if caliber in product_name]
                
                if matching_caliber:
                    caliber = matching_caliber[0]
                    
                    # Fix for database calibers filtering
                    if caliber == '9x19': 
                        caliber = '9x19'
                    if caliber == '.223':
                        caliber = '223 Rem'
                    if caliber == '22LR' or caliber == '22 lr' or caliber == '.22 LR' or caliber == 'kal.22':
                        caliber = '22 LR'
                        if '500 szt' in product_name:
                            product_price = float(product_price) / 500   
                        else: 
                            product_price = float(product_price) / 50 # price for 22LR is for whole 50rds boxes
                    if caliber == '7,62x39':
                        caliber = '7.62x39'
                    
                    if isinstance(product_price,float):
                        product_price = "{:.2f}".format(product_price) # format of X.XX
                        
                    if None in (product_name, product_link, product_price):
                        log.error('One of params is none: name=%s, link=%s, price=%s', product_name, product_link, product_price)
                        continue
                    
                    products.append({
                        'shop': 'Arel',
                        'link': product_link,
                        'caliber': caliber,
                        'product_name': product_name,
                        'price': product_price,  
                        'available' : available
                    })
        else:
            log.error("Error during data collection on page %d: %s", page, response.status_code)
            
    log.info('Items meeting criteria: %s', len(products))
    return products

def run():
    products_arel = scrapper()
    new, updated = push_to_database('Arel', products_arel)
    
    log.info('New: %s, Updated: %s', new, updated)