import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("KrasokAI.Config")

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    logger.info("Environment variables loaded from .env file.")
else:
    load_dotenv()
    logger.warning(".env file not found, loading from system environment variables.")

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

try:
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))
except ValueError:
    logger.warning("Invalid TEMPERATURE in .env, using default 0.3")
    TEMPERATURE = 0.3

try:
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1024"))
except ValueError:
    logger.warning("Invalid MAX_TOKENS in .env, using default 1024")
    MAX_TOKENS = 1024

KNOWLEDGE_BASE_PATH = BASE_DIR / "company_knowledge_base.txt"
KNOWLEDGE_BASE_CONTENT: str = ""

if KNOWLEDGE_BASE_PATH.exists():
    try:
        KNOWLEDGE_BASE_CONTENT = KNOWLEDGE_BASE_PATH.read_text(encoding="utf-8")
        logger.info(f"Successfully loaded company knowledge base from {KNOWLEDGE_BASE_PATH}.")
    except Exception as e:
        logger.critical(f"Failed to read company knowledge base: {e}")
        raise e
else:
    logger.critical(f"Company knowledge base file NOT found at {KNOWLEDGE_BASE_PATH}!")
    raise FileNotFoundError(f"Missing required knowledge base file: {KNOWLEDGE_BASE_PATH}")


def validate_config() -> bool:
    missing = []
    if not TELEGRAM_BOT_TOKEN or "YOUR_TELEGRAM_BOT_TOKEN" in TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not GROQ_API_KEY or "YOUR_GROQ_API_KEY" in GROQ_API_KEY:
        missing.append("GROQ_API_KEY")

    if missing:
        err_msg = f"Missing or placeholder configurations in environment: {', '.join(missing)}"
        logger.error(err_msg)
        return False
    
    logger.info("Configuration validation succeeded.")
    return True
