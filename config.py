import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Telegram Bot Credentials
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "")
    DB_NAME = os.getenv("DB_NAME", "deadpool_renamer_db")

    # Admin IDs (Supports multiple IDs separated by commas or a single ID)
    ADMIN_IDS = [int(admin_id.strip()) for admin_id in os.getenv("ADMIN_IDS", "").split(",") if admin_id.strip()]

    # Force Subscription Channels & Links
    CHANNEL_1_ID = int(os.getenv("CHANNEL_1_ID", "0"))
    CHANNEL_2_ID = int(os.getenv("CHANNEL_2_ID", "0"))
    CHANNEL_1_LINK = os.getenv("CHANNEL_1_LINK", "https://t.me/MrBossTG")
    CHANNEL_2_LINK = os.getenv("CHANNEL_2_LINK", "https://t.me/DeAdPoolKid")

    # Bot Support & Community Links
    SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/MrBossSupport")
    UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL", "https://t.me/MrBossTG")
    OWNER_USERNAME = os.getenv("OWNER_USERNAME", "@ItsPoolBoy")
