"""
RAG Engine for ECG Explanation Generation
Uses Chroma vector DB + Gemini 2.5 Flash to generate patient-friendly ECG explanations.
"""

import os
import warnings
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv
import google.generativeai as genai

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from langchain_core.prompts import PromptTemplate

# Suppress noisy warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load environment variables
load_dotenv()

# Configuration
VECTOR_DB_DIR = Path("data/vector_db")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Diagnosis → search terms
DIAGNOSIS_SEARCH_MAP = {
    "NORM": ["normal ECG", "healthy heart rhythm", "normal sinus rhythm"],
    "MI": ["myocardial infarction", "heart attack", "ischemia", "MI"],
    "STTC": ["ST-T changes", "ischemia", "ST depression", "T wave"],
    "CD": ["conduction disturbance", "AV block", "bundle branch block"],
    "HYP": ["hypertrophy", "LVH", "ventricular thickening"],
}

# For future filtering (optional)
DIAGNOSIS_PDF_MAP = {
    "NORM": ["General_ECG_Guide.pdf"],
    "MI": ["MI_Recovery_Guide.pdf"],
    "STTC": ["STTC_Ischemia_Guide.pdf"],
    "CD": ["Conduction_Disturbance_Guide.pdf"],
    "HYP": ["Hypertrophy_Management.pdf"],
}


class ECGExplainer:
    """RAG-based ECG explanation engine using Gemini 2.5 Flash."""

    def __init__(self):
        print("📘 Initializing ECG RAG Engine...")

        # Validate vector DB exists
        if not VECTOR_DB_DIR.exists():
            raise FileNotFoundError(
                f"Vector database not found at {VECTOR_DB_DIR}. "
                f"Run: python manage.py ingest"
            )

        # Load embeddings
        print("🔤 Loading embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        # Load Chroma DB
        print(f"🗂️ Loading vector DB from: {VECTOR_DB_DIR}")
        self.vectorstore = Chroma(
            persist_directory=str(VECTOR_DB_DIR),
            embedding_function=self.embeddings,
        )

        # Gemini setup
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError(
                "GEMINI_API_KEY missing in .env. Please add it:\n"
                "GEMINI_API_KEY=your_key_here"
            )

        print("🤖 Initializing Gemini 2.5 Flash...")
        genai.configure(api_key=gemini_key)
        self.llm = genai.GenerativeModel("gemini-2.5-flash")
        print("   ✅ Gemini model loaded successfully.")

        # Prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "age", "sex", "diagnosis"],
            template="""
You are a compassionate cardiologist explaining ECG results to a patient.

Patient Information:
- Age: {age}
- Sex: {sex}
- ECG Diagnosis: {diagnosis}

Medical Context from Guidelines:
{context}

Instructions:
1. Explain what the ECG findings mean in simple language.
2. Provide medically accurate insight tailored to this patient's age and sex.
3. Give clear, safe next-step recommendations.
4. Be empathetic, reassuring, and easy to understand.
5. Do NOT provide medication dosages or specific treatments.

Your explanation:
""",
        )

        print("✨ RAG Engine ready.\n")

    # ------------------------------------------
    # BUILD RETRIEVAL QUERY
    # ------------------------------------------
    def _build_query(self, diagnosis: str, age: Optional[int], sex: Optional[str]):
        base_terms = DIAGNOSIS_SEARCH_MAP.get(diagnosis, [diagnosis.lower()])
        age_term = "elderly" if age and age > 50 else "adult"
        query = " ".join(base_terms + [age_term, sex.lower() if sex else ""])
        return query.strip()

    # ------------------------------------------
    # RETRIEVE CONTEXT
    # ------------------------------------------
    def retrieve_context(
        self, diagnosis: str, age: Optional[int], sex: Optional[str], k: int = 3
    ) -> str:

        print("🔍 Retrieving relevant medical context...")
        query = self._build_query(diagnosis, age, sex)
        print(f"   📄 Search query: {query}")

        docs = self.vectorstore.similarity_search(query, k=k)

        context_parts = []
        for doc in docs:
            src = doc.metadata.get("source", "Unknown")
            context_parts.append(f"[Source: {src}]\n{doc.page_content.strip()}")

        context = "\n\n---\n\n".join(context_parts)
        print(f"   ✅ Retrieved {len(docs)} context chunks.")
        return context

    # ------------------------------------------
    # GENERATE EXPLANATION
    # ------------------------------------------
    def generate_explanation(
        self,
        diagnosis: str,
        age: Optional[int],
        sex: Optional[str],
        k_retrieval: int = 3,
    ) -> Dict:

        print("🧠 Generating patient-friendly ECG explanation...")

        # Retrieve context
        context = self.retrieve_context(diagnosis, age, sex, k=k_retrieval)

        # Format prompt
        prompt = self.prompt_template.format(
            context=context,
            age=age if age else "unknown",
            sex=sex if sex else "unknown",
            diagnosis=diagnosis,
        )

        print("🤖 Calling Gemini 2.5 Flash... (This may take 5–10 seconds)")
        try:
            response = self.llm.generate_content(prompt)
            explanation = response.text.strip()
            print("   ✅ Explanation generated successfully.")

        except Exception as e:
            print(f"   ⚠️ Gemini API failed: {e}")
            explanation = self._fallback(diagnosis, age, sex)

        return {
            "explanation": explanation,
            "diagnosis": diagnosis,
            "age": age,
            "sex": sex,
        }

    # ------------------------------------------
    # FALLBACK (no LLM or vector DB issues)
    # ------------------------------------------
    def _fallback(self, diagnosis, age, sex):
        fallback_map = {
            "NORM": "Your ECG appears normal. This indicates healthy electrical activity in the heart.",
            "MI": "Your ECG indicates a possible myocardial infarction (heart attack). Please seek urgent medical evaluation.",
            "STTC": "Your ECG shows ST-T changes, which may indicate reduced blood flow to the heart.",
            "CD": "Your ECG shows conduction abnormalities. Further cardiology evaluation is recommended.",
            "HYP": "Your ECG suggests possible ventricular hypertrophy, which may be related to high blood pressure.",
        }
        base = fallback_map.get(
            diagnosis,
            f"Your ECG shows signs of {diagnosis}. Please consult a cardiologist.",
        )

        if age or sex:
            return (
                f"For a {age or 'patient'}-year-old {sex or 'patient'}, {base.lower()}"
            )

        return base


# ---------------------------------------------------------
# GLOBAL SINGLETON
# ---------------------------------------------------------
_explainer: Optional[ECGExplainer] = None


def get_explainer() -> ECGExplainer:
    global _explainer
    if _explainer is None:
        _explainer = ECGExplainer()
    return _explainer
