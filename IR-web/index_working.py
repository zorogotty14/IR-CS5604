from flask import Flask, render_template, request, session
import requests
from search_app import *
from urlScraper import *
from openai import OpenAI

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")


app = Flask(__name__, static_folder='static')
# Set a secret key for your application
app.secret_key = 'adjdaondpimppoepskop23'

API_URL = "https://newsnow.p.rapidapi.com/newsv2"
API_KEY = "0a0b72559emshc1ca09f720d7505p15e229jsnfcf4f42dc10a"


@app.route('/search', methods=['POST'])
def search():
    query = request.form['search_query']
    results = search_articles(query)
    print(results)
    payload = {
        "query": query,
        "time_bounded": True,
        "from_date": "01/02/2021",
        "to_date": "05/06/2021",
        "location": "us",
        "language": "en",
        "page": 1
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "newsnow.p.rapidapi.com"
    }
    response = requests.post(API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        web_search_results = response.json()
        session['web_search_results'] = web_search_results
        return render_template('search_results.html', query=query, db_results=results, web_results=web_search_results)
    else:
        return "Error: Unable to retrieve search results"


@app.route('/article-search', methods=['POST'])
def article_search():
    article_text = request.form['article_text']
    # completion = client.chat.completions.create(
    # model="QuantFactory/Meta-Llama-3-8B-Instruct-GGUF",
    # messages=[
    #     {"role": "system", "content": "Always answer in rhymes."},
    #     {"role": "user", "content": "Introduce yourself." }
    # ],
    # temperature=0.7,
    # )
    # result = completion.choices[0].message.content
    with open('test.txt', 'r', encoding='utf-8') as file:
        result = file.read().replace('#','')
    return render_template('article_results.html',article_text=article_text, result=result)

@app.route('/url-search', methods=['POST'])
def url_search():
    url = request.form['search_url']
    article_data = json.loads(detect_and_scrape(url))
    articles = [article_data]
    completion = client.chat.completions.create(
    model="QuantFactory/Meta-Llama-3-8B-Instruct-GGUF",
    messages=[
        {"role": "system", "content": "Always answer in rhymes."},
        {"role": "user", "content": "Introduce yourself." }
    ],
    temperature=0.7,
    )
    result = completion.choices[0].message.content
    return render_template('url_search_results.html', url=url, result=articles, LLM=result)
    

@app.route('/')
def search_results():
    if 'search_results' in session:
        search_results = session['search_results']
        query = search_results.get('query')
        return render_template('search_results.html', query=query, results=search_results)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
