import logging
from bs4 import BeautifulSoup

from utils.common import push_to_database, fetch_data

log = logging.getLogger('GardaArms')


def get_number_of_pages(soup):
    pagination = soup.find('div', class_='product-list__pagination')
    if pagination:
        pages = pagination.find_all('li', class_='pagination__link')
        return len(pages) - 2  # Odejmujemy 2, ponieważ ostatni element to "Next", a pierwszy to "Prev"
    return 0

def scrapper():
    base_url = 'https://www.gardaarms.pl/produkty/amunicja/2-239'
    products = []
    
    accepted_calibers = ["9 mm", '9x19', '223', '.22 LR', ' 9mm', '9MM', '7,62x39']
    
    response = fetch_data(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        number_of_pages = get_number_of_pages(soup)
        log.info("Number of pages: %d", number_of_pages)

    for page in range(1, number_of_pages + 1):
        url = f'{base_url}?sort=1&pageId={page}#products'
        response = fetch_data(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            product_elements = soup.find_all('a', class_='product-url rndA')
            
            log.info('Items found: %s page %s', len(product_elements), page)

            for product in product_elements:
                product_link = "https://www.gardaarms.pl/" + product['href']
                product_name = product.find('h2').get_text(strip=True)

                product_price = product.select('span.price:not(.hidden)')
                product_price = product_price[0].get_text(strip=True)
                product_price = product_price.replace(',', '.').replace('zł', '').strip()
                
                # get availabiliy
                availability_response = fetch_data(product_link)
                if availability_response.status_code == 200:
                    availability_soup = BeautifulSoup(availability_response.text, 'html.parser')
                    availability_elem = availability_soup.find('span', class_='productDetails-info--value value')
                    if "Niedostępny" in availability_elem.text.strip():
                        available = 'nie'
                    else:
                        available = 'tak'
                else:
                    available = 'brak danych'
                
                log.debug('%s %s', product_name, product_price)

                matching_caliber = [caliber for caliber in accepted_calibers if caliber in product_name]
                
                if matching_caliber:
                    caliber = matching_caliber[0]
                    
                    # Fix for database calibers filtering
                    if caliber == '9 mm' or caliber == '9x19mm' or caliber == ' 9mm' or caliber == '9MM': 
                        caliber = '9x19'
                    if caliber == '223':
                        caliber = '223 Rem'
                    if caliber == '.22 LR':
                        caliber = '22 LR'
                    if caliber == '7,62x39':
                        caliber = '7.62x39'
                    
                    products.append({
                        'shop': 'Garda Arms',
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
    products_garda = scrapper()
    new, updated = push_to_database('GardaArms', products_garda, config)
    
    log.info('New: %s, Updated: %s', new, updated)