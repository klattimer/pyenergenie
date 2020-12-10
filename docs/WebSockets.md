# WebSocket message handler

WebSockets can be used directly on the server and can be queried via the RESTServer for their availability.
WebSockets can allow direct integration with PyEnergenie from a web user interface. Used along side the RESTServer
WebSockets can allow full over-the-browser interaction with PyEnergenie running on a RaspberryPi.

## Configuration

The websocket handler can be added with minimal configuration:

```
"WebSocketChannel": {
    "type": "WebSocketHandler"
    "port": 8765
}
```

The specified port is also a default and can be safely omitted if no adjustment is required.

## Messages

#### Reporting an incoming message
```
```

#### Activating a valve
```
```
