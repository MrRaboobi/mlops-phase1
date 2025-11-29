"""
Document Ingestion Pipeline for RAG Engine
Loads PDFs, splits into chunks, embeds, and stores in ChromaDB.
"""

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

# Configuration
DOCS_DIR = Path("data/docs")
VECTOR_DB_DIR = Path("data/vector_db")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_pdfs(docs_dir: Path):
    """Load all PDF files from the docs directory."""
    pdf_files = list(docs_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {docs_dir}")

    print(f"Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")

    documents = []
    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf_file))
            docs = loader.load()
            # Add metadata about source file
            for doc in docs:
                doc.metadata["source_file"] = pdf_file.name
                doc.metadata["source_path"] = str(pdf_file)
            documents.extend(docs)
            print(f"  ✓ Loaded {len(docs)} pages from {pdf_file.name}")
        except Exception as e:
            print(f"  ✗ Error loading {pdf_file.name}: {e}")

    return documents


def split_documents(documents, chunk_size=500, chunk_overlap=50):
    """Split documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = text_splitter.split_documents(documents)
    print(f"\nSplit {len(documents)} documents into {len(chunks)} chunks")
    return chunks


def create_vector_store(chunks, vector_db_dir: Path, embedding_model: str):
    """Create and persist vector store using ChromaDB."""
    print(f"\nInitializing embeddings with model: {embedding_model}")
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={"device": "cpu"},  # Use CPU for compatibility
        encode_kwargs={"normalize_embeddings": True},
    )

    print(f"Creating vector store in {vector_db_dir}...")
    # Remove existing vector store if it exists
    if vector_db_dir.exists():
        import shutil

        shutil.rmtree(vector_db_dir)
        print("  Removed existing vector store")

    vector_db_dir.mkdir(parents=True, exist_ok=True)

    # Create ChromaDB vector store
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(vector_db_dir),
    )

    # ChromaDB auto-persists, no need to call persist() explicitly
    print(f"  ✓ Vector store created and persisted to {vector_db_dir}")

    return vectorstore


def main():
    """Main ingestion pipeline."""
    print("=" * 60)
    print("RAG Document Ingestion Pipeline")
    print("=" * 60)

    # Step 1: Load PDFs
    print("\n[Step 1] Loading PDFs...")
    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"Docs directory not found: {DOCS_DIR}")

    documents = load_pdfs(DOCS_DIR)
    print(f"  ✓ Loaded {len(documents)} total pages")

    # Step 2: Split into chunks
    print("\n[Step 2] Splitting documents into chunks...")
    chunks = split_documents(documents, CHUNK_SIZE, CHUNK_OVERLAP)

    # Step 3: Create vector store
    print("\n[Step 3] Creating vector store...")
    vectorstore = create_vector_store(chunks, VECTOR_DB_DIR, EMBEDDING_MODEL)

    # Step 4: Verify
    print("\n[Step 4] Verifying vector store...")
    sample_query = "myocardial infarction"
    results = vectorstore.similarity_search(sample_query, k=2)
    print(f"  ✓ Test query '{sample_query}' returned {len(results)} results")
    if results:
        print(f"  Sample result: {results[0].page_content[:100]}...")

    print("\n" + "=" * 60)
    print("✅ Ingestion complete!")
    print(f"Vector database saved to: {VECTOR_DB_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
