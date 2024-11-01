from scrappers import dixiepomerania, gardaarms, rusznikarnia
from utils.common import push_to_database

import logging, io, sys


if __name__ == '__main__':
    
    set_level = logging.INFO
    
    # Create and configure the stream handler with UTF-8 encoding
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s"))
    wrapped_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    stream_handler.setStream(wrapped_stdout)
    
    logging.basicConfig(
        level=set_level,
        handlers=[stream_handler]
    )
    
    log = logging.getLogger('runner')
    
    log.info('Starting!')
    
    dixiepomerania.run()
    gardaarms.run()
    rusznikarnia.run()
    
    log.info('Finished!')