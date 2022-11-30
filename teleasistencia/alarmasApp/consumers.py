import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class Consumer(WebsocketConsumer):

    # Función que se ejecutará cuando un WebSocket cliente trate de conectarse al servidor
    def connect(self):
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