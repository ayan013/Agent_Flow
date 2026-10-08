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
    }
]

# --------------------------------------------------
# TOOL REGISTRY
# --------------------------------------------------

TOOL_FUNCTION = {
    "get_candidate_history": get_candidate_history,
    "get_role_requirements": get_role_requirements
}

# --------------------------------------------------
# DISPATCHER
# --------------------------------------------------

def dispatch_tool(tool_name, arguments):
    tool_function = TOOL_FUNCTION.get(tool_name)

    if tool_function is None:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
     return tool_function(**arguments)
    except Exception as exc:
        return {"error":str(exc)}

# --------------------------------------------------
# FIRST MODEL CALL
# --------------------------------------------------

response = client.responses.create(

    model="gpt-6-luna",

    instructions="""
    You are an interview assessment assistant.
    
    When comparing a candidate with a role:
    
    1. Identify requirements that match candidate strengths.
    2. Identify requirements that are candidate weaknesses.
    3. Identify requirements for which no evidence exists.
    4. Give an overall readiness assessment.
    
    Use tools whenever candidate-specific
    or role-specific data is required.
    """,

    input="""
    Compare candidate C101's previous performance
    with the requirements for a Python backend role.
    """,

    tools=tools
)

# --------------------------------------------------
# COLLECT TOOL CALLS
# --------------------------------------------------

function_calls = [item for item in response.output if item.type == "function_call"]


# No tool needed
if not function_calls:

    print(response.output_text)

    raise SystemExit

# --------------------------------------------------
# EXECUTE TOOLS
# --------------------------------------------------
tool_outputs = []
for function_call in function_calls:

    print("\nTOOL:",function_call.name)

    print("ARGUMENTS:",function_call.arguments)

    arguments = json.loads(function_call.arguments)

    result = dispatch_tool(function_call.name,arguments)

    print("RESULT:",result)

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

# --------------------------------------------------
# SECOND MODEL CALL
# --------------------------------------------------

final_response = client.responses.create(

    model="gpt-6-luna",

    previous_response_id=response.id,

    tools=tools,

    input=tool_outputs
)


print("\nFINAL ANSWER:")
print(final_response.output_text)