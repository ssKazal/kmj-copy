from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """Consumer for notification sends

    Methods
    -------
    connect():
        Creates socket connection and makes a room for the user
        then adds that room to the channel layer
    receive_json(content=""):
        Receives messages from client side
    disconnect(close_code=int):
        To destroy socket connection
    message_notification(close_code=dict["", ""]):
        Sends messages to a respective layer
    """
    async def connect(self):

        """Creates socket connection and makes a room for authenticated user
        then adds that room to the channel layer"""

        await self.accept()  # Creates connection

        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.room_name = f"notification_room_{self.user.id}"  # Room

            await self.channel_layer.group_add(
                self.room_name, self.channel_name
            )  # Adding room to layer

    async def receive_json(self, content: str) -> None:
        """Receives messages from client side"""
        pass

    async def disconnect(self, close_code: int) -> None:
        """To destroy socket connection"""

        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def message_notification(self, event: dict[str, str]) -> None:
        """Sends messages to a respective layer"""

        await self.send_json(event)
