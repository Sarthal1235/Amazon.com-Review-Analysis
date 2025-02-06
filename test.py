import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import nltk
import tldextract
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

SITE_SCRAPING_CONFIG = {
    "amazon": "//span[@data-hook='review-body']",
    "flipkart": "._2-N8zT",
    "ebay": ".review-item-content",
    "walmart": ".review-text",
    "aliexpress": ".feedback-item"
}

def get_website_name(url):
    ext = tldextract.extract(url)
    return ext.domain  # Extracts amazon, flipkart, etc.

def get_driver():
    options = Options()
    options.add_argument("--headless")  # No UI mode for cloud
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Prevents memory issues
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service("/usr/bin/chromedriver")  # Use system-installed ChromeDriver
    return webdriver.Chrome(service=service, options=options)

def extract_reviews(url):
    site_name = get_website_name(url)
    xpath_pattern = SITE_SCRAPING_CONFIG.get(site_name)

    if not xpath_pattern:
        return ["Website not supported for scraping"]

    driver = get_driver()
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    reviews = []
    try:
        review_elements = driver.find_elements(By.XPATH, xpath_pattern)
        reviews = [review.text.strip() for review in review_elements if review.text.strip()]
    except Exception as e:
        print("Error extracting reviews:", e)
    
    driver.quit()
    return reviews

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

st.title("E-Commerce Product Review Analyzer")
st.markdown("Enter any product URL from major e-commerce platforms to check authenticity and analyze sentiment.")

url = st.text_input("Product URL", "")
if st.button("Analyze"):
    site_name = get_website_name(url)
    if site_name not in SITE_SCRAPING_CONFIG:
        st.error(f"Website '{site_name}' is not supported yet.")
    else:
        reviews = extract_reviews(url)
        if not reviews or "Website not supported" in reviews:
            st.error("Could not fetch reviews. Please try another product.")
        else:
            sentiment = analyze_sentiment(reviews)
            authenticity = detect_fake_reviews(reviews)
            
            st.subheader("Analysis Result")
            st.write(f"**Product Authenticity:** {authenticity}")
            st.write(f"**Sentiment Analysis:** {sentiment}")
            
            st.subheader("Sample Reviews")
            st.write(pd.DataFrame(reviews[:5], columns=["Reviews"]))