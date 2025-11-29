"""
RAG Engine for ECG Explanation Generation
Retrieves relevant medical context and generates patient-friendly explanations.
"""

import os
import warnings
from pathlib import Path
from typing import Optional
from langchain_huggingface import HuggingFaceEmbeddings

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load .env file - try multiple locations
env_paths = [".env", Path(__file__).parent.parent / ".env"]
for env_path in env_paths:
    if Path(env_path).exists():
        load_dotenv(env_path, override=True)
        break
else:
    load_dotenv()  # Fallback to default location

# Configuration
VECTOR_DB_DIR = Path("data/vector_db")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# Using tiiuae/falcon-7b-instruct - confirmed to work with text-generation task
# Falcon models are specifically designed for instruction following and text generation
LLM_MODEL = "tiiuae/falcon-7b-instruct"  # Reliable text-generation model


# Get token - will be reloaded in __init__ to ensure it's fresh
def get_huggingface_token():
    """Get HuggingFace token, reloading .env if needed."""
    # Reload .env to ensure we have the latest
    for env_path in env_paths:
        if Path(env_path).exists():
            load_dotenv(env_path, override=True)
            break
    else:
        load_dotenv(override=True)

    token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    # Also try alternative names
    if not token:
        token = os.getenv("HF_API_TOKEN")
    if not token:
        token = os.getenv("HUGGINGFACE_API_TOKEN")

    # Debug output (without exposing full token)
    if token:
        print(f"   ✅ Token loaded successfully (length: {len(token)})")
    else:
        print(f"   ❌ Token not found. Checked paths: {[str(p) for p in env_paths]}")

    return token


# Map model predictions to search terms for better retrieval
DIAGNOSIS_SEARCH_MAP = {
    "NORM": ["normal sinus rhythm", "normal ECG", "healthy heart"],
    "MI": ["myocardial infarction", "heart attack", "MI", "coronary"],
    "STTC": ["ST-T changes", "ischemia", "ST segment", "T wave"],
    "CD": ["conduction disturbance", "bundle branch block", "AV block"],
    "HYP": ["hypertrophy", "LVH", "left ventricular", "thickened heart"],
}

# Map diagnosis to relevant PDF files for filtering
DIAGNOSIS_PDF_MAP = {
    "NORM": ["General_ECG_Guide.pdf"],
    "MI": ["MI_Recovery_Guide.pdf"],
    "STTC": ["STTC_Ischemia_Guide.pdf"],
    "CD": ["Conduction_Disturbance_Guide.pdf"],
    "HYP": ["Hypertrophy_Management.pdf"],
}


class ECGExplainer:
    """RAG-based ECG explanation generator."""

    def __init__(self, vector_db_dir: Path = VECTOR_DB_DIR):
        """Initialize the RAG engine with vector store and LLM."""
        if not vector_db_dir.exists():
            raise FileNotFoundError(
                f"Vector database not found at {vector_db_dir}. "
                f"Run 'python manage.py ingest' first."
            )

        print("Loading RAG engine...")

        # Load embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        # Load vector store
        print(f"   📚 Loading vector database from: {vector_db_dir}")
        self.vectorstore = Chroma(
            persist_directory=str(vector_db_dir),
            embedding_function=self.embeddings,
        )

        # Get collection info to show document count and previews
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            print(f"   ✅ Vector DB loaded: {count} document chunks available")

            # Show sample of documents (first few)
            if count > 0:
                print("   📄 Retrieving sample documents for preview...")
                sample_docs = self.vectorstore.similarity_search("ECG", k=min(3, count))
                for i, doc in enumerate(sample_docs, 1):
                    source = doc.metadata.get("source_file", "Unknown")
                    first_line = doc.page_content.split("\n")[0][
                        :100
                    ]  # First 100 chars of first line
                    print(f"      📑 Document {i}: {source}")
                    print(f"         First line: {first_line}...")
        except Exception as e:
            print(f"   ⚠️  Could not retrieve document info: {e}")

        # Initialize LLM - reload token to ensure it's fresh
        huggingface_token = get_huggingface_token()
        if not huggingface_token:
            raise ValueError(
                "HUGGINGFACEHUB_API_TOKEN not found in environment variables. "
                "Please set it in your .env file in the project root directory.\n"
                f"Checked paths: {env_paths}\n"
                "Make sure the .env file contains: HUGGINGFACEHUB_API_TOKEN=your_token_here"
            )

        print(f"   🔑 Using HuggingFace API token (length: {len(huggingface_token)})")
        # Falcon-7b-instruct works with text-generation task (confirmed)
        print(f"   🔄 Initializing LLM with text-generation task for {LLM_MODEL}...")
        self.llm = HuggingFaceEndpoint(
            repo_id=LLM_MODEL,
            task="text-generation",  # Falcon models use text-generation task
            huggingfacehub_api_token=huggingface_token,
            temperature=0.3,
            max_new_tokens=400,  # Increased for better responses
            top_p=0.95,
            timeout=30,
        )
        self.llm_task = "text-generation"  # Store task type
        print("   ✅ LLM initialized with text-generation task")

        # Create prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "age", "sex", "diagnosis"],
            template="""You are a compassionate cardiologist explaining ECG results to a patient.

Patient Information:
- Age: {age} years old
- Sex: {sex}
- ECG Diagnosis: {diagnosis}

Medical Context (from guidelines):
{context}

Instructions:
1. Explain what the ECG diagnosis means in simple, patient-friendly language.
2. Discuss what this condition typically means for someone of this age and sex.
3. Explain what steps the patient should take next (e.g., follow-up appointments, lifestyle changes).
4. Be empathetic and reassuring while being medically accurate.
5. Do NOT provide specific medication dosages or treatment plans - always recommend consulting with their cardiologist.

Your explanation:""",
        )

        print("✅ RAG engine loaded successfully")

    def _build_search_query(
        self, diagnosis: str, age: Optional[int] = None, sex: Optional[str] = None
    ) -> str:
        """Build an optimized search query based on diagnosis and patient metadata."""
        # Start with diagnosis-specific terms
        base_terms = DIAGNOSIS_SEARCH_MAP.get(diagnosis, [diagnosis.lower()])

        # Add age-related terms if available
        age_terms = []
        if age:
            if age < 30:
                age_terms.append("young adult")
            elif age < 50:
                age_terms.append("middle-aged")
            else:
                age_terms.append("elderly")

        # Combine terms
        query_parts = base_terms + age_terms
        query = " ".join(query_parts)

        return query

    def _retrieve_context(
        self,
        diagnosis: str,
        age: Optional[int] = None,
        sex: Optional[str] = None,
        k: int = 3,
        user_question: Optional[str] = None,
    ) -> str:
        """Retrieve relevant context from vector store, filtered by diagnosis."""
        print("   🔍 Building search query...")

        # Get relevant PDF files for this diagnosis FIRST
        relevant_pdfs = DIAGNOSIS_PDF_MAP.get(diagnosis, [])
        if not relevant_pdfs:
            print(
                f"   ⚠️  No PDF mapping found for diagnosis: {diagnosis}, searching all documents"
            )
        else:
            print(
                f"   📚 STRICT FILTERING: Only searching in documents for {diagnosis}: {relevant_pdfs}"
            )

        # Build search query - combine user question with diagnosis terms for better relevance
        if user_question:
            # For chat: Combine user question with diagnosis-specific terms
            print("      📝 CHAT MODE: Combining user question with diagnosis context")
            print(f"      User question: '{user_question}'")
            # Get diagnosis search terms to enhance the query
            diagnosis_terms = DIAGNOSIS_SEARCH_MAP.get(diagnosis, [])
            if diagnosis_terms:
                # Combine user question with diagnosis terms for better semantic matching
                enhanced_query = f"{user_question} {' '.join(diagnosis_terms[:2])}"  # Add 2 most relevant terms
                search_query = enhanced_query
                print(
                    f"      ✅ Enhanced query with diagnosis context: '{search_query}'"
                )
            else:
                search_query = user_question
        else:
            # For initial explanation: Use diagnosis-based query
            print(f"      Diagnosis: {diagnosis}")
            if age:
                print(f"      Age context: {age} years old")
            if sex:
                print(f"      Sex context: {sex}")
            search_query = self._build_search_query(diagnosis, age, sex)

        print(f"   📝 Final search query: '{search_query}'")

        # Retrieve relevant documents using similarity search WITH SCORES
        # CRITICAL: Filter by source_file metadata BEFORE searching using ChromaDB where clause
        print(
            f"   🔎 Searching vector DB for {k} relevant chunks using similarity search..."
        )
        print(f"   📊 Query being embedded and searched: '{search_query[:100]}...'")

        # Use ChromaDB's where filter to ONLY search in relevant PDFs
        try:
            if relevant_pdfs:
                # Search each relevant PDF separately and combine results
                # This ensures we ONLY get chunks from the correct PDF(s)
                all_docs_with_scores = []

                for pdf_name in relevant_pdfs:
                    try:
                        # Use ChromaDB's where filter to filter BEFORE search
                        # This is the key fix - filter at the database level, not after
                        # Try both 'where' and 'filter' parameter names for compatibility
                        try:
                            filtered_docs = (
                                self.vectorstore.similarity_search_with_score(
                                    search_query,
                                    k=k * 2,  # Get more from each PDF
                                    where={
                                        "source_file": pdf_name
                                    },  # ChromaDB where clause (preferred)
                                )
                            )
                        except TypeError:
                            # Fallback to 'filter' parameter if 'where' doesn't work
                            filtered_docs = (
                                self.vectorstore.similarity_search_with_score(
                                    search_query,
                                    k=k * 2,
                                    filter={"source_file": pdf_name},
                                )
                            )
                        all_docs_with_scores.extend(filtered_docs)
                        print(
                            f"      ✅ Found {len(filtered_docs)} chunks in {pdf_name}"
                        )
                    except Exception as pdf_error:
                        print(f"      ⚠️  Error searching {pdf_name}: {pdf_error}")
                        # Try without filter as fallback for this PDF, then manually filter
                        try:
                            unfiltered = self.vectorstore.similarity_search_with_score(
                                search_query, k=k * 5
                            )
                            # Manually filter by source_file
                            for doc, score in unfiltered:
                                if doc.metadata.get("source_file") == pdf_name:
                                    all_docs_with_scores.append((doc, score))
                            print(
                                f"      ✅ Fallback: Found {len([d for d, s in all_docs_with_scores if d.metadata.get('source_file') == pdf_name])} chunks via manual filtering"
                            )
                        except Exception as fallback_error:
                            print(f"      ❌ Fallback also failed: {fallback_error}")

                # Sort by similarity score (lower is better for distance, higher is better for similarity)
                # ChromaDB uses distance, so lower scores are better
                all_docs_with_scores.sort(
                    key=lambda x: x[1]
                )  # Sort by score (distance)

                # Take top k results
                docs_with_scores = all_docs_with_scores[:k]

                # Verify all results are from correct PDFs and filter out irrelevant chunks
                verified_docs = []
                irrelevant_keywords = [
                    "copyright",
                    "©",
                    "all rights reserved",
                    "wolters kluwer",
                ]

                for doc, score in docs_with_scores:
                    source_file = doc.metadata.get("source_file", "")
                    content = doc.page_content.lower()

                    # Skip if from wrong PDF
                    if source_file not in relevant_pdfs:
                        print(
                            f"      ⚠️  WARNING: Found chunk from wrong PDF: {source_file}, skipping"
                        )
                        continue

                    # Skip if chunk is too short (likely metadata/header)
                    if len(doc.page_content.strip()) < 50:
                        print(
                            f"      ⚠️  Skipping very short chunk ({len(doc.page_content)} chars)"
                        )
                        continue

                    # Skip if contains copyright/irrelevant content
                    if any(keyword in content for keyword in irrelevant_keywords):
                        print("      ⚠️  Skipping irrelevant chunk (copyright/metadata)")
                        continue

                    verified_docs.append((doc, score))

                # If we filtered out too many, take more from the original list
                if len(verified_docs) < k and len(all_docs_with_scores) > len(
                    docs_with_scores
                ):
                    # Get more candidates
                    for doc, score in all_docs_with_scores[len(docs_with_scores) :]:
                        if len(verified_docs) >= k:
                            break
                        source_file = doc.metadata.get("source_file", "")
                        content = doc.page_content.lower()
                        if (
                            source_file in relevant_pdfs
                            and len(doc.page_content.strip()) >= 50
                            and not any(
                                keyword in content for keyword in irrelevant_keywords
                            )
                        ):
                            verified_docs.append((doc, score))

                docs_with_scores = verified_docs[:k]

                if len(docs_with_scores) < k:
                    print(
                        f"   ⚠️  Only found {len(docs_with_scores)} chunks in relevant PDFs (requested {k})"
                    )
            else:
                # No specific PDFs mapped, search all (shouldn't happen, but handle gracefully)
                docs_with_scores = self.vectorstore.similarity_search_with_score(
                    search_query, k=k
                )

            print(
                f"   ✅ Retrieved {len(docs_with_scores)} document chunks with similarity scores"
            )

            # Extract docs and scores
            docs = [doc for doc, score in docs_with_scores]
            scores = [score for doc, score in docs_with_scores]
        except Exception as e:
            # Fallback to regular similarity_search if with_score fails
            print(
                f"   ⚠️  similarity_search_with_score with filter failed: {e}, using fallback"
            )
            try:
                # Try with regular search and manual filtering
                all_docs = self.vectorstore.similarity_search(search_query, k=k * 5)

                # Filter by relevant PDFs
                if relevant_pdfs:
                    filtered_docs = [
                        doc
                        for doc in all_docs
                        if doc.metadata.get("source_file", "") in relevant_pdfs
                    ]
                    docs = filtered_docs[:k]
                    print(
                        f"   ✅ Fallback: Found {len(docs)} chunks after manual filtering"
                    )
                else:
                    docs = all_docs[:k]
                scores = [None] * len(docs)
            except Exception as fallback_error:
                print(f"   ❌ Fallback also failed: {fallback_error}")
                docs = []
                scores = []

        # Combine retrieved context
        context_parts = []
        for i, (doc, score) in enumerate(zip(docs, scores), 1):
            source = doc.metadata.get("source_file", "Unknown")
            first_line = doc.page_content.split("\n")[0][
                :80
            ]  # First 80 chars of first line
            context_parts.append(f"[Source: {source}]\n{doc.page_content}")
            score_str = f" (similarity: {score:.3f})" if score is not None else ""
            print(
                f"   📄 Chunk {i}: {source} ({len(doc.page_content)} chars){score_str}"
            )
            print(f"      First line: {first_line}...")
            print(
                "      ✅ Retrieved via semantic similarity search (not sequential chunks)"
            )

        context = "\n\n---\n\n".join(context_parts)
        print(
            f"   ✅ Combined context: {len(context)} characters from {len(docs)} unique chunks"
        )
        return context

    def generate_explanation(
        self,
        diagnosis: str,
        age: Optional[int] = None,
        sex: Optional[str] = None,
        k_retrieval: int = 3,
    ) -> dict:
        """
        Generate patient-friendly explanation using RAG.

        Args:
            diagnosis: ECG diagnosis (e.g., "MI", "NORM", "STTC", "CD", "HYP")
            age: Patient age in years
            sex: Patient sex ("Male", "Female", or None)
            k_retrieval: Number of document chunks to retrieve

        Returns:
            Dictionary with explanation and metadata
        """
        try:
            print("   📚 Starting RAG explanation generation...")
            print(f"      Diagnosis: {diagnosis}, Age: {age}, Sex: {sex}")

            # Retrieve relevant context
            print("   🔍 Step 4.1: Retrieving context from Vector DB...")
            context = self._retrieve_context(diagnosis, age, sex, k=k_retrieval)

            # Format prompt
            print("   📝 Step 4.2: Formatting prompt for LLM...")
            prompt = self.prompt_template.format(
                context=context,
                age=age if age else "unknown",
                sex=sex if sex else "unknown",
                diagnosis=diagnosis,
            )
            print(f"   ✅ Prompt formatted ({len(prompt)} characters)")

            # Generate explanation using LLM
            print("   🤖 Step 4.3: Calling HuggingFace LLM API...")
            print(f"      Model: {LLM_MODEL}")
            print("      This may take 15-30 seconds...")

            # Try to invoke with timeout handling
            try:
                # Handle different task formats
                if getattr(self, "llm_task", None) == "conversational":
                    # For conversational task, need to format as conversation
                    from langchain_core.messages import HumanMessage

                    messages = [HumanMessage(content=prompt)]
                    response = self.llm.invoke(messages)
                    # Extract text from response
                    if hasattr(response, "content"):
                        explanation = response.content
                    elif isinstance(response, dict) and "generated_text" in response:
                        explanation = response["generated_text"]
                    else:
                        explanation = str(response)
                else:
                    # For text-generation task, use prompt directly
                    response = self.llm.invoke(prompt)
                    # Extract text from response
                    if isinstance(response, str):
                        explanation = response
                    elif hasattr(response, "content"):
                        explanation = response.content
                    elif isinstance(response, dict):
                        explanation = response.get("generated_text", str(response))
                    else:
                        explanation = str(response)
                print(f"   ✅ LLM response received ({len(explanation)} characters)")
            except Exception as llm_error:
                print(f"   ⚠️  LLM API call failed: {llm_error}")
                # Return a simpler explanation based on diagnosis
                explanation = self._generate_fallback_explanation(diagnosis, age, sex)
                print("   ✅ Using fallback explanation")

            # Clean up explanation (remove any prompt artifacts)
            explanation = explanation.strip()
            if explanation.startswith("Your explanation:"):
                explanation = explanation.replace("Your explanation:", "").strip()

            return {
                "explanation": explanation,
                "diagnosis": diagnosis,
                "age": age,
                "sex": sex,
                "retrieved_sources": k_retrieval,
            }

        except Exception as e:
            # Fallback explanation if RAG fails
            import traceback

            print(f"   ❌ RAG generation error: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            explanation = self._generate_fallback_explanation(diagnosis, age, sex)
            return {
                "explanation": explanation,
                "diagnosis": diagnosis,
                "age": age,
                "sex": sex,
                "error": str(e),
                "fallback": True,
            }

    def _generate_fallback_explanation(
        self, diagnosis: str, age: Optional[int] = None, sex: Optional[str] = None
    ) -> str:
        """Generate a simple fallback explanation without LLM."""
        explanations = {
            "NORM": "Your ECG shows a normal rhythm. This is a good sign, indicating that your heart's electrical activity is functioning normally. Continue with regular check-ups and maintain a healthy lifestyle.",
            "MI": "Your ECG indicates signs of Myocardial Infarction (heart attack). This is a serious condition that requires immediate medical attention. Please consult with a cardiologist urgently for proper evaluation and treatment.",
            "STTC": "Your ECG shows ST-T changes, which may indicate ischemia (reduced blood flow to the heart). This requires medical evaluation. Please consult with a cardiologist to determine the cause and appropriate treatment.",
            "CD": "Your ECG shows a conduction disturbance, which means there may be an issue with how electrical signals travel through your heart. Please consult with a cardiologist for further evaluation and management.",
            "HYP": "Your ECG indicates signs of hypertrophy (thickening of the heart muscle). This may be related to high blood pressure or other conditions. Please consult with a cardiologist for proper evaluation and treatment recommendations.",
        }

        base_explanation = explanations.get(
            diagnosis,
            f"Your ECG shows {diagnosis}. Please consult with a cardiologist for detailed interpretation.",
        )

        if age or sex:
            personalized = f" For a {age if age else 'patient'}-year-old {sex.lower() if sex else 'patient'}, "
            return personalized + base_explanation.lower()

        return base_explanation


# Global instance (lazy loading)
_explainer: Optional[ECGExplainer] = None


def get_explainer() -> ECGExplainer:
    """Get or create the global ECGExplainer instance."""
    global _explainer
    if _explainer is None:
        _explainer = ECGExplainer()
    return _explainer
