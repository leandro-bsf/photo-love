from ninja import NinjaAPI, Router
from django.contrib.auth.hashers import make_password, check_password
from .models import Fotografo, Ensaio ,EnsaioFoto
from .auth import JWTBearer, create_jwt_token
from .schemas import RegisterSchema, LoginSchema, EnsaioFotoSchema,EnsaioSchema,TokenResponseSchema,  EnsaioUpdateSchema,EnsaioFotoOutSchema ,EnsaioCreateSchema
from django.shortcuts import get_object_or_404
import jwt
from django.http import Http404
from .auth import JWTBearer
from django.http import JsonResponse
from ninja import Router, File, UploadedFile
from typing import List

# Instância principal do NinjaAPI sem autenticação na rota de registro
api = NinjaAPI()

router = Router()

# Rota de Registro (não protegida)
@router.post("/register", response={201: TokenResponseSchema, 400: str})
def register(request, data: RegisterSchema):
    # Verifica se o email já existe no banco de dados
    if Fotografo.objects.filter(email=data.email).exists():
        return 400, "Email já cadastrado."

    # Criação do hash da senha
    hashed_password = make_password(data.senha)
    
    fotografo = Fotografo(
        nome=data.nome,
        senha=hashed_password,
        fone=data.fone,
        email=data.email,
    )
    fotografo.save()

    # Geração do token JWT
    token = create_jwt_token(fotografo.id)
    return 201, {"access_token": token, "token_type": "Bearer"}

# Rota de Login (gerando token após autenticação)
@router.post("/login", response={200: TokenResponseSchema, 401: str})
def login(request, data: LoginSchema):
    try:
        fotografo = Fotografo.objects.get(email=data.email)
    except Fotografo.DoesNotExist:
        return 401, "Credenciais inválidas: usuário não encontrado."
    
    # Verifica a senha fornecida com o hash armazenado
    if not check_password(data.senha, fotografo.senha):  # Comparando com o hash armazenado
        return 401, "Credenciais inválidas: senha incorreta."
    
    # Se a senha estiver correta, gera o token
    token = create_jwt_token(fotografo.id)
    return 200, {"access_token": token, "token_type": "Bearer"}


@router.post("/ensaio/", auth=JWTBearer())  # Protegendo o endpoint com JWT
def create_ensaio(request, ensaio_data: EnsaioCreateSchema):
    user_id = request.auth  # O ID do usuário autenticado

    # Verificar se o usuário está autenticado
    if not user_id:
        return JsonResponse({"detail": "Usuário não autenticado ou inválido."}, status=401)

    # Buscar o fotógrafo autenticado
    fotografo = get_object_or_404(Fotografo, id=user_id)

    # Criação do novo ensaio
    ensaio = Ensaio.objects.create(
        descricao=ensaio_data.descricao,
        val_ensaio=ensaio_data.val_ensaio,
        qtd_fotos=ensaio_data.qtd_fotos,
        pago=ensaio_data.pago,
        val_foto_extra=ensaio_data.val_foto_extra,
        data_escolha=ensaio_data.data_escolha,
        fotografo=fotografo,  # Associa o ensaio ao fotógrafo autenticado
        senha_acesso= ensaio_data.senha_acesso
    )

    # Retornar apenas a mensagem com o nome do ensaio
    return JsonResponse({"message": f"Ensaio '{ensaio.descricao}' cadastrado com sucesso!"})


@router.get("/ensaio/", auth=JWTBearer())
def get_ensaios(request):
    user_id = request.auth  # O ID do usuário autenticado

    # Verificar se o usuário está autenticado
    if not user_id:
        return JsonResponse({"detail": "Usuário não autenticado ou inválido."}, status=401)

    # Buscar o fotógrafo autenticado
    fotografo = get_object_or_404(Fotografo, id=user_id)

    # Buscar os ensaios do fotógrafo autenticado
    ensaios = Ensaio.objects.filter(fotografo=fotografo)

    # Serializar os dados para a resposta
    ensaios_data = [{"id": ensaio.id, "descricao": ensaio.descricao, "data_criacao": ensaio.data_criacao, "Senha_acesso": ensaio.senha_acesso} for ensaio in ensaios]

    return JsonResponse({"ensaio": ensaios_data})

@router.put("/ensaio/{ensaio_id}/", auth=JWTBearer())
def update_ensaio(request, ensaio_id: int, ensaio_data: EnsaioUpdateSchema):
    user_id = request.auth  # O ID do usuário autenticado

    # Verificar se o usuário está autenticado
    if not user_id:
        return JsonResponse({"detail": "Usuário não autenticado ou inválido."}, status=401)

    # Buscar o fotógrafo autenticado
    fotografo = get_object_or_404(Fotografo, id=user_id)

    # Buscar o ensaio pelo ID
    ensaio = get_object_or_404(Ensaio, id=ensaio_id)

    # Verificar se o ensaio pertence ao fotógrafo autenticado
    if ensaio.fotografo != fotografo:
        return JsonResponse({"detail": "Você não tem permissão para editar este ensaio."}, status=403)

    # Atualizar os dados do ensaio com os dados recebidos
    ensaio.descricao = ensaio_data.descricao
    ensaio.val_ensaio = ensaio_data.val_ensaio
    ensaio.qtd_fotos = ensaio_data.qtd_fotos
    ensaio.pago = ensaio_data.pago
    ensaio.val_foto_extra = ensaio_data.val_foto_extra
    ensaio.data_escolha = ensaio_data.data_escolha

    # Salvar as alterações no banco de dados
    ensaio.save()

    return JsonResponse({"message": f"Ensaio '{ensaio.descricao}' atualizado com sucesso!"})



@router.delete("/ensaio/{ensaio_id}/", auth=JWTBearer())
def delete_ensaio(request, ensaio_id: int):
    user_id = request.auth  # O ID do usuário autenticado

    # Verificar se o usuário está autenticado
    if not user_id:
        return JsonResponse({"detail": "Usuário não autenticado ou inválido."}, status=401)

    # Buscar o fotógrafo autenticado
    fotografo = get_object_or_404(Fotografo, id=user_id)

    # Buscar o ensaio pelo ID
    ensaio = get_object_or_404(Ensaio, id=ensaio_id)

    # Verificar se o ensaio pertence ao fotógrafo autenticado
    if ensaio.fotografo != fotografo:
        return JsonResponse({"detail": "Você não tem permissão para excluir este ensaio."}, status=403)

    # Excluir o ensaio
    ensaio.delete()

    return JsonResponse({"message": f"Ensaio '{ensaio.descricao}' excluído com sucesso!"})


 
# Usando o JWTBearer para autenticação
@router.post("/ensaiofotos/multi-upload/", auth=JWTBearer())
def create_ensaio_fotos(request, ensaio_id: int, fotos: List[UploadedFile], escolhida: bool = False):
    # Obtém o usuário autenticado
    user_id = request.auth

    # Verificar se o usuário está autenticado
    if not user_id:
        return JsonResponse({"detail": "Usuário não autenticado ou inválido."}, status=401)

    # Buscar o fotógrafo
    fotografo = get_object_or_404(Fotografo, id=user_id)

    # Buscar o ensaio
    ensaio = get_object_or_404(Ensaio, id=ensaio_id, fotografo=fotografo)

    ensaio_fotos = []

    for foto in fotos:
        foto_data = foto.read()  # Lê os dados binários da imagem

        # Salvar os dados binários da foto no banco de dados
        ensaio_foto = EnsaioFoto.objects.create(
            ensaio=ensaio,
            fotografo=fotografo,
            foto=foto_data,  # Armazenando os dados binários diretamente no banco
            escolhida=escolhida
        )

        # Adiciona o ensaio foto ao resultado, usando o schema para converter os dados binários em base64
        ensaio_fotos.append(EnsaioFotoSchema.from_orm(ensaio_foto))

    return JsonResponse({"detail": "Fotos do ensaio criadas com sucesso.", "ensaio_fotos": [foto.dict() for foto in ensaio_fotos]})




@router.delete("/ensaiofotos/multi-delete/")
def delete_ensaio_fotos(request, ensaio_id: int, foto_ids: List[int]):
    # Obtém o fotógrafo autenticado do request
    fotografo = request.user  # Captura o fotógrafo do token JWT

    # Verifica se o ensaio existe e está associado ao fotógrafo autenticado
    ensaio = get_object_or_404(Ensaio, id=ensaio_id, fotografo=fotografo)

    # Lista para armazenar as fotos deletadas
    deleted_fotos = []

    # Itera sobre os IDs das fotos e tenta deletá-las
    for foto_id in foto_ids:
        ensaio_foto = get_object_or_404(EnsaioFoto, id=foto_id, ensaio=ensaio, fotografo=fotografo)
        ensaio_foto.delete()  # Deleta a foto
        deleted_fotos.append(foto_id)  # Adiciona o ID da foto deletada à lista

    return {"mensagem": "Fotos deletadas com sucesso", "deletadas": deleted_fotos}


@router.get("/ensaio/{ensaio_id}/detalhes")
def get_ensaio_com_fotos(request, ensaio_id: int):
    # Busca o ensaio com as fotos relacionadas
    ensaio = get_object_or_404(Ensaio.objects.prefetch_related('fotos'), id=ensaio_id)
    
    # Converte o ensaio para o formato do schema
    ensaio_data = EnsaioSchema.from_orm(ensaio)
    
    # Retorna o ensaio com as fotos
    return ensaio_data


# Adiciona o roteador na instância principal da API
api.add_router("/fotografo", router)
