from openai import OpenAI
from dotenv import load_dotenv
import os,json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))


def get_candidate_history(candidate_id: str):
    candidates = {
        "C101": {
            "score": 7,
            "weak_topics": [
                "decorators",
                "asyncio"
            ],
            "strong_topics": [
                "FastAPI",
                "REST APIs"
            ]
        },
        "C102": {
            "score": 9,
            "weak_topics": [
                "database indexing"
            ],
            "strong_topics": [
                "Python",
                "FastAPI",
                "PostgreSQL"
            ]
        }
    }

    return candidates.get(candidate_id,{"Candidate not found"})

tools = [
    {
        "type": "function",
        "name": "get_candidate_history",

        "description":
            "Get a candidate's previous interview performance.",

        "parameters": {
            "type": "object",

            "properties": {
                "candidate_id": {
                    "type": "string",
                    "description":
                        "Candidate ID, for example C101"
                }
            },

            "required": ["candidate_id"],

            "additionalProperties": False
        },

        "strict": True
    }
]

response = client.responses.create(

    model="gpt-6-luna",

    instructions="""
    You are an interview assessment assistant.

    Use candidate history when the user asks
    about previous interview performance.
    """,

    input="""
    what is dependency injection?
    """,

    tools = tools
)

function_call = None

for item in response.output:

    if item.type == "function_call":
        function_call = item
        break

if function_call is None:
    # No tool required
    print(response.output_text)
    raise SystemExit


arguments = json.loads(
    function_call.arguments
    )
# print(arguments["candidate_id"])

if function_call.name == "get_candidate_history":

    result = get_candidate_history(
        candidate_id=arguments["candidate_id"]
    )
else:
    raise ValueError(
        f"Unknown tool: {function_call.name}"
    )

print(result)

tool_output = {
    "type": "function_call_output",

    "call_id": function_call.call_id,

    "output": json.dumps(result)
}

final_response = client.responses.create(

    model="gpt-6-luna",

    previous_response_id=response.id,

    tools=tools,

    input=[
        tool_output
    ]
)

print(final_response.output_text)