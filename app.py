import streamlit as st
from auth import login_page, register_page
from text_summarizer import summarize_page
from translator import translate_page
from file_processor import file_upload_page
from sentiment_analyzer import sentiment_page
from similarity_checker import similarity_page
from visualizations import visualizations_page
from text_to_speech import tts_page


def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'selected_text' not in st.session_state:
        st.session_state.selected_text = ""

def main():
    init_session_state()
    st.set_page_config(page_title="AI-POWERED INSIGHT GENERATOR", layout="wide")

    if not st.session_state.logged_in:
        st.title("AI-POWERED INSIGHT GENERATOR")
        option = st.radio("Choose an option", ["Login", "Register"])
        if option == "Login":
            login_page()
        elif option == "Register":
            register_page()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}")
        options = {
            "Summarize Text": summarize_page,
            "Translate Text": translate_page,
            "Upload File": file_upload_page,
            "Sentiment Analysis": sentiment_page,
            "Text Similarity": similarity_page,
            "Visualizations": visualizations_page,
            "Text-to-Speech": tts_page
        }
        selected = st.sidebar.radio("Navigation", list(options.keys()))
        options[selected]()

        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
            
if __name__ == "__main__":
    main()