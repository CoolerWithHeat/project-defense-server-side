from django.db.models.signals import post_save
from django.dispatch import receiver
import json
from channels.consumer import AsyncConsumer, StopConsumer as BreakConnection
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async 
from .models import Comment, Tag, Item
from datetime import datetime
from rest_framework.authtoken.models import Token

ConnectionProperties = set()

@database_sync_to_async
def default_behaviour(*args, **kwargs):
    return True, None

@database_sync_to_async
def exterminate_tag(dataFlow):
    id = dataFlow.get('tag_id', None)
    if id:
        filtered = Tag.objects.filter(id=id)
        requested_tag = filtered[0] if filtered else None
        deleted_object = requested_tag.delete() if requested_tag else False
        return not deleted_object, deleted_object or None
    else:
        return True, None
    
@database_sync_to_async
def comment_addition(text):
    if text:
        try:
            text['item'] = Item.objects.get(id=text['item'])
            comment = Comment.objects.create(**text)
            return None, {'id':comment.id, 'text':comment.text, 'commenter':'No Name' if comment.user.full_name=='Not Known' else comment.user.full_name}
        except:
            return 'Please Sign in !', None


def validToken(urlRoute):
    try:
        submittedToken = urlRoute.scope['path'].split('token=')[-1]
        valid_token = Token.objects.get(key=submittedToken)
        return valid_token.user
    except:
        return False

def retrieveTime(timestamp):
    dt = datetime.strptime(str(timestamp)[:19], '%Y-%m-%d %H:%M:%S')
    formatted_date = dt.strftime('%B %d, %Y')
    return formatted_date


def Get_Item_ID(Connection, itemItself=False):
    try:
        itemID = Connection.scope['url_route']['kwargs']['item_id']
        return int(itemID)
    except:
        return False

class CommentsConsumer(AsyncConsumer):
    layerCode = 'comments_line_'

    async def websocket_connect(self, event):
        requested_item_comment_flow = await database_sync_to_async(Get_Item_ID)(self)
        print(requested_item_comment_flow)
        if requested_item_comment_flow:
            ConnectionProperties.add(self)
            self.layerCode = f'comments_line_{requested_item_comment_flow}'
            await self.send({
                "type": "websocket.accept",
            })
            
            await self.channel_layer.group_add(
                self.layerCode,
                self.channel_name
            )
        else:
            await self.channel_layer.group_discard(
                self.layerCode,
                self.channel_name,
            )
            raise BreakConnection


    async def websocket_disconnect(self, event):
        ConnectionProperties.discard(self)
        await self.channel_layer.group_discard(
            self.layerCode,
            self.channel_name,
        )
        raise BreakConnection
    
    async def message_send(self, event):
        
        data = json.loads(event['text'])

        await self.send({
            'type':'websocket.send',
            'text':json.dumps(data)
        })
    
    async def websocket_receive(self, event):
        data = json.loads(event['text']) or None
        requesting_user = await database_sync_to_async(validToken)(self)
        current_item = await database_sync_to_async(Get_Item_ID)(self)
        text = data.get('text', None)
        command = data.get('operation', None)
        tag_id = data.get('tagID')
        
        available_commands = {
            'delete_tag': exterminate_tag,
            'add_comment': comment_addition,
            None : default_behaviour,
        }

        prepared_data = {'user': requesting_user, 'item':current_item, 'text':text, 'tag_id': tag_id}

        if requesting_user and (perform := available_commands.get(command)):
            error, obj = await perform(prepared_data)
            await self.channel_layer.group_send(self.layerCode, {
                'type': 'message.send',
                'text': json.dumps({'message': error or 'Done', 'code': None if not error else 111})      
            })
        else:
            await self.channel_layer.group_send(self.layerCode, {
                'type': 'message.send',
                'text': json.dumps({'message': 'please sign in!', 'code':111})      
            })


    @receiver(post_save, sender=Comment)
    def handle_model_change(sender, instance, created, **kwargs):
        self = ConnectionProperties.pop() if ConnectionProperties else None
        requestedID = Get_Item_ID(self)
        comment_text = instance.text
        belongs_to = instance.item.id
        commenter = "Anonymous" if instance.user.full_name == 'Not Known' else instance.user.full_name
        date = retrieveTime(instance.timestamp)
        response = {'id':requestedID, 'commenter':commenter, 'date':date, 'text': comment_text}
        async_to_sync(self.channel_layer.group_send)(self.layerCode, {
            'type': 'message.send',
            'text': json.dumps({'comment': response})      
        })