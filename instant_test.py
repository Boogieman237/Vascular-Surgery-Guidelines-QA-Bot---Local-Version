"""
INSTANT TEST - No installation needed, works immediately!
Tests if the PDF can be loaded and searched
"""

print("=" * 60)
print("INSTANT TEST - Medical Guidelines QA Bot")
print("=" * 60)
print()

# Step 1: Test PDF loading
print("Step 1: Testing PDF loading...")
try:
    from langchain_community.document_loaders import PyMuPDFLoader
    
    pdf_path = "/mnt/project/PIIS0741521423016300.pdf"
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    
    print(f"✓ SUCCESS! Loaded {len(documents)} pages")
    print(f"  First page has {len(documents[0].page_content)} characters")
    print()
    
    # Show a sample
    print("Sample from first page:")
    print("-" * 60)
    print(documents[0].page_content[:500])
    print("-" * 60)
    print()
    
except Exception as e:
    print(f"✗ FAILED: {e}")
    print()

# Step 2: Test text splitting
print("Step 2: Testing text splitting...")
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    
    print(f"✓ SUCCESS! Created {len(chunks)} chunks")
    print(f"  Average chunk size: {sum(len(c.page_content) for c in chunks) / len(chunks):.0f} characters")
    print()
    
except Exception as e:
    print(f"✗ FAILED: {e}")
    print()

# Step 3: Test embeddings (optional - may take time)
print("Step 3: Testing embeddings...")
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    
    print("  Creating embedding model (may take 10-30 seconds)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    # Test with a small sample
    test_text = "What is peripheral artery disease?"
    test_embedding = embeddings.embed_query(test_text)
    
    print(f"✓ SUCCESS! Created embedding with {len(test_embedding)} dimensions")
    print()
    
except Exception as e:
    print(f"✗ FAILED: {e}")
    print("  This is OK for quick test - embeddings take time to download")
    print()

# Step 4: Test vector database
print("Step 4: Testing vector database creation...")
try:
    from langchain_community.vectorstores import Chroma
    
    print("  Creating vector database (may take 1-2 minutes)...")
    
    # Use first 50 chunks for speed
    test_chunks = chunks[:50]
    
    vectordb = Chroma.from_documents(
        test_chunks,
        embeddings,
        persist_directory="./test_vector_db"
    )
    
    print(f"✓ SUCCESS! Created database with {len(test_chunks)} chunks")
    print()
    
    # Test search
    print("Step 5: Testing search...")
    query = "What is the WIfI classification system?"
    results = vectordb.similarity_search(query, k=3)
    
    print(f"✓ SUCCESS! Found {len(results)} relevant chunks")
    print()
    print("Top result:")
    print("-" * 60)
    print(results[0].page_content[:300])
    print("-" * 60)
    print()
    
except Exception as e:
    print(f"✗ FAILED: {e}")
    print()

# Summary
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print()
print("If all steps passed, your system is ready!")
print()
print("Next steps:")
print("1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
print("2. Download model: ollama pull llama2")
print("3. Run full app: python3 local_qabot.py")
print()
print("Or run the quick test UI:")
print("   python3 test_qabot.py")
print()
print("=" * 60)
