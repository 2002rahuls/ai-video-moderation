from dotenv import load_dotenv
load_dotenv()   # loads .env into environment
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# --- OpenAI ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- Video Processing ---
FRAME_INTERVAL = float(os.getenv("FRAME_INTERVAL", 0.1))  # every 10s
MAX_FRAMES = int(os.getenv("MAX_FRAMES", 30))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", 45))

# --- Batch Processing ---
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 8))

# --- Firebase ---
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
