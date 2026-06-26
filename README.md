# 📝 Task Manager Agent

A conversational **Task Manager** powered by a local LLM (via [Ollama](https://ollama.com/)) and orchestrated with [LangGraph](https://langchain-ai.github.io/langgraph/).

You talk to it in plain English — _"add a task to buy milk"_, _"show me all pending tasks"_, _"mark buy milk as completed"_ — and the agent figures out your intent, runs the right database operation, and replies in natural language.

It uses **PostgreSQL** for task storage and **Redis** as a response cache so repeated questions return instantly.

---

## ✨ Features

- 🗣️ **Natural-language CRUD** — create, view, update, check, and delete tasks by chatting.
- 🧠 **Intent extraction** — an LLM converts your message into structured `{ intent, title, status }` JSON.
- 🤖 **Friendly responses** — a second LLM pass ("Leo") turns raw DB results into human-friendly replies.
- ⚡ **Redis caching** — identical requests are served straight from cache, skipping the LLM and DB.
- 🔀 **LangGraph state machine** — clear, node-based flow that's easy to extend.

---

## 🏗️ Architecture

The app is a LangGraph state machine. Each request flows through these nodes:

```
          ┌──────────────┐
START ──▶ │ check_cache  │
          └──────┬───────┘
                 │
        cache hit? ──────────────▶ END   (return cached response)
                 │ no
                 ▼
        ┌─────────────────┐
        │ get_user_intent │   LLM → { intent, title, status }
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │  intent_query   │   run matching DB operation
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │    chat_bot     │   LLM → friendly natural reply
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │   save_cache    │   store response in Redis
        └────────┬────────┘
                 ▼
                END
```

### Files

| File | Responsibility |
|------|----------------|
| `main.py` | Entry point — reads user input and invokes the graph. |
| `graph.py` | Defines the `AgentState`, all nodes, and wires the LangGraph state machine. |
| `db.py` | PostgreSQL connection + table/enum creation (`task_manager` table). |
| `db_query.py` | CRUD query functions (add, get, update, delete, check status). |
| `cache.py` | Redis `get_cache` / `set_cache` helpers. |
| `system_prompt.py` | The intent-extraction prompt and the "Leo" response prompt. |
| `.env` | `POSTGRES_DB_URL` connection string (git-ignored). |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **PostgreSQL** database (a connection URL — local or hosted)
- **Redis** running on `localhost:6379`
- **Ollama** with the `gemma3:4b` model pulled

### 1. Install dependencies

```bash
pip install redis psycopg2-binary python-dotenv langgraph langchain-ollama typing_extensions
```

### 2. Start Ollama and pull the model

```bash
ollama pull gemma3:4b
```

### 3. Start Redis

```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis

# ...or via Homebrew
brew services start redis
```

Verify it's reachable:

```bash
redis-cli ping        # → PONG
# or, if Redis runs in Docker:
docker exec -it redis redis-cli ping
```

### 4. Configure the database

Create a `.env` file in the project root:

```env
POSTGRES_DB_URL="postgres://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require"
```

The `task_manager` table and `task_status` enum are created automatically the first time `db.py` is imported.

### 5. Run the agent

```bash
python main.py
```

```
📝 Ask for Task CRUD -> add a task to buy milk
📝 You Task Info ----->
 Your task has been added successfully.
```

---

## 💬 Example Prompts

| You say | Intent | What happens |
|---------|--------|--------------|
| `add a task to buy milk` | `add_task` | Inserts a new task. |
| `show me all my tasks` | `get_all_tasks` | Lists every task. |
| `what are my pending tasks?` | `get_all_task_with_status` | Filters by status. |
| `is buy milk done?` | `check_task_status` | Returns that task's status. |
| `mark buy milk as completed` | `update_task` | Updates the task status. |
| `delete buy milk` | `delete_task` | Removes the task. |
| `hi` / `what can you do?` / `what's your name?` | `greeting` / `capability` / `bot_name` | Conversational replies. |

---

## 🗄️ Data Model

```sql
CREATE TYPE task_status AS ENUM ('pending', 'ongoing', 'completed');

CREATE TABLE task_manager (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(255) NOT NULL,
    status     VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 Configuration Notes

- **LLM model** — change `gemma3:4b` in `graph.py` to any model available in your Ollama install.
- **Redis** — host/port are set in `cache.py` (`localhost:6379`).
- **Cache key** — the raw user input string is used as the cache key, so wording must match exactly for a cache hit.

---

## ⚠️ Security

Keep your real `POSTGRES_DB_URL` out of version control — `.env` is already listed in `.gitignore`. If credentials were ever committed, rotate them.

---

## 🛠️ Tech Stack

- **LangGraph** — agent orchestration
- **LangChain + Ollama** (`gemma3:4b`) — local LLM inference
- **PostgreSQL** (`psycopg2`) — task storage
- **Redis** — response caching
- **python-dotenv** — environment configuration
