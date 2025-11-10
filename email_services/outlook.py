import asyncio
import requests
import random
import string
import re

async def create_outlook_email():
    try:
        session = requests.Session()
        
        # Получаем токен
        response = session.get('https://signup.live.com/')
        if response.status_code != 200:
            return {"status": "error", "error": "Failed to get page"}
        
        # Ищем токен
        token_match = re.search(r'sCtx":"([^"]+)"', response.text)
        if not token_match:
            return {"status": "error", "error": "Token not found"}
        
        # Генерируем данные
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        email = f"{username}@outlook.com"
        password = f"Pass{random.randint(100000, 999999)}!"
        
        # Данные для регистрации
        data = {
            "SignUpOption": "Email",
            "Email": email,
            "Password": password,
            "FirstName": "User",
            "LastName": str(random.randint(1000, 9999)),
            "BirthDate": f"19{random.randint(80, 99)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "Country": "US",
            "PostalCode": str(random.randint(10000, 99999)),
            "Gender": random.choice(["1", "2"]),
            "MSAKe": "0",
            "scid": "100118"
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Отправляем запрос
        response = session.post(
            "https://signup.live.com/API/CreateAccount",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            return {
                "email": email,
                "password": password,
                "service": "outlook",
                "status": "success"
            }
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"status": "error", "error": str(e)}
