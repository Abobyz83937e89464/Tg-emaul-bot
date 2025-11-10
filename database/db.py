import requests
from config import SUPABASE_URL, SUPABASE_KEY

class Database:
    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.headers = {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json'
        }
    
    def insert_user(self, telegram_id):
        data = {
            'telegram_id': telegram_id,
            'created_at': 'now()'
        }
        response = requests.post(f"{self.url}/rest/v1/users", json=data, headers=self.headers)
        return response.json() if response.status_code == 200 else None
    
    def get_user(self, telegram_id):
        response = requests.get(
            f"{self.url}/rest/v1/users?telegram_id=eq.{telegram_id}",
            headers=self.headers
        )
        return response.json()[0] if response.status_code == 200 and response.json() else None
    
    def update_user_last_email(self, telegram_id):
        data = {
            'last_email_created': 'now()'
        }
        response = requests.patch(
            f"{self.url}/rest/v1/users?telegram_id=eq.{telegram_id}",
            json=data,
            headers=self.headers
        )
        return response.status_code == 200
    
    def insert_email(self, user_id, email, service):
        data = {
            'user_id': user_id,
            'email': email,
            'email_service': service
        }
        response = requests.post(f"{self.url}/rest/v1/email_accounts", json=data, headers=self.headers)
        return response.status_code == 200
    
    def get_all_emails(self):
        response = requests.get(f"{self.url}/rest/v1/email_accounts", headers=self.headers)
        return response.json() if response.status_code == 200 else []
    
    def get_user_by_id(self, user_id):
        response = requests.get(f"{self.url}/rest/v1/users?id=eq.{user_id}", headers=self.headers)
        return response.json()[0] if response.status_code == 200 and response.json() else None
