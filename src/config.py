import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class Config:
    
    STEAM_API_KEY = os.getenv("STEAM_API_KEY", "")
    STEAM_API_DELAY = float(os.getenv("STEAM_API_DELAY", "1.5"))
    
    STEAM_STORE_API = "https://store.steampowered.com/api/"
    STEAM_APP_DETAILS = f"{STEAM_STORE_API}appdetails"
    STEAM_SEARCH_URL = "https://store.steampowered.com/search/"
    
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
    DEFAULT_PAGES = int(os.getenv("DEFAULT_PAGES", "3"))
    MAX_RETRIES = 3
    
    OUTPUT_DIR = Path(__file__).parent.parent / "output"
    
    @classmethod
    def validate(cls):
        if not cls.STEAM_API_KEY or cls.STEAM_API_KEY == "YOUR_API_KEY_HERE":
            raise ValueError(
                "❌ STEAM_API_KEY не найден!\n"
                "1. Создай файл .env в корне проекта\n"
                "2. Добавь туда: STEAM_API_KEY=твой_ключ\n"
                "3. Ключ можно получить на https://steamcommunity.com/dev/apikey"
            )
        return True
    
    @classmethod
    def ensure_output_dir(cls):
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        return cls.OUTPUT_DIR