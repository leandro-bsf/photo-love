# Usar a imagem oficial do Python
FROM python:3.11-slim

# Atualizar pacotes do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    libopencv-dev \
    python3-opencv
# Definir o diretório de trabalho no container
WORKDIR /PHOTO_LOVE

# Copiar os arquivos de requisitos para o container
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação para o container
COPY . .

# Expor a porta 88
EXPOSE 87

# Comando para rodar a aplicação com Uvicorn no Python Ninja
CMD ["python", "manage.py", "runserver", "0.0.0.0:87"]