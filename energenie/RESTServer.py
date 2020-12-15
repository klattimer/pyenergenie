from flask import Flask, request, redirect, jsonify, render_template
from werkzeug.exceptions import HTTPException, NotFound, BadRequest
from energenie.Registry import DeviceRegistry
from energenie.Devices import DeviceFactory
from energenie.Handlers import HandlerRegistry
import threading
app = Flask(__name__)

__version__ = "v1"


@app.route('/')
def root():
    if request.content_type == 'application/json':
        return redirect("/api/" + __version__ + "/", code=302)
    return render_template('Templates/index.html')


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
@app.route('/api/v1/devices', methods=['GET', 'POST'])
def devices():
    registry = DeviceRegistry.singleton()
    if request.method == 'POST':
        data = request.get_json()
        model = data['type']
        del(data['type'])
        d = DeviceFactory.get_device_from_model(model, **data)
        registry.add(d)
    elif request.method == 'GET':
        return jsonify({k: registry.get(k).serialise() for k in registry.list()})
    raise BadRequest("Bad Request")


# - Get device state
@app.route('/api/v1/devices/<device_uuid>', methods=['GET', 'DELETE'])
def device(device_uuid):
    registry = DeviceRegistry.singleton()
    if request.method == 'DELETE':
        if device_uuid is None:
            raise BadRequest("Bad Request")
        try:
            registry.remove(device_uuid)
        except KeyError as e:
            raise NotFound(device_uuid + " Not found")
    elif request.method == 'GET':
        device = registry.get(device_uuid)
        data = device.serialise()
        data['states'] = device.state()
        return jsonify(data)
    raise BadRequest("Bad Request")


# - Get/Set value on device
@app.route('/api/v1/devices/<device_uuid>/states/<state>', methods=['GET', 'POST'])
def states(device_uuid, state):
    registry = DeviceRegistry.singleton()
    if request.method == 'POST':
        device = registry.get(device_uuid)
        device.do_set_state(request.get_json()['value'])
    elif request.method == 'GET':
        device = registry.get(device_uuid)
        return jsonify({
            'value': device.state()[state]
        })
    raise BadRequest("Bad Request")


# - Registered handlers (get, post, delete)
@app.route('/api/v1/handlers/<name>', methods=['GET', 'POST', 'DELETE'])
def handlers(name=None):
    hr = HandlerRegistry.singleton()
    if request.method == 'POST':
        try:
            hr.add(request.get_json())
        except KeyError as e:
            raise BadRequest("Invalid POST data")
    elif request.method == 'DELETE':
        if name is None:
            raise BadRequest("Bad Request")
        try:
            hr.remove(name)
        except KeyError as e:
            raise NotFound(name + " Not found")
    elif request.method == 'GET':
        if name is None:
            return {k: hr.get(k).serialise() for k in hr.list()}
        return hr.get(name).serialise()
    return jsonify({
        'status': 'ok'
    })


def start():
    def run():
        app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
    thread = threading.Thread(target=run)
    thread.start()
    return thread
