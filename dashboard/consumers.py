import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async, sync_to_async
from .models import Message
from .services.ai_service import correct_text_grammar

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        print(f"DEBUG: Received raw data: {text_data}") 
        try:
            data = json.loads(text_data)
            raw_message = data['message']
            print(f"DEBUG: Message parsed: {raw_message}")
            
            # AI Correction
            corrected_message = await sync_to_async(correct_text_grammar)(raw_message)
            print(f"DEBUG: AI response: {corrected_message}")
            
            # Save to Database
            await self.save_message(corrected_message)
            
            # Broadcast
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': corrected_message,
                    'sender': self.scope['user'].username
                }
            )
        except Exception as e:
            print(f"ERROR: Something went wrong in receive: {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, content):
        if self.scope['user'].is_authenticated:
            Message.objects.create(
                sender=self.scope['user'],
                content=content
            )