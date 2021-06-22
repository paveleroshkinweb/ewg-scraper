from abc import ABC, abstractmethod
from network import get_html_by_url
from bs4 import BeautifulSoup
from columns import *
from contextlib import suppress
from urllib.parse import urljoin
import logging
import re


logger = logging.getLogger(__name__)

DOMAIN = 'https://www.ewg.org/'

class Scraper(ABC):

    def __init__(self, html):
        self.html = html
        self.parser = BeautifulSoup(html, 'lxml')

    @abstractmethod
    def scrape_items_page(self):
        pass

    @abstractmethod
    def scrape_item(self, **kwargs):
        pass
    
    def get_text_by_selector(self, selector):
        node = self.parser.select_one(selector)
        if node:
            return node.text.strip()
        return None
    
    def get_text_by_selector_in_cont(self, container, selector):
        node = container.select_one(selector)
        if node:
            return node.text.strip()
        return None


class SunScraper(Scraper):

    def __init__(self, html):
        super(SunScraper, self).__init__(html)

    def scrape_items_page(self):
        next_link = None
        try:
            link_elements = self.parser.select('ul.search_results_list li a')
            if link_elements:
                links = set([link['href'] for link in link_elements])
                next_url_elements = self.parser.select('ul.cd-pagination li.button a')
                if next_url_elements:
                    next_link = next_url_elements[-1]['href']
                return next_link, links
        except Exception as e:
            logger.exception(e)
            return None, []

    def _get_product_name(self):
        return self.get_text_by_selector('h1.tyty2015_class_truncate_title_specific_product_page')

    def _get_list_of_ingridients(self):
        ingridients = []
        try:
            containers = self.parser.select('div.ingredient_right h1 a')
            for container in containers:
                ingridients.append(container.text.strip())
        except Exception as e:
            logger.exception(e)
        return ', '.join(ingridients)
    
    def _get_chemicals(self):
        chemicals = []
        try:
            chemical_scores = self.parser.select('div#ing_score_wrap div.score_left.center img[title="Score"][src]')
            chemical_scores = [score['src'] for score in chemical_scores if score['src'] is not None and not score['src'].startswith('data:')]
            ingridents = self.parser.select('div#ing_score_wrap div.ingredient_right')[1:]
            for score, ingridient in zip(chemical_scores, ingridents):
                with suppress(Exception):
                    concern = self.get_text_by_selector_in_cont(ingridient, 'p')
                    if concern and concern.startswith('Concerns:'):
                        concern = concern[10:]
                    data = {
                        NAME: self.get_text_by_selector_in_cont(ingridient, 'a'),
                        CONCERNS: concern,
                        EWG_SCORE: re.search(r'-(\d+).png', score).group(1)
                    }
                    chemicals.append(data)
        except Exception as e:
            logger.exception(e)
        return chemicals

    def scrape_item(self, **kwargs):
        data = {}
        try:
            data[PRODUCT_NAME] = self._get_product_name()
            data[BRAND] = None
            data[LIST_OF_INGREDIENTS] = self._get_list_of_ingridients()
            data[EWG_SCORE] = 'EWG verified'
            data[UPC_CODE] = None
            data[TERA_CATEGORY] = kwargs['category']
            data[URL] = kwargs['url']
            data['db'] = kwargs['db']
            data[CHEMICALS] = self._get_chemicals()
            data[SKIN_DEEP] = {
                CANCER: None,
                DEVELOPMENTAL_REPRODUCTIVE_TOXICITY: None,
                ALLERGIES_IMMUNOTOXICITY: None,
                USE_RESTRICTIONS: None
            }
            if not data[PRODUCT_NAME]:
                logger.debug(f'{PRODUCT_NAME} is abscent, do not saving item')
                return None
            return data
        except Exception as e:
            logger.exception(e)
            return None


class CleaningScraper(Scraper):

    def __init__(self, html):
        super(CleaningScraper, self).__init__(html)
    
    def scrape_items_page(self):
        next_link = None
        try:
            link_elements = self.parser.select('div.individual_products_row div.individual_products_row_col2 a')
            if link_elements:
                links = set([urljoin(DOMAIN, link['href']) for link in link_elements])
                next_url_element = self.parser.select_one('a.next_page')
                if next_url_element:
                    next_link = urljoin(DOMAIN, next_url_element['href'])
                return next_link, links
        except Exception as e:
            logger.exception(e)
            return None, []
    
    def _get_product_name(self):
        return self.get_text_by_selector('h1.h1large') or \
               self.get_text_by_selector('h1.h1medium') or \
               self.get_text_by_selector('h1.h1small') or \
               self.get_text_by_selector('h1.h1verysmall') or \
               self.get_text_by_selector('div#productname')
    
    def _get_brand(self):
        with suppress(Exception):
            containers = self.parser.select('div#prodname_name')
            if containers:
                for container in containers:
                    if container.text.startswith('Brand'):
                        brand = container.text.split(':')[-1].strip()
                        if brand.endswith('...'):
                            brand = brand[:-3]
                        return brand.strip()

    def _get_cleaning(self):
        cleaning = {}
        try:
            containers = self.parser.select('div#bars div.individualbar_3col')
            if containers:
                for container in containers:
                    field_name = self.get_text_by_selector_in_cont(container, 'div.individualbar_col1')
                    if field_name:
                        field_name = field_name.replace('&', '& ')
                        field_value = self.get_text_by_selector_in_cont(container, 'div.individualbar_col3')
                        if field_value:
                            cleaning[field_name] = field_value
        except Exception as e:
            logger.exception(e)
        return cleaning

    def _get_list_of_ingridients(self):
        ingridients = []
        try:
            containers = self.parser.select('a.substance_ahref')
            if containers:
                for container in containers:
                    ingridients.append(container.text)
        except Exception as e:
            logger.exception(e)
        return ', '.join(ingridients)
    
    def _get_chemicals(self):
        chemicals = []
        try:
            containers = self.parser.select('div#Product_Ingredients div.innertab div.datarow')[1:]
            for container in containers:
                data = {
                    NAME: self.get_text_by_selector_in_cont(container, 'a.substance_ahref'),
                    CONCERNS: self.get_text_by_selector_in_cont(container, 'div.dcol2_4 b'),
                    EWG_SCORE: self.get_text_by_selector_in_cont(container, 'div.dcol3_4 a[rel="popup_scores"]')
                }
                chemicals.append(data)
        except Exception as e:
            logger.exception(e)
        return chemicals

    def scrape_item(self, **kwargs):
        data = {}
        try:
            data[PRODUCT_NAME] = self._get_product_name()
            data[BRAND] = self._get_brand()
            data[LIST_OF_INGREDIENTS] = self._get_list_of_ingridients()
            data[EWG_SCORE] = 'EWG verified'
            data[UPC_CODE] = None
            data[TERA_CATEGORY] = kwargs['category']
            data[URL] = kwargs['url']
            data['db'] = kwargs['db']
            data[CHEMICALS] = self._get_chemicals()
            data[CLEANING] = self._get_cleaning()
            if not data[PRODUCT_NAME] or not data[BRAND]:
                logger.debug(f'{PRODUCT_NAME} or {BRAND} is abscent, do not saving item')
                return None
            return data
        except Exception as e:
            logger.exception(e)
            return None