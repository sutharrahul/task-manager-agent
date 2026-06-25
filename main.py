import redis
from typing_extensions import TypedDict
from db_query import (
    add_task,
    get_all_taks,
    get_all_task_with_status,
    check_task_status,
    delete_task,
    update_task,
)
from system_prompt import INTENT_SYSTEM_PROMPT, SYSTEM_PROMPT

r = redis.Redis(host="localhost", port=6367, db=0, decode_responses=True)


class AgentState(TypedDict):
    user_input: str
    history: list
    extract_data: dict
    db_result: any
    response: str
    intent: str
    title: str
    status: str
    cache: bool


user_input = input("📝 Ask for Task CRUD -> ")


# cache node
def pre_input_result(state: AgentState):
    res = r.get(state["user_input"])

    if res:
        state["response"] = res
        state["cache"] = True
    else:
        state["cache"] = False

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
        state["db_result"] == "bot_name"
    else:
        state["db_result"] == "unsupported"

    return state

