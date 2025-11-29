"""
Chat endpoint for follow-up questions about ECG results.
Uses the RAG engine to provide contextual answers.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
from src.rag_engine import get_explainer

router = APIRouter()


class ChatMessage(BaseModel):
    """Single chat message."""

    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str
    diagnosis: str
    age: Optional[int] = None
    sex: Optional[str] = None
    conversation_history: Optional[List[Dict]] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str
    diagnosis: str


@router.post("/chat", tags=["Chat"])
def chat_with_rag(request: ChatRequest):
    """
    Chat endpoint for asking follow-up questions about ECG results.

    Uses the RAG engine to retrieve relevant medical context and generate
    personalized responses based on the patient's diagnosis, age, and sex.
    """
    try:
        # Get the RAG explainer
        explainer = get_explainer()

        # Build a context-aware query
        # Combine the user's question with diagnosis information
        query = f"{request.message}. Patient has {request.diagnosis} diagnosis."
        if request.age:
            query += f" Patient is {request.age} years old."
        if request.sex:
            query += f" Patient is {request.sex}."

        # Retrieve relevant context from vector store
        # IMPORTANT: Pass the user's actual question for better retrieval
        print(f"\n{'='*60}")
        print("💬 CHAT REQUEST")
        print(f"   User Question: '{request.message}'")
        print(f"   Diagnosis: {request.diagnosis}")
        print(f"   Age: {request.age}, Sex: {request.sex}")
        print(f"{'='*60}")
        context = explainer._retrieve_context(
            diagnosis=request.diagnosis,
            age=request.age,
            sex=request.sex,
            k=5,  # Retrieve more chunks for chat (5 instead of 3)
            user_question=request.message,  # Pass the actual user question!
        )

        # Check if context was retrieved
        if not context or len(context.strip()) < 50:
            raise ValueError(
                f"Retrieved context is too short or empty ({len(context) if context else 0} chars). Check if vector DB has relevant documents."
            )

        print(f"   ✅ Context retrieved: {len(context)} characters")

        # Build a conversational prompt
        prompt = f"""You are a helpful medical assistant explaining ECG results to a patient.

Patient Information:
- Diagnosis: {request.diagnosis}
- Age: {request.age if request.age else 'Not specified'}
- Sex: {request.sex if request.sex else 'Not specified'}

Relevant Medical Context:
{context}

Patient's Question: {request.message}

Instructions:
1. Answer the patient's question in a clear, empathetic, and patient-friendly way.
2. Use the medical context provided to give accurate information.
3. If the question is about lifestyle changes, provide practical advice.
4. If the question is about the condition itself, explain it simply.
5. Always remind the patient to consult with their cardiologist for personalized medical advice.
6. Do NOT provide specific medication dosages or treatment plans.

Your response:"""

        # Generate response using LLM
        # Handle different task formats
        print(
            f"   🤖 Calling LLM with task: {getattr(explainer, 'llm_task', 'unknown')}"
        )
        try:
            if getattr(explainer, "llm_task", None) == "conversational":
                from langchain_core.messages import HumanMessage

                messages = [HumanMessage(content=prompt)]
                response = explainer.llm.invoke(messages)
                print(
                    f"   📥 Response type: {type(response)}, value: {str(response)[:200]}"
                )
                # Extract text from response
                if hasattr(response, "content"):
                    response_text = response.content
                elif isinstance(response, dict) and "generated_text" in response:
                    response_text = response["generated_text"]
                elif isinstance(response, list) and len(response) > 0:
                    # Handle list responses
                    first_item = response[0]
                    if isinstance(first_item, dict) and "generated_text" in first_item:
                        response_text = first_item["generated_text"]
                    else:
                        response_text = str(first_item)
                else:
                    response_text = str(response)
            else:
                # For text-generation task, use prompt directly
                response = explainer.llm.invoke(prompt)
                print(
                    f"   📥 Response type: {type(response)}, value: {str(response)[:200]}"
                )
                # Extract text from response - text-generation can return various formats
                if isinstance(response, str):
                    response_text = response
                elif isinstance(response, list):
                    # HuggingFace text-generation often returns a list of dicts
                    if len(response) > 0:
                        first_item = response[0]
                        if isinstance(first_item, dict):
                            # Try common keys
                            response_text = first_item.get(
                                "generated_text",
                                first_item.get(
                                    "text", first_item.get("response", str(first_item))
                                ),
                            )
                        else:
                            response_text = str(first_item)
                    else:
                        response_text = "No response generated"
                elif isinstance(response, dict):
                    response_text = response.get(
                        "generated_text",
                        response.get("text", response.get("response", str(response))),
                    )
                elif hasattr(response, "content"):
                    response_text = response.content
                else:
                    response_text = str(response)

            # Clean up response
            response_text = response_text.strip()
            if not response_text or len(response_text) < 10:
                raise ValueError(f"Response too short or empty: '{response_text}'")

            # Remove prompt artifacts
            if response_text.startswith("Your response:"):
                response_text = response_text.replace("Your response:", "").strip()
            if prompt[:50] in response_text:
                # Remove the prompt if it was included in the response
                response_text = response_text.replace(prompt[:100], "").strip()

            print(f"   ✅ Extracted response ({len(response_text)} chars)")

        except Exception as llm_error:
            error_details = f"{type(llm_error).__name__}: {str(llm_error)}"
            print(f"   ❌ LLM invocation failed: {error_details}")
            print(
                f"   📋 Response object was: {type(response) if 'response' in locals() else 'N/A'}"
            )
            raise Exception(f"LLM generation failed: {error_details}") from llm_error

        return ChatResponse(response=response_text, diagnosis=request.diagnosis)

    except Exception as e:
        # Fallback response if RAG fails
        import traceback

        error_msg = str(e) if str(e) else f"{type(e).__name__} (no message)"
        error_trace = traceback.format_exc()
        print(f"⚠️  Chat RAG failed: {error_msg}")
        print(f"📋 Full traceback:\n{error_trace}")

        fallback_response = f"""I understand you're asking about {request.diagnosis}.

While I'm having trouble accessing detailed medical information right now, I can tell you that:
- It's important to follow up with your cardiologist for personalized advice
- Make sure to attend all scheduled follow-up appointments
- Keep track of any symptoms you experience

For specific questions about your condition, please consult with your healthcare provider who can give you personalized guidance based on your complete medical history.

Error details: {error_msg}"""

        return ChatResponse(response=fallback_response, diagnosis=request.diagnosis)
