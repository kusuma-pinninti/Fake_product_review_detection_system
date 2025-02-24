import streamlit as st
import requests
from bs4 import BeautifulSoup
from utils import (
    text_preprocess, model, vectorizer,
    nlp, gemini_model
)

# Hero Section
st.markdown("""
    <div class="hero-section">
        <h1>Product Review Analysis</h1>
        <p>Comprehensive analysis of multiple reviews for deeper insights</p>
    </div>
    """, unsafe_allow_html=True)

# Features Overview
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="feature-card">
            <h3>🎯 Features</h3>
            <ul>
                <li>Bulk review analysis</li>
                <li>Sentiment analysis</li>
                <li>Trend detection</li>
                <li>AI-powered insights</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <h3>📊 What You Get</h3>
            <ul>
                <li>Authenticity percentage</li>
                <li>Detailed pros and cons</li>
                <li>Overall product rating</li>
                <li>AI-generated summary</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def scrape_amazon_product_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        product_name = soup.find('span', {'id': 'productTitle'})
        product_name = product_name.text.strip() if product_name else "Product Name Not Found"

        image_tag = soup.find('img', {'id': 'landingImage'}) or soup.find('img', {'class': 'a-dynamic-image'})
        image_url = image_tag['src'] if image_tag else None

        reviews = [review.text for review in soup.find_all('span', {'data-hook': 'review-body'})]
        return product_name, image_url, reviews
    except Exception as e:
        return None, None, None

# Function to compute rating using only genuine reviews
def compute_average_rating(sentiment_score, genuine_count):
    if genuine_count == 0:
        return 2.5  # Default neutral rating if no genuine reviews exist

    # Normalize sentiment score between 1 and 5 using only genuine reviews
    min_score, max_score = -genuine_count, genuine_count  # Worst-case and best-case scenario
    normalized_score = (sentiment_score - min_score) / (max_score - min_score)  # Scale to 0-1 range
    avg_rating = 1 + normalized_score * 4  # Scale from 1 to 5

    return round(avg_rating, 2)  # Keep within 2 decimal places

# Cache the review analysis function
@st.cache_data
def analyze_reviews(reviews):
    fake_count, genuine_count = 0, 0
    feature_sentiments = {}
    sentiment_score = 0  # Track sentiment score from genuine reviews only

    for review in reviews:
        processed = text_preprocess(review)
        if processed:
            tfidf_review = vectorizer.transform([processed])
            prediction = model.predict(tfidf_review)[0]

            if prediction == "OR":  # Genuine review
                genuine_count += 1  # Only count genuine reviews for rating
                
                # Extract sentiment from genuine reviews only
                doc = nlp(review)
                for token in doc:
                    if token.pos_ == "ADJ" and token.head.pos_ == "NOUN":
                        feature = token.head.text
                        sentiment = 1 if token.text in ["good", "great", "excellent", "love", "amazing"] else -1 if token.text in ["bad", "poor", "worst", "disappointed", "awful"] else 0
                        
                        if sentiment != 0:
                            feature_sentiments[feature] = feature_sentiments.get(feature, 0) + sentiment
                            sentiment_score += sentiment  # Sum sentiment scores from genuine reviews

            else:
                fake_count += 1  # Fake review, ignore sentiment score

    total = len(reviews)
    fake_percentage = (fake_count / total) * 100 if total > 0 else 0
    genuine_percentage = 100 - fake_percentage

    # Compute Rating Using Only Genuine Reviews
    avg_rating = compute_average_rating(sentiment_score, genuine_count)

    # Extract top 5 positive and negative features
    pros = [f for f, score in sorted(feature_sentiments.items(), key=lambda x: x[1], reverse=True) if score > 0][:5]
    cons = [f for f, score in sorted(feature_sentiments.items(), key=lambda x: x[1]) if score < 0][:5]

    return {
        'fake_percentage': fake_percentage,
        'genuine_percentage': genuine_percentage,
        'average_rating': avg_rating,
        'pros': pros,
        'cons': cons
    }

# Cache Gemini API calls
@st.cache_data(ttl=3600)
def analyze_reviews_with_gemini(reviews):
    try:
        combined_reviews = " ".join(reviews)
        prompt = f"Analyze the following product reviews and provide a summary of pros and cons:\n\n{combined_reviews}\n\nPros:\n1. \n\nCons:\n1. "
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return None

st.title("Product Review Analysis")
st.write("Enter an Amazon product URL to analyze its reviews.")

product_url = st.text_input("Enter Amazon product URL:")

if st.button("Analyze Product"):
    if product_url.strip():
        if "amazon" in product_url.lower():
            with st.spinner("Analyzing product reviews..."):
                product_name, product_image, reviews = scrape_amazon_product_info(product_url)
                if product_name:
                    if product_image:
                        st.image(product_image, caption=product_name, use_column_width=False, width=300)
                    else:
                        st.markdown(f"<h2 style='text-align: center;'>{product_name}</h2>", unsafe_allow_html=True)

                    if reviews:
                        results = analyze_reviews(reviews)
                        st.subheader("🔍 Analysis Results")
                        st.write(f"Fake Reviews: {results['fake_percentage']:.2f}%")
                        st.write(f"Genuine Reviews: {results['genuine_percentage']:.2f}%")
                        st.write(f"Estimated Rating: {results['average_rating']}/5")

                        with st.spinner("Getting AI insights..."):
                            st.subheader("Features Analysis")
                            gemini_result = analyze_reviews_with_gemini(reviews)
                            if gemini_result:
                                st.write(gemini_result)
                            else:
                                st.warning("Unable to analyze reviews with Gemini API.")
                    else:
                        st.warning("Unable to retrieve reviews. Check the URL or try another product.")
                else:
                    st.error("Failed to scrape product information. Please check the URL.")
        else:
            st.error("Unsupported website. Please provide a valid Amazon URL.")
    else:
        st.warning("Please enter a valid product URL.")

if st.button("Back to Home"):
    st.switch_page("main.py")