from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from .models import *
from django.db.models import Q
from .serializers import MessageSerializer

class ChatConsumer(JsonWebsocketConsumer) :

    def connect(self):
        if self.scope['user'].is_anonymous:
            return self.close()
        
        def init_all() :
            u = self.scope['user']
            requetes = Voyage.objects.filter(Q(voyageur__pk = u.pk) | Q(voyage_correspondant__user__pk = u.pk))
            for req in requetes :
                async_to_sync(self.channel_layer.group_add)('req.' + str(req.pk), self.channel_name)

        init_all()
        return super().connect()
    
    def echo(self, ev) :
        return self.send_json(ev)
    
    def message(self, ev) :
        return self.send_json(ev)

    def receive_json(self, content, **kwargs):
        u = self.scope['user']
        print("receive data -> ", content)
        if content['type'] == 'c_m' :

            result : dict = content['result']
            message = Message.objects.create(user = u, text = result.get('text', None), voyage = Voyage.objects.get(pk = int(result.get('req'))))
            if 'image' in result.keys() :
                message.image = Image.objects.get(pk = int(result.get('image')))
            #not audio yet
            message.save()
            async_to_sync(self.channel_layer.group_send)(f'req.{result["req"]}' ,{
                'type' : 'message',
                'result' : MessageSerializer(message).data
            })

    def disconnect(self, code):
        return super().disconnect(code)

