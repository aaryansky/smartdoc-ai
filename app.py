import streamlit as st
import os
import fitz # PyMuPDF
from src.ocr_engine import OCREngine
from src.llm_engine import LLMEngine

# 1. Setup Page
st.set_page_config(page_title="SmartDoc AI", layout="wide")
st.title("📄 SmartDoc: Intelligent Document Assistant")
st.markdown("---")

# 2. Initialize Engines
@st.cache_resource
def load_engines():
    return OCREngine(), LLMEngine()

ocr, llm = load_engines()

# 3. Sidebar
with st.sidebar:
    st.header("Settings")
    st.info("💡 Supports Images (JPG/PNG) and PDF Resumes!")
    ocr_mode = st.radio("OCR Mode", ["EasyOCR (Text/PDF)", "ChandraOCR (Layouts)"])

# 4. Main Interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Upload Document")
    # UPDATED: Added 'pdf' to accepted types
    uploaded_file = st.file_uploader("Upload Document", type=['png', 'jpg', 'jpeg', 'pdf'])

    if uploaded_file:
        os.makedirs("data/uploads", exist_ok=True)
        save_path = os.path.join("data/uploads", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # PREVIEW LOGIC
        file_ext = os.path.splitext(save_path)[1].lower()
        
        if file_ext == '.pdf':
            # Generate a preview of the first page for PDFs
            with fitz.open(save_path) as doc:
                page = doc.load_page(0)
                pix = page.get_pixmap()
                st.image(pix.tobytes("png"), caption="PDF Preview (Page 1)", use_column_width=True)
        else:
            # Standard image preview
            st.image(save_path, caption="Image Preview", use_container_width=True)

        # Extraction Trigger
        if st.button("🔍 Extract Text"):
            with st.spinner(f"Processing with {ocr_mode}..."):
                if "EasyOCR" in ocr_mode:
                    extracted_text = ocr.extract_with_paddle(save_path)
                else:
                    extracted_text = ocr.extract_with_chandra(save_path)
                
                st.session_state['context'] = extracted_text
                st.success("Extraction Complete!")

with col2:
    st.subheader("2. Chat with Document")
    
    if 'context' in st.session_state:
        with st.expander("View Extracted Data"):
            st.text_area("Raw Output", st.session_state['context'], height=200)
        
        user_question = st.text_input("Ask a question about the document:")
        
        if user_question:
            with st.spinner("Nemotron is reasoning..."):
                answer = llm.ask_nemotron(st.session_state['context'], user_question)
                st.markdown("### 🤖 Answer")
                st.write(answer)
    else:
        st.info("Upload a document to start.")
        
if st.sidebar.button("🗑️ Reset App"):
    st.session_state.clear()
    st.rerun()
