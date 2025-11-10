import asyncio
from playwright.async_api import async_playwright
import random
import string

async def create_outlook_email():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Генерация случайных данных
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%', k=16))
        email = f"{username}@outlook.com"
        
        try:
            # Симуляция человеческого поведения с задержками
            await page.goto("https://signup.live.com/")
            await asyncio.sleep(random.uniform(2, 4))
            
            # Заполнение формы с паузами
            await page.fill('[name="Email"]', email)
            await asyncio.sleep(random.uniform(1, 2))
            
            await page.click('[type="submit"]')
            await asyncio.sleep(random.uniform(3, 5))
            
            # Дальнейшие шаги регистрации...
            
            await browser.close()
            return {"email": email, "password": password, "status": "success"}
            
        except Exception as e:
            await browser.close()
            return {"email": email, "password": password, "status": "error", "error": str(e)}
