from fastapi import WebSocket
from typing import Dict,List

class SocketConnectionManager:
    def __init__(self) -> None:
        self.active_connections:Dict[str,WebSocket] = {}
        self.conversion_history:Dict[str,List[Dict[str,str]]] ={} 
        
    async def connect(self,websocket:WebSocket, client_id:str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        if client_id not in self.conversion_history:
            self.conversion_history[client_id] = []
    def disconnect(self,client_id:str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_message_json(self,client_id:str,message:dict):
        websocket = self.active_connections.get(client_id)
        if websocket:
            await websocket.send_json(message)
            self.conversion_history[client_id].append({"sender":"Bot","message":str(message)})
            
    async def send_message(self,client_id:str,message:str):
        websocket = self.active_connections.get(client_id)
        if websocket:
            await websocket.send_text(message)
            self.conversion_history[client_id].append({"sender":"Bot","message":message})
            
    async def receive_message(self,client_id)-> str:
        websocket = self.active_connections.get(client_id)
        if websocket:
            message = await websocket.receive_text()
            self.conversion_history[client_id].append({"sender":"User","message":message})
            return message
        return ""
        
    
    def _get_chat_history(self,client_id:str)->List[Dict[str,str]]:
       return self.conversion_history.get(client_id,[])
   
    async def send_chat_history(self, client_id: str):
        chat_history = self._get_chat_history(client_id)
        for entry in chat_history:
            if isinstance(entry["message"], dict):
                await self.send_message_json(client_id, entry["message"])
            else:
                await self.send_message(client_id, entry["message"])
                
    async def broadcast_to_team(self, team_members: List[str], message: str):
        for member_id in team_members:
            websocket = self.active_connections.get(member_id)
            if websocket:
                await websocket.send_text(message)
                self.conversion_history[member_id].append({"sender": "chatbot", "message": message})
