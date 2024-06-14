# Trabalho_Websockets - Chat com FastAPI

Este projeto é uma aplicação de chat simples utilizando WebSockets com o framework FastAPI.

Requisitos:

Python 3.7+
FastAPI
Uvicorn

Instalação
Clone o repositório:

git clone https://github.com/seuusuario/websocket-chat.git
cd websocket-chat

Crie um ambiente virtual (opcional, mas recomendado):

python -m venv venv

Ative o ambiente virtual:

source venv/bin/activate  # No Windows, use venv\Scripts\activate

Instale as dependências:

pip install fastapi 
pip install fastapi uvicorn

Executando a Aplicação

Inicie o servidor:

uvicorn main:app --reload

Abra seu navegador e acesse http://localhost:8000 ou http://127.0.0.1:8000 para ver a interface do chat.

Estrutura do Projeto
main.py: Contém o código principal da aplicação FastAPI.

Funcionalidades
Conectar ao chat com um nome de usuário.
Enviar mensagens para todos os usuários conectados.
Notificação quando um usuário entra ou sai do chat.

Código Explicado
Frontend (HTML + JavaScript)
O frontend está embutido diretamente na rota principal do FastAPI:
Local: \templates\index.html

O HTML define a estrutura da interface do usuário, incluindo campos de entrada para o nome de usuário e mensagens, 
além de elementos para exibir as mensagens do chat.

Backend (FastAPI)
O backend é implementado utilizando FastAPI, com uma rota WebSocket para gerenciar as conexões e troca de mensagens:

Licença
Este projeto está licenciado sob a MIT License.