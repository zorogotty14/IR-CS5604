from flask import Flask, render_template, request, session
import requests
from search_app import *
from urlScraper import *
from openai import OpenAI

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

app = Flask(__name__)
# Set a secret key for your application
app.secret_key = 'app_secret_key'

API_URL = "https://newsnow.p.rapidapi.com/newsv2"
API_KEY = "add your API key"


@app.route('/search', methods=['POST'])
def search():
    query = request.form['search_query']
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
        search_results = response.json()
        session['search_results'] = search_results
        return render_template('search_results.html', query=query, results=search_results)
    else:
        return "Error: Unable to retrieve search results"


@app.route('/article-search', methods=['POST'])
def article_search():
    article_text = request.form['article_text']
    completion = client.chat.completions.create(
    model="zz-xx/gemma-7b-bnb-4bit-bias-q5_k_m",
    messages=[
        {"role": "user", "content": article_text }
    ],
    temperature=0.7,
    )
    result = completion.choices[0].message.content
    return render_template('article_results.html',article_text=article_text, result=result)

@app.route('/url-search', methods=['POST'])
def url_search():
    url = request.form['search_url']
    article_data = json.loads(detect_and_scrape(url))
    articles = [article_data]
    completion = client.chat.completions.create(
    model="zz-xx/gemma-7b-bnb-4bit-bias-q5_k_m",
    messages=[
        {"role": "user", "content": f"{article_data['title']}\n\n{article_data['body']}" }
    ],
    temperature=0.8,
    )
    result = completion.choices[0].message.content
    return render_template('url_search_results.html', url=url, result=articles, LLM=result)


if __name__ == '__main__':
    app.run(debug=True)
