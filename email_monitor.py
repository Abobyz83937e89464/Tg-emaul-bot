import asyncio
import aiohttp
import imaplib
import email
from email.header import decode_header
from config import BOT_TOKEN
from telegram import Bot
from database.db import Database

bot = Bot(token=BOT_TOKEN)
db = Database()

async def check_email_inbox(email_address, password):
    try:
        # Подключаемся к IMAP Outlook
        mail = imaplib.IMAP4_SSL("outlook.office365.com", 993)
        mail.login(email_address, password)
        mail.select("inbox")
        
        # Ищем непрочитанные письма
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        
        emails_data = []
        
        for e_id in email_ids:
            _, msg_data = mail.fetch(e_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Получаем информацию о письме
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
                
            from_email = msg["From"]
            
            # Извлекаем текст письма
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')
            
            emails_data.append({
                "subject": subject,
                "from": from_email,
                "body": body[:1000]  # Ограничиваем длину
            })
        
        mail.close()
        mail.logout()
        return emails_data
        
    except Exception as e:
        print(f"❌ Ошибка проверки почты {email_address}: {str(e)}")
        return []

async def monitor_all_emails():
    print("🚀 Монитор почты запущен")
    
    while True:
        try:
            # Получаем все почты из базы
            emails_data = db.get_all_emails()
            
            for email_acc in emails_data:
                email_address = email_acc['email']
                user_id = email_acc['user_id']
                password = email_acc.get('password', 'TempPass123!')
                
                # Проверяем входящие письма
                new_emails = await check_email_inbox(email_address, password)
                
                for email_msg in new_emails:
                    # Находим пользователя
                    user = db.get_user_by_id(user_id)
                    if user:
                        telegram_id = user['telegram_id']
                        
                        # Отправляем письмо в бота
                        await bot.send_message(
                            chat_id=telegram_id,
                            text=f"📧 Новое письмо для {email_address}\n\n"
                                 f"📨 От: {email_msg['from']}\n"
                                 f"📋 Тема: {email_msg['subject']}\n"
                                 f"📝 Текст: {email_msg['body'][:500]}..."
                        )
            
            # Проверяем каждые 60 секунд
            await asyncio.sleep(60)
            
        except Exception as e:
            print(f"❌ Ошибка монитора: {str(e)}")
            await asyncio.sleep(120)
