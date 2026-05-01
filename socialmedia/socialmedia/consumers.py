from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumner(AsyncWebsocketConsumer):

    async def connect(self):
        print("connected")
        await self.accept()

    async def disconnect(self, close_code):
        print("disconnected")

    async def receive(self, text_data=None):
        if not text_data:
            await self.send(text_data="Error: No message provided")
            return
        print(f"message received: {text_data}")
        # Echo plain text message back
        await self.send(text_data=text_data)
            