import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver

DB_PATH = "agent_checkpoints.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

memory = SqliteSaver(conn)
