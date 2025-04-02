import streamlit as st
from deep_translator import GoogleTranslator
from googletrans import LANGUAGES
import pyperclip
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
import re

# Download NLTK data
nltk.download(['punkt', 'stopwords', 'wordnet'])

# Helper Functions
def clean_text(text):
    """Remove extra spaces and clean text"""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def translate_text(text, dest_language='en'):
    try:
        if not text.strip():
            return ""
        translated = GoogleTranslator(source='auto', target=dest_language).translate(text)
        return clean_text(translated)
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return ""

def summarize_text(text, word_count=50):
    if not text.strip():
        return "", 0
    
    # Text processing
    lemmatizer = WordNetLemmatizer()
    sentences = sent_tokenize(text)
    words = [lemmatizer.lemmatize(w.lower()) for w in word_tokenize(text) 
             if w.isalnum() and w.lower() not in stopwords.words('english')]
    
    # Calculate word frequencies
    freq_table = Counter(words)
    
    # Score sentences
    sentence_scores = {}
    for sentence in sentences:
        sentence_words = [lemmatizer.lemmatize(w.lower()) 
                         for w in word_tokenize(sentence) if w.isalnum()]
        score = sum(freq_table.get(word, 0) for word in sentence_words)
        sentence_scores[sentence] = score / len(sentence_words) if sentence_words else 0
    
    # Sort sentences by score
    sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Build summary with complete sentences
    summary, total_words = [], 0
    for sentence, score in sorted_sentences:
        words_in_sentence = len(word_tokenize(sentence))
        if total_words + words_in_sentence <= word_count:
            summary.append(sentence)
            total_words += words_in_sentence
    
    return clean_text(" ".join(summary)), total_words

def chunk_text(text, max_chunk_size=10000):
    """Chunk text into manageable parts"""
    sentences = sent_tokenize(text)
    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(word_tokenize(chunk + sentence)) > max_chunk_size:
            chunks.append(chunk)
            chunk = sentence
        else:
            chunk += " " + sentence
    if chunk:
        chunks.append(chunk)
    return chunks

def translate_page():
    st.subheader("📝 Text Translation & Summarization")
    
    # Initialize session state
    if 'translation_results' not in st.session_state:
        st.session_state.translation_results = {
            'original': "",
            'translated': "",
            'summary': "",
            'target_lang': "english",
            'input_words': 0,
            'output_words': 0
        }
    
    # Input Section
    with st.form("translation_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            text_input = st.text_area("Enter text to translate and summarize", 
                                    height=300,
                                    placeholder="Type or paste your text here...")
        
        with col2:
            # Language selection
            lang_names = sorted(list(LANGUAGES.values()))
            target_lang = st.selectbox("Target Language", 
                                     lang_names,
                                     index=lang_names.index("english"))
            
            # User-defined number input for summary length
            summary_length = st.number_input("Summary length (words)", 
                                           min_value=1,
                                           max_value=20000,
                                           value=50,
                                           step=1,
                                           help="Enter exact number of words for summary")
        
        submitted = st.form_submit_button("✨ Translate & Summarize")
    
    # Processing
    if submitted and text_input.strip():
        with st.spinner("Processing..."):
            try:
                # Clean input text
                cleaned_text = clean_text(text_input)
                
                # Split the input into manageable chunks
                chunks = chunk_text(cleaned_text, max_chunk_size=10000)
                
                # Initialize results storage
                full_translation = ""
                full_summary = ""
                
                # Process each chunk
                for chunk in chunks:
                    # Translate
                    translated = translate_text(chunk, target_lang)
                    
                    # Summarize translation
                    summary, summary_words = summarize_text(translated, summary_length)
                    
                    # Append results
                    full_translation += translated + "\n\n"
                    full_summary += summary + "\n\n"
                
                # Calculate word counts
                input_word_count = len(word_tokenize(cleaned_text))
                summary_word_count = len(word_tokenize(full_summary))
                
                # Store results
                st.session_state.translation_results = {
                    'original': cleaned_text,
                    'translated': full_translation,
                    'summary': full_summary,
                    'target_lang': target_lang,
                    'input_words': input_word_count,
                    'output_words': summary_word_count
                }
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display Results
    if st.session_state.translation_results['original']:
        st.markdown("---")
        
        # Metrics
        col1, col2 = st.columns(2)
        col1.metric("Original Words", st.session_state.translation_results['input_words'])
        col2.metric("Summary Words", st.session_state.translation_results['output_words'])
        
        # Translated Text
        st.subheader(f"Translated to {st.session_state.translation_results['target_lang'].title()}")
        st.markdown(f'<div style="background-color:#f0f2f6; padding:10px; border-radius:5px;">{st.session_state.translation_results["translated"]}</div>', 
                   unsafe_allow_html=True)
        if st.button("📋 Copy Translation", key="copy_translation"):
            pyperclip.copy(st.session_state.translation_results['translated'])
            st.success("Translation copied to clipboard!")
        
        # Summary
        if st.session_state.translation_results['summary']:
            st.subheader("Summary")
            st.markdown(f'<div style="background-color:#f0f2f6; padding:10px; border-radius:5px;">{st.session_state.translation_results["summary"]}</div>', 
                       unsafe_allow_html=True)
            if st.button("📋 Copy Summary", key="copy_summary"):
                pyperclip.copy(st.session_state.translation_results['summary'])
                st.success("Summary copied to clipboard!")

if __name__ == "__main__":
    st.set_page_config(page_title="Translator", layout="wide")
    translate_page()
