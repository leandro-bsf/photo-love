# fotografo/schemas.py

from ninja import Schema
from typing import Optional
from datetime import date, datetime
import base64

# Schema para Registro usando o modelo Fotografo
class RegisterSchema(Schema):
    nome: str
    senha: str
    fone: Optional[str] = None
    email: str

# Schema para Login
class AuthSchema(Schema):
    email: str
    senha: str

# Schema para Criação de Ensaio
class EnsaioCreateSchema(Schema):
    descricao: str
    val_ensaio: float
    qtd_fotos: int
    pago: Optional[bool] = False
    val_foto_extra: Optional[float] = None
    data_escolha: Optional[date] = None
     

# Schema para Visualização de Ensaio
class EnsaioOutSchema(Schema):
    id: int
    descricao: str
    val_ensaio: float
    qtd_fotos: int
    pago: bool
    data_criacao: datetime
    val_foto_extra: Optional[float] = None
    data_escolha: Optional[date] = None
    fotografo_id: int
    total_fotos_escolhidas: int


# Schemas para EnsaioFoto
class EnsaioFotoCreateSchema(Schema):
    ensaio_id: int
    fotografo_id: int
    escolhida: Optional[bool] = False

class EnsaioFotoOutSchema(Schema):
    id: int
    ensaio_id: int
    fotografo_id: int
    foto: Optional[str] = None  # Imagem em base64
    escolhida: bool

    @staticmethod
    def resolve_foto(obj):
        if obj.foto:
            return base64.b64encode(obj.foto).decode("utf-8")
        return None