import os
from dotenv import load_dotenv

# -------------------------------------------------------
# Load API Key from .env
# -------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file!")

# -------------------------------------------------------
# Gemini LLM Setup
# -------------------------------------------------------
try:
    import google.generativeai as genai
except ImportError:
    raise ImportError(
        "google-generativeai not installed. Install with: pip install google-generativeai"
    )

genai.configure(api_key=API_KEY)


# -------------------------------------------------------
# Test LLM Connectivity
# -------------------------------------------------------
def test_gemini():
    print("🔄 Testing Gemini API connectivity...")

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content("Hello Gemini! Can you hear me?")

        print("\n✅ Gemini API connection successful!")
        print("--------------------------------------------------------------")
        print(response.text)
        print("--------------------------------------------------------------")

    except Exception as e:
        print("\n❌ Gemini API test failed!")
        print("Error details:")
        print("--------------------------------------------------------------")
        print(e)
        print("--------------------------------------------------------------")


if __name__ == "__main__":
    test_gemini()
