from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

response = client.responses.create(
    model="does-not-exist",
    instructions="Explain technical concepts to a backend developer."
                 "Keep the explanation under 150 words.",
    input="Explain vector embeddings."
)


print("ID:")
print(response.id)

print("\nOUTPUT:")
print(response.output_text)

print("\nUSAGE:")
print(response.usage)