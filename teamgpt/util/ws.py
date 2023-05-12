from typing import List, Dict, Optional

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, ws: WebSocket, channel: str):
        await ws.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(ws)

    def disconnect(self, ws: WebSocket, channel: str):
        self.active_connections[channel].remove(ws)

    @staticmethod
    async def send_personal_message(message: str, ws: WebSocket):
        await ws.send_text(message)

    async def broadcast(self, message: str, channel: Optional[str] = None):
        if channel is None:
            for connections in self.active_connections.values():
                for connection in connections:
                    await connection.send_text(message)
        else:
            if channel in self.active_connections:
                connections = self.active_connections[channel]
                for connection in connections:
                    await connection.send_text(message)


manager = ConnectionManager()
