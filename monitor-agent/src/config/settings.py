import os
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:3000")
API_KEY = os.getenv("API_KEY", "default-agent-key")
AGENT_NAME = os.getenv("AGENT_NAME", "unknown-agent")
COLLECT_INTERVAL = int(os.getenv("COLLECT_INTERVAL", "10"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
