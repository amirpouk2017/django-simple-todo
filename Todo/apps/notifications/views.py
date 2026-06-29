from channels.generic.websocket import AsyncWebsocketConsumer


class HelloConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data="hello")

    async def disconnect(self, close_code):
        pass
