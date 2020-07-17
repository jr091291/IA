from typing import List

class PaginationOption:
    def __init__(self, active: bool, link: str, parametes_link: str,  max_page: int, min_page: int, step_page: int):
        super().__init__()
        self.active = active
        self.link = link
        self.parametes_link = parametes_link
        self.max_page = max_page
        self.min_page = min_page
        self.step_page = step_page

class QueryWebScraper:
    def __init__(self, items: str, fields: List[object]):
        super().__init__()
        self.items = items
        self.fields = fields

class Query:
    def __init__(self, selector:str, key:str='', return_type = 'text', value = '', default=''):
        super().__init__()
        self.key = key
        self.selector = selector
        self.return_type = return_type
        self.value = value
        self.default = default

class Config:
    def __init__(self, url: str, max_items: int ,paginationConfig: PaginationOption, queries: QueryWebScraper):
        super().__init__()
        self.url = url
        self.max_items = max_items
        self.pagination = paginationConfig
        self.queries = queries