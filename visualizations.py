import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import defaultdict
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import pandas as pd
import spacy

# Load English language model for lemmatization
nlp = spacy.load("en_core_web_sm")
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def get_unique_lemmas(text):
    """Extract unique lemmas (base forms) from text"""
    doc = nlp(text)
    lemmas = set()
    for token in doc:
        if token.is_alpha and not token.is_stop and len(token.text) > 2:
            lemma = token.lemma_.lower()
            lemmas.add(lemma)
    return lemmas

def extract_unique_keywords(text, top_n=20):
    """Get top keywords with unique meanings"""
    doc = nlp(text)
    lemma_counts = defaultdict(int)
    
    for token in doc:
        if (token.is_alpha and not token.is_stop and 
            len(token.text) > 2 and token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB']):
            lemma = token.lemma_.lower()
            lemma_counts[lemma] += 1
    
    # Get most frequent unique lemmas
    sorted_lemmas = sorted(lemma_counts.items(), key=lambda x: x[1], reverse=True)
    return [lemma for lemma, count in sorted_lemmas[:top_n]]

def generate_wordcloud(text):
    """Generate word cloud with unique meaning words"""
    keywords = extract_unique_keywords(text, 50)
    wordcloud = WordCloud(
        width=1000, 
        height=500,
        background_color='white',
        collocations=False,
        prefer_horizontal=0.8
    ).generate(' '.join(keywords))
    
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    return plt

def generate_frequency_chart(text):
    """Create frequency chart with unique meaning words"""
    keywords = extract_unique_keywords(text, 20)
    freq_dist = defaultdict(int)
    
    words = [token.lemma_.lower() for token in nlp(text) 
             if token.is_alpha and not token.is_stop]
    
    for word in words:
        freq_dist[word] += 1
    
    data = {kw: freq_dist[kw] for kw in keywords if kw in freq_dist}
    df = pd.DataFrame.from_dict(data, orient='index', columns=['Count'])
    return df

def visualizations_page():
    st.subheader("Advanced Text Visualizations")
    text = st.text_area("Enter text for visualization", height=200, 
                       value=st.session_state.get('selected_text', ''))
    
    if text:
        viz_option = st.selectbox("Choose visualization", 
                                ["Enhanced Word Cloud", 
                                 "Keyword Frequency Chart", 
                                 "Text Metrics"])
        
        if viz_option == "Enhanced Word Cloud":
            st.subheader("Word Cloud ")
            plt = generate_wordcloud(text)
            st.pyplot(plt)
            
            with st.expander("Word Cloud Details"):
                unique_words = extract_unique_keywords(text, 50)
                st.write(f"Showing {len(unique_words)} unique meaning words:")
                st.write(", ".join(unique_words))
        
        elif viz_option == "Keyword Frequency Chart":
            st.subheader("Keyword Frequency ")
            df = generate_frequency_chart(text)
            st.bar_chart(df)
            
            with st.expander("Frequency Details"):
                st.dataframe(df.sort_values('Count', ascending=False))
        
        elif viz_option == "Text Metrics":
            st.subheader("Text Statistics ")
            
            # Get unique words count
            unique_lemmas = get_unique_lemmas(text)
            words = word_tokenize(text)
            sentences = sent_tokenize(text)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Characters", len(text))
            with col2:
                st.metric("Words", len(words))
            with col3:
                st.metric("Unique Words", len(unique_lemmas))
            
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg. Word Length", f"{avg_word_length:.1f} chars")
            with col2:
                st.metric("Avg. Sentence Length", f"{avg_sentence_length:.1f} words")
            
            with st.expander("Advanced Metrics"):
                st.write(f"**Vocabulary Richness:** {len(unique_lemmas)/len(words):.2%}")
                st.write(f"**Stopwords Removed:** {len([w for w in words if w.lower() in stop_words])}")