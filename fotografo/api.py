# fotografo/api.py

from ninja import NinjaAPI, Router
from fotografo.models import Ensaio, Fotografo ,EnsaioFoto
from fotografo.schemas import RegisterSchema, AuthSchema,AcessoEnsaioSchema,  EnsaioCreateSchema, EnsaioOutSchema ,EnsaioFotoCreateSchema ,EnsaioFotoOutSchema
from ninja.security import HttpBearer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.shortcuts import get_object_or_404
from ninja.files import UploadedFile
from typing import List
from django.contrib.auth.hashers import check_password
import base64

# Instância principal da API Ninja
api = NinjaAPI()

# Classe de autenticação JWT
class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            access_token = AccessToken(token)  # Valida o token de acesso
            request.user = Fotografo.objects.get(id=access_token['user_id'])
            return token
        except Exception:
            return None

jwt_auth = JWTAuth()

# Função para gerar tokens para o usuário
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Endpoint de Registro usando Fotografo
@api.post("/public/register/")
def register(request, data: RegisterSchema):
    if Fotografo.objects.filter(email=data.email).exists():
        return {"success": False, "message": "Email já registrado."}
    fotografo = Fotografo.objects.create(
        nome=data.nome,
        senha=make_password(data.senha),
        fone=data.fone,
        email=data.email
    )
    return {"success": True, "message": "Fotógrafo registrado com sucesso."}

# Endpoint de Login
@api.post("/public/login/")
def login(request, data: AuthSchema):
    fotografo = authenticate(username=data.email, password=data.senha)
    if fotografo is not None:
        tokens = get_tokens_for_user(fotografo)
        return {"success": True, "tokens": tokens}
    return {"success": False, "message": "Credenciais inválidas."}

# Roteador para rotas protegidas
router = Router(auth=jwt_auth)

@router.get("/ensaios/", response=list[EnsaioOutSchema])
def list_ensaios(request):
    return Ensaio.objects.all()

@router.post("/ensaios/", response=EnsaioOutSchema)
def create_ensaio(request, ensaio_data: EnsaioCreateSchema):
    fotografo = request.user  # Usa o usuário autenticado diretamente do token JWT

    # Cria o ensaio associado ao fotógrafo autenticadoAcessoEnsaioSchema
    ensaio = Ensaio.objects.create(
        descricao=ensaio_data.descricao,
        val_ensaio=ensaio_data.val_ensaio,
        qtd_fotos=ensaio_data.qtd_fotos,
        pago=ensaio_data.pago,
        val_foto_extra=ensaio_data.val_foto_extra,
        data_escolha=ensaio_data.data_escolha,
        fotografo=fotografo  # Associa o ensaio ao fotógrafo autenticado
    )
    return ensaio




# Atualizar Ensaio (PUT)
@router.put("/ensaios/{ensaio_id}/", response=EnsaioOutSchema)
def update_ensaio(request, ensaio_id: int, ensaio_data: EnsaioCreateSchema):
    ensaio = get_object_or_404(Ensaio, id=ensaio_id)
    for attr, value in ensaio_data.dict().items():
        setattr(ensaio, attr, value)
    ensaio.save()
    return ensaio

# Deletar Ensaio (DELETE)
@router.delete("/ensaios/{ensaio_id}/")
def delete_ensaio(request, ensaio_id: int):
    ensaio = get_object_or_404(Ensaio, id=ensaio_id)
    ensaio.delete()
    return {"success": True, "message": "Ensaio deletado com sucesso."}

@router.post("/ensaiofotos/multi-upload/", response=List[EnsaioFotoOutSchema])
def create_ensaio_fotos(request, ensaio_id: int, fotos: List[UploadedFile], escolhida: bool = False):
    # Obtém o fotógrafo autenticado do request
    fotografo = request.user  # Captura o fotógrafo do token JWT

    # Verifica se o ensaio existe e está associado ao fotógrafo autenticado
    ensaio = get_object_or_404(Ensaio, id=ensaio_id, fotografo=fotografo)

    # Lista para armazenar os registros criados
    ensaio_fotos = []

    # Itera sobre cada arquivo e cria um registro `EnsaioFoto` para cada foto
    for foto in fotos:
        foto_data = foto.read()  # Lê os dados binários da imagem
        ensaio_foto = EnsaioFoto.objects.create(
            ensaio=ensaio,
            fotografo=fotografo,
            foto=foto_data,  # Armazena a imagem como BLOB
            escolhida=escolhida
        )
        ensaio_fotos.append(ensaio_foto)

    return ensaio_fotos

@router.delete("/ensaiofotos/{foto_id}/")
def delete_ensaio_foto(request, foto_id: int):
    ensaio_foto = get_object_or_404(EnsaioFoto, id=foto_id)
    ensaio_foto.delete()
    return {"success": True, "message": "EnsaioFoto deletado com sucesso."}

@router.get("/ensaiofotos/{ensaio_id}/", response=List[EnsaioFotoOutSchema])
def list_ensaio_fotos(request, ensaio_id: int):
    # Verifica se o ensaio existe
    ensaio = get_object_or_404(Ensaio, id=ensaio_id)

    # Busca todas as fotos associadas ao ensaio
    fotos = EnsaioFoto.objects.filter(ensaio=ensaio)

    return fotos

# Endpoint público para acessar o ensaio e suas fotos com validação de senha
@router.post("/ensaio/{ensaio_id}/acesso/", response=List[EnsaioFotoOutSchema])
def acesso_ensaio(request, ensaio_id: int, acesso_data: AcessoEnsaioSchema):
    # Verifica se o ensaio existe
    ensaio = get_object_or_404(Ensaio, id=ensaio_id)

    # Valida a senha de acesso
    if not check_password(acesso_data.senha_acesso, ensaio.senha_acesso):
        return {"detail": "Senha incorreta"}, 403  # Retorna erro 403 se a senha estiver incorreta

    # Busca todas as fotos associadas ao ensaio
    fotos = EnsaioFoto.objects.filter(ensaio=ensaio)

    return fotos

api.add_router("/fotografo", router)
