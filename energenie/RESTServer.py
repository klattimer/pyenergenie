from flask import Flask, request, redirect, jsonify
from energenie.Registry import DeviceRegistry
from energenie.Devices import DeviceFactory
import threading
app = Flask(__name__)

__version__ = "v1"


@app.route('/')
def root():
    return redirect("/api/" + __version__ + "/", code=302)


# redirect / -> /api/v1
@app.route('/api/v1/')
def apiroot():
    return jsonify({
        'application': 'pyenergenie',
        'author': 'Karl Lattimer <karl@qdh.org.uk>',
        'url': 'github.com/klattimer/pyenergenie'
    })


# - Supported devices (get)
@app.route('/api/v1/hardware')
def hardware():
    devicefactory = DeviceFactory.singleton()
    return jsonify({k: devicefactory[k].describe() for k in devicefactory.keys()})


# - Registered devices (get, post, delete)
@app.route('/api/v1/devices')
def devices():
    registry = DeviceRegistry.singleton()
    return jsonify({k: registry.get(k).serialise() for k in registry.list()})


# - Get device state
@app.route('/api/v1/device/<device_uuid>')
def device(device_uuid):
    registry = DeviceRegistry.singleton()
    device = registry.get(device_uuid)
    data = device.serialise()
    data['readings'] = device.state()
    return jsonify(data)


# - Get/Set value on device
@app.route('/api/v1/device/<uuid>/feature')
def feature():
    pass


# - Registered handlers (get, post, delete)
@app.route('/api/v1/handlers')
def handlers():
    pass


def start():
    def run():
        app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
    thread = threading.Thread(target=run)
    thread.start()
    return thread
