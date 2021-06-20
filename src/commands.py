from abc import ABC, abstractmethod
import logging
from exception import InvalidArgsException
from url_config import EWG_DATABASES
from network import get_html_by_url

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
            raise InvalidArgsException(f'db should be one of: {EWG_DATABASES.keys()}!')
            raise InvalidArgsException(CommandHandlerFactory.ERROR_MSG % 'db')
        if args['category'] is None and any(args[key] is not None for key in ['subcategory', 'child', 'url', 'items_url']):
            raise InvalidArgsException(CommandHandlerFactory.ERROR_MSG % 'category')
        if args['subcategory'] is None and any(args[key] is not None for key in ['child', 'url', 'items_url']):
            raise InvalidArgsException(CommandHandlerFactory.ERROR_MSG % 'subcategory')
        if args['child'] is None and any(args[key] is not None for key in ['url', 'items_url']):
            raise InvalidArgsException(CommandHandlerFactory.ERROR_MSG % 'child')
        CommandHandlerFactory._validate_path(args)


    @staticmethod
    def getCommandByArguments(args):

        def is_default_command(args):
            return all(value is None for value in args.values())
        
        def is_url_scrape_command(args):
            return args['url'] is not None

        CommandHandlerFactory._validate_args(args)
        if is_default_command(args):
            return DefaultCommandHandler(args)
        if is_url_scrape_command(args):
            return ItemCommandHandler(args)


class CommandHandler(ABC):

    def __init__(self, args):
        self.args = args
        logger.debug(f"Handler {type(self)} was created!")

    @abstractmethod
    def process(self):
        pass


class DefaultCommandHandler(CommandHandler):

    def __init__(self, args):
        super(DefaultCommandHandler, self).__init__(args)

    def process(self):
        results = []
        for db_name in EWG_DATABASES.keys():
            command_args = {**self.args, 'db': db_name}
            handler = DatabaseCommandHandler(command_args)
            handler_results = handler.process()
            results.extend(handler_results)
        return results


class DatabaseCommandHandler(CommandHandler):
    
    def __init__(self, args):
        super(DatabaseCommandHandler, self).__init__(args)
    
    def process(self):
        db = EWG_DATABASES[self.args['db']]
        results = []
        for category_name in db.keys():
            command_args = {**self.args, 'category': category_name}
            handler = CategoryCommandHandler(command_args)
            handler_results = handler.process()
            results.extend(handler_results)
        return results


class CategoryCommandHandler(CommandHandler):

    def __init__(self, args):
        super(CategoryCommandHandler, self).__init__(args) 

    def process(self):
        return []
        # db = EWG_DATABASES[args['db']]
        # schema = db['schema']
        # pass


class ChildCommandHandler(CommandHandler):
    
    def __init__(self, args):
        super(ChildCommandHandler, self).__init__(args) 

    def process(self):
        pass


class ItemCommandHandler(CommandHandler):

    def __init__(self, args):
        super(ItemCommandHandler, self).__init__(args)
    
    def process(self):
        db = EWG_DATABASES[self.args['db']]
        url = self.args['url']
        scraper_cls = db[self.args['category']][self.args['subcategory']]['child'][self.args['child']]
        logger.info(f'Scraping {self.args["db"]} item_url {url}')
        html = None
        try:
            html = get_html_by_url(url)
        except Exception:
            logger.exception(f"Couldn't access item_url {url}, skipping...")
            return []
        scraper = scraper_cls(html)
        return [scraper.scrape_item()]
