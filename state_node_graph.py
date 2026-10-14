from openai import OpenAI
from dotenv import load_dotenv
import os,json
from typing import TypedDict


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
# STATE
# --------------------------------------------------

class InterviewState(TypedDict,total=False):
    candidate_id: str
    candidate_history: dict
    weak_topic: str
    questions: list[str]
    selected_question: str
    status: str
    error: str

# --------------------------------------------------
# NODE - A step of the workflow
# --------------------------------------------------

def get_candidate_node(state: TypedDict) -> dict:

    history = get_candidate_history(state["candidate_id"])
    if "error" in history:
        return{"error":history["error"]}
    return{
        "candidate_history": history
    }

def select_weak_topic_node(state: InterviewState) -> dict:

    weak_topics = (
        state["candidate_history"].get("weak_topics", [])
    )

    if not weak_topics:
        return {
            "error":
                "No weak topics found."
        }

    return {
        "weak_topic":
            weak_topics[0]
    }

def question_bank_node(state: InterviewState) -> dict:

    result = search_question_bank(state["weak_topic"])

    questions = result.get("questions",[])

    if not questions:
        return {
            "error":
                "No questions found."
        }

    return {
        "questions": questions
    }


def select_question_node(state: InterviewState) -> dict:

    questions = state.get(
        "questions",
        []
    )

    if not questions:
        return {
            "error":
                "No questions available."
        }

    return {
        "selected_question":questions[0],"status":"completed"
    }

# --------------------------------------------------
# Conditional Edge - It defines which node to select next
# --------------------------------------------------

def route(state: InterviewState) -> str:

    if state.get("error"):
        return "error"

    if "candidate_history" not in state:
        return "get_candidate"

    if "weak_topic" not in state:
        return "select_weak_topic"

    if "questions" not in state:
        return "question_bank"

    if "selected_question" not in state:
        return "select_question"

    return "end"

# --------------------------------------------------
#  Dispatcher - Gets actual function names
# --------------------------------------------------

NODES = {
    "get_candidate":
        get_candidate_node,

    "select_weak_topic":
        select_weak_topic_node,

    "question_bank":
        question_bank_node,

    "select_question":
        select_question_node
}

# --------------------------------------------------
#  First State build
# --------------------------------------------------

state: InterviewState = {
    "candidate_id": "C101"
}

MAX_STEPS = 10
step = 0


while True:

    step += 1


    if step > MAX_STEPS:

        state["error"] = "Maximum steps exceeded."
        break


    next_node = route(state)


    print(
        f"\n========== "
        f"STEP {step} =========="
    )

    print("ROUTE:",next_node)


    if next_node == "end":
        break

    if next_node == "error":
        break

    node_function = NODES[next_node]

    update = node_function(state)

    print("UPDATE:",update)

    state.update(update)

print("\nFINAL STATE:")

print(state)

if state.get("error"):
    print("\nERROR:",state["error"])
else:
    print("\nINTERVIEW QUESTION:")

    print(state["selected_question"])