import logging
from bs4 import BeautifulSoup

from utils.common import push_to_database, fetch_data

log = logging.getLogger('Rusznikarnia')


def get_number_of_pages(soup):
    pagination = soup.find('ul', class_='page-numbers')
    if pagination:
        pages = pagination.find_all('li')
        return len(pages) - 1  # Odejmujemy 1, ponieważ ostatni element to "Next"
    return 0

def scrapper():
    base_url = 'https://rusznikarnia.eu/kategoria/amunicja/'
    products = []
    
    accepted_calibers = ['9x19', '9mm', '.223 Rem', '.22 LR', '22LR', '7,62x39', '7,62×39']
    
    response = fetch_data(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        number_of_pages = get_number_of_pages(soup)
        log.info("Number of pages: %d", number_of_pages)

    for page in range(1, number_of_pages + 1):
        url = f'{base_url}/page/{page}'
        response = fetch_data(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            product_elements = soup.find_all('div', class_='product-outer product-item__outer')
            
            log.info('Items found: %s page %s', len(product_elements), page)

            for product in product_elements:
                product_link = product.find('a').get('href')
                product_name = product.find('h2', class_='woocommerce-loop-product__title').get_text(strip=True)

                product_price = product.find('bdi')
                if product_price:
                    product_price = product_price.text.split()[0]
                    product_price = product_price.replace(',', '.').strip()
                    
                # get availabiliy
                availability_response = fetch_data(product_link)
                if availability_response.status_code == 200:
                    availability_soup = BeautifulSoup(availability_response.text, 'html.parser')
                    availability_elem = availability_soup.find('div', class_='availability')
                    if availability_elem:
                        available = 'nie'
                    else:
                        available = 'tak'
                else:
                    available = 'brak danych'

                matching_caliber = [caliber for caliber in accepted_calibers if caliber in product_name]
                
                if matching_caliber:
                    caliber = matching_caliber[0]
                    
                    # Fix for database calibers filtering
                    if caliber == '9mm' or caliber == '9x19': 
                        caliber = '9x19'
                    if caliber == '.223 Rem':
                        caliber = '223 Rem'
                    if caliber == '.22 LR' or caliber == '22LR':
                        caliber = '22 LR'
                    if caliber == '7,62x39' or caliber == '7,62×39':
                        caliber = '7.62x39'
                    
                    products.append({
                        'shop': 'Rusznikarnia',
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

def run(config):
    products_rusznikarnia = scrapper()
    new, updated = push_to_database('Rusznikarnia', products_rusznikarnia, config)
    
    log.info('New: %s, Updated: %s', new, updated)