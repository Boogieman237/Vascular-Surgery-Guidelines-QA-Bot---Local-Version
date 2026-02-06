"""
Improved QA Bot for Vascular Surgery Guidelines
Features:
1. Support for multiple PDFs
2. Pre-loaded documents (no drag-drop required)
3. Local setup capability
4. Persistent vector database
5. Better chunk size for medical documents
"""

from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames
from ibm_watsonx_ai import Credentials
from langchain_ibm import WatsonxLLM, WatsonxEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.chains import RetrievalQA
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

# Directory to store PDFs (you can add your PDFs here)
PDF_DIRECTORY = "./medical_pdfs"
# Directory for vector database (persistent storage)
VECTOR_DB_DIRECTORY = "./vector_db"

# Create directories if they don't exist
os.makedirs(PDF_DIRECTORY, exist_ok=True)
os.makedirs(VECTOR_DB_DIRECTORY, exist_ok=True)

# ============================================================================
# LLM CONFIGURATION
# ============================================================================

def get_llm():
    """Initialize the LLM model"""
    model_id = 'ibm/granite-3-2-8b-instruct'
    parameters = {
        "decoding_method": "sample",
        "max_new_tokens": 512,  # Increased for more detailed answers
        "min_new_tokens": 1,
        "repetition_penalty": 1.0,
        "temperature": 0.3  # Lower for more focused medical answers
    }
    project_id = "skills-network"
    
    watsonx_llm = WatsonxLLM(
        model_id=model_id,
        url="https://us-south.ml.cloud.ibm.com",
        project_id=project_id,
        params=parameters,
    )
    return watsonx_llm

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
            # Add metadata about source file
            for doc in documents:
                doc.metadata['source_file'] = os.path.basename(pdf_file)
            all_documents.extend(documents)
        except Exception as e:
            print(f"Error loading {pdf_file}: {str(e)}")
    
    print(f"Loaded {len(all_documents)} pages from {len(pdf_files)} PDF files")
    return all_documents

def text_splitter(data):
    """Split documents into chunks - optimized for medical documents"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Larger chunks for medical context
        chunk_overlap=200,  # More overlap to preserve context
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]  # Better splitting for medical text
    )
    chunks = text_splitter.split_documents(data)
    return chunks

# ============================================================================
# EMBEDDING AND VECTOR DATABASE
# ============================================================================

def watsonx_embedding():
    """Initialize embedding model"""
    embed_params = {
        EmbedTextParamsMetaNames.TRUNCATE_INPUT_TOKENS: 3,
        EmbedTextParamsMetaNames.RETURN_OPTIONS: {"input_text": True},
    }

    watsonx_embedding_model = WatsonxEmbeddings(
        model_id="ibm/slate-125m-english-rtrvr-v2",
        url="https://us-south.ml.cloud.ibm.com",
        project_id="skills-network",
        params=embed_params,
    )
    
    return watsonx_embedding_model

def create_or_load_vector_database(force_recreate=False):
    """
    Create or load persistent vector database
    Args:
        force_recreate: If True, recreate the database even if it exists
    """
    embedding_model = watsonx_embedding()
    
    # Check if database exists
    if os.path.exists(VECTOR_DB_DIRECTORY) and not force_recreate:
        print("Loading existing vector database...")
        vectordb = Chroma(
            persist_directory=VECTOR_DB_DIRECTORY,
            embedding_function=embedding_model
        )
        print(f"Loaded vector database with {vectordb._collection.count()} documents")
    else:
        print("Creating new vector database...")
        # Load all PDFs from directory
        documents = load_all_pdfs_from_directory(PDF_DIRECTORY)
        
        if not documents:
            raise ValueError(f"No documents found in {PDF_DIRECTORY}. Please add PDF files.")
        
        # Split into chunks
        chunks = text_splitter(documents)
        print(f"Created {len(chunks)} chunks from documents")
        
        # Create vector database
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

# Global variable for vector database
global_vectordb = None

def initialize_system():
    """Initialize the QA system"""
    global global_vectordb
    try:
        global_vectordb = create_or_load_vector_database()
        return "✓ System initialized successfully!"
    except Exception as e:
        return f"✗ Error initializing system: {str(e)}"

def add_new_pdf(pdf_file):
    """Add a new PDF to the system"""
    global global_vectordb
    
    if pdf_file is None:
        return "Please upload a PDF file"
    
    try:
        # Copy file to PDF directory
        filename = os.path.basename(pdf_file.name)
        destination = os.path.join(PDF_DIRECTORY, filename)
        
        # Read and write file
        with open(pdf_file.name, 'rb') as src:
            with open(destination, 'wb') as dst:
                dst.write(src.read())
        
        # Reload vector database
        global_vectordb = create_or_load_vector_database(force_recreate=True)
        
        return f"✓ Successfully added {filename} to the database!"
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
        llm = get_llm()
        retriever = global_vectordb.as_retriever(
            search_kwargs={"k": num_sources}  # Number of relevant chunks to retrieve
        )
        
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        
        response = qa.invoke({"query": query})
        
        # Format response with sources
        answer = response['result']
        sources = response['source_documents']
        
        # Add source information
        if sources:
            answer += "\n\n---\n**Sources:**\n"
            for i, doc in enumerate(sources, 1):
                source_file = doc.metadata.get('source_file', 'Unknown')
                page = doc.metadata.get('page', 'Unknown')
                answer += f"{i}. {source_file} (Page {page})\n"
        
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
        result += f"{i}. {os.path.basename(pdf)}\n"
    
    return result

# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(title="Medical Guidelines QA Bot") as app:
        gr.Markdown(
            """
            # 🏥 Medical Guidelines QA Bot
            ### Vascular Surgery & Diabetic Foot Guidelines Assistant
            
            This system helps you query medical guidelines using AI-powered retrieval.
            """
        )
        
        with gr.Tab("Ask Questions"):
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
                    ask_button = gr.Button("Get Answer", variant="primary")
                
                with gr.Column(scale=3):
                    answer_output = gr.Textbox(
                        label="Answer",
                        lines=15,
                        show_copy_button=True
                    )
            
            ask_button.click(
                fn=answer_question,
                inputs=[query_input, num_sources],
                outputs=answer_output
            )
            
            # Example questions
            gr.Markdown("### Example Questions:")
            example_questions = [
                "What are the diagnostic criteria for peripheral artery disease in diabetic patients?",
                "What is the WIfI classification system and how is it used?",
                "What are the recommendations for revascularization in diabetic foot ulcers?",
                "What bedside tests should be performed for PAD diagnosis?",
                "What are the target HbA1c levels for patients with diabetes and PAD?"
            ]
            
            for question in example_questions:
                gr.Button(question, size="sm").click(
                    lambda q=question: q,
                    outputs=query_input
                )
        
        with gr.Tab("Manage Documents"):
            gr.Markdown("### Add New PDFs or View Current Documents")
            
            with gr.Row():
                with gr.Column():
                    init_button = gr.Button("Initialize System", variant="primary")
                    init_output = gr.Textbox(label="Status", lines=2)
                    
                    gr.Markdown("---")
                    
                    pdf_upload = gr.File(
                        label="Add New PDF",
                        file_types=[".pdf"],
                        type="filepath"
                    )
                    add_button = gr.Button("Add PDF to Database")
                    add_output = gr.Textbox(label="Status", lines=2)
                
                with gr.Column():
                    list_button = gr.Button("List Available PDFs")
                    list_output = gr.Textbox(label="Available Documents", lines=10)
            
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
        
        with gr.Tab("Setup Instructions"):
            gr.Markdown(
                """
                ## 📋 Setup Instructions
                
                ### Using the System
                
                1. **First Time Setup:**
                   - Click "Initialize System" in the "Manage Documents" tab
                   - This will load all PDFs from the `medical_pdfs` directory
                
                2. **Ask Questions:**
                   - Go to "Ask Questions" tab
                   - Type your question or click an example
                   - Adjust the number of sources if needed
                   - Click "Get Answer"
                
                3. **Add More PDFs:**
                   - Go to "Manage Documents" tab
                   - Upload a new PDF file
                   - Click "Add PDF to Database"
                   - The system will automatically rebuild the database
                
                ### Adding PDFs Without the Interface
                
                Simply copy your PDF files to the `medical_pdfs` directory and restart the application.
                
                ### Local Setup (No IBM Cloud Required)
                
                To run this completely locally, you can replace IBM WatsonX with local alternatives:
                
                ```python
                # Option 1: Use Ollama (local LLM)
                from langchain_community.llms import Ollama
                llm = Ollama(model="llama2")
                
                # Option 2: Use HuggingFace models
                from langchain_community.embeddings import HuggingFaceEmbeddings
                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                ```
                
                See the README file for complete local setup instructions.
                """
            )
    
    return app

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False  # Set to True if you want a public link
    )
