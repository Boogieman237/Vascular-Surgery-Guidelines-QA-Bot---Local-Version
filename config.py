"""
Configuration file for Medical Guidelines QA Bot
Edit these settings to customize the application
"""

# ============================================================================
# DIRECTORY SETTINGS
# ============================================================================

# Directory where PDF files are stored
PDF_DIRECTORY = "./medical_pdfs"

# Directory for vector database (persistent storage)
VECTOR_DB_DIRECTORY = "./vector_db_local"

# ============================================================================
# LLM SETTINGS (for local version)
# ============================================================================

# Ollama model to use
# Options: "llama2", "mistral", "llama3", "mixtral", "codellama", etc.
# See available models: ollama list
OLLAMA_MODEL = "llama2"

# LLM parameters
LLM_TEMPERATURE = 0.3  # Lower = more focused, Higher = more creative (0.0 - 1.0)
LLM_MAX_TOKENS = 512   # Maximum length of generated answers

# ============================================================================
# EMBEDDING SETTINGS
# ============================================================================

# HuggingFace embedding model
# Options:
#   - "sentence-transformers/all-MiniLM-L6-v2" (lightweight, fast)
#   - "sentence-transformers/all-mpnet-base-v2" (better quality, slower)
#   - "pritamdeka/S-PubMedBert-MS-MARCO" (medical-specific)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Device for embeddings: "cpu" or "cuda" (if you have GPU)
EMBEDDING_DEVICE = "cpu"

# ============================================================================
# TEXT PROCESSING SETTINGS
# ============================================================================

# Chunk size for splitting documents
# Larger = more context but slower, Smaller = faster but less context
CHUNK_SIZE = 1000

# Overlap between chunks (helps maintain context)
CHUNK_OVERLAP = 200

# Text separators for splitting (in order of preference)
TEXT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

# ============================================================================
# RETRIEVAL SETTINGS
# ============================================================================

# Default number of source documents to retrieve
DEFAULT_NUM_SOURCES = 3

# Maximum number of sources users can select
MAX_NUM_SOURCES = 10

# ============================================================================
# UI SETTINGS
# ============================================================================

# Server settings
SERVER_NAME = "0.0.0.0"  # "0.0.0.0" for all interfaces, "127.0.0.1" for localhost only
SERVER_PORT = 7860

# Enable public sharing (creates a public URL)
ENABLE_SHARE = False

# Gradio theme
# Options: "default", "soft", "monochrome", "glass", etc.
UI_THEME = "soft"

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# Enable verbose logging
VERBOSE = True

# Cache directory for HuggingFace models
HF_CACHE_DIR = "./hf_cache"

# Maximum file size for PDF upload (in MB)
MAX_PDF_SIZE_MB = 100

# ============================================================================
# PROMPT TEMPLATE
# ============================================================================

PROMPT_TEMPLATE = """You are a medical assistant specialized in vascular surgery and diabetic foot guidelines. 
Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Always cite the specific recommendations or guidelines when applicable.
Provide accurate, evidence-based information.

Context: {context}

Question: {question}

Detailed Answer:"""

# ============================================================================
# EXAMPLE QUESTIONS
# ============================================================================

EXAMPLE_QUESTIONS = [
    "What are the diagnostic criteria for peripheral artery disease in diabetic patients?",
    "What is the WIfI classification system and how is it used?",
    "What are the recommendations for revascularization in diabetic foot ulcers?",
    "What bedside tests should be performed for PAD diagnosis?",
    "What are the target HbA1c levels for patients with diabetes and PAD?",
    "What is the role of the ankle-brachial index in diagnosis?",
    "When should urgent vascular consultation be performed?",
    "What are the recommendations for antiplatelet therapy in PAD patients?",
    "What are the signs of ischaemia in diabetic foot ulcers?",
    "How should infection be managed in diabetic foot with PAD?"
]

# ============================================================================
# IBM WATSONX SETTINGS (for improved_qabot.py)
# ============================================================================

# IBM WatsonX API settings
WATSONX_URL = "https://us-south.ml.cloud.ibm.com"
WATSONX_PROJECT_ID = "skills-network"

# LLM Model for WatsonX
WATSONX_MODEL_ID = "ibm/granite-3-2-8b-instruct"

# Embedding Model for WatsonX
WATSONX_EMBEDDING_MODEL = "ibm/slate-125m-english-rtrvr-v2"
