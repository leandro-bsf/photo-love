# fotografo/schemas.py

from ninja import Schema
from typing import Optional
from datetime import date, datetime
import base64
from typing import List


from pydantic import BaseModel
 
class RegisterSchema(BaseModel):
    nome: str
    senha: str
    fone: str = None
    email: str


class LoginSchema(BaseModel):
    email: str
    senha: str


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "Bearer"
# Schema para Criação de Ensaio

class EnsaioCreateSchema(Schema):
    descricao: str
    val_ensaio: float
    qtd_fotos: int
    pago: Optional[bool] = False
    val_foto_extra: Optional[float] = None
    data_escolha: Optional[date] = None
    senha_acesso: str
     
class ErrorSchema(BaseModel):
    detail: str 
# Schema para Visualização de Ensaio
class EnsaioUpdateSchema(BaseModel):
    descricao: str
    val_ensaio: float
    qtd_fotos: int
    pago: bool
    val_foto_extra: float
    data_escolha: datetime

class EnsaioOutSchema(BaseModel):
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
    
class AcessoEnsaioSchema(Schema):
    senha_acesso: str


class EnsaioFotoSchema(BaseModel):
    id: int
    foto: str  # A foto será retornada como uma string base64
    escolhida: bool

    class Config:
        orm_mode = True
        from_attributes = True  # Permite o uso de from_orm diretamente com Django ORM

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            foto=base64.b64encode(obj.foto).decode('utf-8'),  # Convertendo para base64
            escolhida=obj.escolhida
        )

class EnsaioSchema(BaseModel):
    id: int
    descricao: str
    data_criacao: str  # Alterando o nome para 'data_criacao'
    fotos: List[EnsaioFotoSchema]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, obj):
        # Ajustando para acessar 'data_criacao' no lugar de 'data'
        data_criacao = obj.data_criacao.strftime('%Y-%m-%d') if obj.data_criacao else None
        fotos = [EnsaioFotoSchema.from_orm(foto) for foto in obj.fotos.all()]

        return cls(
            id=obj.id,
            descricao=obj.descricao,
            data_criacao=data_criacao,  # Alterando para 'data_criacao'
            fotos=fotos
        )