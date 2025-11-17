import logging
from pyrogram import Client
from telegram.ext import Application

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

from shivu.config import Development as Config

api_id = Config.api_id
api_hash = Config.api_hash
TOKEN = Config.TOKEN
GROUP_ID = Config.GROUP_ID
CHARA_CHANNEL_ID = Config.CHARA_CHANNEL_ID
PHOTO_URL = Config.PHOTO_URL
SUPPORT_CHAT = Config.SUPPORT_CHAT
UPDATE_CHAT = Config.UPDATE_CHAT
BOT_USERNAME = Config.BOT_USERNAME
sudo_users = Config.sudo_users
OWNER_ID = Config.OWNER_ID

# Telegram Bot applications
application = Application.builder().token(TOKEN).build()
shivuu = Client("Shivu", api_id, api_hash, bot_token=TOKEN)

# ----- In-memory replacements for MongoDB collections -----
collection = {}  # anime characters {id: character_dict}
user_totals_collection = {}  # {chat_id: {"message_frequency": int, ...}}
user_collection = {}  # {user_id: {"characters": [character_dicts], ...}}
group_user_totals_collection = {}  # {group_id: {user_id: total}}
top_global_groups_collection = {}  # {group_id: total_guesses}
pm_users = {}  # {user_id: {"first_name": str, "username": str}}
