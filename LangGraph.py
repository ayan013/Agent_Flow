from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# ==================================================
# STATE
# ==================================================

class InterviewState(
    TypedDict,
    total=False
):
    candidate_id: str
    candidate_history: dict
    weak_topic: str
    questions: list[str]
    selected_question: str
    status: str
    error: str


# ==================================================
# NORMAL APPLICATION FUNCTIONS
# ==================================================

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

    return candidates.get(
        candidate_id,
        {
            "error":
                "Candidate not found"
        }
    )


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

    return { "topic":topic,"questions":questions.get(topic,[])}


# ==================================================
# GRAPH NODES
# ==================================================

def get_candidate_node(state: InterviewState) -> dict:

    print(
        "\nNODE: get_candidate"
    )

    history = get_candidate_history(
        state["candidate_id"]
    )

    return {"candidate_history":history}


def select_weak_topic_node(state: InterviewState) -> dict:

    print(
        "\nNODE: select_weak_topic"
    )

    weak_topics = state[
        "candidate_history"
    ]["weak_topics"]

    return {"weak_topic":weak_topics[0]}


def question_bank_node(state: InterviewState) -> dict:

    print(
        "\nNODE: question_bank"
    )

    result = search_question_bank(
        state["weak_topic"]
    )

    return {"questions":result["questions"]}


def select_question_node(state: InterviewState) -> dict:

    print("\nNODE: select_question")

    return {"selected_question":state["questions"][0],"status":"completed"}


# ==================================================
# BUILD GRAPH
# ==================================================

builder = StateGraph(InterviewState)


builder.add_node(
    "get_candidate",
    get_candidate_node
)


builder.add_node(
    "select_weak_topic",
    select_weak_topic_node
)


builder.add_node(
    "question_bank",
    question_bank_node
)


builder.add_node(
    "select_question",
    select_question_node
)


# ==================================================
# EDGES
# ==================================================

builder.add_edge(
    START,
    "get_candidate"
)


builder.add_edge(
    "get_candidate",
    "select_weak_topic"
)


builder.add_edge(
    "select_weak_topic",
    "question_bank"
)


builder.add_edge(
    "question_bank",
    "select_question"
)


builder.add_edge(
    "select_question",
    END
)


# ==================================================
# COMPILE
# ==================================================

graph = builder.compile()


# ==================================================
# RUN GRAPH
# ==================================================

initial_state: InterviewState = {
    "candidate_id":
        "C102",

    "status":
        "running"
}


result = graph.invoke(initial_state)

for update in graph.stream({"candidate_id": "C102","status": "running"},
    stream_mode="updates"
):
    print(
        "\nGRAPH UPDATE:"
    )

    print(update)

print("\nFINAL STATE:")
print(result)


print("\nINTERVIEW QUESTION:")
print(result["selected_question"])