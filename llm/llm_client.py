import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class LLMClient:

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in .env"
            )

        self.client = Groq(
            api_key=api_key
        )

        self.model = "openai/gpt-oss-20b"


    def generate(
        self,
        prompt,
        json_mode=False
    ):

        kwargs = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        }

        if json_mode:

            kwargs["response_format"] = {
                "type": "json_object"
            }

        response = (
            self.client.chat.completions.create(
                **kwargs
            )
        )

        return response.choices[0].message.content