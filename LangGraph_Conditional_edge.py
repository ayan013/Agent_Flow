from typing import TypedDict,Literal
from langgraph.graph import StateGraph,START,END



# ==================================================
# STATE
# ==================================================

class InterviewState(TypedDict,total=False):

    candidate_id: str

    candidate_history: dict

    weak_topic: str

    questions: list[str]

    selected_question: str

    status: str

    error: str


# ==================================================
# APPLICATION FUNCTIONS
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


    return {
        "topic":
            topic,

        "questions":
            questions.get(
                topic,
                []
            )
    }


# ==================================================
# NODES
# ==================================================

def get_candidate_node(state: InterviewState) -> dict:

    print(
        "\nNODE: get_candidate"
    )


    history = get_candidate_history(
        state["candidate_id"]
    )


    if "error" in history:

        return {
            "error":
                history["error"]
        }


    return {
        "candidate_history":
            history
    }


def select_weak_topic_node(state: InterviewState) -> dict:

    print(
        "\nNODE: select_weak_topic"
    )


    weak_topics = state[
        "candidate_history"
    ].get(
        "weak_topics",
        []
    )


    if not weak_topics:

        return {
            "error":
                "No weak topics found"
        }


    return {
        "weak_topic":
            weak_topics[0]
    }


def question_bank_node(state: InterviewState) -> dict:

    print(
        "\nNODE: question_bank"
    )


    result = search_question_bank(state["weak_topic"])


    return {
        "questions":
            result["questions"]
    }


def select_question_node(state: InterviewState) -> dict:

    print(
        "\nNODE: select_question"
    )


    return {
        "selected_question":
            state["questions"][0],

        "status":
            "completed"
    }


def error_node(state: InterviewState) -> dict:

    print(
        "\nNODE: error_handler"
    )


    return {
        "status":
            "failed"
    }


# ==================================================
# ROUTER
# ==================================================

def route_after_candidate(state: InterviewState) -> Literal["continue","error"]:

    if state.get("error"):

        print(
            "\nROUTER: error"
        )

        return "error"


    print(
        "\nROUTER: continue"
    )

    return "continue"


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


builder.add_node(
    "error_handler",
    error_node
)


# ==================================================
# EDGES
# ==================================================

builder.add_edge(
    START,
    "get_candidate"
)


builder.add_conditional_edges(
    "get_candidate",

    route_after_candidate,

    {
        "continue":
            "select_weak_topic",

        "error":
            "error_handler"
    }
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


builder.add_edge(
    "error_handler",
    END
)


# ==================================================
# COMPILE
# ==================================================

graph = builder.compile()


# ==================================================
# RUN
# ==================================================

initial_state: InterviewState = {

    "candidate_id":
        "C102",

    "status":
        "running"
}


result = graph.invoke(initial_state)

# for update in graph.stream(
#     {
#         "candidate_id":
#             "C999",
#
#         "status":
#             "running"
#     },
#
#     stream_mode="updates"
# ):
#
#     print(
#         "\nGRAPH UPDATE:"
#     )
#
#     print(update)

print("\nFINAL STATE:")

print(result)