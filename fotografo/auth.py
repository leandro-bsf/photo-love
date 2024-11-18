import jwt
import datetime
from ninja.security import HttpBearer
from django.conf import settings
 
from django.conf import settings
# Usando uma chave secreta configurada em settings.py (ou você pode definir uma chave diretamente aqui)
SECRET_KEY = settings.SECRET_KEY

class JWTBearer(HttpBearer):
       def authenticate(self, request, token: str) -> int:
        try:
            # Decodifica o token JWT
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get('id')  # Pegue o 'id' do payload do token
            if user_id:
                return user_id
            return None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

def create_jwt_token(user_id):
    # Criação do payload do JWT
    payload = {
        "id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # Token válido por 1 hora
        "iat": datetime.datetime.utcnow(),  # Hora de emissão
    }
    # Geração do token JWT com a chave secreta
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
