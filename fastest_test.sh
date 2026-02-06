#!/bin/bash

# FASTEST TEST SCRIPT - Medical Guidelines QA Bot
# This script sets up and tests the system in the fastest way possible

echo "=========================================="
echo "FASTEST TEST - Medical Guidelines QA Bot"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "local_qabot.py" ]; then
    echo "❌ Error: local_qabot.py not found"
    echo "Please run this script from the project directory"
    exit 1
fi

# Step 1: Create directories
echo "📁 Step 1/5: Creating directories..."
mkdir -p medical_pdfs
mkdir -p vector_db_local
echo "✓ Done"

# Step 2: Copy the vascular surgery PDF
echo ""
echo "📄 Step 2/5: Setting up PDF..."
if [ -f "/mnt/project/PIIS0741521423016300.pdf" ]; then
    cp /mnt/project/PIIS0741521423016300.pdf medical_pdfs/
    echo "✓ Copied vascular surgery guideline PDF"
else
    echo "⚠️  PDF not found at /mnt/project/PIIS0741521423016300.pdf"
    echo "   Please copy your PDF manually to medical_pdfs/"
fi

# Step 3: Install minimal dependencies
echo ""
echo "📦 Step 3/5: Installing Python packages (this may take a minute)..."
pip install -q langchain langchain-community chromadb sentence-transformers gradio pymupdf ollama

if [ $? -eq 0 ]; then
    echo "✓ Packages installed"
else
    echo "❌ Failed to install packages"
    exit 1
fi

# Step 4: Check Ollama
echo ""
echo "🤖 Step 4/5: Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama found"
    
    # Check if llama2 is available
    if ollama list | grep -q llama2; then
        echo "✓ llama2 model ready"
    else
        echo "⚠️  llama2 not found. Downloading (this takes a few minutes)..."
        ollama pull llama2
    fi
else
    echo "❌ Ollama not installed!"
    echo ""
    echo "Quick install:"
    echo "  curl -fsSL https://ollama.ai/install.sh | sh"
    echo "  ollama pull llama2"
    echo ""
    echo "For now, testing with a simplified version..."
    # We'll create a test version that doesn't need Ollama
fi

# Step 5: Create a quick test version
echo ""
echo "🧪 Step 5/5: Creating quick test version..."

cat > test_qabot.py << 'TESTEOF'
"""Quick test version - uses simple retrieval without LLM for fastest testing"""
import gradio as gr
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import glob

PDF_DIRECTORY = "./medical_pdfs"
VECTOR_DB_DIRECTORY = "./vector_db_test"

global_vectordb = None

def load_pdfs():
    """Load all PDFs"""
    pdf_files = glob.glob(os.path.join(PDF_DIRECTORY, "*.pdf"))
    if not pdf_files:
        return []
    
    all_docs = []
    for pdf in pdf_files:
        loader = PyMuPDFLoader(pdf)
        docs = loader.load()
        for doc in docs:
            doc.metadata['source_file'] = os.path.basename(pdf)
        all_docs.extend(docs)
    return all_docs

def initialize_system():
    """Initialize the test system"""
    global global_vectordb
    try:
        print("Loading PDFs...")
        documents = load_pdfs()
        
        if not documents:
            return "❌ No PDFs found in medical_pdfs/ directory"
        
        print(f"Loaded {len(documents)} pages")
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks")
        
        # Create embeddings
        print("Creating embeddings (this may take a minute)...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Create vector database
        global_vectordb = Chroma.from_documents(
            chunks,
            embeddings,
            persist_directory=VECTOR_DB_DIRECTORY
        )
        
        return f"✓ System initialized! Loaded {len(pdf_files)} PDFs with {len(chunks)} chunks"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def search_documents(query, num_results=3):
    """Search documents and return relevant chunks"""
    global global_vectordb
    
    if global_vectordb is None:
        return "Please initialize the system first!"
    
    if not query.strip():
        return "Please enter a question"
    
    try:
        # Search for relevant documents
        results = global_vectordb.similarity_search(query, k=num_results)
        
        if not results:
            return "No relevant information found."
        
        # Format response
        response = f"**Found {len(results)} relevant sections:**\n\n"
        
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get('source_file', 'Unknown')
            page = doc.metadata.get('page', 'Unknown')
            content = doc.page_content[:500].replace('\n', ' ')
            
            response += f"**{i}. {source} (Page {page})**\n"
            response += f"{content}...\n\n"
            response += "---\n\n"
        
        response += "\n**Note:** This is a simplified test version showing raw document chunks. "
        response += "For AI-generated answers, use the full version with Ollama."
        
        return response
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="QA Bot - Quick Test") as app:
    gr.Markdown(
        """
        # 🧪 Medical Guidelines QA Bot - QUICK TEST VERSION
        
        This simplified version shows document retrieval without AI generation.
        It's perfect for testing that everything works!
        """
    )
    
    with gr.Tab("Initialize"):
        gr.Markdown("### Step 1: Initialize the System")
        init_button = gr.Button("🚀 Initialize System", variant="primary", size="lg")
        init_output = gr.Textbox(label="Status", lines=3)
        
        init_button.click(
            fn=initialize_system,
            outputs=init_output
        )
    
    with gr.Tab("Search"):
        gr.Markdown("### Step 2: Search the Documents")
        
        query_input = gr.Textbox(
            label="Your Question",
            placeholder="e.g., What are the diagnostic criteria for PAD?",
            lines=2
        )
        
        num_results = gr.Slider(
            minimum=1,
            maximum=5,
            value=3,
            step=1,
            label="Number of results"
        )
        
        search_button = gr.Button("🔍 Search", variant="primary")
        search_output = gr.Textbox(label="Results", lines=20)
        
        search_button.click(
            fn=search_documents,
            inputs=[query_input, num_results],
            outputs=search_output
        )
        
        # Example questions
        gr.Markdown("### Example Questions:")
        examples = [
            "What is the WIfI classification system?",
            "What are the diagnostic criteria for PAD?",
            "When should revascularization be considered?",
        ]
        
        for question in examples:
            gr.Button(question, size="sm").click(
                lambda q=question: q,
                outputs=query_input
            )
    
    gr.Markdown(
        """
        ---
        **Next Step:** Once this works, run `python3 local_qabot.py` for full AI-powered answers!
        """
    )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
TESTEOF

echo "✓ Test version created"

echo ""
echo "=========================================="
echo "✅ SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "🚀 FASTEST TEST (no AI, just document retrieval):"
echo "   python3 test_qabot.py"
echo ""
echo "   1. Open http://localhost:7860"
echo "   2. Click 'Initialize' tab"
echo "   3. Click 'Initialize System' button"
echo "   4. Click 'Search' tab"
echo "   5. Try an example question!"
echo ""
echo "📊 This shows the documents are loading correctly."
echo "    You'll see raw text chunks from the PDF."
echo ""
echo "=========================================="
echo "💪 FULL VERSION (with AI answers):"
echo "=========================================="
echo ""
echo "If Ollama is installed:"
echo "   python3 local_qabot.py"
echo ""
echo "If not, install Ollama first:"
echo "   curl -fsSL https://ollama.ai/install.sh | sh"
echo "   ollama pull llama2"
echo "   python3 local_qabot.py"
echo ""
echo "=========================================="
echo "Ready to test!"
echo "=========================================="
