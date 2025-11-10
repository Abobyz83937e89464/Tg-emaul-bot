from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import os
from supabase import create_client, Client
import asyncio
import random
from config import SUPABASE_URL, SUPABASE_KEY, BOT_TOKEN

# Инициализация Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# Инициализация Telegram бота
bot_app = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Добавляем пользователя в базу если его нет
    supabase.table('users').upsert({
        'telegram_id': user_id,
        'created_at': 'now()'
    }).execute()
    
    await update.message.reply_text(
        f"Добро пожаловать! Используйте /create_email для регистрации почты\n"
        f"CD: 2 часа между созданиями"
    )

async def create_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверяем CD
    user_data = supabase.table('users').select('*').eq('telegram_id', user_id).execute()
    if user_data.data:
        last_created = user_data.data[0].get('last_email_created')
        if last_created:
            # Логика проверки 2 часов CD
            pass
    
    await update.message.reply_text(
        "Выберите сервис для регистрации:\n"
        "• Outlook.com (без номера)\n"  
        "• Yahoo Mail (без номера)\n"
        "• Mail.com (без номера)\n"
        "• ProtonMail (без номера)"
    )

# Регистрируем обработчики
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("create_email", create_email))

@app.on_event("startup")
async def startup_event():
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()

@app.on_event("shutdown") 
async def shutdown_event():
    await bot_app.updater.stop()
    await bot_app.stop()
    await bot_app.shutdown()

@app.get("/")
async def root():
    return {"status": "Bot is running"}
