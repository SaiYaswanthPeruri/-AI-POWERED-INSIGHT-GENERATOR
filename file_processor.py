import streamlit as st
import pdfplumber
from docx import Document
from nltk.tokenize import word_tokenize
from text_processing import extract_quality_keywords as extract_keywords, improved_summarize as summarize_text
import nltk
nltk.download('punkt')

def file_upload_page():
    st.subheader("File Upload and Analysis")
    uploaded_file = st.file_uploader("Choose a file (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        try:
            # Display file information
            st.write(f"**File Name:** {uploaded_file.name}")
            st.write(f"**File Type:** {uploaded_file.type}")
            st.write(f"**File Size:** {uploaded_file.size/1024:.2f} KB")
            
            text = ""
            # Handle PDF files
            if uploaded_file.type == "application/pdf":
                with pdfplumber.open(uploaded_file) as pdf:
                    text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            
            # Handle Word documents
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(uploaded_file)
                text = "\n".join([para.text for para in doc.paragraphs if para.text])
            
            # Handle plain text files
            else:
                text = uploaded_file.getvalue().decode("utf-8")

            if text.strip():
                st.session_state.selected_text = text
                st.success("✅ File processed successfully!")
                st.text_area("Extracted Text", text, height=200)
                
                # Allow user to define summary length
                summary_length = st.number_input(
                    "Summary length (words)", 
                    min_value=1, 
                    max_value=1000, 
                    value=100, 
                    step=1, 
                    help="Specify the maximum number of words for the summary"
                )

                # Analysis buttons in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📝 Quick Summary", help="Generate a brief summary"):
                        with st.spinner("Generating summary..."):
                            # Generate a summary with user-defined word length
                            summary, word_count = summarize_text(text, summary_length)
                            
                            # Ensure the summary is complete and doesn't end abruptly
                            sentences = summary.split('.')
                            if len(sentences) > 1:
                                summary = '. '.join(sentences[:-1]) + '.'  # Complete the last sentence
                            
                            st.write(f"**Summary ({word_count} words):**")
                            st.write(summary)
                
                with col2:
                    if st.button("🔑 Top Keywords", help="Extract important keywords"):
                        with st.spinner("Extracting keywords..."):
                            keywords = extract_keywords(text, 15)
                            st.write("**Keywords:**", ", ".join(keywords))
            else:
                st.warning("⚠️ The file appears to be empty or couldn't be processed.")
                
        except pdfplumber.PDFSyntaxError:
            st.error("❌ Invalid PDF file. Please upload a valid PDF document.")
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")

# For testing the component standalone
if __name__ == "__main__":
    st.title("File Processor Test")
    file_upload_page()
