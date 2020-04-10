import re
import traceback
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

from core.custom_exceptions import ResourceUnavailable, ParsingElementNotFound
from core.async_abstract_bowl import AsyncAbstractBowl


class AsyncPythonJobsBowl(AsyncAbstractBowl):
    default_pages = 4
    list_url_template = 'https://www.pythonjobs.com/'
    url_root = 'https://www.pythonjobs.com'
    doc_type = 'job'

    def __init__(self, storage_object, session_obj, logger_name, **kwargs):
        super().__init__(storage_object, session_obj, logger_name, doc_type=self.doc_type, **kwargs)

    @staticmethod
    def elasticsearch_get_setup_settings():

        mappings = {
            "properties": {
                "title": {"type": "text"},
                "skills": {"type": "text", "copy_to": "suggest"},
                "type": {"type": "keyword"},
                'date': {'type': 'date', 'format': 'date_hour_minute_second'},
                "description": {"type": "text"},
                "location": {"type": "text", "copy_to": "suggest"},
                "poster": {"type": "nested"},
                "url": {"type": "keyword"},
                "external_id": {"type": "keyword"},
                "suggest": {
                    "type": "completion",
                }
            }
        }

        return mappings

    async def get_links(self):
        self.logger.info('Getting links ...')

        async def get_pages(n):
            list_url_template = self.list_url_template
            go_on = True
            i = 1
            while go_on and i <= n:
                page_text = await self.session_obj.get(list_url_template.format(i), (2, 7))
                page_bs = BeautifulSoup(page_text, 'html.parser')
                if page_bs.find_all('h1', text='No Record Found'):
                    go_on = False
                yield page_bs
                i += 1

        async for page_soup in get_pages(n=self.default_pages):
            for link in page_soup.find_all(name="a", class_='jobList-title'):
                # links are relative, must turn them into absolute
                link['href'] = self.url_root + link['href']
                if self.storage_object.record_exists('links_crawled', 'url', link['href']):
                    self.logger.info('{} already visited. Ending link aquisition.'.format(link['href']))
                    return
                self.curent_links.append(link['href'])

    async def parse_page(self, url):
        self.curent_parse_error = False
        job = {
            'poster': {}
        }
        self.logger.info('Sending request for url {}'.format(url))
        page = await self.session_obj.get(url, (2, 5))
        page_bs = BeautifulSoup(page, 'html.parser')

        try:
            self.logger.info('Parsing...')
            if page_bs.find(string=re.compile('Project Deleted')) or page_bs.find(string=re.compile('Private Project')):
                raise ResourceUnavailable
            
            employer, location, type = self.get_header_info(page_bs)

            job['url'] = url
            job['external_id'] = re.search(r'jobs/(\d+)', url).group(1)
            job['title'] = self.extract_text(
                page_bs.find(class_='u-textH2').text,
                'title'
            )
            job['skills'] = ''
            job['description'] = self.extract_text(
                bs_result=page_bs.find(class_='job-body').find(name='div'),
                error_id='description',
                modify=lambda s: s[s.find('Title'):s.find('Apply')] 
            )
            job['location'] = self.extract_text(
                location,
                'location'
            )
            job['type'] = self.extract_text(
                type,
                'type'
            )
            job['poster']['name'] = self.extract_text(
                employer,
                'poster:name'
            )
        except AttributeError as e:
            msg = traceback.format_exc()
            raise ParsingElementNotFound('Error while parsing. Traceback: \n {}'.format(msg))

        if self.curent_parse_error:
            self.links_errors += 1
            self.register_parse_error()

        return job
    
    
    def get_header_info(self, bs) -> list:
        raw = bs.find(class_='jobDetail-headerIntro').find(class_="u-mt--large")
        l = []
        for c in raw.children:
            if type(c) != NavigableString:
                txt = c.get_text().split('\n')
                l += txt
        while "" in l: l.remove("")
        return l
        
