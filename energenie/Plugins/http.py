
# Publishes a route for
# - Describing this device
# redirect / -> /api/v1
@route('/api/v1/')
# - Supported devices (get)
@route('/api/v1/hardware')
# - Registered devices (get, post, delete)
@route('/api/v1/devices')
# - Get device state
@route('/api/v1/device')
# - Get/Set value on device
@route('/api/v1/device/<uuid>/feature')
# - Registered handlers (get, post, delete)
@route('/api/v1/handlers')
