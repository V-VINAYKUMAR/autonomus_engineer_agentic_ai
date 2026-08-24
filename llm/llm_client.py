import os

from dotenv import load_dotenv
from google import genai
from groq import Groq


load_dotenv()


class LLMClient:

    def __init__(self):

        # ==========================================
        # Gemini
        # ==========================================

        self.gemini_key = os.getenv(
            "GEMINI_API_KEY"
        )

        self.gemini_client = None

        if self.gemini_key:

            self.gemini_client = genai.Client(
                api_key=self.gemini_key
            )


        # ==========================================
        # Groq
        # ==========================================

        self.groq_key = os.getenv(
            "GROQ_API_KEY"
        )

        self.groq_client = None

        if self.groq_key:

            self.groq_client = Groq(
                api_key=self.groq_key
            )


        # ==========================================
        # Models
        # ==========================================

        self.gemini_model = (
            "gemini-2.5-flash"
        )

        self.groq_model = (
            "openai/gpt-oss-20b"
        )


    # ==========================================
    # Generate response
    # ==========================================

    def generate(
        self,
        prompt,
        json_mode=False
    ):

        # ======================================
        # Try Gemini first
        # ======================================

        if self.gemini_client:

            try:

                print(
                    "\nLLM Provider: Gemini"
                )

                response = (
                    self.gemini_client
                    .models
                    .generate_content(
                        model=self.gemini_model,
                        contents=prompt
                    )
                )

                text = response.text

                if text:

                    return text.strip()


            except Exception as e:

                error_text = str(e)

                print(
                    "\n⚠️ Gemini failed:"
                )

                print(
                    error_text
                )

                print(
                    "\nTrying Groq fallback..."
                )


        # ======================================
        # Try Groq
        # ======================================

        if self.groq_client:

            try:

                print(
                    "\nLLM Provider: Groq"
                )

                kwargs = {
                    "model": self.groq_model,

                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }


                if json_mode:

                    kwargs[
                        "response_format"
                    ] = {
                        "type": "json_object"
                    }


                response = (
                    self.groq_client
                    .chat
                    .completions
                    .create(
                        **kwargs
                    )
                )


                text = (
                    response
                    .choices[0]
                    .message
                    .content
                )


                if text:

                    return text.strip()


            except Exception as e:

                print(
                    "\n❌ Groq failed:"
                )

                print(
                    str(e)
                )


        # ======================================
        # Both failed
        # ======================================

        raise RuntimeError(
            "All configured LLM providers failed."
        )