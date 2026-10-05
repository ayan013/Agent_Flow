from openai import OpenAI
from dotenv import load_dotenv
import os, time

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

start = time.perf_counter()
response = client.responses.create(
    model = "gpt-6-luna",
    instructions = "Explain briefly to a backend developer.",
    input = "What problem does Redis solve?"
)

end = time.perf_counter()

latency = end - start

print(response.output_text)

print("\n--- METRICS ---")
print("Input Tokens:- ", response.usage.input_tokens)
print("Output tokens:", response.usage.output_tokens)
print("Total tokens:", response.usage.total_tokens)
print("Latency:", round(latency, 2), "seconds")
