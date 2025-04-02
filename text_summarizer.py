import nltk

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('vader_lexicon')

# Rest of your imports...
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
# ... rest of your file
import streamlit as st
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pyperclip
from collections import Counter
from fpdf import FPDF
from docx import Document
import io

# Initialize NLTK resources
nltk.download(['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger'])


def create_pdf(summary_text):
    """Create PDF with proper encoding and space handling"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Clean the text: remove extra spaces and replace problematic Unicode characters
    cleaned_text = ' '.join(summary_text.split())
    replacements = {
        '\u2018': "'", '\u2019': "'",  # Smart quotes
        '\u201c': '"', '\u201d': '"',  # Smart double quotes
        '\u2013': '-', '\u2014': '--', # Dashes
        '\u2026': '...',               # Ellipsis
    }
    for k, v in replacements.items():
        cleaned_text = cleaned_text.replace(k, v)
    
    pdf.multi_cell(0, 10, txt=cleaned_text)
    
    # Encode to Latin-1 with error handling
    try:
        return pdf.output(dest='S').encode('latin-1')
    except UnicodeEncodeError:
        # Fallback: replace any remaining problematic characters
        return pdf.output(dest='S').encode('latin-1', errors='replace')

def create_word(summary_text):
    """Create Word document with cleaned text"""
    doc = Document()
    
    # Clean the text: remove extra spaces
    cleaned_text = ' '.join(summary_text.split())
    doc.add_paragraph(cleaned_text)
    
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

def extract_powerful_keywords(text, top_n=15):
    try:
        stop_words = set(stopwords.words("english"))
        words = word_tokenize(text.lower())
        
        filtered_words = [
            word for word in words 
            if word.isalnum() and word not in stop_words and len(word) > 2
        ]
        
        try:
            tagged_words = nltk.pos_tag(filtered_words)
            nouns = [word for word, pos in tagged_words if pos.startswith('NN')]
            adjectives = [word for word, pos in tagged_words if pos.startswith('JJ')]
            meaningful_words = nouns + adjectives
        except:
            meaningful_words = filtered_words
        
        freq_dist = Counter(meaningful_words)
        return [word for word, _ in freq_dist.most_common(top_n)]
    
    except Exception as e:
        st.error(f"Keyword extraction error: {str(e)}")
        return []

def summarize_text(text, word_count=50):
    if not text:
        return "Text is empty. Please provide text to summarize.", 0
    
    sentences = sent_tokenize(text)
    if len(sentences) == 0:
        return "The text is too short for summarization.", 0
    
    lemmatizer = WordNetLemmatizer()
    words = word_tokenize(text)
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    text = " ".join(lemmatized_words)
    
    custom_stopwords = set(stopwords.words("english")).union({
        "initially", "essentially", "basically", "usually", "often", 
        "sometimes", "also", "may", "might", "could", "would", "said"
    })
    
    words = word_tokenize(text)
    filtered_words = [
        word for word in words 
        if word.lower() not in custom_stopwords 
        and not word.isdigit() 
        and len(word) > 2
    ]
    text = " ".join(filtered_words)
    
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text.lower())
    freq_table = {
        word: words.count(word) 
        for word in words 
        if word.isalnum() and word not in stop_words
    }
    
    sentence_scores = {
        sentence: sum(freq_table.get(word.lower(), 0) 
                     for word in word_tokenize(sentence.lower())) 
        for sentence in sentences
    }
    
    sorted_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    
    summary, total_words = [], 0
    
    for sentence in sorted_sentences:
        words_in_sentence = len(word_tokenize(sentence))
        if total_words + words_in_sentence <= word_count:
            summary.append(sentence)
            total_words += words_in_sentence
    
    return " ".join(summary), total_words

def summarize_page():
    st.subheader("Advanced Text Summarization")
    
    # Initialize session state variables
    if 'generated_summary' not in st.session_state:
        st.session_state.generated_summary = None
    if 'extracted_keywords' not in st.session_state:
        st.session_state.extracted_keywords = None
    if 'input_text' not in st.session_state:
        st.session_state.input_text = st.session_state.get("selected_text", "")
    
    # Text input with submit button
    with st.form("text_input_form"):
        text = st.text_area("Enter your text here", 
                          height=200, 
                          value=st.session_state.input_text,
                          key="text_input")
        submitted = st.form_submit_button("Submit Text")
    
    if submitted:
        st.session_state.input_text = text
        st.session_state.generated_summary = None
        st.session_state.extracted_keywords = None
        st.rerun()
    
    if st.session_state.input_text:
        input_word_count = len(word_tokenize(st.session_state.input_text))
        st.write(f"Input Word Count: {input_word_count}")
        
        tab1, tab2 = st.tabs(["Keywords Extraction", "Text Summarization"])
        
        with tab1:
            st.markdown("### Keywords")
            
            if st.button("Extract Keywords", key="extract_keywords"):
                keywords = extract_powerful_keywords(st.session_state.input_text)
                if keywords:
                    st.session_state.extracted_keywords = ", ".join(keywords)
            
            if st.session_state.extracted_keywords:
                st.markdown("**Extracted Keywords:**")
                st.write(st.session_state.extracted_keywords)
                
                if st.button("📋 Copy Keywords", key="copy_keywords"):
                    pyperclip.copy(st.session_state.extracted_keywords)
                    st.success("Keywords copied to clipboard!")
        
        with tab2:
            st.markdown("### Summary Generator")
            summary_length = st.number_input(
                "Enter summary length (words)",
                min_value=10,
                max_value=input_word_count,
                value=min(50, input_word_count),
                step=1,
                key="summary_length"
            )
            
            if st.button("Generate Summary", key="generate_summary"):
                with st.spinner("Creating concise summary..."):
                    summary, summary_word_count = summarize_text(st.session_state.input_text, summary_length)
                    st.session_state.generated_summary = summary
                    st.session_state.summary_word_count = summary_word_count
            
            if st.session_state.generated_summary:
                st.markdown("**Generated Summary:**")
                st.write(st.session_state.generated_summary)
                st.write(f"Summary contains {st.session_state.summary_word_count} words (Requested: {summary_length})")
                
                if st.button("📋 Copy Summary", key="copy_summary"):
                    pyperclip.copy(st.session_state.generated_summary)
                    st.success("Summary copied to clipboard!")
                
                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download as PDF",
                        data=create_pdf(st.session_state.generated_summary),
                        file_name="summary.pdf",
                        mime="application/pdf"
                    )
                with col2:
                    st.download_button(
                        label="Download as Word",
                        data=create_word(st.session_state.generated_summary),
                        file_name="summary.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

