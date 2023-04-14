import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from utilidad.logging import magenta, cyan

# URL Protocolo://dominioOIP:Puerto/ws/webRTC/socket-server/
class Consumer(WebsocketConsumer):

    # Función que se ejecutará cuando un WebSocket cliente trate de conectarse al servidor
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None

    def connect(self):
        magenta("Consumer", "Client connected")
        self.room_group_name = 'teleoperadores'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    # Función que se ejecutará cuando un WebSocket cliente se desconecte del servidor
    def disconnect(self, code):
        magenta("Consumer", f"Closed websocket with code {code}")
        async_to_sync(self.channel_layer.group_discard)(
            'teleoperadores',
            self.channel_name
        )
        self.close()

    # Función que utilizaremos para enviar mensajes de notifiación de Alarmas a nuestros clientes
    # El modelo automáticamente se encarga de notificar cuando son creadas
    def notify_clients(self, event):
        action = event['action']
        alarma = event['alarma']

        body = json.dumps({
            'action': action,
            'alarma': alarma
        })

        magenta("Consumer", f"Notificando clientes: {body}")
        self.send(text_data=body)


# URL Protocolo://dominioOIP:Puerto/ws/webRTC/NombreDeLaSala/
class ConsumerWebRTC(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None
        self.room_name = None

    # Función que se ejecutará cuando un WebSocket cliente trate de conectarse al servidor
    def connect(self):
        magenta("ConsumerWebRTC", "Client connected")
        # Obtiene la sala a la que se va a conectar para conexión de WebRTC con WebSocket
        self.room_group_name = self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    # Función que se ejecutará cuando un WebSocket cliente se desconecte del servidor
    def disconnect(self, code):
        magenta("Consumer", f"Closed websocket with code {code}")
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        self.close()

    def receive(self, text_data):
        # TODO: logging (magenta para conexiones)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat.message",
                "data": text_data,
                'sender_channel_name': self.channel_name
            },
        )

    def chat_message(self, event):
        # TODO: logging (magenta para conexiones)
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=event["data"])
