import asyncio
import aiohttp
import random
import string
import re

async def create_outlook_email():
    try:
        # Генерируем данные
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        password = f"Pass{random.randint(100000, 999999)}!"
        email = f"{username}@outlook.com"
        
        print(f"🔄 Пытаюсь зарегистрировать: {email}")
        
        async with aiohttp.ClientSession() as session:
            # 1. Получаем страницу регистрации
            async with session.get('https://signup.live.com/') as response:
                html = await response.text()
                
            # 2. Ищем токены
            flow_token = re.search(r'flowToken":"([^"]+)"', html)
            api_canary = re.search(r'apiCanary":"([^"]+)"', html)
            
            if not flow_token or not api_canary:
                return {"status": "error", "error": "Не найдены токены"}
            
            # 3. Отправляем данные регистрации
            data = {
                "username": email,
                "password": password,
                "firstName": "User",
                "lastName": str(random.randint(1000, 9999)),
                "birthDate": f"19{random.randint(80, 99)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "country": "US",
                "postalCode": str(random.randint(10000, 99999)),
                "gender": random.choice(["1", "2"]),
                "flowToken": flow_token.group(1),
                "uaid": "",
                "Proofs": []
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "canary": api_canary.group(1)
            }
            
            async with session.post(
                "https://signup.live.com/API/InternalCreateAccount",
                json=data,
                headers=headers
            ) as response:
                result = await response.json()
                
                if response.status == 200 and result.get("success"):
                    return {
                        "email": email,
                        "password": password,
                        "service": "outlook",
                        "status": "success"
                    }
                else:
                    return {"status": "error", "error": result.get("error", "Unknown error")}
                    
    except Exception as e:
        return {"status": "error", "error": str(e)}
