import pandas as pd
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import string
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')  # For lemmatization
nltk.download('vader_lexicon')

def remove_stopwords_and_lemmatize(text):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    word_tokens = word_tokenize(text)
    # Remove stopwords and lemmatize
    filtered_text = ' '.join([lemmatizer.lemmatize(word.lower()) for word in word_tokens if word.lower() not in stop_words])
    return filtered_text


def main():
    data = pd.read_csv('C:/Users/gauth/Desktop/courses/CS5604/project/IR-web/updateInfoStorage/updateInfoStorage/data/articles1.csv', nrows=10000)
    print("Processing text")
    data['title_filtered'] = data['title'].apply(remove_stopwords_and_lemmatize)

    # Vectorizers for title and first 50 words
    title_vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    
    print("Vectorizing title and content")
    title_matrix = title_vectorizer.fit_transform(data['title_filtered'])
    
    # Save vectorizers
    with open('title_vectorizer.pkl', 'wb') as f:
        pickle.dump(title_vectorizer, f)
    
    sid = SentimentIntensityAnalyzer()
    client = MongoClient('mongodb://localhost:27017')
    db = client['articles_database']
    collection = db['articles_database']
    
    # Store articles with vectors
    for index, row in data.iterrows():
        sentiment = sid.polarity_scores(row['content'])
        article = {
            "id": row['id'],
            "title": row['title'],
            "author": row['author'],
            "publication": row['publication'],
            "date": row['date'],
            "url": row['url'],
            "content": row['content'],
            "title_vector": title_matrix[index].todense().tolist(),
            "sentiment": {
                "positive": sentiment['pos'],
                "negative": sentiment['neg'],
                "neutral": sentiment['neu']
            }
        }
        collection.insert_one(article)
        print(f"Inserted article {row['id']}")

if __name__ == "__main__":
    main()