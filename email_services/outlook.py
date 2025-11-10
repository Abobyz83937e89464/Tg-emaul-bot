import asyncio
import random
import string

async def create_outlook_email():
    await asyncio.sleep(5)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{username}@outlook.com"
    
    return {
        "email": email,
        "service": "outlook",
        "status": "success"
    }
