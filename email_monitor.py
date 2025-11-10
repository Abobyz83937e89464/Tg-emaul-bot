import asyncio
from config import BOT_TOKEN
from telegram import Bot
from database.db import Database

bot = Bot(token=BOT_TOKEN)
db = Database()

async def monitor_all_emails():
    print("🚀 Монитор почты запущен")
    while True:
        try:
            await asyncio.sleep(300)  # Проверяем раз в 5 минут
        except Exception as e:
            print(f"Ошибка: {e}")
            await asyncio.sleep(60)
