from datetime import datetime
import os


def create_json():
    filename = f'results_{datetime.now()}.json'
    new_file = open(f'{os.getcwd()}/links/{filename}', 'w')
    return new_file
