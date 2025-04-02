import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(text1, text2):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
    return round(similarity * 100, 2)

def similarity_page():
    st.subheader("Text Similarity Analyzer")
    col1, col2 = st.columns(2)
    
    with col1:
        text1 = st.text_area("First Text", height=150)
    with col2:
        text2 = st.text_area("Second Text", height=150)
    
    if text1 and text2 and st.button("Compare Texts"):
        with st.spinner("Calculating similarity..."):
            similarity = calculate_similarity(text1, text2)
            st.metric("Similarity Score", f"{similarity}%")
            st.progress(similarity / 100)
            
            if similarity > 80:
                st.success("Very High Similarity")
            elif similarity > 60:
                st.info("High Similarity")
            elif similarity > 40:
                st.warning("Moderate Similarity")
            elif similarity > 20:
                st.warning("Low Similarity")
            else:
                st.error("Very Different Content")