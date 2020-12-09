import asyncio
import websockets


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

        start_server = websockets.serve(self.server, "localhost", 8765)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def register(self, client):
        self._clients.add(client)

    async def unregister(self, client):
        self._clients.remove(client)

    async def server(self, websocket, path):
        await self.register(websocket)
        #
        # name = await websocket.recv()
        # print(f"< {name}")
        #
        # greeting = f"Hello {name}!"
        #
        # await websocket.send(greeting)
        # print(f"> {greeting}")

    async def handle_reading(self, device, key, value):
        device = self.registry.get(device)
        message = {

        }
        if len(self._clients) == 0:
            return

        await asyncio.wait([client.send(json.dumps(message)) for client in self._clients])
