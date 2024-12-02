import argparse
import logging
import sys
import yaml

import multiprocessing
from multiprocessing import current_process

from scrappers import dixiepomerania, gardaarms, rusznikarnia, arel, tarcza

class ProcessNameFilter(logging.Filter):
    def filter(self, record):
        record.processName = current_process().name
        return True

def configure_logging():
    set_level = logging.INFO

    logger = logging.getLogger()
    logger.handlers.clear()

    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(processName)s] [%(name)s] %(message)s"
    )
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.setLevel(set_level)
    logger.addFilter(ProcessNameFilter())


def configure_logging_for_process():
    logger = logging.getLogger()
    logger.handlers.clear()

    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(processName)s] [%(name)s] %(message)s"
    )
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)


def run_scraper(scraper_function, config):
    configure_logging_for_process()
    log = logging.getLogger(scraper_function.__module__)

    try:
        log.info(f"Starting scraper: {scraper_function.__module__}")
        scraper_function(config)
        log.info(f"Finished scraper: {scraper_function.__module__}")
    except Exception as e:
        log.error(f"Error in scraper {scraper_function.__module__}: {e}")

def main():
    multiprocessing.set_start_method("spawn")

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="path to the configuration file", required=True)
    args = parser.parse_args()

    try:
        with open(args.config, encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        sys.exit("ERROR: config.yaml file not found. Create one referring to README.")
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

    processes = []
    for scraper_function, scraper_config in scrapers:
        process = multiprocessing.Process(target=run_scraper, args=(scraper_function, scraper_config))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    log.info('Finished!')

if __name__ == '__main__':
    main()
