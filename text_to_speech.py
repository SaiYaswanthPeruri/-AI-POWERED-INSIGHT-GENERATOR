import streamlit as st
from gtts import gTTS
import tempfile
import os
from deep_translator import GoogleTranslator
from googletrans import Translator
from text_processing import improved_summarize as summarize_text

def tts_page():
    st.subheader("Text-to-Speech Conversion")
    
    # Initialize session state
    if 'summary_result' not in st.session_state:
        st.session_state.summary_result = None
    
    tab1, tab2 = st.tabs(["Direct Conversion", "Summarize & Convert"])
    
    with tab1:
        st.write("Convert full text to speech")
        text = st.text_area("Enter text to convert", 
                          height=150, 
                          value=st.session_state.get('selected_text', ''),
                          key="direct_text")
        
        col1, col2 = st.columns(2)
        with col1:
            target_lang = st.selectbox("Select Language", [
                ('English', 'en'),
                ('Spanish', 'es'),
                ('French', 'fr'),
                ('German', 'de'),
                ('Hindi', 'hi'),
                ('Telugu', 'te')
            ], format_func=lambda x: x[0], key="direct_lang")
        
        if st.button("Generate Audio", key="direct_btn"):
            if text:
                with st.spinner("Creating audio..."):
                    # Translate to selected language if needed
                    translator = Translator()
                    detected = translator.detect(text)
                    
                    if detected.lang != target_lang[1]:
                        text = GoogleTranslator(
                            source='auto', 
                            target=target_lang[1]
                        ).translate(text)
                    
                    generate_audio(text, target_lang[1])
            else:
                st.warning("Please enter some text")

    with tab2:
        st.write("Summarize text before conversion")
        text = st.text_area("Enter text to summarize", 
                          height=150, 
                          value=st.session_state.get('selected_text', ''),
                          key="summary_input_text")
        
        col1, col2 = st.columns(2)
        with col1:
            target_lang = st.selectbox("Select Language", [
                ('English', 'en'),
                ('Spanish', 'es'),
                ('French', 'fr'),
                ('German', 'de'),
                ('Hindi', 'hi'),
                ('Telugu', 'te')
            ], format_func=lambda x: x[0], index=0, key="summary_lang")
        
        with col2:
            summary_length = st.number_input(
                "Summary length (words)",
                min_value=10,
                max_value=500,
                value=50,
                step=5,
                help="Number of words for the summary",
                key="summary_length_input"
            )
        
        if st.button("Summarize Text", key="summary_btn"):
            if text:
                with st.spinner("Generating summary..."):
                    # Generate summary and translate to target language immediately
                    summary, _ = summarize_text(text, summary_length)
                    translator = Translator()
                    detected = translator.detect(summary)
                    
                    if detected.lang != target_lang[1]:
                        summary = GoogleTranslator(
                            source='auto', 
                            target=target_lang[1]
                        ).translate(summary)
                    
                    st.session_state.summary_result = summary
            else:
                st.warning("Please enter some text")
        
        if st.session_state.summary_result:
            st.text_area("Summary preview in selected language", 
                       st.session_state.summary_result, 
                       height=150,
                       key="summary_preview")
            
            if st.button("Generate Audio", 
                        key="summary_audio_btn"):
                with st.spinner("Creating audio..."):
                    generate_audio(st.session_state.summary_result, 
                                 target_lang[1])

def generate_audio(text, lang_code):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(fp.name)
            
            audio_bytes = open(fp.name, 'rb').read()
            st.audio(audio_bytes, format='audio/mp3')
            
            st.download_button(
                label="Download Audio",
                data=audio_bytes,
                file_name=f"speech_{lang_code}.mp3",
                mime="audio/mp3",
                key=f"download_{lang_code}"
            )
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
    finally:
        if 'fp' in locals() and fp.name:
            try:
                os.unlink(fp.name)
            except:
                pass