from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List

app = FastAPI()

html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSocket Chat</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }

        h1 {
            text-align: center;
            color: #333;
        }

        form {
            margin-bottom: 10px;
        }

        label {
            display: block;
            margin-bottom: 5px;
        }

        input[type="text"] {
            width: calc(100% - 80px);
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        button {
            padding: 8px 16px;
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        button:hover {
            background-color: #0056b3;
        }

        .chat-box {
            display: none;
            margin-top: 20px;
        }

        .message-list {
            list-style-type: none;
            padding: 0;
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: #f9f9f9;
            padding: 10px;
        }

        .message-list li {
            margin-bottom: 5px;
            padding: 8px;
            border-radius: 4px;
            background-color: #fff;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        .message-list li:last-child {
            margin-bottom: 0;
        }

        .message-list li:nth-child(even) {
            background-color: #f0f0f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>WebSocket Chat</h1>
        <form id="connectForm" onsubmit="connect(event)">
            <label for="username">Nome:</label>
            <input type="text" id="username" autocomplete="off" required>
            <button type="submit">Conectar</button>
        </form>
        <div id="chat" class="chat-box">
            <form id="messageForm" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off" required>
                <button type="submit">Enviar</button>
            </form>
            <ul id="messages" class="message-list">
            </ul>
            <button onclick="disconnect()">Desconectar</button>
        </div>
    </div>

    <script>
        var ws;
        var username;

        function connect(event) {
            username = document.getElementById("username").value;
            ws = new WebSocket("ws://localhost:8000/ws?username=" + username);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var content = document.createTextNode(event.data);
                message.appendChild(content);
                messages.appendChild(message);
                // Scroll para a última mensagem
                messages.scrollTop = messages.scrollHeight;
            };
            ws.onopen = function(event) {
                document.getElementById('chat').style.display = 'block';
                document.getElementById('connectForm').style.display = 'none'; // Esconde o formulário de conexão
            };
            ws.onclose = function(event) {
                alert("Desconectado");
                document.getElementById('chat').style.display = 'none';
                document.getElementById('connectForm').style.display = 'block'; // Mostra o formulário de conexão novamente
            };
            event.preventDefault();
        }

        function sendMessage(event) {
            var input = document.getElementById("messageText");
            if (input.value.trim() !== "") {
                ws.send(input.value);
            }
            input.value = '';
            event.preventDefault();
        }

        function disconnect() {
            ws.close();
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.usernames: List[str] = []

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.usernames.append(username)
        await self.broadcast(f"{username} joined the chat")

    def disconnect(self, websocket: WebSocket):
        index = self.active_connections.index(websocket)
        username = self.usernames.pop(index)
        self.active_connections.remove(websocket)
        return username

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    username = websocket.query_params.get("username")
    await manager.connect(websocket, username)
    try:
        while True:
            data = await websocket.receive_text()
            message = f"{username}: {data}"
            await manager.broadcast(message)
    except WebSocketDisconnect:
        username = manager.disconnect(websocket)
        await manager.broadcast(f"{username} left the chat")
