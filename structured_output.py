from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Literal

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

class InterviewEvaluation(BaseModel):
    difficulty: Literal[
        "easy",
        "medium",
        "hard"
    ]
    score: int
    strengths: list[str]
    improvements: list[str]
    summary: str

response = client.responses.parse(
    model = "gpt-6-luna",
    input = [
        {"role":"developer",
         "content": """
           You are a Python backend interviewer.
           Evaluate the candidate's answer.
           """
         },
        {
           "role": "user",
           "content": """
           Question:
           What is dependency injection in FastAPI?

           Candidate answer:
           Dependency injection means FastAPI installs Python packages
automatically when the API starts.
           """
        }
    ],
    text_format = InterviewEvaluation
)

result = response.output_parsed
print(result.score)

print("Difficulty\n")
print(result.difficulty)
print("Strength\n")
for strength in result.strengths:
    print(strength)

print("Improvments\n")
for improvement in result.improvements:
    print("-", improvement)

print("\nSummary:")
print(result.summary)

formatted = result.model_dump()
print(formatted.get("score"))
