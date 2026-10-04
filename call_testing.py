from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

first = client.responses.create(
    model = "gpt-6-luna",
    input = "My preferred database is PostgreSQL")

print(first.output_text)

second = client.responses.create(
    model="gpt-6-luna",
    previous_response_id = first.id,
    input="What is my preferred database?"
)

print(second.output_text)