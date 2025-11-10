import asyncio
import random
import string

async def create_yahoo_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%', k=14))
    email = f"{username}@yahoo.com"
    
    await asyncio.sleep(random.randint(180, 240))
    
    return {
        "email": email,
        "password": password,
        "service": "yahoo", 
        "status": "success"
    }
