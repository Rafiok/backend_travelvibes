from .models import *
from .serializers import *

@receiver(post_save, sender = Message)
def send_message(sender, instance : Message, created, **kwargs) :
    channel_layer = get_channel_layer()
    if created :
        async_to_sync(channel_layer.group_send)(f"req.{instance.pk}", {
                'type' : 'message',
                'result' : MessageSerializer(instance).data
            })
        