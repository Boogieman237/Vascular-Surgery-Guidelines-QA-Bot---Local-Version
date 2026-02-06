# Quick Start Guide - Medical Guidelines QA Bot

## 🚀 5-Minute Setup (Local Version)

### Step 1: Install Ollama (2 minutes)

**Option A - macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Option B - Windows:**
1. Go to [https://ollama.ai](https://ollama.ai)
2. Download the installer
3. Run the installer

### Step 2: Download a Model (2 minutes)

```bash
ollama pull llama2
```

Wait for download to complete (~4GB)

### Step 3: Install Python Packages (1 minute)

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install langchain langchain-community chromadb sentence-transformers gradio pymupdf ollama
```

### Step 4: Add Your PDFs

```bash
# Create directory
mkdir medical_pdfs

# Copy your PDF
cp /path/to/guideline.pdf medical_pdfs/
```

### Step 5: Run!

```bash
python3 local_qabot.py
```

Open browser to: **http://localhost:7860**

---

## 📖 First Use

### 1. Initialize the System

1. Click **"Manage Documents"** tab
2. Click **"Initialize System"** button
3. Wait for "✓ System initialized successfully!"

### 2. Ask Your First Question

1. Click **"Ask Questions"** tab
2. Type a question or click an example
3. Click **"Get Answer"**
4. View answer with sources!

### 3. Add More PDFs (Optional)

**Method A - Through interface:**
1. Go to "Manage Documents" tab
2. Upload PDF file
3. Click "Add PDF to Database"

**Method B - Direct copy:**
```bash
cp new_guideline.pdf medical_pdfs/
# Then reinitialize in the interface
```

---

## 💡 Common Questions

### Q: Do I need internet after setup?
**A:** No! Everything runs locally once models are downloaded.

### Q: How much disk space do I need?
**A:** ~5-10GB (4GB for model + PDFs + database)

### Q: Can I use different models?
**A:** Yes! Edit `config.py` and change `OLLAMA_MODEL` to:
- `mistral` (faster)
- `llama3` (newer)
- `mixtral` (more powerful)

### Q: Is my data private?
**A:** Yes! Nothing leaves your computer.

### Q: How do I stop the application?
**A:** Press `Ctrl+C` in the terminal

### Q: Can I change the port?
**A:** Yes, edit `config.py` and change `SERVER_PORT`

---

## 🎯 Usage Tips

### Get Better Answers

1. **Be specific:** "What are the ABI thresholds for PAD diagnosis?" 
   vs "Tell me about ABI"

2. **Use medical terms:** The system understands medical terminology

3. **Ask follow-ups:** Build on previous questions

4. **Increase sources:** Use the slider for complex questions

### Example Workflow

```
1. "What is the WIfI classification?"
   → Get basic explanation

2. "What are the ischaemia grades in WIfI?"
   → Get specific details

3. "What WIfI stage indicates high amputation risk?"
   → Get clinical application
```

---

## 🔧 Customization

### Change Answer Length

Edit `config.py`:
```python
LLM_MAX_TOKENS = 1024  # Longer answers
```

### Use Better Embeddings

Edit `config.py`:
```python
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
```

### Enable GPU (if available)

Edit `config.py`:
```python
EMBEDDING_DEVICE = "cuda"
```

---

## 📱 Using from Other Devices

### Access from Phone/Tablet

1. Find your computer's IP address:
   ```bash
   # Linux/Mac
   ifconfig | grep "inet "
   
   # Windows
   ipconfig
   ```

2. Open browser on phone: `http://YOUR_IP:7860`
   Example: `http://192.168.1.100:7860`

### Share with Team

Edit `config.py`:
```python
ENABLE_SHARE = True
```

This creates a public URL (works for 72 hours).

---

## 🆘 Quick Troubleshooting

### "Ollama not available"
```bash
# Start Ollama
ollama serve

# Try again
python3 local_qabot.py
```

### Slow responses
```bash
# Use faster model
ollama pull mistral

# Edit config.py:
OLLAMA_MODEL = "mistral"
```

### Out of memory
- Close other applications
- Use smaller model: `llama2` instead of `llama3`
- Reduce chunk size in `config.py`

### PDFs not loading
- Check PDFs are in `medical_pdfs/` folder
- Try reinitializing system
- Check console for errors

---

## 📚 Next Steps

1. **Read the full README.md** for advanced features
2. **Check config.py** for all customization options
3. **Try different models** to find best performance
4. **Add all your guidelines** to build a complete database

---

## 🎉 That's It!

You now have a powerful, private, AI-powered medical guidelines assistant running on your own computer!

**Need help?** Check README.md or the troubleshooting section.

**Want to contribute?** Suggestions welcome!
