#!/bin/bash

# Medical Guidelines QA Bot - Setup Script
# This script automates the setup process

echo "=================================================="
echo "Medical Guidelines QA Bot - Setup Script"
echo "=================================================="
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
echo "🔍 Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Found: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_VERSION=$(python --version)
    echo "✓ Found: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "✗ Python not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check pip
echo ""
echo "🔍 Checking pip installation..."
if command_exists pip3; then
    PIP_CMD="pip3"
    echo "✓ pip3 found"
elif command_exists pip; then
    PIP_CMD="pip"
    echo "✓ pip found"
else
    echo "✗ pip not found. Please install pip."
    exit 1
fi

# Create directories
echo ""
echo "📁 Creating directories..."
mkdir -p medical_pdfs
mkdir -p vector_db_local
echo "✓ Directories created: medical_pdfs/, vector_db_local/"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
echo "This may take a few minutes..."
$PIP_CMD install langchain langchain-community chromadb sentence-transformers gradio pymupdf ollama

if [ $? -eq 0 ]; then
    echo "✓ Python dependencies installed successfully"
else
    echo "✗ Failed to install Python dependencies"
    exit 1
fi

# Check for Ollama
echo ""
echo "🔍 Checking Ollama installation..."
if command_exists ollama; then
    OLLAMA_VERSION=$(ollama --version 2>&1 | head -n 1)
    echo "✓ Ollama found: $OLLAMA_VERSION"
    
    # Ask if user wants to pull a model
    echo ""
    echo "Would you like to download a language model? (recommended)"
    echo "Options:"
    echo "  1) llama2 (7B) - Good balance, 4GB"
    echo "  2) mistral (7B) - Fast and accurate, 4GB"
    echo "  3) llama3 (8B) - Latest, very good, 5GB"
    echo "  4) Skip (I'll do it manually)"
    read -p "Enter your choice (1-4): " model_choice
    
    case $model_choice in
        1)
            echo "Downloading llama2..."
            ollama pull llama2
            ;;
        2)
            echo "Downloading mistral..."
            ollama pull mistral
            ;;
        3)
            echo "Downloading llama3..."
            ollama pull llama3
            ;;
        4)
            echo "Skipping model download. Remember to pull a model with:"
            echo "  ollama pull llama2"
            ;;
        *)
            echo "Invalid choice. Skipping model download."
            ;;
    esac
else
    echo "⚠️  Ollama not found. Please install it from https://ollama.ai"
    echo ""
    echo "Installation instructions:"
    echo "  macOS/Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "  Windows: Download from https://ollama.ai"
    echo ""
    echo "After installing Ollama, run:"
    echo "  ollama pull llama2"
fi

# Copy the guideline PDF if it exists
echo ""
echo "📄 Looking for PDF files to add..."
if [ -f "PIIS0741521423016300.pdf" ]; then
    cp PIIS0741521423016300.pdf medical_pdfs/
    echo "✓ Copied PIIS0741521423016300.pdf to medical_pdfs/"
else
    echo "ℹ️  No PDF file found. You can add PDFs manually to the medical_pdfs/ directory"
fi

# Create a simple launcher script
echo ""
echo "📝 Creating launcher script..."
cat > run_qabot.sh << 'EOF'
#!/bin/bash
# Launch the Medical Guidelines QA Bot

echo "Starting Medical Guidelines QA Bot..."
echo ""
echo "The application will be available at: http://localhost:7860"
echo "Press Ctrl+C to stop"
echo ""

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve > /dev/null 2>&1 &
    sleep 2
fi

# Run the application
python3 local_qabot.py
EOF

chmod +x run_qabot.sh
echo "✓ Created run_qabot.sh launcher"

# Create a Windows launcher
cat > run_qabot.bat << 'EOF'
@echo off
echo Starting Medical Guidelines QA Bot...
echo.
echo The application will be available at: http://localhost:7860
echo Press Ctrl+C to stop
echo.

python local_qabot.py
pause
EOF
echo "✓ Created run_qabot.bat launcher (Windows)"

# Final instructions
echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Add your PDF files to the medical_pdfs/ directory"
echo "   Example: cp /path/to/your/guideline.pdf medical_pdfs/"
echo ""
echo "2. Make sure Ollama is running:"
echo "   ollama serve"
echo ""
echo "3. Run the application:"
echo "   • Linux/Mac: ./run_qabot.sh"
echo "   • Or: python3 local_qabot.py"
echo "   • Windows: run_qabot.bat"
echo ""
echo "4. Open your browser to: http://localhost:7860"
echo ""
echo "5. Click 'Initialize System' in the Manage Documents tab"
echo ""
echo "6. Start asking questions!"
echo ""
echo "=================================================="
echo "For help, see README.md"
echo "=================================================="
