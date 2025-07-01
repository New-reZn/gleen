from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return
        
        self.group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
    async def disconnect(self,*args):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def user_notification(self, event):
        await self.send(text_data=json.dumps(event["text"]))