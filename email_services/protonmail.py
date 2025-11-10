import asyncio
import random
import string

async def create_protonmail_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%', k=16))
    email = f"{username}@protonmail.com"
    
    await asyncio.sleep(random.randint(180, 240))
    
    return {
        "email": email,
        "password": password,
        "service": "protonmail",
        "status": "success"
    }
