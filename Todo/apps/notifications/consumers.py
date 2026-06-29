from channels.generic.websocket import AsyncWebsocketConsumer


class HelloConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        print("WS USER:", user)

        await self.accept()
        await self.send(text_data=f"Hello {user}")

    async def disconnect(self, close_code):
        pass
