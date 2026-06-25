import redis
from typing_extensions import TypedDict
from langchain_ollama import ChatOllama
from db_query import (
    add_task,
    get_all_taks,
    get_all_task_with_status,
    check_task_status,
    delete_task,
    update_task,
)
from system_prompt import INTENT_SYSTEM_PROMPT, SYSTEM_PROMPT
import json
from langgraph.graph import StateGraph, START, END

r = redis.Redis(host="localhost", port=6367, db=0, decode_responses=True)


class AgentState(TypedDict):
    user_input: str
    extract_data: dict
    db_result: any
    response: any
    intent: str
    title: str
    status: str
    cache: bool


user_input = input("📝 Ask for Task CRUD -> ")


# cache node
def check_cache(state: AgentState):
    res = r.get(state["user_input"])

    if res:
        state["response"] = res
        state["cache"] = True
    else:
        state["cache"] = False

    return state


# get intent from LLM


def get_user_intent(state: AgentState):
    res_llm = ChatOllama(model="gemma3:4b")

    message = [("system", INTENT_SYSTEM_PROMPT), ("user", state["user_search"])]

    response = res_llm.invoke(message)
    data = json.loads(response.content)

    state["intent"] = data.get("intent")
    state["title"] = data.get("title")
    state["status"] = data.get("status")

    return state


# db node
def intent_query(state: AgentState):
    intent = state["intent"]

    if intent == "add_task":
        state["db_result"] = add_task(state["title"])
    elif intent == "get_all_taks":
        state["db_result"] = get_all_taks()
    elif intent == "get_all_task_with_status":
        state["db_result"] = get_all_task_with_status(state["status"])
    elif intent == "check_task_status":
        state["db_result"] = check_task_status(state["title"])
    elif intent == "delete_task":
        state["db_result"] = delete_task(state["title"], state["status"])
    elif intent == "update_task":
        state["db_result"] = update_task(state["title"], state["status"])
    elif intent == "greeting":
        state["db_result"] = "greeting"
    elif intent == "capability":
        state["db_result"] = "capability"
    elif intent == "bot_name":
        state["db_result"] = "bot_name"
    else:
        state["db_result"] = "unsupported"

    return state


def chat_bot(state: AgentState):
    llm = ChatOllama(model="gemma3:4b")

    message = [
        ("system", SYSTEM_PROMPT),
        (
            "user",
            f"User request{state['user_input']} \n DB Result {state['db_result']}",
        ),
    ]

    response = llm.invoke(message)

    state["response"] = response.content

    return state


def save_cache(state: AgentState):
    r.set(state["user_input"], state["response"])
    return state


def evaluate_response(state: AgentState):
    if state["cache"]:
        return END
    else:
        return "get_user_intent"


graph_builder = StateGraph(AgentState)

graph_builder.add_node("check_cache", check_cache)
graph_builder.add_node("get_user_intent", get_user_intent)
graph_builder.add_node("intent_query", intent_query)
graph_builder.add_node("chat_bot", chat_bot)
graph_builder.add_node("save_cache", save_cache)

graph_builder.add_edge(START, "check_cache")
graph_builder.add_conditional_edges("check_cache", evaluate_response)
graph_builder.add_edge("get_user_intent", "intent_query")
graph_builder.add_edge("intent_query", "chat_bot")
graph_builder.add_edge("chat_bot", END)

app = graph_builder.compile()

result = app.invoke(
    {
        "user_input": user_input,
        "db_result": None,
        "extract_data": None,
        "intent": None,
        "response": None,
        "status": None,
        "title": None,
        "cache": False,
    }
)

print(f"📝 You Task Info -----> \n {result["response"]}")
