from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat</title>
</head>
<body>
    <h1>WebSocket Chat</h1>
    <form action="" onsubmit="connect(event)">
        <label for="username">Name:</label>
        <input type="text" id="username" autocomplete="off" required/>
        <button type="submit">Connect</button>
    </form>
    <div id="chat" style="display:none;">
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off" required/>
            <button type="submit">Send</button>
        </form>
        <ul id="messages">
        </ul>
        <button onclick="disconnect()">Disconnect</button>
    </div>
    <script>
        var ws;
        var username;

        function connect(event) {
            username = document.getElementById("username").value;
            ws = new WebSocket("ws://localhost:8000/ws?username=" + username);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            ws.onopen = function(event) {
                document.getElementById('chat').style.display = 'block';
            };
            ws.onclose = function(event) {
                alert("Disconnected");
                document.getElementById('chat').style.display = 'none';
            };
            event.preventDefault();
        }

        function sendMessage(event) {
            var input = document.getElementById("messageText")
            ws.send(input.value)
            input.value = ''
            event.preventDefault()
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
    def __init__(self):  # Corrigido aqui
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
