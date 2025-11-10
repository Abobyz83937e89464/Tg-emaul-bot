from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
from datetime import datetime, timedelta
from config import BOT_TOKEN
from database.db import Database
from email_monitor import monitor_all_emails
from email_services.outlook import create_outlook_email

db = Database()
app = FastAPI()
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def set_commands():
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("create_email", "Создать почту"),
    ]
    await bot_app.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not db.get_user(user_id):
        db.insert_user(user_id)
    
    web_app_button = KeyboardButton(
        text="📱 Открыть приложение",
        web_app=WebAppInfo(url="https://tg-emaul-bot-11.onrender.com/webapp")
    )
    reply_markup = ReplyKeyboardMarkup([[web_app_button]], resize_keyboard=True)
    
    await update.message.reply_text(
        "🤖 Бот для регистрации почт\n\nНажми кнопку ниже или используй /create_email",
        reply_markup=reply_markup
    )

async def create_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        db.insert_user(user_id)
        user = db.get_user(user_id)
    
    # Проверяем CD
    if user.get('last_email_created'):
        last_created = datetime.fromisoformat(user['last_email_created'].replace('Z', '+00:00'))
        time_diff = datetime.now().astimezone() - last_created
        if time_diff.total_seconds() < 7200:
            remaining = 7200 - int(time_diff.total_seconds())
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            await update.message.reply_text(f"❌ CD не прошел. Ждите еще {hours}ч {minutes}м.")
            return
    
    await update.message.reply_text("🔄 Начинаю реальную регистрацию Outlook...")
    
    try:
        result = await create_outlook_email()
        if result['status'] == 'success':
            db.insert_email(user['id'], result['email'], 'outlook')
            db.update_user_last_email(user_id)
            
            await update.message.reply_text(
                f"✅ Реальная почта создана!\n\n"
                f"Email: {result['email']}\n"
                f"Password: {result['password']}\n\n"
                f"Следующая регистрация через 2 часа"
            )
        else:
            await update.message.reply_text(f"❌ Ошибка: {result.get('error')}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

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
