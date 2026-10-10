from openai import OpenAI
from dotenv import load_dotenv
import os,json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

# --------------------------------------------------
# FUNCTIONS
# --------------------------------------------------

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

    return candidates.get(candidate_id,{"error": "Candidate not found"})

def get_role_requirements(role: str):

    roles = {
        "python_backend": {
            "required_topics": [
                "Python",
                "FastAPI",
                "asyncio",
                "PostgreSQL",
                "REST APIs",
                "database indexing"
            ]
        },

        "devops": {
            "required_topics": [
                "Linux",
                "Docker",
                "Kubernetes",
                "CI/CD"
            ]
        }
    }

    return roles.get(role,{"error": "Role not found"})

def search_question_bank(topic: str):

    questions = {
        "database indexing": [
            "What problem does a database index solve?",
            "Why can too many indexes slow down writes?"
        ],

        "asyncio": [
            "What problem does asyncio solve in Python?",
            "When would you use async def in FastAPI?"
        ],

        "decorators": [
            "What is a Python decorator?",
            "Give one practical use case for decorators."
        ]
    }

    return {
            "topic": topic,
            "questions": questions.get(topic,["No questions found"])
            }


# --------------------------------------------------
# TOOL REGISTRY
# --------------------------------------------------

TOOL_REGISTRY = {
    "get_candidate_history":
        get_candidate_history,

    "get_role_requirements":
        get_role_requirements,

    "search_question_bank":
        search_question_bank
}

# --------------------------------------------------
# TOOL SCHEMAS
# --------------------------------------------------

tools = [
    {
     "type":"function", #This identifies the tool category. It tells the model that this tool represents a callable function.
     "name": "get_candidate_history", #This is the identifier the model uses in a tool call
     "description": #The description explains what the tool does and, indirectly, when it should be selected
            "Get the candidate's previous interview score, "
            "strong topics and weak topics.",
     "parameters":{ # the arguments the tool may accept.
         "type":"object", #The function arguments must be represented as a JSON object
         "properties":{ #Properties lists the fields that are defined inside the argument object
             "candidate_id":{
                 "type":"string", #argument type
                 "description":"Candidate ID such as C101" #helps the model understand what the field represents. It is
                                                           #particularly valuable when names such as id, value, code, or key are ambiguous.
             }
         },
         "required":["candidate_id"],
         "additionalProperties":False
     },
     "strict":True # follow the declared parameter structure closel
    },
    {
        "type": "function",
        "name": "get_role_requirements",

        "description":
            "Get the technical topics required for a job role.",

        "parameters": {
            "type": "object",

            "properties": {
                "role": {
                    "type": "string",
                    "enum": [
                        "python_backend",
                        "devops"
                    ]
                }
            },

            "required": ["role"],
            "additionalProperties": False
        },

        "strict": True
    },
    {
        "type": "function",

        "name": "search_question_bank",

        "description":
            "Retrieve interview questions for a "
            "specific technical topic.",

        "parameters": {
            "type": "object",

            "properties": {
                "topic": {
                    "type": "string",
                    "description":
                        "Technical topic for which "
                        "questions are required."
                }
            },

            "required": ["topic"],

            "additionalProperties": False
        },

        "strict": True
    }

]

# --------------------------------------------------
# DISPATCHER
# --------------------------------------------------

def dispatch_tool(tool_name, arguments):
    tool_function = TOOL_REGISTRY.get(tool_name)

    if tool_function is None:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
     return tool_function(**arguments)
    except Exception as exc:
        return {"error":str(exc)}


# ==================================================
# STABLE AGENT INSTRUCTIONS
# ==================================================

INSTRUCTIONS = """
You are an interview assessment agent.

Use available tools whenever external
candidate, role, or question-bank data
is required.

When asked to create a question based
on a candidate's weakness:

1. Retrieve the candidate's history.
2. Determine one weak topic from the result.
3. Search the question bank for that topic.
4. Return one relevant interview question.

Do not invent candidate history or question-bank data.
"""

# ==================================================
# FIRST RESPONSE
# ==================================================

response = client.responses.create(

    model="gpt-6-luna",

    instructions=INSTRUCTIONS,

    input="""
    Find candidate C102's weakest topic
    and give me one interview question
    specifically about that weakness.
    """,

    tools=tools
)

# ==================================================
# AGENT LOOP
# ==================================================

step = 0
MAX_STEPS = 5


while True:

    step += 1

    print(
        f"\n========== STEP {step} =========="
    )


    if step > MAX_STEPS:

        print(
            "Agent stopped: "
            "maximum steps exceeded."
        )

        break


    function_calls = [
        item
        for item in response.output
        if item.type == "function_call"
    ]

    #print(function_calls)

    # ----------------------------------------------
    # TERMINATION CONDITION
    # ----------------------------------------------

    if not function_calls:

        print("\nFINAL ANSWER:")
        print(response.output_text)

        break


    # ----------------------------------------------
    # EXECUTE ALL TOOLS REQUESTED THIS ROUND
    # ----------------------------------------------

    tool_outputs = []


    for function_call in function_calls:

        print("\nTOOL:",
            function_call.name
        )

        print(
            "ARGUMENTS:",
            function_call.arguments
        )


        arguments = json.loads(
            function_call.arguments
        )


        result = dispatch_tool(
            function_call.name,
            arguments
        )


        print(
            "RESULT:",
            result
        )


        tool_outputs.append(
            {
                "type":
                    "function_call_output",

                "call_id":
                    function_call.call_id,

                "output":
                    json.dumps(result)
            }
        )


    # ----------------------------------------------
    # MODEL OBSERVES RESULTS AND DECIDES AGAIN
    # ----------------------------------------------

    response = client.responses.create(

        model="gpt-6-luna",

        instructions=INSTRUCTIONS,

        previous_response_id=response.id,

        input=tool_outputs,

        tools=tools
    )