from scrappers import dixiepomerania, gardaarms, rusznikarnia, arel, tarcza

import logging
import io
import sys
from multiprocessing import Process, current_process


class ProcessNameFilter(logging.Filter):
    def filter(self, record):
        record.processName = current_process().name
        return True

def configure_logging():
    set_level = logging.INFO
    
    # Create and configure the stream handler with UTF-8 encoding
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(processName)s] [%(name)s] %(message)s"
    )
    stream_handler.setFormatter(formatter)
    
    wrapped_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    stream_handler.setStream(wrapped_stdout)
    
    logging.basicConfig(
        level=set_level,
        handlers=[stream_handler]
    )
    # Add process name filter to root logger
    logging.getLogger().addFilter(ProcessNameFilter())

def run_scraper(scraper_function):
    configure_logging()
    log = logging.getLogger(scraper_function.__module__)
    
    try:
        log.info(f"Starting scraper: {scraper_function.__module__}")
        scraper_function()
        log.info(f"Finished scraper: {scraper_function.__module__}")
    except Exception as e:
        log.error(f"Error in scraper {scraper_function.__module__}: {e}")

if __name__ == '__main__':
    
    configure_logging()    
    log = logging.getLogger('runner')
    
    log.info('Starting!')
    
    scrapers = [dixiepomerania.run, 
                gardaarms.run, 
                rusznikarnia.run, 
                arel.run, 
                tarcza.run]
    
    # Create and start processes
    processes = []
    for scraper in scrapers:
        process = Process(target=run_scraper, args=(scraper, ))
        processes.append(process)
        process.start()
    
    # Wait for all processes to finish
    for process in processes:
        process.join()
    
    log.info('Finished!')