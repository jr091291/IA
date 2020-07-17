import bs4
import requests
import re

from config_model import Config, QueryWebScraper, PaginationOption, Query

class WebPage:
    def __init__(self, config : Config):
        self._config = config
        self._html = None
        
    def _get_request_url(self, url:str) -> bool:
        try:
            url_regex = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            if re.match(url_regex, url):
                response = requests.get(url)
                response.raise_for_status()
                self._html = bs4.BeautifulSoup(response.text, 'html.parser')
                return True
        except:
            self._html = None
            return False

    def _select(self, query :Query , limit = 0):
        result = []
        if self._html:
            query_result = self._html.select(query.selector)  
        
            if query_result:
                max_items = lambda limit,items: True if limit and len(items)>= limit else False
        
                if query.return_type == 'attr':
                    for el in query_result:
                        if el.has_attr(query.value) :
                            result.append(el[query.value])
                            if max_items(limit, result):
                                break
                else:
                    for el in query_result:
                        result.append(el.text)
                        if max_items(limit, result):
                                    break
        return result
    
    def _items_complite(self, link_list):
        if len(link_list) < self._config.max_items:
            return False
        return True

    @staticmethod
    def build_full_link(host, link):
        is_root_path = re.compile(r'^/.+$')
        
        if is_root_path.match(link):
            host =  re.findall("^https?:\/\/?www\.?[^\/]+",host)
            if host:
                return '{host}{uri}'.format(host=host[0],uri=link)
        else:
            return link
        return '{host}{uri}'.format(host=host,uri=link)


class HomePage(WebPage):

    def __init__(self, config : Config):
        super().__init__(config)
        self._get_request_url(self._config.url)

    @property
    def items_links(self):
        items = []
        count_items = 0
        no_fount_new_items = 0
        
        items = self._get_links_items(items)

        if not self._items_complite(items)  and self._config.pagination.active:
            for page in range( self._config.pagination.max_page + 1 ):
                url = self._build_page_url(page)             
                goPage = self._get_request_url(url)

                if goPage:
                    items = self._get_links_items(items)
                    
                    temp = len(items)
                    
                    if temp > count_items:
                        count_items = temp
                        print('{} links found on {} pages. {}'.format(count_items, page+2, url))
                    else: 
                        no_fount_new_items += 1
                
                if not goPage or  self._items_complite(items) or no_fount_new_items > 5:
                        break
        return items[:self._config.max_items]

    def _get_links_items(self, link_list: list):
        q =  Query(**self._config.queries.items)
        for link in self._select(q):
            link_list.append(self.build_full_link(self._config.url, link))

        return  list(set(link_list))

    def _build_page_url(self, page:int):
         for param in self._config.pagination.parametes_link.split("|"):
            regex = r'('+ param +')\d+'
            num_page = ( self._config.pagination.min_page + self._config.pagination.step_page * page )
            string_page = param + str(num_page)
            url = re.sub(regex, string_page, self._config.pagination.link)
            return url

class ItemPage(WebPage):   
    def __init__(self, config : Config, url: str):
        super().__init__(config)
        self.url = url
     
    @property
    def item_data(self):
        try:
            data = {}
            if self._get_request_url(self.url):
                fields = self._config.queries.fields
            
                for q in fields:
                    field_html = self._select(q, limit=1)
                    
                    if field_html:
                        _data = field_html[0]
                        _data = re.sub(r"[\n+\t]+","",_data)
                        data[q.key] = _data
                    else:
                        data[q.key] = q.default
            return data
        except :
            return None
     
