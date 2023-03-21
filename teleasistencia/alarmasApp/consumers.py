import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


# URL Protocolo://dominioOIP:Puerto/ws/webRTC/socket-server/
class Consumer(WebsocketConsumer):

    # Función que se ejecutará cuando un WebSocket cliente trate de conectarse al servidor
    def connect(self):
        print("llega aquI")
        self.room_group_name = 'teleoperadores'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    # Función que se ejecutará cuando un WebSocket cliente se desconecte del servidor
    def disconnect(self, code):
        print("Closed websocket with code: ", code)
        async_to_sync(self.channel_layer.group_discard)(
            'teleoperadores',
            self.channel_name
        )
        self.close()

    # Función que utilizaremos para enviar mensajes de notifiación de Alarmas a nuestros clientes
    def notify_clients(self, event):
        action = event['action']
        alarma = event['alarma']

        self.send(text_data=json.dumps({
            'action': action,
            'alarma': alarma
        }))


# URL Protocolo://dominioOIP:Puerto/ws/webRTC/NombreDeLaSala/
class ConsumerWebRTC(WebsocketConsumer):

    # Función que se ejecutará cuando un WebSocket cliente trate de conectarse al servidor
    def connect(self):
        # Obtiene la sala a la que se va a conectar para conexión de WebRTC con WebSocket
        self.room_group_name =self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    # Función que se ejecutará cuando un WebSocket cliente se desconecte del servidor
    def disconnect(self, code):
        print("Closed websocket with code: ", code)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        self.close()


    def receive(self, text_data):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat.message",
                "data": text_data,
                'sender_channel_name': self.channel_name
            },
        )
    def chat_message(self, event):
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=event["data"])
