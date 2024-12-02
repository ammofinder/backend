import logging
import re

from bs4 import BeautifulSoup

from utils.common import push_to_database, fetch_data

log = logging.getLogger('DixiePomerania')

def scrapper():
    url = 'https://dixiepomerania.pl/?page_id=55'

    response = fetch_data(url)
    
    log.info('Stating scrapper.')
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        products = []
        
        paragraphs = soup.find_all('p')
        
        accepted_calibers = ["9 mm", '223 Remington', '22 LR', '.22LR', '7.62 x 39']
        
        for paragraph in paragraphs:
            line = paragraph.get_text(strip=True)
            
            if "NIEDOSTĘPNA" in line:
                available = 'nie'
            else:
                available = 'tak'

            match = re.search(r'^(.*?)(?:Cena za sztukę (.*?)zł)', line)
            matching_caliber = [caliber for caliber in accepted_calibers if caliber in line]
            
            if match and matching_caliber:
                caliber = matching_caliber[0]
                product_name = match.group(1).strip()
                product_price = match.group(2).replace(',', '.').strip()
                
                # Fix for database calibers filtering
                if caliber == '9 mm': 
                    caliber = '9x19'
                if caliber == '223 Remington':
                    caliber = '223 Rem'
                if caliber == '.22LR':
                    caliber = '22 LR'
                if caliber == '7.62 x 39':
                    caliber = '7.62x39'
                
                products.append({
                    'shop': 'Dixie Pomerania',
                    'link': 'https://dixiepomerania.pl/?page_id=55',
                    'caliber': caliber,
                    'product_name': product_name,
                    'price': product_price,
                    'available': available  
                })
            
        return products
        
    else:
        log.error("Error during data collection: %s", response.status_code)

def run(config):
    products_dixie = scrapper()
    new, updated = push_to_database('Dixie', products_dixie, config)
    
    log.info('New: %s, Updated: %s', new, updated)