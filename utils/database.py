from datetime import datetime
import logging
import sys

from tenacity import retry, wait_incrementing, stop_after_attempt
import mariadb

log = logging.getLogger('mariadb')

def log_attempt_number(retry_state):
    """return the result of the last call attempt"""
    log.info('Connecting to MariaDB database failed, retry attempt: %s...', retry_state.attempt_number)
class MariaDBManager:
    def __init__(self, config):
        try:
            self.host = config['database']['host']
            self.port = config['database']['port']
            self.user = config['database']['user']
            self.password = config['database']['password']
            self.database = config['database']['db']
            self.table = config['database']['table']
            self.connection = None
            self.cursor = None
        except Exception as e:
            log.error('Cannot load configuration file. %s', e)
            sys.exit(1)

    @retry(stop=stop_after_attempt(3), wait=wait_incrementing(start=5, increment=10), after=log_attempt_number)
    def connect(self):
        try:
            self.connection = mariadb.Connection(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.connection.ping()
            self.cursor = self.connection.cursor()
            log.debug('Connected to MariaDB database')
        except Exception as e:
            log.error('Error connecting to MariaDB database: %s', e)

    def disconnect(self):
        try:
            self.connection.ping()
            self.cursor.close()
            self.connection.close()
            log.debug('Disconnected from MariaDB database')
        except Exception as e:
            log.error('Disconnect failed: %s', e)

    def insert_data(self, product):
        try:
            query = f"INSERT INTO {self.table} (caliber, shop, link, product_name, price, available, date_updated) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            data = (product['caliber'], 
                    product['shop'], 
                    product['link'], 
                    product['product_name'], 
                    product['price'],
                    product['available'],
                    datetime.now())
            
            self.cursor.execute(query, data)
            self.connection.commit()
            log.debug('NEW - Data inserted successfully: %s', product)
        except Exception as e:
            log.error('Error inserting data: %s', e)
            
    def update_data(self, shop, price, available, column_to_search, value_to_search):
        try:
            query = f"UPDATE {self.table} SET date_updated = '{datetime.now()}', price = '{price}', available = '{available}' " \
                f"WHERE {column_to_search} = '{value_to_search}'"

            self.cursor.execute(query)
            self.connection.commit()
            log.debug('EXISTS - Data updated successfully: Shop: %s, Item: %s, New price: %s, Available: %s', 
                    shop, value_to_search, price, available)
        except Exception as e:
            log.error('Error updating data: %s', e)
    
    def check_for_duplicates(self):
        values = []
        try:
            query = f"SELECT link FROM {self.table}"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            for row in rows:
                values.append(row[0])
            log.debug('Got values from link column, insert only unique, update already added.')
        except Exception as e:
            log.error('Error retrieving reported_link values: %s', e)
        return values
        

    def check_for_duplicates_dixie(self):
        values = []
        try:
            query = f"SELECT product_name FROM {self.table} WHERE shop = 'Dixie Pomerania'"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            for row in rows:
                values.append(row[0])
            log.debug('Got values from product_name column, insert only unique, update already added.')
        except Exception as e:
            log.error('Error retrieving reported_link values: %s', e)
        return values
        