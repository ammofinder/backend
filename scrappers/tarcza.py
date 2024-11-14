import requests
import logging
from bs4 import BeautifulSoup

from utils.common import push_to_database

log = logging.getLogger('Tarcza')


def get_number_of_pages(soup):
    pagination = soup.find('div', class_='IndexStron')
    if pagination:
        a_elements = pagination.find_all('a', string=True)
        numbered_pages = [a for a in a_elements if a.string.isdigit()]
        return len(numbered_pages)
    return 1

def scrapper():
    base_url = 'https://sklep-strzelecki.pl/amunicja-c-4.html'
    products = []
    
    accepted_calibers = ['9x19', '223Rem', '22LR', '22 lr', '.22 LR', 'kal.22', '7,62x39']
    
    response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        number_of_pages = get_number_of_pages(soup)
        log.info("Number of pages: %d", number_of_pages)

    for page in range(1, number_of_pages + 1):
        url = f'{base_url}/s={page}'
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            product_elements = soup.find_all('div', class_='Okno OknoRwd')
            
            log.info('Items found: %s page %s', len(product_elements), page)

            for product in product_elements:
                name_tag = product.find('h3')
                product_name = name_tag.text.strip() if name_tag else None
                
                product_tag = product.find('h3').find('a')
                product_link = product_tag['href'] if product_tag else None
                
                price_tag = product.find('span', class_='Cena')
                product_price = price_tag.text.strip() if price_tag else None
                product_price = product_price.replace(',', '.').replace('zł', '').strip()
                
                availability_element = soup.find('ul', class_='ListaOpisowa')
                available = "tak" if "Dostępny" in availability_element.text else "nie"
                
                log.debug('%s %s', product_name, product_price)

                matching_caliber = [caliber for caliber in accepted_calibers if caliber in product_name]
                
                if matching_caliber:
                    caliber = matching_caliber[0]
                    
                    # Fix for database calibers filtering
                    if caliber == '9x19': 
                        caliber = '9x19'
                    if caliber == '223Rem':
                        caliber = '223 Rem'
                    if caliber == '22LR' or caliber == '22 lr' or caliber == '.22 LR' or caliber == 'kal.22':
                        caliber = '22 LR'
                    if caliber == '7,62x39':
                        caliber = '7.62x39'
                    
                    if isinstance(product_price,float):
                        product_price = "{:.2f}".format(product_price) # format of X.XX
                        
                    if None in (product_name, product_link, product_price):
                        log.error('One of params is none: name=%s, link=%s, price=%s', product_name, product_link, product_price)
                        continue
                    
                    products.append({
                        'shop': 'Tarcza',
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
    products_tarcza = scrapper()
    new, updated = push_to_database('Tarcza', products_tarcza)
    
    log.info('New: %s, Updated: %s', new, updated)