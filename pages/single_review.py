import streamlit as st
from utils import text_preprocess, model, vectorizer

#st.set_page_config(page_title="Single Review Analysis", layout="wide")

# Hero Section
st.markdown("""
    <div class="hero-section">
        <h1>Single Review Analysis</h1>
        <p>Get instant insights into the authenticity of any review</p>
    </div>
    """, unsafe_allow_html=True)

# Features Overview
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="feature-card">
            <h3>✨ Features</h3>
            <ul>
                <li>Advanced AI-powered analysis</li>
                <li>Instant results</li>
                <li>Detailed authenticity score</li>
                <li>Pattern recognition</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <h3>🎯 How to Use</h3>
            <ol>
                <li>Paste your review in the text box below</li>
                <li>Click "Analyze Review"</li>
                <li>Get instant results</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)

# Analysis Section
st.markdown("### 📝 Enter Your Review")
review = st.text_area("", height=150, placeholder="Paste your review here...")

if st.button("Analyze Review", key="analyze_button"):
    if review.strip():
        with st.spinner("Analyzing review..."):
            processed_review = text_preprocess(review)
            tfidf_review = vectorizer.transform([processed_review])
            prediction = model.predict(tfidf_review)[0]

            if prediction == "OR":
                st.success("✅ Genuine Review")
                st.markdown("""
                    <div class="feature-card">
                        <h4>Analysis Details</h4>
                        <p>This review shows characteristics of authentic user feedback:</p>
                        <ul>
                            <li>Natural language patterns</li>
                            <li>Genuine user sentiment</li>
                            <li>Authentic experience sharing</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error("⚠ Fake Review")
                st.markdown("""
                    <div class="feature-card">
                        <h4>Analysis Details</h4>
                        <p>This review shows potential signs of being fake:</p>
                        <ul>
                            <li>Unusual patterns detected</li>
                            <li>Potential automated content</li>
                            <li>Suspicious language structures</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Please enter a review to analyze.")

if st.button("Back to Home"):
    st.switch_page("main.py")