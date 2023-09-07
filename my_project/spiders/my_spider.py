import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import scrapy
from scrapy import Spider, Request  # Added Request here
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

visited_urls = set()

def format_url(url):
    return url.replace(":", "_").replace("/", "_").replace("?", "_")

def is_relative_url(url):
    return not bool(urlparse(url).netloc)

def Ingest(html_content, url, depth=0, max_depth=10):
    if depth > max_depth:
        print(f"Reached max depth of {max_depth}. Stopping.")
        return

    if url in visited_urls:
        print(f"Already visited {url}. Skipping.")
        return

    visited_urls.add(url)
    output_directory = "DATA"
    os.makedirs(output_directory, exist_ok=True)
    filename = format_url(url) + ".html"
    filepath = os.path.join(output_directory, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)

    for link in links:
        href = link['href']
        if is_relative_url(href):
            href = urljoin(url, href)
        Ingest(html_content, href, depth=depth+1, max_depth=max_depth)

class MySpider(scrapy.Spider):
    name = 'my_spider'
    
    def __init__(self, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        
        # Initialize Selenium WebDriver
        service = Service('D:\\chromedriver-win64\\chromedriver.exe')
        self.driver = webdriver.Chrome(service=service)
        
    def start_requests(self):
        start_url = "https://online.hsc.com.vn/"
        self.driver.get(start_url)
        
        # Wait for 3 seconds
        time.sleep(3)
        
        # Get the page source and create a Scrapy Selector
        sel = Selector(text=self.driver.page_source)
        
        # Process the fetched content with your Ingest function
        Ingest(sel.get(), start_url)
        
        # Close the WebDriver
        self.driver.quit()
        
        # Yield a Scrapy Request object to meet Scrapy's requirements
        yield Request(url=start_url, callback=self.parse)

    def parse(self, response):
        # Your parsing logic here, if any. 
        # For now, it's empty because you're doing most of the work in Ingest.
        pass
