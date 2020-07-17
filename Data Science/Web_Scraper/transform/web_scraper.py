import requests
from bs4 import BeautifulSoup

class Scraper:
  def __init__(self, url, parser = 'html.parser'):
    self.parser = parser
    self.html = None
    self._url = url  
    self.set_url(url)
  
  def set_url(self, url):
    self._url = url
    self.get(url, self.parser)

  def get(self, url, parser):
    try:   
      response = requests.get(url, parser)
      response.raise_for_status()

      if response: 
          self.html = BeautifulSoup(response.text, parser)
    except:
      return []

  def query(self, selector):
    try:   
      return self.html.select(selector)
    except:
      return None