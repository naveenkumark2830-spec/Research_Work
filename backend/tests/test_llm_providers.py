import os
from dotenv import load_dotenv
from google import genai
from groq import Groq

# Load backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")


def test_gemini():
    print("\n========== GEMINI TEST ==========")

    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY missing")
        return

    print(f"Model: {GEMINI_MODEL}")

    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=(
            "You are Teddy, an educational Hadoop AI assistant. "
            "Explain HDFS in exactly two short sentences."
        ),
    )

    print("✅ Gemini connected")
    print("Response:")
    print(response.text)


def test_groq():
    print("\n========== GROQ TEST ==========")

    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY missing")
        return

    print(f"Model: {GROQ_MODEL}")

    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are Teddy, an educational Hadoop AI assistant.",
            },
            {
                "role": "user",
                "content": "Explain HDFS in exactly two short sentences.",
            },
        ],
    )

    print("✅ Groq connected")
    print("Response:")
    print(response.choices[0].message.content)


if __name__ == "__main__":
    test_gemini()
    test_groq()