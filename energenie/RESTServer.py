from flask import Flask, request, redirect
import threading
import json
app = Flask(__name__)

__version__ = "v1"


@app.route('/')
def root():
    return redirect("/api/" + __version__ + "/", code=302)


# redirect / -> /api/v1
@app.route('/api/v1/')
def apiroot():
    return json.dumps({
        'application': 'pyenergenie',
        'author': 'Karl Lattimer <karl@qdh.org.uk>',
        'url': 'github.com/klattimer/pyenergenie'
    })


# - Supported devices (get)
@app.route('/api/v1/hardware')
def hardware():
    pass


# - Registered devices (get, post, delete)
@app.route('/api/v1/devices')
def devices():
    pass


# - Get device state
@app.route('/api/v1/device')
def device():
    pass


# - Get/Set value on device
@app.route('/api/v1/device/<uuid>/feature')
def feature():
    pass


# - Registered handlers (get, post, delete)
@app.route('/api/v1/handlers')
def handlers():
    pass


def start():
    threading.Thread(target=app.run).start()
    return app
