from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import os
from supabase import create_client, Client
import asyncio
import random
from datetime import datetime, timedelta
from config import SUPABASE_URL, SUPABASE_KEY, BOT_TOKEN

# Импорты сервисов почт
from email_services.outlook import create_outlook_email
from email_services.yahoo import create_yahoo_email
from email_services.mailcom import create_mailcom_email
from email_services.protonmail import create_protonmail_email

# Инициализация Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# Инициализация Telegram бота
bot_app = Application.builder().token(BOT_TOKEN).build()

# Словарь сервисов
EMAIL_SERVICES = {
    'outlook': create_outlook_email,
    'yahoo': create_yahoo_email, 
    'mailcom': create_mailcom_email,
    'protonmail': create_protonmail_email
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Добавляем пользователя в базу если его нет
    supabase.table('users').upsert({
        'telegram_id': user_id,
        'created_at': 'now()'
    }).execute()
    
    await update.message.reply_text(
        f"🤖 Бот для регистрации почт\n\n"
        f"Используйте /create_email для создания почты\n"
        f"CD: 2 часа между регистрациями\n\n"
        f"Доступные сервисы:\n"
        f"• Outlook.com (без номера)\n"  
        f"• Yahoo Mail (без номера)\n"
        f"• Mail.com (без номера)\n"
        f"• ProtonMail (без номера)"
    )

async def create_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Проверяем CD
    user_data = supabase.table('users').select('*').eq('telegram_id', user_id).execute()
    
    if user_data.data:
        user = user_data.data[0]
        if user.get('last_email_created'):
            last_created = datetime.fromisoformat(user['last_email_created'].replace('Z', '+00:00'))
            if datetime.now().astimezone() - last_created < timedelta(hours=2):
                await update.message.reply_text("❌ CD не прошел. Ждите 2 часа между созданиями.")
                return
    
    # Выбор сервиса
    service_keys = list(EMAIL_SERVICES.keys())
    service = random.choice(service_keys)
    
    await update.message.reply_text(f"🔄 Начинаю регистрацию {service}...")
    
    try:
        # Создаем почту
        result = await EMAIL_SERVICES[service]()
        
        if result['status'] == 'success':
            # Сохраняем в базу
            email_data = {
                'user_id': user['id'],
                'email_service': service,
                'email': result['email'],
                'password': result['password']
            }
            supabase.table('email_accounts').insert(email_data).execute()
            
            # Обновляем время последней регистрации
            supabase.table('users').update({
                'last_email_created': datetime.now().isoformat()
            }).eq('telegram_id', user_id).execute()
            
            await update.message.reply_text(
                f"✅ Почта создана!\n\n"
                f"Сервис: {service}\n"
                f"Email: {result['email']}\n"
                f"Password: {result['password']}\n\n"
                f"Следующая регистрация через 2 часа"
            )
        else:
            await update.message.reply_text(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при регистрации: {str(e)}")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
