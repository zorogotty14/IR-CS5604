import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import re

def fetch_html(url):
    """Fetch HTML content from a given URL."""
    response = requests.get(url)
    return response.content if response.status_code == 200 else None

def clean_text(text):
    """Clean text by removing unwanted characters and normalizing whitespace."""
    text = text.replace('\\"', '"').replace('\xa0', ' ')
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape_cnn(url):
    """Scrape CNN article and return cleaned data as a dictionary."""
    html = fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    headline = soup.find('h1', id='maincontent')
    content_container = soup.select_one('div.article__content')
    paragraphs = content_container.find_all('p') if content_container else []
    return {
        'url': url,
        'title': clean_text(headline.text) if headline else 'Headline not found',
        'body': ' '.join(clean_text(paragraph.text) for paragraph in paragraphs if paragraph.text)
    }

def scrape_fox(url):
    """Scrape Fox News article and return cleaned data as a dictionary."""
    html = fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    headline = soup.select_one('header.article-header h1.headline')
    content_container = soup.select_one('div.article-body')
    paragraphs = content_container.find_all('p') if content_container else []
    return {
        'url': url,
        'title': clean_text(headline.text) if headline else 'Headline not found',
        'body': ' '.join(clean_text(paragraph.text) for paragraph in paragraphs if paragraph.text)
    }

def scrape_nyt(url):
    """Scrape The New York Times article and return cleaned data as a dictionary."""
    html = fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    headline = soup.find('h1', {'data-test-id': 'headline'})
    content_container = soup.find('section', {'name': 'articleBody'})
    paragraphs = content_container.find_all('p') if content_container else []
    return {
        'url': url,
        'title': clean_text(headline.text) if headline else 'Headline not found',
        'body': ' '.join(clean_text(paragraph.text) for paragraph in paragraphs if paragraph.text)
    }

def scrape_wapo(url):
    """Scrape The Washington Post article and return cleaned data as a dictionary."""
    html = fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    headline = soup.find('h1')
    content_container = soup.find('article')
    paragraphs = content_container.find_all('p') if content_container else []
    return {
        'url': url,
        'title': clean_text(headline.text) if headline else 'Headline not found',
        'body': ' '.join(clean_text(paragraph.text) for paragraph in paragraphs if paragraph.text)
    }

def scrape_usatoday(url):
    """Scrape USA Today article and return cleaned data as a dictionary."""
    html = fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    headline = soup.find('h1', {'class': 'gnt_ar_hl'})
    content_container = soup.find('div', {'class': 'gnt_ar_b'})
    paragraphs = content_container.find_all('p') if content_container else []
    return {
        'url': url,
        'title': clean_text(headline.text) if headline else 'Headline not found',
        'body': ' '.join(clean_text(paragraph.text) for paragraph in paragraphs if paragraph.text)
    }

def detect_and_scrape(url):
    """Detect the news site from the URL and return scraped and cleaned data as JSON."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if 'cnn.com' in domain:
        article_data = scrape_cnn(url)
    elif 'foxnews.com' in domain:
        article_data = scrape_fox(url)
    elif 'nytimes.com' in domain:
        article_data = scrape_nyt(url)
    elif 'washingtonpost.com' in domain:
        article_data = scrape_wapo(url)
    elif 'usatoday.com' in domain:
        article_data = scrape_usatoday(url)
    else:
        article_data = {'error': 'Site not supported'}
    return json.dumps(article_data, indent=4)

# if __name__ == "__main__":
#     urls = [
#         'https://www.cnn.com/2024/04/25/politics/takeaways-trump-immunity-supreme-court/index.html',
#         'https://www.foxnews.com/media/usc-sparks-backlash-canceling-main-stage-commencement', 
#         'https://www.washingtonpost.com/politics/2024/04/25/trump-trials-supreme-court/',
#         'https://www.usatoday.com/story/news/politics/elections/2024/04/25/supreme-court-obstruction-jan-6/73458039007/' 
#     ]
#     for url in urls:
#         print(detect_and_scrape(url))
