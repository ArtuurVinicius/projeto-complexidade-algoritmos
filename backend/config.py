from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
GRAPHS_STORE = BASE_DIR / 'graphs_store'
DB_PATH = GRAPHS_STORE / 'graphs.db'

# Ensure store directory exists
GRAPHS_STORE.mkdir(parents=True, exist_ok=True)
