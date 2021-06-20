from abc import ABC, abstractmethod
from network import get_html_by_url
from bs4 import BeautifulSoup
from columns import *
import logging


logger = logging.getLogger(__name__)


class Scraper(ABC):

    def __init__(self, html):
        self.html = html
        self.parser = BeautifulSoup(html, 'lxml')

    @abstractmethod
    def scrape_items_page(self):
        pass

    @abstractmethod
    def scrape_item(self):
        pass
    
    def get_text_by_selector(self, selector):
        node = self.parser.select_one(selector)
        if node:
            return node.text
        return None

class SkinDeepScraper(Scraper):

    def __init__(self, html):
        super(SkinDeepScraper, self).__init__(html)

    def scrape_items_page(self):
        pass

    def scrape_item(self):
        pass


class CleaningScraper(Scraper):

    SELCTORS = {
       PRODUCT_NAME : 'h1.h1large',
       BRAND: 'div#prodname_name'
    }

    def __init__(self, html):
        super(CleaningScraper, self).__init__(html)
    
    def scrape_items_page(self):
        pass
    
    def _get_product_name():
        return self.get_text_by_selector(CleaningScraper.SELCTORS[PRODUCT_NAME])
    
    def _get_brand():
        try:
            brand = self.get_text_by_selector(CleaningScraper.SELCTORS[BRAND])
            return brand.split(':')[-1].strip()
        except Exception:
            return None
    
    def _get_cleaning():
        cleaning = {}

    def scrape_item(self):
        data = {}
        data[PRODUCT_NAME] = self._get_product_name()
        data[BRAND] = self._get_brand()
        data = {**data, **self._get_cleaning()}
        

        data[UPC_CODE] = None



