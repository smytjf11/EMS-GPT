########################################################
#
# A Python script to scrape the full text from a specific website and its subpages, excluding external links and higher-level pages. 
#
########################################################

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
from llama_index import download_loader
from langchain import OpenAI
import openai
import os
from llama_index import Document
from dotenv import load_dotenv

load_dotenv()
openai.api_key =  os.environ["OPENAI_API_KEY"]
SimpleWebPageReader = download_loader("SimpleWebPageReader")

def get_internal_links(starting_url, soup):
    domain = urlparse(starting_url).netloc
    internal_links = set()
    
    for link in soup.find_all('a'):
        href = link.get('href')
        joined_url = urljoin(starting_url, href)
        
        if urlparse(joined_url).netloc == domain and joined_url.startswith(starting_url):
            internal_links.add(joined_url)

    return internal_links

def extract_text(soup):
    relevant_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    text = []
    
    for tag in relevant_tags:
        for element in soup.find_all(tag):
            text.append(element.get_text(separator=' '))
            
    return ' '.join(text)

def recursive_scrape(url, visited=None):
    if visited is None:
        visited = set()
    if url in visited:
        return pd.DataFrame(columns=['site', 'text'])
    
    visited.add(url)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        print(f"Error: Failed to retrieve {url}")
        return pd.DataFrame(columns=['site', 'text'])

    soup = BeautifulSoup(response.content, 'html.parser')
    internal_links = get_internal_links(url, soup)

    doc =  Document(extract_text(soup))

    text_tbl = pd.DataFrame([[url, doc]], \
                columns=['site', 'text'])

    for link in internal_links:
        print(link)
        text_tbl = pd.concat([text_tbl, recursive_scrape(link, visited)])

    return text_tbl

if __name__ == "__main__":
    #starting_url = 'https://www.ruralhealthinfo.org/toolkits/emergency-preparedness'
    #content = recursive_scrape(starting_url)
    #content.reset_index().to_json("./ruralhealthinfo.json")

    content = pd.read_json("./ruralhealthinfo.json")
    print(content)



