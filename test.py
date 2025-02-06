import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import joblib
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Load a pre-trained fake review detection model (if you have one)
# model = joblib.load("fake_review_detector.pkl")

def extract_reviews(url):
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no browser UI)
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(url)
    time.sleep(5)  # Wait for the page to load fully

    reviews = []
    try:
        review_elements = driver.find_elements(By.XPATH, "//span[@data-hook='review-body']")
        reviews = [review.text.strip() for review in review_elements if review.text.strip()]
    except Exception as e:
        print("Error extracting reviews:", e)
    
    driver.quit()
    return reviews

def analyze_sentiment(reviews):
    sentiments = [sia.polarity_scores(review)["compound"] for review in reviews]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    return "Positive" if avg_sentiment > 0.05 else "Negative" if avg_sentiment < -0.05 else "Neutral"

# Fake review detection (Placeholder for actual ML model prediction)
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
