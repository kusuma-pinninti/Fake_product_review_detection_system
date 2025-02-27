import streamlit as st
import requests
from pydantic import BaseModel, Field
from utils import (
    text_preprocess, model, vectorizer,
    nlp, gemini_model
)

# ScraperAPI Configuration
SCRAPERAPI_KEY = "1e539fae26943c2d809b5c2f2988555d"
SCRAPERAPI_URL = "http://api.scraperapi.com"

class ExtractSchema(BaseModel):
    product_title: str = Field(default="Product Name Not Found")
    product_image: str = Field(default=None)
    product_reviews: list[str] = Field(default=[])
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
        # Check if reviews are empty
        if not reviews:
            st.warning("No reviews found. Try another product.")
            return None
        
        # Combine reviews into a single string
        combined_reviews = " ".join(reviews)
        
        # Create the prompt for Gemini
        prompt = f"Analyze the following product reviews and provide a summary of pros and cons:\n\n{combined_reviews}\n\nPros:\n1. \n\nCons:\n1. "
        
        # Log the prompt being sent to Gemini
        print("Sending prompt to Gemini:", prompt)
        
        # Send the prompt to Gemini
        response = gemini_model.generate_content(prompt)
        
        # Log the response from Gemini
        print("Response from Gemini:", response.text)
        
        # Validate the response
        if response and hasattr(response, "text"):
            return response.text
        else:
            print("Invalid response from Gemini:", response)
            return None
    except Exception as e:
        # Log the error
        print(f"Error analyzing reviews with Gemini: {e}")
        return None
def fetch_product_info_scraperapi(url):
    """Fetch product details and reviews using ScraperAPI."""
    params = {
        "api_key": SCRAPERAPI_KEY,
        "url": url,
        "render": "true"
    }
    try:
        response = requests.get(SCRAPERAPI_URL, params=params)
        response.raise_for_status()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        product_name, product_image, reviews = None, None, []

        if "amazon" in url.lower():
            product_name = soup.find("span", {"id": "productTitle"})
            image_tag = soup.find("img", {"id": "landingImage"})
            reviews = [review.text.strip() for review in soup.find_all("span", {"data-hook": "review-body"})]
            product_image = image_tag["src"] if image_tag else None

        elif "flipkart" in url.lower():
            # Extract product name
            product_name = soup.find("span", {"class": "VU-ZEz"})
            
            # Extract product image
            image_tag = soup.find("img", {"class": "_396cs4 _2amPTt _3qGmMb"})
            product_image = image_tag["src"] if image_tag else None

            # Extract reviews
            review_divs = soup.find_all("div", {"class": "ZmyHeo"})
            for review_div in review_divs:
                review_text_div = review_div.find("div", {"class": ""})  # Review text is in a div with no class
                if review_text_div:
                    review_text = review_text_div.text.strip()
                    reviews.append(review_text)

        elif "myntra" in url.lower():
            product_name = soup.find("h1", {"class": "pdp-name"})
            image_div = soup.find("div", {"class": "image-grid-image"})
            reviews = [review.text.strip() for review in soup.find_all("div", {"class": "user-review-reviewTextWrapper"})]

            # Extract image from inline style
            if image_div:
                style_attr = image_div.get("style", "")
                import re
                match = re.search(r'url\(&quot;(.*?)&quot;\)', style_attr)
                if match:
                    product_image = match.group(1)

        # Ensure product_name is a valid string
        product_name = product_name.text.strip() if product_name else "Product Name Not Found"

        # Fix protocol-relative URLs for images
        if product_image and product_image.startswith("//"):
            product_image = "https:" + product_image

        return product_name, product_image, reviews

    except Exception as e:
        st.error(f"API Request Failed: {e}")
        return None, None, None


# Streamlit UI
st.title("Product Review Analysis")
st.write("Enter a product URL from Amazon, Flipkart, or Myntra to analyze its reviews.")

product_url = st.text_input("Enter Product URL:", key="product_url_input")

if st.button("Analyze Product"):
    if product_url.strip():
        if any(domain in product_url.lower() for domain in ["amazon", "flipkart", "myntra"]):
            with st.spinner("Fetching product details..."):
                product_name, product_image, reviews = fetch_product_info_scraperapi(product_url)
            
            if product_name:
                if product_image and not product_image.endswith(".svg"):  # Skip SVG images
                    st.image(product_image, caption=product_name, width=300)
                else:
                    st.markdown(f"<h2 style='text-align: center;'>{product_name}</h2>", unsafe_allow_html=True)
                
                if reviews:
                    st.subheader("🔍 Analysis Results")
                    results = analyze_reviews(reviews)
                    st.write(f"Fake Reviews: {results['fake_percentage']:.2f}%")
                    st.write(f"Genuine Reviews: {results['genuine_percentage']:.2f}%")
                    st.write(f"Estimated Rating: {results['average_rating']}/5")
                    
                    with st.spinner("Getting AI insights..."):
                        gemini_result = analyze_reviews_with_gemini(reviews)
                        if gemini_result:
                            st.subheader("Features Analysis")
                            st.write(gemini_result)
                        else:
                            st.warning("Unable to analyze reviews with Gemini API.")
                else:
                    st.warning("No reviews found. Try another product.")
            else:
                st.error("Failed to fetch product information. Please check the URL.")
        else:
            st.error("Unsupported website. Please provide a valid Amazon, Flipkart, or Myntra URL.")
    else:
        st.warning("Please enter a valid product URL.")
