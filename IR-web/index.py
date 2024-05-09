from flask import Flask, render_template, request, session
import requests

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
    return render_template('article_results.html',article_text=article_text)
    

@app.route('/')
def search_results():
    if 'search_results' in session:
        search_results = session['search_results']
        query = search_results.get('query')
        return render_template('search_results.html', query=query, results=search_results)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
