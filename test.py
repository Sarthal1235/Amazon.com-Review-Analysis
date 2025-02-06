import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import joblib
import pandas as pd

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Function to extract reviews without Selenium
def extract_reviews(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    review_elements = soup.select("span[data-hook='review-body']")

    return [review.text.strip() for review in review_elements if review.text.strip()]

def analyze_sentiment(reviews):
    sentiments = [sia.polarity_scores(review)["compound"] for review in reviews]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    return "Positive" if avg_sentiment > 0.05 else "Negative" if avg_sentiment < -0.05 else "Neutral"

def detect_fake_reviews(reviews):
    if not reviews:
        return "Not enough data"
    
    fake_reviews = sum(1 for review in reviews if "fake" in review.lower() or "scam" in review.lower())
    percentage_fake = (fake_reviews / len(reviews)) * 100
    return "Fake Product" if percentage_fake > 50 else "Real Product"

# Streamlit UI
st.title("Amazon Product Review Analyzer")
st.markdown("Enter an Amazon product URL to check if the product is genuine and analyze customer sentiment.")

url = st.text_input("Amazon Product URL", "")
if st.button("Analyze"):
    if not re.match(r'https?://(www\.)?amazon\.(in|com)/', url):
        st.error("Please enter a valid Amazon product URL")
    else:
        reviews = extract_reviews(url)
        if not reviews:
            st.error("Could not fetch reviews. Please try another product.")
        else:
            sentiment = analyze_sentiment(reviews)
            authenticity = detect_fake_reviews(reviews)
            
            st.subheader("Analysis Result")
            st.write(f"**Product Authenticity:** {authenticity}")
            st.write(f"**Sentiment Analysis:** {sentiment}")
            
            st.subheader("Sample Reviews")
            st.write(pd.DataFrame(reviews[:5], columns=["Reviews"]))
