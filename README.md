# Pachico

Pachico is the ultimate AI nutrition coach built with LangGraph. You can either use it via telegram, CLI or browser. 
Pachico Capabilities:
- Food logs
- Food tracking
- Real nutrion data via USDA API integration
- Generation of charts
- constant memory
- Recipes 
- Data exports
- Goals definition

## Architecture

```
User (Telegram / Browser)
        │
        ▼
   FastAPI (:8000)
   POST /api/chat
        │
        ▼
  ┌─ LangGraph Router ──────────────────┐
  │                                      │
  │  "I ate a chicken burrito"           │
  │       → food_entry subgraph          │
  │                                      │
  │  "How many calories today?"          │
  │       → data_review subgraph         │
  │                                      │
  │  "Show me a protein chart this week" │
  │       → chart subgraph               │
  │                                      │
  │  "What's a good high-protein snack?" │
  │       → chatbot (general)            │
  └──────────────────────────────────────┘
        │
        ▼
   PostgreSQL (food_db)
   SQLite (agent checkpoints)
```

**Router**: Uses structured output (Instructor + JSON mode) to classify every message into one of four paths.

**Checkpointer**: LangGraph's checkpointer maintains the thread so the bot knows it's you and remembers what you ate this morning.


## Core Features

### (A) Food Logging

- User describes what they ate in plain text.
- The agent searches USDA FoodData Central for matches.
- It presents the nutritional data and asks for confirmation.
- Only after confirmation does it save to PostgreSQL.
- If USDA has no match, the LLM estimates (marked as `source: llm_estimation`).

### (B) Data Review

- Query your food log with filters: date range, meal type, food keyword.
- Get summaries: "How many calories did I eat today?"
- Export to CSV for spreadsheet nerds.

### (C) Chart Generation

- Request charts for any macro: calories, protein, fat, carbs.
- Weekly or monthly time periods.
- Generated with matplotlib, returned as PNG images.

### (D) General Chat

- Anything that doesn't fit the above routes to a general chatbot.
- Recipe ideas, nutrition questions, meal planning.


## Tools

The agent has 5 tools:

| Tool | What it does |
|------|-------------|
| `search_usda_foods` | Search USDA FoodData Central by query |
| `save_food_to_db` | Save a confirmed food entry to PostgreSQL |
| `query_food_entries` | Query food log with filters (date, meal type, keyword) |
| `export_food_csv` | Export filtered entries to CSV file |
| `generate_nutrition_chart` | Generate PNG chart for a macro over a time period |


## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Framework | LangGraph |
| LLM | Grok 4 Fast via OpenRouter |
| Structured Output | Instructor (JSON mode) |
| Data Source | USDA FoodData Central API |
| Database | PostgreSQL + SQLAlchemy ORM + Alembic |
| Backend | FastAPI + Uvicorn |
| Frontend (Web) | Next.js + Tailwind CSS |
| Frontend (Telegram) | python-telegram-bot |
| Charts | matplotlib |
| Package Manager | uv |


## Project Structure

```
Pachico/
├── App/
│   ├── MyAgent/
│   │   ├── clients/
│   │   │   ├── model.py              # LLM client (OpenRouter)
│   │   │   └── usda_api.py           # USDA FoodData Central client
│   │   ├── utils/
│   │   │   ├── nodes.py              # Router, chatbot, picker nodes
│   │   │   ├── state.py              # Agent state & router schema
│   │   │   ├── tools.py              # 5 tool definitions
│   │   │   ├── subgraph.py           # Food entry subgraph
│   │   │   ├── data_review_subgraph.py
│   │   │   ├── chart_subgraph.py
│   │   │   └── checkpointer.py
│   │   └── graph.py                  # Main graph definition
│   ├── api/
│   │   ├── __init__.py               # FastAPI app + CORS + Telegram lifecycle
│   │   └── routes.py                 # POST /api/chat
│   ├── bot/
│   │   └── telegram_bot.py           # Telegram handlers
│   ├── database/
│   │   ├── models.py                 # FoodEntry model
│   │   └── session.py                # DB session manager
│   ├── service/
│   │   └── agent_service.py          # Agent invocation layer
│   ├── cli/
│   │   └── cli.py                    # Terminal interface
│   ├── web/                           # Next.js frontend
│   │   ├── src/
│   │   │   ├── components/            # Chat UI components
│   │   │   ├── hooks/                 # useConversations, useChat
│   │   │   └── lib/                   # API client, types, storage
│   │   └── Dockerfile
│   └── config.py                      # Environment config (dev/test/prod)
├── alembic/                           # Database migrations
├── main.py                            # Entry point
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```


## Setup

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- Node.js 22+ (for the web frontend)
- PostgreSQL (or use Docker)

### 1. Clone & Install

```bash
git clone https://github.com/David-J3R/Pachico.git
cd Pachico
uv sync
```

### 2. Environment Variables

Create a `.env` file in the project root:

```
ENV_STATE=dev

DEV_OPENROUTER_API_KEY=your-openrouter-key
DEV_USDA_API_KEY=your-usda-key
DEV_TELEGRAM_BOT_TOKEN=your-telegram-bot-token

DEV_POSTGRE_USER=pachico
DEV_POSTGRE_PASSWORD=your-password
DEV_POSTGRE_NAME=food_db
DEV_POSTGRE_HOST=127.0.0.1
DEV_POSTGRE_PORT=5432
```

Get your keys:
- **OpenRouter**: https://openrouter.ai/keys
- **USDA**: https://fdc.nal.usda.gov/api-key-signup
- **Telegram**: Talk to [@BotFather](https://t.me/BotFather)

### 3. Database

```bash
uv run alembic upgrade head
```

### 4. Run

```bash
# API server + Telegram bot
uv run python main.py

# Web frontend (separate terminal)
cd App/web
npm install
npm run dev
```

- **Browser**: http://localhost:3000
- **Telegram**: Message your bot
- **CLI**: `uv run python main.py cli`


## Docker

Run the entire stack with one command:

```bash
docker compose up --build
```

This starts:
- **PostgreSQL** — `food_db` database
- **Backend** — FastAPI + Telegram bot on `:8000`
- **Frontend** — Next.js on `:3000`

Both Telegram and browser work simultaneously. The `.env` file provides all secrets at runtime — nothing is baked into the images.


## API

Single endpoint:

```
POST /api/chat
```

Request:
```json
{
  "message": "I ate 2 scrambled eggs for breakfast",
  "thread_id": "some-uuid"
}
```

Response:
```json
{
  "text": "I found scrambled eggs in the USDA database...",
  "file_paths": []
}
```

Exported charts and CSVs are served at `/exports/<filename>`.


## Risks & Design Decisions

### (A) The "Vision" Trap

- **The Problem**: You send a picture of a burrito. The best Vision model sees a burrito. It does not see the 2 tablespoons of lard inside the beans or the extra cheese hidden under the salsa. Vision models are notoriously bad at volumetric estimation. They can identify what food it is, but rarely how much it weighs.
- **Current Status**: Photo-based logging is not yet implemented. When it is, it will use a Human-in-the-Loop node: Image → Estimate → Pause → "I see a chicken burrito. Is this small (300g) or large (600g)?" → User replies → Save.

### (B) The "Context Window" Bottleneck

- **The Problem**: You want the AI to analyze "monthly progress." If you feed 30 days x 3 meals x 5 ingredients into the LLM context window every time, you burn through tokens and hit latency limits. LLMs are also terrible at calculating averages over long lists of numbers.
- **Solution**: The agent doesn't do math. It has SQL tools. It queries PostgreSQL directly: `SELECT SUM(calories) FROM food_entries WHERE created_at > '2026-02-01'`. The LLM writes the query, the tool executes it, the LLM formats the result.

### (C) USDA First, LLM Second

- Every food entry is searched against the USDA FoodData Central database first.
- The LLM's internal knowledge is a fallback of last resort.
- When the LLM does estimate, it's marked as `source: llm_estimation` so you know the confidence level.

### (D) Structured Output is Mandatory

- The LLM doesn't "chat" about calories. It outputs structured JSON.
- The router uses Instructor to force classification into exactly one of four paths.
- Food entries are validated through Pydantic before hitting the database.
