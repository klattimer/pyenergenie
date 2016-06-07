# run.py  31/05/2016  D.J.Whale
#
# Run the web_console

from bottle import run, debug, template, get, redirect, request

import energenie
import session

#===== DECORATORS =============================================================

def mode(m):
    """Redirect to mode handler, if one is active in the session"""
    def inner(*args, **kwargs):
        # get any current mode
        s = session.get_store()
        try:
            mode = s.get("mode")
        except KeyError:
            # mode is not defined
            return m(*args, **kwargs) # just call method unmodified

        # mode is defined
        if request.url == mode:
            # already at the right place
            return m(*args, **kwargs) # just call the method unmodified
        # if not in the right place, send redirect to the mode handler URL
        redirect(mode)

    return inner


def set_mode(s, url=None):
    """Set a mode URL to use for redirects"""
    if url == None:
        url = request.url # assume we are in the handler for the mode already
    s.set("mode", url)


def clear_mode(s):
    """Clear any mode URL to prevent mode redirects"""
    s.delete("mode")


#===== URL HANDLERS ===========================================================

# default session state brings user here
@get('/')
def do_home():
    """Render the home page"""
    return template('home')


@get('/list')
@session.needed
def do_list(s):
    try:
        registry = s.get("registry")
    except KeyError:
        # Try to make this as safe as possible, only init on very first use
        if energenie.registry == None:
            energenie.init()
        registry = energenie.registry
        s.set("registry", registry)

    # Get readings for any device that can send
    readings = {}
    for name in registry.names():
        c = energenie.registry.peek(name)
        if c.can_send():
            r = c.get_readings_summary()
            readings[name] = r

    return template("device_list", names=registry.names(), readings=readings)


@get('/edit/<name>')
@session.required
def do_edit(s, name):
    return template("edit", name=name)


is_receiving = False

@get('/receive_loop')
def do_receive_loop():
    """A cheat's way of pumping the receive loop, for testing"""
    # This will probably be fetched by the javascript on a repeating timer

    #TODO: Need to put a failing lock around this to prevent threading issues in web context
    #web server is single threaded at the moment, so we won't hit this quite yet.

    # Re-entrancy trap
    global is_receiving
    if not is_receiving:
        is_receiving = True
        energenie.loop()
        is_receiving = False
        redirect('/list')
    else:
        redirect('/list?busy')


@get('/watch_device/<name>')
@session.required
def do_watch_device(s, name):
    c = energenie.registry.get(name)
    energenie.fsk_router.list() # to console
    ##TESTING
    ##dummy_payload = {
    ##    "recs":[
    ##        {
    ##            "paramid": energenie.OpenThings.PARAM_DOOR_SENSOR,
    ##            "value": 1
    ##        }
    ##    ]
    ##}
    ##c.handle_message(dummy_payload)
    # Store device class instance in session store, so we can easily get its readings
    s.set("device.%s" % name, c)
    return "Watch is now active for %s" % name


@get('/unwatch_device/<name>')
@session.required
def do_unwatch_device(s, name):
    s.delete("device.%s" % name)
    energenie.registry.unget(name)
    return "Watch is now inactive for %s" % name


@get('/switch_device/<name>/<state>')
@session.required
def do_switch_device(s, name, state):
    ci = energenie.registry.get(name)
    state = state.upper()
    if state in ['1','YES', 'Y', 'TRUE', 'T', 'ON']:
        state = True
    else:
        state = False
    ci.set_switch(state)
    return "device %s switched to:%s" % (name, state)


# session state could lock us here regardless of URL, it is a mode
@get('/legacy_learn')
@session.required
def do_legacy_learn(s):
    return "TODO: legacy learning page - this enters a sticky MODE"
    # collect house code and device index
    # start broadcasting (new page)
    #   button to stop broadcasting (but if come back to web site, this is page you get)
    # stop goes back to list page  (or initiating page in HTTP_REFERRER?)


# session state could lock us here regardless of URL, it is a mode
@get('/mihome_discovery')
@session.required
def do_mihome_discovery(s):
    return "TODO: MiHome discovery page - this enters a sticky MODE"""
    # start listening
    #   page refreshes every few seconds with any new details
    #   button to stop listening (but if come back to website, this is the page you get)
    # stop goes back to list page  (or initiating page in HTTP_REFERRER?)


@get('/logger') # session state could lock us here regardless of URL, it is a mode
@session.required
def do_logger(s):
    return "TODO: Logger page - this enters a sticky MODE"
    # start listening
    #   page refreshes every few seconds with any new details
    #   button to stop logging (but if come back to website, this is the page you get)


@get('/rename_device/<old_name>/<new_name>')
@session.required
def do_rename_device(s, old_name, new_name):
    energenie.registry.rename(old_name, new_name)
    return "renamed device %s as %s" % (old_name, new_name)


@get('/delete_device/<name>')
@session.required
def do_delete_device(s, name):
    energenie.registry.delete(name)
    return "deleted device %s" % name


#----- APPLICATION STARTUP ----------------------------------------------------

debug(True)
run(port=8081, host="0.0.0.0")

# END
