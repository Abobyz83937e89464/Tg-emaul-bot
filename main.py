from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import random
from datetime import datetime, timedelta
from config import SUPABASE_URL, SUPABASE_KEY, BOT_TOKEN
from supabase import create_client
from sms_monitor import monitor_all_emails

from email_services.outlook import create_outlook_email
from email_services.yahoo import create_yahoo_email
from email_services.mailcom import create_mailcom_email
from email_services.protonmail import create_protonmail_email

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
app = FastAPI()
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

EMAIL_SERVICES = {
    'outlook': create_outlook_email,
    'yahoo': create_yahoo_email, 
    'mailcom': create_mailcom_email,
    'protonmail': create_protonmail_email
}

async def set_commands():
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("create_email", "Создать почту"),
    ]
    await bot_app.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    supabase.table('users').upsert({'telegram_id': user_id, 'created_at': 'now()'}).execute()
    
    web_app_button = KeyboardButton(
        text="📱 Открыть приложение",
        web_app=WebAppInfo(url="https://tg-emaul-bot.onrender.com/webapp")
    )
    reply_markup = ReplyKeyboardMarkup([[web_app_button]], resize_keyboard=True)
    
    await update.message.reply_text(
        "🤖 Бот для регистрации почт\n\n"
        "Нажми кнопку ниже или используй /create_email\n"
        "Все SMS с почт будут приходить сюда",
        reply_markup=reply_markup
    )

async def create_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = supabase.table('users').select('*').eq('telegram_id', user_id).execute()
    
    if user_data.data:
        user = user_data.data[0]
        if user.get('last_email_created'):
            last_created = datetime.fromisoformat(user['last_email_created'].replace('Z', '+00:00'))
            if datetime.now().astimezone() - last_created < timedelta(hours=2):
                await update.message.reply_text("❌ CD не прошел. Ждите 2 часа.")
                return
    
    service = 'outlook'
    await update.message.reply_text(f"🔄 Начинаю регистрацию {service}...")
    
    try:
        result = await EMAIL_SERVICES[service]()
        if result['status'] == 'success':
            email_data = {
                'user_id': user['id'],
                'email_service': service,
                'email': result['email']
            }
            supabase.table('email_accounts').insert(email_data).execute()
            supabase.table('users').update({'last_email_created': datetime.now().isoformat()}).eq('telegram_id', user_id).execute()
            
            await update.message.reply_text(
                f"✅ Почта создана!\n\n"
                f"Email: {result['email']}\n\n"
                f"Все SMS с этой почты будут приходить сюда\n"
                f"Следующая регистрация через 2 часа"
            )
        else:
            await update.message.reply_text(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при регистрации: {str(e)}")

@app.get("/webapp")
async def webapp():
    return FileResponse("static/index.html")

@app.post("/create_email")
async def web_create_email(request: Request):
    return {"success": True, "email": "test@outlook.com"}

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("create_email", create_email))
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    await set_commands()
    asyncio.create_task(monitor_all_emails())

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
