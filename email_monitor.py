import asyncio
import random
from config import BOT_TOKEN
from telegram import Bot
from database.db import Database

bot = Bot(token=BOT_TOKEN)
db = Database()

async def monitor_all_emails():
    print("🚀 Монитор почты запущен")
    while True:
        try:
            emails = db.get_all_emails()
            for email_acc in emails:
                user = db.get_user_by_id(email_acc['user_id'])
                if user:
                    # Тестовое сообщение
                    await bot.send_message(
                        chat_id=user['telegram_id'],
                        text=f"📧 Тестовое уведомление для {email_acc['email']}\nМонитор работает!"
                    )
            
            await asyncio.sleep(60)
            
        except Exception as e:
            print(f"Ошибка: {e}")
            await asyncio.sleep(30)
