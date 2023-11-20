from channels.db import database_sync_to_async 
from channels.consumer import AsyncConsumer
from .models import Tag
import json, random

def search(key):
    result = Tag.objects.filter(name__startswith=str(key).capitalize()).values_list('name', flat=True)[:3]
    return list(result)

class SearchBase(AsyncConsumer):
    layerCode = f'searching-channel_'
    async def websocket_connect(self, event):
        random_channelCode = str(random.randint(9, 999999))
        await self.send({
            "type": "websocket.accept",
        })
        self.layerCode = self.layerCode+random_channelCode
        await self.channel_layer.group_add(
            self.layerCode,
            self.channel_name
        )
        print(self.layerCode)

    async def websocket_disconnect(self, event):
        pass

    async def message_send(self, event):
        data = json.loads(event['text'])
        await self.send({
            'type': 'websocket.send',
            'text': json.dumps(data)
        })

    async def websocket_receive(self, event):
        data = json.loads(event['text']) or None
        if data:
            requested_key = data.get('keyword')
            query = await database_sync_to_async(search)(requested_key)
            await self.channel_layer.group_send(
                self.layerCode,
                {
                    'type': 'message.send',
                    'text': json.dumps({'result': query})
                }
            )