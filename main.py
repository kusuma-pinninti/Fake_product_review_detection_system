# main.py
import streamlit as st

st.set_page_config(page_title="Fake Review Detection System", layout="wide")

# Enhanced CSS with animations and better styling
st.markdown("""
    <style>
    .main .block-container {
        max-width: 90%;
        padding: 2rem;
        margin: auto;
    }
    .hero-section {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    .stat-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem;
    }
    .footer {
        padding: 20px;
        background-color: #f0f2f6;
        border-top: 2px solid #ddd;
        text-align: center;
        font-family: Arial, sans-serif;
        color: #333;
        margin-top: 30px;
    }
    .cta-button {
        background-color: #2a5298;
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin-top: 1rem;
        transition: background-color 0.3s ease;
    }
    .cta-button:hover {
        background-color: #1e3c72;
    }
    </style>
    """, unsafe_allow_html=True)

# Hero Section
st.markdown("""
    <div class="hero-section">
        <h1>🛒 Fake Review Detection System</h1>
        <p style="font-size: 1.2rem; margin: 1rem 0;">
            Unleash the power of AI to detect fake reviews and make informed decisions
        </p>
    </div>
    """, unsafe_allow_html=True)

# Statistics Section
st.markdown("### 📊 Why Choose Our System?")
col1, col2, col3= st.columns(3)

with col1:
    st.markdown("""
        <div class="stat-card">
            <h3>95%</h3>
            <p>Accuracy Rate</p>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class="stat-card">
            <h3>24/7</h3>
            <p>Real-time Analysis</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="stat-card">
            <h3>AI-Powered</h3>
            <p>Advanced ML Models</p>
        </div>
    """, unsafe_allow_html=True)

# Features Section
st.markdown("### 🚀 Choose Your Analysis Method")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="feature-card">
            <h3>📝 Single Review Analysis</h3>
            <p>Instantly analyze individual reviews with our advanced AI model.</p>
            <ul>
                <li>Real-time analysis</li>
                <li>Detailed authenticity score</li>
                <li>Instant results</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Try Single Review Analysis"):
        st.switch_page("pages/single_review.py")

with col2:
    st.markdown("""
        <div class="feature-card">
            <h3>🔍 Product Review Analysis</h3>
            <p>Get comprehensive insights from multiple reviews of a product.</p>
            <ul>
                <li>Bulk review analysis</li>
                <li>Sentiment analysis</li>
                <li>Trend detection</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Try Product Review Analysis"):
        st.switch_page("pages/product_review.py")

# How It Works Section
st.markdown("### 🔄 How It Works")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="feature-card">
            <h4>1. Input</h4>
            <p>Enter a review or product URL that you want to analyze</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <h4>2. Analysis</h4>
            <p>Our AI model processes the content using advanced algorithms</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-card">
            <h4>3. Results</h4>
            <p>Get detailed insights and authenticity scores instantly</p>
        </div>
    """, unsafe_allow_html=True)

# Footer with Contributors
st.markdown("---")
st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: space-around;">
            <div>
                <h3>Project Contributors</h3>
                <p><strong>Pinninti Kusuma</strong></p>
                <p><strong>Polamarasetti Vivek Vardhan</strong></p>
                <p><strong>Pinninti Sai Manikanta</strong></p>
                <p><strong>Potabatuula Arya</strong></p>
            </div>
            <div>
                <h3>Guided by</h3>
                <p><strong>Dr. N.V.S Lakshmipathi Raju</strong></p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)