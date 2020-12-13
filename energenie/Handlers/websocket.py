from energenie.Handlers import Handler
from energenie import Registry
import asyncio
import websockets
import logging
import json


class WebSocketHandler(Handler):
    protocol = 'ws'
    description = 'Websocket handler'
    args = {
        'port': {
            'type': 'int',
            'prompt': 'Port number (default: 1883)',
            'default': 8765
        }
    }

    def __init__(self, **kw_args):
        super(WebSocketHandler, self).__init__(**kw_args)

        self.registry = Registry.DeviceRegistry.singleton()
        self.port = kw_args.get('port')
        self._clients = set()

        start_server = websockets.serve(self.server, "localhost", self.port)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def register(self, client):
        self._clients.add(client)

    async def unregister(self, client):
        self._clients.remove(client)

    async def server(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                self.handle_message(message)
        finally:
            await self.unregister(websocket)

    async def handle_message(self, message):
        device = message['uuid']
        device = self.registry.get(device)
        for key, value in message['states']:
            device.do_set_state(key, value)

    async def handle_reading(self, device, key, value):
        if len(self._clients) == 0:
            return
        device = self.registry.get(device)
        message = {
            'uuid': device.uuid,
            'states': {
                key: value
            }
        }

        await asyncio.wait([client.send(json.dumps(message)) for client in self._clients])
