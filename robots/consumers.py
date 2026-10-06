from channels.generic.websocket import AsyncJsonWebsocketConsumer


class RobotConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.group_name = "robots"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

        await self.send_json({
            "type": "connection",
            "message": "Connected to robot live feed",
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def robot_update(self, event):
        await self.send_json({
            "type": "robot_update",
            "robot": event["robot"],
        })