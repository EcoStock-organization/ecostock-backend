import requests
from rest_framework.exceptions import APIException
import os


AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth_backend:8000/api')

class AuthService:
    @staticmethod
    def criar_usuario_auth(username, email, password):
        url = f"{AUTH_SERVICE_URL}/users/"
        
        try:
            response = requests.post(url, json={
                "username": username,
                "email": email,
                "password": password
            })
            
            if response.status_code == 201:
                return response.json()
            else:
                raise APIException(detail=f"Erro no serviço de Auth: {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise APIException(detail=f"Falha de conexão com serviço de Auth: {str(e)}")
