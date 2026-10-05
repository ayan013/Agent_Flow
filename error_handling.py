import openai
from openai import OpenAI
from dotenv import load_dotenv
import os, time

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

try:
    response = client.responses.create(
        model="gpt-6-luna",
        input="Explain RAG."
    )

    print(response.output_text)

except openai.AuthenticationError:
    print("Authentication failed.")

except openai.NotFoundError:
    print("Model or resource was not found.")

except openai.RateLimitError:
    print("Rate limit reached.")

except openai.APITimeoutError:
    print("Request timed out.")

except openai.APIConnectionError:
    print("Could not connect to OpenAI.")

except openai.InternalServerError:
    print("OpenAI server error.")