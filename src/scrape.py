import logging
import argparse
from commands import CommandHandlerFactory
from json_handler import create_json
import sys
import json
import os


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
    parser.add_argument('-limit', type=int, default=float('inf'))
    args = vars(parser.parse_args())
    try:
        json_obj = {
            'skin': [],
            'cleaning': []
        }
        command_hanlder = CommandHandlerFactory.getCommandByArguments(args)
        limit_flag = False
        for chunk in command_hanlder.process():
            for data in chunk:
                json_obj[data['db']].append(data)
                if len(json_obj['skin']) + len(json_obj['cleaning']) >= args['limit']:
                    limit_flag = True
                    break
            if limit_flag:
                break
        json_file = create_json()
        json_file.write(json.dumps(json_obj))
        json_file.close()
    except Exception as e:
        logger.exception(e)
