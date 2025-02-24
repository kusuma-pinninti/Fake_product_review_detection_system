import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import spacy
import joblib
import gdown
import google.generativeai as genai
import streamlit as st
import os

# Only download NLTK resources if they don't exist
@st.cache_resource
def download_nltk_resources():
    try:
        stopwords.words("english")
    except LookupError:
        nltk.download("stopwords", quiet=True)
    try:
        word_tokenize("test")
    except LookupError:
        nltk.download("punkt", quiet=True)

# Load spaCy model with caching
@st.cache_resource
def load_spacy():
    return spacy.load("en_core_web_sm")

# Cache model downloads and loading
@st.cache_resource
def download_and_load_models():
    model_path = "random_forest_model.pkl"
    vectorizer_path = "tfidf_vectorizer.pkl"
    
    # Only download if files don't exist
    if not os.path.exists(model_path):
        gdown.download(f"https://drive.google.com/uc?id=1XEaBunWsBdU9-Vjp9pE8nffR4HxDrpY3", model_path, quiet=True)
    if not os.path.exists(vectorizer_path):
        gdown.download(f"https://drive.google.com/uc?id=1eqhrs7kp4X0DXskiI4rBMS5V3m0eZN8j", vectorizer_path, quiet=True)
    
    return joblib.load(model_path), joblib.load(vectorizer_path)

# Initialize resources once
download_nltk_resources()
nlp = load_spacy()
model, vectorizer = download_and_load_models()

# Configure Gemini API once
GEMINI_API_KEY = "AIzaSyDKl3pN0X1sIA6RCAu1kjb1c8xuKt9Hylc"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-pro")

# Cache text preprocessing
@st.cache_data
def text_preprocess(text):
    text = text.lower()
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Use spaCy tokenizer
    doc = nlp(text)
    words = [token.text for token in doc if token.is_alpha and token.text not in stopwords.words("english")]
    
    return " ".join(words)
