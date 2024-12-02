import argparse
import logging
import io
import sys
import yaml

from multiprocessing import Process, current_process

from scrappers import dixiepomerania, gardaarms, rusznikarnia, arel, tarcza

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
    
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.addHandler(stream_handler)
    logger.setLevel(set_level)
    # Add process name filter to root logger
    logger.addFilter(ProcessNameFilter())

def run_scraper(scraper_function, config):
    configure_logging()
    log = logging.getLogger(scraper_function.__module__)
    
    try:
        log.info(f"Starting scraper: {scraper_function.__module__}")
        scraper_function(config)
        log.info(f"Finished scraper: {scraper_function.__module__}")
    except Exception as e:
        log.error(f"Error in scraper {scraper_function.__module__}: {e}")

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="path to the configuration file", required=True)
    args = parser.parse_args()
    
    try:
        with open(args.config, encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        sys.exit("ERROR: config.yaml file not found. Create one reffering to README.")
    except yaml.YAMLError:
        sys.exit("ERROR: Error while loading config.yaml file.")
        
    configure_logging()    
    log = logging.getLogger('runner')
    
    log.info('Starting!')
    
    scrapers = [
        (dixiepomerania.run, config),
        (gardaarms.run, config),
        (rusznikarnia.run, config),
        (arel.run, config),
        (tarcza.run, config),
    ]
    
    # Create and start processes
    processes = []
    for scraper_function, scraper_config in scrapers:
        process = Process(target=run_scraper, args=(scraper_function, scraper_config))
        processes.append(process)
        process.start()
    
    # Wait for all processes to finish
    for process in processes:
        process.join()
    
    log.info('Finished!')

if __name__ == '__main__':
    main()
