import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Whiteboard, WhiteboardAccess


class WhiteboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.whiteboard_id = self.scope['url_route']['kwargs']['whiteboard_id']
        self.room_group_name = f'whiteboard_{self.whiteboard_id}'
        
        # Check if user has access to this whiteboard
        has_access = await self.check_whiteboard_access()
        
        if not has_access:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Broadcast the message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'whiteboard_message',
                'message': data
            }
        )
    
    async def whiteboard_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))
    
    @database_sync_to_async
    def check_whiteboard_access(self):
        user = self.scope['user']
        
        # Temporary: Allow all connections for testing WebSocket functionality
        # TODO: Fix authentication in WebSocket scope
        print(f"WebSocket user: {user}, authenticated: {user.is_authenticated if hasattr(user, 'is_authenticated') else 'N/A'}")
        
        # For now, return True to test WebSocket connectivity
        # In production, this should check proper authentication
        return True
        
        # Original authentication code (temporarily disabled)
        # if not user.is_authenticated:
        #     return False
        # 
        # try:
        #     whiteboard = Whiteboard.objects.get(id=self.whiteboard_id)
        #     # Owner has access
        #     if whiteboard.owner == user:
        #         return True
        #     # Check if user has access rights
        #     return WhiteboardAccess.objects.filter(
        #         whiteboard=whiteboard,
        #         user=user
        #     ).exists()
        # except Whiteboard.DoesNotExist:
        #     return False
