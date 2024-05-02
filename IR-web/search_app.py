import json
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Necessary NLTK resource downloads
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')  # For lemmatization
# nltk.download('vader_lexicon')

def preprocess_query(query):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    # Remove punctuation
    query = query.translate(str.maketrans('', '', string.punctuation))
    word_tokens = word_tokenize(query)
    # Remove stopwords and lemmatize
    filtered_query = ' '.join([lemmatizer.lemmatize(word.lower()) for word in word_tokens if word.lower() not in stop_words])
    return filtered_query

def load_vectorizers():
    with open('title_vectorizer.pkl', 'rb') as f:
        title_vectorizer = pickle.load(f)
    return title_vectorizer

def search_articles(query):
    # Preprocess the query
    processed_query = preprocess_query(query)
    
    # Load vectorizers
    title_vectorizer = load_vectorizers()
    
    # Transform query using both vectorizers
    query_title_vec = title_vectorizer.transform([processed_query])
    
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017')
    db = client['articles_database']
    collection = db['articles_database']
    
    # Fetch all article vectors from MongoDB
    articles = list(collection.find({}, {"title_vector": 1, "content_vector": 1, "title": 1, "content": 1, "url": 1}))
    
    # Calculate cosine similarity and combine scores
    results = []
    for article in articles:
        title_sim = cosine_similarity(query_title_vec, article["title_vector"])[0][0]
        combined_score = title_sim
        results.append({
            'score': combined_score,
            'title': article['title'],
            'content': article['content']
        })
    
    # Sort results based on combined scores and return top 10
    results.sort(reverse=True, key=lambda x: x['score'])
    return results[:10]  # Returns a list of dictionaries

# Example usage:
# query = "Federal Reserve interest rates"
# results = search_articles(query)
# print(json.dumps(results, indent=4))  # Printing the JSON formatted string