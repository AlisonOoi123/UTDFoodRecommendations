import numpy as np
import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

def extract_features_from_reviews(reviews):
    # Convert the list of reviews to a Pandas Series
    reviews_series = pd.Series(reviews)

    # TF-IDF Vectorization
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(reviews_series)

    # Sentiment Analysis
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = reviews_series.apply(lambda x: sia.polarity_scores(x)['compound'])

    # Combine TF-IDF and Sentiment scores
    features = np.hstack([tfidf_matrix.toarray(), sentiment_scores.values.reshape(-1, 1)])

    return features
