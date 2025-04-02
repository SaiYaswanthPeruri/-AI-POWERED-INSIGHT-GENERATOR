import streamlit as st
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
import nltk

nltk.download('vader_lexicon')

def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    sentences = sent_tokenize(text)
    
    results = {
        'positive': [],
        'negative': [],
        'neutral': [],
        'scores': {'compound': 0, 'pos': 0, 'neg': 0, 'neu': 0}
    }
    
    for sentence in sentences:
        scores = sia.polarity_scores(sentence)
        results['scores']['compound'] += scores['compound']
        results['scores']['pos'] += scores['pos']
        results['scores']['neg'] += scores['neg']
        results['scores']['neu'] += scores['neu']
        
        if scores['compound'] >= 0.05:
            results['positive'].append(sentence)
        elif scores['compound'] <= -0.05:
            results['negative'].append(sentence)
        else:
            results['neutral'].append(sentence)
    
    num_sentences = len(sentences)
    for key in results['scores']:
        results['scores'][key] = round(results['scores'][key] / num_sentences, 2) if num_sentences > 0 else 0
    
    return results

def sentiment_page():
    st.subheader("Advanced Sentiment Analysis")
    text = st.text_area("Enter text for sentiment analysis", height=200, 
                       value=st.session_state.get('selected_text', ''))
    
    if text and st.button("Analyze Sentiment"):
        with st.spinner("Analyzing sentiment..."):
            results = analyze_sentiment(text)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Overall Sentiment", 
                         "Positive" if results['scores']['compound'] >= 0.05 else 
                         "Negative" if results['scores']['compound'] <= -0.05 else 
                         "Neutral")
            with col2:
                st.metric("Positive Score", f"{results['scores']['pos']:.2f}")
            with col3:
                st.metric("Negative Score", f"{results['scores']['neg']:.2f}")
            
            tab1, tab2, tab3 = st.tabs(["Positive", "Negative", "Neutral"])
            with tab1:
                st.write(f"**{len(results['positive'])} Positive Sentences:**")
                for sent in results['positive']:
                    st.write(f"- {sent}")
            with tab2:
                st.write(f"**{len(results['negative'])} Negative Sentences:**")
                for sent in results['negative']:
                    st.write(f"- {sent}")
            with tab3:
                st.write(f"**{len(results['neutral'])} Neutral Sentences:**")
                for sent in results['neutral']:
                    st.write(f"- {sent}")