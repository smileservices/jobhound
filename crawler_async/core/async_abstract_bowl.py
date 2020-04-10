from string import ascii_letters, digits
from abc import ABC, abstractmethod
import logging
import datetime
from core.custom_exceptions import ResourceUnavailable, ParsingElementNotFound, ParsingErrorThresholdPassed
import bs4
from bs4.element import Tag, NavigableString

class AsyncAbstractBowl(ABC):
    parsing_errors = 0
    curent_parse_error = False

    doc_type = 'document'

    curent_links = []
    links_crawled = 0
    links_errors = 0

    def __init__(self, storage_object, session_obj, logger_name, err_threshold=(10, 0.7), **kwargs):
        default_chars = list(ascii_letters) + list(digits) + [' ', ',', '(', ')', ';', '.', '!', '-', '&', '/', '$',
                                                              '?']
        self.permitted_chars = kwargs['permitted_chars'] if 'permitted_chars' in kwargs else default_chars
        self.storage_object = storage_object
        self.session_obj = session_obj
        self.logger = logging.getLogger(logger_name)
        self.err_threshold = err_threshold

    def extract_text(self, bs_result, error_id, is_list=False, modify=lambda s: s):
        def get_text(stuff):
            if type(stuff) == str:
                return modify(stuff)
            if type(stuff) == NavigableString:
                s = ''
                for l in stuff:
                    if type(l) != NavigableString:
                        s += str(l.get_text()) + '\n'
                return modify(s)
            if stuff == None:
                self.curent_parse_error = True
                self.logger.info('Parse error for field {}'.format(error_id))
                return ''
            else:
                return stuff.text

        def sanitize_string(string):
            ld = list(str(string))
            for i, c in enumerate(ld):
                if c not in self.permitted_chars:
                    ld[i] = ''
            result = ''.join(ld)
            return result

        if is_list:
            sanitized_list = []
            for res in bs_result:
                sanitized_list.append(sanitize_string(get_text(res)))
            result = sanitized_list
        else:
            result = sanitize_string(get_text(bs_result))

        return result

    async def start(self):
        self.logger.info('starting truelancer crawler...')
        await self.get_links()

        for url in self.curent_links:
            try:
                result = await self.parse_page(url)
                self.links_crawled += 1
                self.storage_object.save(self.doc_type, self.add_timestamp(result), result['external_id'])
                self.storage_object.save('links_crawled', self.add_timestamp({'url': url, 'status': 'ok'}))

            except ResourceUnavailable:
                self.links_crawled += 1
                self.storage_object.save('links_crawled', self.add_timestamp({'url': url, 'status': 'unavailable'}))
                pass

            except ParsingElementNotFound as err:
                self.links_errors += 1
                self.storage_object.save('links_crawled', self.add_timestamp({'url': url, 'status': 'parse error'}))
                try:
                    self.register_parse_error(err)
                except ParsingErrorThresholdPassed:
                    self.logger.info('ParsingErrorThresholdPassed: Sending email to admin ...')
                pass

            except ParsingErrorThresholdPassed:
                self.logger.info('ParsingErrorThresholdPassed: Sending email to admin ...')
                self.storage_object.save('links_crawled', self.add_timestamp({'url': url, 'status': 'parse error'}))

        self.logger.info('truelancer crawler finished')
        # return True

    def add_timestamp(self, dict, fieldname='date'):
        date_now = datetime.datetime.now()
        date_iso = date_now.replace(microsecond=0).isoformat()
        dict[fieldname] = date_iso
        return dict

    def register_parse_error(self, err=None):
        self.parsing_errors += 1
        total_links_visited = self.links_crawled + self.links_errors
        parsed_err = self.parsing_errors / total_links_visited
        self.logger.warning(
            'Error: ParsingElementNotFound -- {} err ratio -- {} errors / {} pages\n Error threshold: {}'.format(
                parsed_err,
                self.parsing_errors,
                total_links_visited,
                self.err_threshold
            )
        )
        self.logger.warning(str(err)) if err else None
        if total_links_visited > self.err_threshold[0] and parsed_err > self.err_threshold[1]:
            self.logger.error(
                'ParsingErrorThresholdPassed raised by {}: {} errs ratio'.format(
                    self.__class__.__name__,
                    parsed_err
                )
            )
            raise ParsingErrorThresholdPassed

    @abstractmethod
    async def get_links(self):
        pass

    @abstractmethod
    async def parse_page(self, url):
        pass
