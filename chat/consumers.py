import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .modules.ai import Asklama

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        prompt = text_data.strip()
        if not prompt:
            await self.send(text_data="Error: Empty prompt received.")
            return

        try:
            async for token in self.stream_response(prompt):
                await self.send(text_data=token)
        except Exception as e:
            await self.send(text_data=f"Error: {str(e)}")

    async def stream_response(self, prompt):
        for token in Asklama(prompt, 2000):
            await asyncio.sleep(0)  # Allow other tasks to run
            yield token
