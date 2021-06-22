import logging
import argparse
from commands import CommandHandlerFactory
import sys


if __name__ == '__main__':
    sys.tracebacklimit = 0
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s %(levelname)s:%(message)s')
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(description='Scrape EWG entities.')
    parser.add_argument('-db', type=str)
    parser.add_argument('-category', type=str)
    parser.add_argument('-subcategory', type=str)
    parser.add_argument('-child', type=str)
    parser.add_argument('-items_url', type=str)
    parser.add_argument('-url', type=str)
    args = vars(parser.parse_args())
    try:
        command_hanlder = CommandHandlerFactory.getCommandByArguments(args)
        for chunk in command_hanlder.process():
            print(chunk)
    except Exception as e:
        logger.exception(e)
