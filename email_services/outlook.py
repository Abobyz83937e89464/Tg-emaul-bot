import asyncio
import requests
import random
import string
import re

async def create_outlook_email():
    try:
        # Генерация данных
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%', k=14))
        email = f"{username}@outlook.com"
        
        # Сессия requests
        session = requests.Session()
        
        # Получаем начальную страницу
        response = session.get('https://signup.live.com/')
        
        # Ищем CSRF токен
        csrf_token = re.search(r'apiCanary":"([^"]+)"', response.text)
        if not csrf_token:
            return {"status": "error", "error": "CSRF token not found"}
        
        # Данные для регистрации
        data = {
            "SignUpOption": "Email",
            "Email": email,
            "Password": password,
            "FirstName": "John",
            "LastName": "Doe",
            "BirthDate": "1990-01-01",
            "Country": "US",
            "PostalCode": "10001",
            "Gender": "1",
            "MSAKe": "0",
            "CaptchaAnswer": "",
            "Proofs": [],
            "uaid": "",
            "scid": "100118",
            "hpgid": "200110"
        }
        
        # Отправляем запрос регистрации
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
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
            return {
                "status": "error", 
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {"status": "error", "error": str(e)}
