"""
LOCAL QA Bot for Vascular Surgery Guidelines
This version runs completely locally without cloud dependencies
Uses: Ollama for LLM and HuggingFace for embeddings
"""

from langchain_ollama import OllamaLLM # New package
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma # New package
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

# Note: RetrievalQA is being replaced by 'create_retrieval_chain', 
# but updating the imports above will fix your immediate error.

import gradio as gr
import os
import glob
from pathlib import Path

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

PDF_DIRECTORY = "./medical_pdfs"
VECTOR_DB_DIRECTORY = "./vector_db_local"

# Ollama model to use (make sure it's installed)
OLLAMA_MODEL = "llama2"  # or "mistral", "llama3", etc.

# Create directories
os.makedirs(PDF_DIRECTORY, exist_ok=True)
os.makedirs(VECTOR_DB_DIRECTORY, exist_ok=True)

# ============================================================================
# LOCAL LLM CONFIGURATION
# ============================================================================

def get_local_llm():
    """Initialize local LLM using Ollama"""
    try:
        llm = OllamaLLM(
            model=OLLAMA_MODEL,
            temperature=0.5,
            num_predict=512,  # Max tokens to generate
        )
        return llm
    except Exception as e:
        print(f"Error initializing Ollama: {e}")
        print("Make sure Ollama is installed and running: https://ollama.ai")
        raise

# ============================================================================
# LOCAL EMBEDDINGS
# ============================================================================

def get_local_embeddings():
    """Initialize local embeddings using HuggingFace"""
    # Using a lightweight but effective model
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cuda'},  # Use 'cuda' if you have GPU
        encode_kwargs={'normalize_embeddings': True}
    )
    return embeddings

# ============================================================================
# DOCUMENT PROCESSING
# ============================================================================

def load_all_pdfs_from_directory(directory):
    """Load all PDFs from a directory"""
    pdf_files = glob.glob(os.path.join(directory, "*.pdf"))
    
    if not pdf_files:
        print(f"Warning: No PDF files found in {directory}")
        return []
    
    all_documents = []
    for pdf_file in pdf_files:
        try:
            print(f"Loading: {os.path.basename(pdf_file)}")
            loader = PyMuPDFLoader(pdf_file)
            documents = loader.load()
            for doc in documents:
                doc.metadata['source_file'] = os.path.basename(pdf_file)
            all_documents.extend(documents)
        except Exception as e:
            print(f"Error loading {pdf_file}: {str(e)}")
    
    print(f"Loaded {len(all_documents)} pages from {len(pdf_files)} PDF files")
    return all_documents

def text_splitter_func(data):
    """Split documents into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(data)
    return chunks

# ============================================================================
# VECTOR DATABASE
# ============================================================================

global_vectordb = None

def create_or_load_vector_database(force_recreate=True):
    """Create or load persistent vector database"""
    embedding_model = get_local_embeddings()
    
    if os.path.exists(VECTOR_DB_DIRECTORY) and not force_recreate:
        print("Loading existing vector database...")
        vectordb = Chroma(
            persist_directory=VECTOR_DB_DIRECTORY,
            embedding_function=embedding_model
        )
        print(f"Loaded vector database with {vectordb._collection.count()} documents")
    else:
        print("Creating new vector database...")
        documents = load_all_pdfs_from_directory(PDF_DIRECTORY)
        
        if not documents:
            raise ValueError(f"No documents found in {PDF_DIRECTORY}. Please add PDF files.")
        
        chunks = text_splitter_func(documents)
        print(f"Created {len(chunks)} chunks from documents")
        
        vectordb = Chroma.from_documents(
            chunks, 
            embedding_model,
            persist_directory=VECTOR_DB_DIRECTORY
        )
        print("Vector database created and persisted")
    
    return vectordb

# ============================================================================
# QA SYSTEM
# ============================================================================

def initialize_system():
    """Initialize the QA system"""
    global global_vectordb
    
    # Check if already initialized
    if global_vectordb is not None:
        return "✓ System already initialized! Ready to answer questions."
    
    try:
        # Test Ollama connection
        try:
            test_llm = get_local_llm()
            test_response = test_llm.invoke("test")
            print("Ollama connection successful")
        except Exception as e:
            return f"✗ Ollama not available: {str(e)}\nPlease install Ollama from https://ollama.ai and run: ollama pull {OLLAMA_MODEL}"
        
        global_vectordb = create_or_load_vector_database(force_recreate=False)  # CHANGED: False instead of no parameter
        return "✓ System initialized successfully! You can now ask questions."
    except Exception as e:
        return f"✗ Error initializing system: {str(e)}"
        
def add_new_pdf(pdf_file):
    """Add a new PDF to the system"""
    global global_vectordb
    
    if pdf_file is None:
        return "Please upload a PDF file"
    
    try:
        # Get filename
        if hasattr(pdf_file, 'name'):
            filename = os.path.basename(pdf_file.name)
            source_path = pdf_file.name
        else:
            filename = os.path.basename(pdf_file)
            source_path = pdf_file
            
        destination = os.path.join(PDF_DIRECTORY, filename)
        
        # Check if file already exists
        if os.path.exists(destination):
            return f"⚠️  {filename} already exists in database. Please reinitialize system to update."
        
        # Copy file
        import shutil
        shutil.copy2(source_path, destination)
        
        # Force recreate ONLY if a new file was added
        global_vectordb = None  # Reset global
        global_vectordb = create_or_load_vector_database(force_recreate=True)
        
        return f"✓ Successfully added {filename} to the database!\nTotal documents: {global_vectordb._collection.count()}"
    except Exception as e:
        return f"✗ Error adding PDF: {str(e)}"

def answer_question(query, num_sources=3):
    """Answer a question using the RAG system"""
    global global_vectordb
    
    if global_vectordb is None:
        return "Please initialize the system first by clicking 'Initialize System'"
    
    if not query or query.strip() == "":
        return "Please enter a question"
    
    try:
        llm = get_local_llm()
        retriever = global_vectordb.as_retriever(
            search_kwargs={"k": num_sources}
        )
        
        # Custom prompt for medical context
        
        prompt_template = """You are a medical assistant specialized in vascular surgery and diabetic foot guidelines. 
        Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Always cite the specific recommendations or guidelines when applicable.

        Context: {context}

        Question: {question}

        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template, 
            input_variables=["context", "question"]
        )
        
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        response = qa.invoke({"query": query})
        
        answer = response['result']
        sources = response['source_documents']
        
        if sources:
            answer += "\n\n---\n**Sources:**\n"
            for i, doc in enumerate(sources, 1):
                source_file = doc.metadata.get('source_file', 'Unknown')
                page = doc.metadata.get('page', 'Unknown')
                preview = doc.page_content[:150].replace('\n', ' ')
                answer += f"\n{i}. **{source_file}** (Page {page})\n   Preview: {preview}...\n"
        
        return answer
    
    except Exception as e:
        return f"Error: {str(e)}"

def list_available_pdfs():
    """List all PDFs in the database"""
    pdf_files = glob.glob(os.path.join(PDF_DIRECTORY, "*.pdf"))
    if not pdf_files:
        return "No PDFs currently loaded"
    
    result = "**Available PDFs:**\n\n"
    for i, pdf in enumerate(pdf_files, 1):
        file_size = os.path.getsize(pdf) / (1024 * 1024)  # MB
        result += f"{i}. {os.path.basename(pdf)} ({file_size:.2f} MB)\n"
    
    return result

# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(title="Medical Guidelines QA Bot (Local)", theme=gr.themes.Soft()) as app:
        gr.Markdown(
            """
            # 🏥 Medical Guidelines QA Bot (Local Version)
            ### Vascular Surgery & Diabetic Foot Guidelines Assistant
            
            **Running 100% locally** - No cloud dependencies required!
            - LLM: Ollama ({model})
            - Embeddings: HuggingFace (sentence-transformers)
            """.format(model=OLLAMA_MODEL)
        )
        
        with gr.Tab("💬 Ask Questions"):
            gr.Markdown("### Ask questions about the medical guidelines")
            
            with gr.Row():
                with gr.Column(scale=2):
                    query_input = gr.Textbox(
                        label="Your Question",
                        placeholder="e.g., What are the recommendations for diagnosing PAD in diabetic patients?",
                        lines=3
                    )
                    num_sources = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=3,
                        step=1,
                        label="Number of source documents to consider"
                    )
                    ask_button = gr.Button("🔍 Get Answer", variant="primary", size="lg")
                
                with gr.Column(scale=3):
                    answer_output = gr.Textbox(
                        label="Answer",
                        lines=20,
                        show_copy_button=True
                    )
            
            ask_button.click(
                fn=answer_question,
                inputs=[query_input, num_sources],
                outputs=answer_output
            )
            
            gr.Markdown("### 💡 Example Questions:")
            
            with gr.Row():
                examples = [
                    "What are the diagnostic criteria for peripheral artery disease in diabetic patients?",
                    "What is the WIfI classification system and how is it used?",
                    "What are the recommendations for revascularization in diabetic foot ulcers?",
                ]
                
                for question in examples:
                    gr.Button(question, size="sm").click(
                        lambda q=question: q,
                        outputs=query_input
                    )
            
            with gr.Row():
                examples2 = [
                    "What bedside tests should be performed for PAD diagnosis?",
                    "What are the target HbA1c levels for patients with diabetes and PAD?"
                ]
                
                for question in examples2:
                    gr.Button(question, size="sm").click(
                        lambda q=question: q,
                        outputs=query_input
                    )
        
        with gr.Tab("📚 Manage Documents"):
            gr.Markdown("### Add New PDFs or View Current Documents")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### System Initialization")
                    init_button = gr.Button("🚀 Initialize System", variant="primary", size="lg")
                    init_output = gr.Textbox(label="Status", lines=3)
                    
                    gr.Markdown("---")
                    gr.Markdown("#### Add New PDF")
                    
                    pdf_upload = gr.File(
                        label="Upload PDF File",
                        file_types=[".pdf"],
                        type="filepath"
                    )
                    add_button = gr.Button("➕ Add PDF to Database", variant="secondary")
                    add_output = gr.Textbox(label="Status", lines=3)
                
                with gr.Column():
                    gr.Markdown("#### Current Documents")
                    list_button = gr.Button("📋 List Available PDFs")
                    list_output = gr.Textbox(label="Available Documents", lines=15)
            
            init_button.click(
                fn=initialize_system,
                outputs=init_output
            )
            
            add_button.click(
                fn=add_new_pdf,
                inputs=pdf_upload,
                outputs=add_output
            )
            
            list_button.click(
                fn=list_available_pdfs,
                outputs=list_output
            )
        
        with gr.Tab("⚙️ Setup Guide"):
            gr.Markdown(
                """
                ## 📋 Complete Setup Instructions
                
                ### Prerequisites
                
                1. **Install Ollama** (for local LLM)
                   ```bash
                   # macOS/Linux
                   curl -fsSL https://ollama.ai/install.sh | sh
                   
                   # Or download from: https://ollama.ai
                   ```
                
                2. **Pull a model**
                   ```bash
                   ollama pull llama2
                   # or
                   ollama pull mistral
                   # or
                   ollama pull llama3
                   ```
                
                3. **Install Python dependencies**
                   ```bash
                   pip install langchain langchain-community chromadb \
                               sentence-transformers gradio pymupdf ollama
                   ```
                
                ### Using the System
                
                1. **Add Your PDFs**
                   - Place PDF files in the `medical_pdfs` directory
                   - OR use the "Add New PDF" feature in the interface
                
                2. **Initialize**
                   - Click "Initialize System" in the "Manage Documents" tab
                   - Wait for processing to complete
                
                3. **Ask Questions**
                   - Switch to "Ask Questions" tab
                   - Type or select a question
                   - Get AI-powered answers with sources!
                
                ### Alternative Models
                
                You can use different Ollama models by changing `OLLAMA_MODEL` in the code:
                - `llama2` (7B) - Good balance
                - `mistral` (7B) - Fast and accurate
                - `llama3` (8B) - Latest, very good
                - `mixtral` (47B) - Very powerful but slower
                
                ### System Requirements
                
                - **RAM**: 8GB minimum (16GB+ recommended for larger models)
                - **Storage**: ~5GB for model + space for PDFs
                - **CPU**: Any modern processor (GPU optional but faster)
                
                ### Advantages of Local Setup
                
                ✅ **Privacy**: All data stays on your machine  
                ✅ **No costs**: No API fees or subscriptions  
                ✅ **Offline**: Works without internet  
                ✅ **Customizable**: Use any model you want  
                ✅ **Fast**: No network latency  
                
                ### Troubleshooting
                
                **Problem**: "Ollama not available"  
                **Solution**: Make sure Ollama is running (`ollama serve`) and you've pulled a model
                
                **Problem**: Slow responses  
                **Solution**: Use a smaller model (llama2 7B) or enable GPU
                
                **Problem**: Out of memory  
                **Solution**: Close other applications or use a smaller model
                """
            )
    
    return app

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Medical Guidelines QA Bot - Local Version")
    print("="*60)
    print(f"PDF Directory: {PDF_DIRECTORY}")
    print(f"Vector DB Directory: {VECTOR_DB_DIRECTORY}")
    print(f"LLM Model: {OLLAMA_MODEL}")
    print("="*60)
    
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
