from dotenv import load_dotenv
load_dotenv()

import os

MODEL_NAME = "gemini-2.0-flash"
APP_NAME = "transaction_status_agent"
DEFAULT_USER_ID = "user_12345"
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

