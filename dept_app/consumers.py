from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer


class ChatConsumer(WebsocketConsumer):
    def websocket_connect(self, message):
        self.accept()

    def websocket_receive(self, message):

        self.send("")

    def websocket_disconnect(self, message):
        raise StopConsumer