from channels.generic.websocket import AsyncWebsocketConsumer
import json

class JobConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "job_updates"  # Name of your group

        # Join the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()  # Accept the WebSocket connection

    async def disconnect(self, close_code):
        # Leave the group when disconnected
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming messages from WebSocket (optional for updates)
        text_data_json = json.loads(text_data)
        # Do something with the received message
        pass
    async def send_job_update(self, event):
        print(f"Sending job update: {event}")  # Debugging line

        await self.send(text_data=json.dumps({
            'title': event['title'],
            'company': event['company'],
            'description': event['description'],
            'requirements': event['requirements'],
            'location': event['location'],
            'posted_at': event['posted_at']
        }))

