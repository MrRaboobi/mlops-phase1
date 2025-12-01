"""
Chat endpoint for follow-up questions about ECG results.
Uses the Gemini-powered RAG engine to provide contextual, patient-friendly answers.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict

from src.rag_engine import get_explainer

router = APIRouter()


# -----------------------------------------
# Request / Response Models
# -----------------------------------------


class ChatRequest(BaseModel):
    """Incoming request to the chat endpoint."""

    message: str
    diagnosis: str
    age: Optional[int] = None
    sex: Optional[str] = None
    conversation_history: Optional[List[Dict]] = None


class ChatResponse(BaseModel):
    """Response from the chat model."""

    response: str
    diagnosis: str


# -----------------------------------------
# Chat Endpoint
# -----------------------------------------


@router.post("/chat", tags=["Chat"])
def chat_with_rag(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint for follow-up questions about ECG results.

    Uses the updated Gemini-based RAG engine to:
    1. Retrieve relevant medical guideline context
    2. Generate a natural, empathetic answer to the user's question
    3. Keep responses medically safe and patient-friendly
    """

    try:
        # Load Gemini RAG explainer
        explainer = get_explainer()

        print("\n" + "=" * 60)
        print("💬 NEW CHAT REQUEST")
        print(f"   User Question: {request.message}")
        print(f"   Diagnosis: {request.diagnosis}")
        print(f"   Age: {request.age}, Sex: {request.sex}")
        print("=" * 60)

        # -----------------------------------------
        # Step 1 — Retrieve Relevant Context
        # -----------------------------------------

        context = explainer.retrieve_context(
            diagnosis=request.diagnosis,
            age=request.age,
            sex=request.sex,
            k=5,  # Retrieve more for chat
        )

        if not context or len(context.strip()) < 50:
            raise ValueError("Context retrieval too short or empty.")

        print(f"   ✅ Retrieved {len(context)} chars of context.")
        print(context[:100] + "\n...")

        prompt = f"""
You are a helpful, empathetic medical assistant specializing in cardiology.
You are talking to a patient who recently received an ECG result.

Here is the patient's clinical information:
- Diagnosis: {request.diagnosis}
- Age: {request.age if request.age else "Not provided"}
- Sex: {request.sex if request.sex else "Not provided"}

Relevant Medical Context (extracted from trusted medical guidelines):
{context}

Patient's Question:
"{request.message}"

Instructions for your reply:
1. Respond in a warm, patient-friendly tone.
2. Use simple, non-technical language unless necessary.
3. Provide medically accurate and safe information.
4. If discussing lifestyle or next steps, keep recommendations general.
5. Encourage the patient to consult their cardiologist for personalized guidance.
6. DO NOT give medication doses, treatment plans, or emergencies advice.

Your response:
"""

        print("   🤖 Calling Gemini 2.5 Flash for chat response...")

        # -----------------------------------------
        # Step 3 — Call Gemini LLM
        # -----------------------------------------

        try:
            response = explainer.llm.generate_content(prompt)
            reply = response.text.strip()
            print(f"   ✅ Gemini chat response generated ({len(reply)} chars)")

        except Exception as llm_error:
            raise RuntimeError(f"Gemini LLM failed: {llm_error}")

        return ChatResponse(response=reply, diagnosis=request.diagnosis)

    except Exception as e:
        # -----------------------------------------
        # Fallback Response (Safe Mode)
        # -----------------------------------------

        import traceback

        print("⚠️ Chat RAG failed:", e)
        print(traceback.format_exc())

        fallback_reply = f"""
I'm here to help you understand your ECG results.

You're asking about **{request.diagnosis}**, and while I'm currently unable
to retrieve detailed medical guidance, I can offer general suggestions:

- It's important to follow up with your cardiologist
- Monitor any symptoms such as chest pain, shortness of breath, or dizziness
- Attend all scheduled medical appointments
- Maintain heart-healthy habits such as regular exercise and balanced diet

For personalized medical advice, always consult your healthcare provider.

Error details: {e}
"""

        return ChatResponse(
            response=fallback_reply.strip(), diagnosis=request.diagnosis
        )
