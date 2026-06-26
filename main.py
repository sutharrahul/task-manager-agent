from graph import app

user_input = input("📝 Ask for Task CRUD -> ")

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

print(f"📝 You Task Info -----> \n {result['response']}")
