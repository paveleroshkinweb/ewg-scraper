from abc import ABC, abstractmethod
import logging
from exception import InvalidArgsException
from url_config import EWG_DATABASES
from network import get_html_by_url
import time

logger = logging.getLogger(__name__)

class CommandHandlerFactory:

    ERROR_MSG = '%s should be specified if you want to use advanced command!'

    @staticmethod
    def _validate_path(args):
        keys = [('db', None) , ('category', None), ('subcategory', 'child'), ('child', None)]
        obj = EWG_DATABASES
        for key, postfix in keys:
            if args[key] is None:
                return
            if obj.get(args[key], None) is None:
                raise InvalidArgsException(f'Invalid {key} = {args[key]}')
            obj = obj[args[key]]
            if postfix is not None:
                obj = obj[postfix]


    @staticmethod
    def _validate_args(args):
        if args['db'] is not None and args['db'] not in EWG_DATABASES.keys():
            raise InvalidArgsException(CommandHandlerFactory.ERROR_MSG % 'db')
        if args['category'] is None and any(args[key] is not None for key in ['subcategory', 'child', 'url', 'items_url']):
            raise InvalidArgsException(CommandHandlerFactory.ERROR_MSG % 'category')
        if args['subcategory'] is None and any(args[key] is not None for key in ['child', 'url', 'items_url']):
            raise InvalidArgsException(CommandHandlerFactory.ERROR_MSG % 'subcategory')
        CommandHandlerFactory._validate_path(args)


    @staticmethod
    def getCommandByArguments(args):

        def is_default_command(args):
            return all(value is None for value in args.values())
        
        def is_url_scrape_command(args):
            return args['url'] is not None
        
        def is_child_command(args):
            return args['child'] is not None
        
        def is_subcategory_command(args):
            return args['subcategory'] is not None
        
        def is_category_command(args):
            return args['category'] is not None

        def is_database_command(args):
            return args['db'] is not None

        CommandHandlerFactory._validate_args(args)
        if is_default_command(args):
            return DefaultCommandHandler(args)
        if is_url_scrape_command(args):
            return ItemCommandHandler(args)
        if is_child_command(args):
            return ChildCommandHandler(args)
        if is_subcategory_command(args):
            return SubcategoryCommandHandler(args)
        if is_category_command(args):
            return CategoryCommandHandler(args)
        if is_database_command(args):
            return DatabaseCommandHandler(args)
        return DefaultCommandHandler(args)

class CommandHandler(ABC):

    def __init__(self, args):
        self.args = args

    @abstractmethod
    def process(self):
        pass


class DefaultCommandHandler(CommandHandler):

    def __init__(self, args):
        super(DefaultCommandHandler, self).__init__(args)

    def process(self):
        logger.info("Scraping all EWG databases")
        for db_name in EWG_DATABASES.keys():
            command_args = {**self.args, 'db': db_name}
            handler = DatabaseCommandHandler(command_args)
            for chunk_result in handler.process():
                yield chunk_result


class DatabaseCommandHandler(CommandHandler):
    
    def __init__(self, args):
        super(DatabaseCommandHandler, self).__init__(args)
    
    def process(self):
        db = EWG_DATABASES[self.args['db']]
        logger.info(f"Scraping database {self.args['db']}")
        for category_name in db.keys():
            command_args = {**self.args, 'category': category_name}
            handler = CategoryCommandHandler(command_args)
            for chunk_result in handler.process():
                yield chunk_result


class CategoryCommandHandler(CommandHandler):

    def __init__(self, args):
        super(CategoryCommandHandler, self).__init__(args) 

    def process(self):
        category = EWG_DATABASES[self.args['db']][self.args['category']]
        logger.info(f"Scraping category {self.args['category']}")
        for subcategory_name in category.keys():
            command_args = {**self.args, 'subcategory': subcategory_name}
            handler = SubcategoryCommandHandler(command_args)
            for chunk_result in handler.process():
                yield chunk_result


class SubcategoryCommandHandler(CommandHandler):

    def __init__(self, args):
        super(SubcategoryCommandHandler, self).__init__(args)
    
    def process(self):
        subcategory = EWG_DATABASES[self.args['db']][self.args['category']][self.args['subcategory']]
        logger.info(f"Scraping subcategory {self.args['subcategory']}")
        for child in subcategory['child']:
            command_args = {**self.args, 'child': child}
            handler = ChildCommandHandler(command_args)
            for chunk_result in handler.process():
                yield chunk_result


class ChildCommandHandler(CommandHandler):
    
    def __init__(self, args):
        super(ChildCommandHandler, self).__init__(args) 

    def process(self):
        child =  EWG_DATABASES[self.args['db']][self.args['category']][self.args['subcategory']]['child'][self.args['child']]
        base_url = EWG_DATABASES[self.args['db']][self.args['category']][self.args['subcategory']]['base_url']
        items_url = base_url + child
        command_args = {**self.args, 'items_url': items_url}
        logger.info(f"Scraping child {self.args['child']}")
        handler = ItemsPagesCommandHandler(command_args)
        for chunk_result in handler.process():
            yield chunk_result


class ItemsPagesCommandHandler(CommandHandler):

    def __init__(self, args):
        super(ItemsPagesCommandHandler, self).__init__(args)

    def process(self):
        items_url = self.args['items_url']
        scraper_cls = EWG_DATABASES[self.args['db']][self.args['category']][self.args['subcategory']]['scraper']
        while items_url:
            try:
                html = get_html_by_url(items_url)
                scraper = scraper_cls(html)
                logger.info(f'Scraping items page {items_url}')
                next_page, links = scraper.scrape_items_page()
                chunks = []
                if links:
                    logger.info(f'Scraping {len(links)} links: {links}')
                    for item_link in links:
                        time.sleep(3)
                        command_args = {**self.args, 'url': item_link}
                        handler = ItemCommandHandler(command_args)
                        data = list(handler.process())[0]
                        chunks.extend(data)
                    items_url = next_page
                    logger.info(f"Successfully scraped {len(chunks)} links: {chunks}")
                    yield chunks
            except Exception:
                logger.exception(f"Couldn't process items page {items_url}, skipping...")
                items_url = None
                yield []


class ItemCommandHandler(CommandHandler):

    def __init__(self, args):
        super(ItemCommandHandler, self).__init__(args)

    def process(self):
        db = EWG_DATABASES[self.args['db']]
        url = self.args['url']
        scraper_cls = db[self.args['category']][self.args['subcategory']]['scraper']
        logger.info(f'Scraping {self.args["db"]} item_url {url}')
        html = None
        try:
            html = get_html_by_url(url)
        except Exception:
            logger.exception(f"Couldn't access item_url {url}, skipping...")
            yield []
        scraper = scraper_cls(html)
        logger.info(f'Scraping item page {url}')
        data = scraper.scrape_item(category=self.args['subcategory'], db=self.args['db'], url=url)
        if data:
            yield [data]
        else:
            yield []
