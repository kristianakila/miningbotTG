from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
import dotenv
import os

dotenv.load_dotenv(".env")

TON_API_KEY = os.getenv("TON_API_KEY")
TONCENTER_API_KEY = os.getenv("TONCENTER_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
WITHDRAW_ADDRESS_MNEMONIC = os.getenv("WITHDRAW_ADDRESS_MNEMONIC").split(" ")
WITHDRAW_ADDRESS = os.getenv("WITHDRAW_ADDRESS")
bull_MASTER_ADDRESS = os.getenv("bull_MASTER_ADDRESS")
MIN_WITHDRAW_bull = float(os.getenv("MIN_WITHDRAW_bull"))
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML", link_preview_show_above_text=False),
)
admin_list = [6422235070, 6847407378, 545921]
