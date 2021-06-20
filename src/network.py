import requests
import time
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 ' \
                  'Safari/537.36 '
}

ATTEMPTS = 4
SLEEP = 5
TIMEOUT = 80


def get_html_by_url(url, attempts=ATTEMPTS):
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        return response.text
    except Exception as e:
        if attempts > 0:
            logger.debug(f'Something went wrong, try request again {url} in {SLEEP} seconds.')
            time.sleep(SLEEP)
            return get_html_by_url(url, attempts=attempts-1) 
        raise e



