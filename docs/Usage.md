## Running device discovery

```
$ sudo pyenergenie -d
Listening for OpenThings signals...
(Press CTRL+C to stop)

Device detected
  Model: MIHO013
  ID: 6573

Do you wish to configure this device [Y/n]: y
Device name: Bedroom eTRV

Device detected
  Mode: MIHO0013
  ID: 4521
  
Do you wish to configure this device [Y/n]: y
Device name: Bedroom eTRV
```

## Manually configuring a device

```
sudo pyenergenie -i
Interactive configuration press ? for help.
> ?
  add       Add a device with a type and id
  remove    Remove a device by name or id
  list      list configured devices
  discover  Run discovery mode
  learn     Run OOK learning mode
  teach     Run OOK teaching mode
  debug     Echo raw RF output for debugging
type command ? for more detailed help.
> learn
Received signal 6532
Received signal 4231
> add ENER002 4231
> add MIHO002 6532
```

## Configuration file format 

```json
{
    "radio": {
        "type": "RFM69HCW",
        "frequency": "434.30 MHz",
        "MOSI": 10,
        "MISO": 9,
        "SCLK": 11,
        "CS": 7,
        "RESET": 25
    },
    "mqtt": {
        "host": "192.168.1.1",
        "port": 1172,
        "username": "energenie",
        "password": "secret"
    },
    "webhooks": [
        {
            "url": "https://192.168.1.1/my/endpoint",
            "headers": {
            		"Authorization": "Bearer xFgbHASsdASwDASASfeg.x.y"
            },
            "format": "JSON",
            "polling_interval": 600
        }
    ],
    "devices": [
        {
            "name": "Bedroom Radiator",
            "type": "MIHO013",
            "device_id": 3627,
            "enabled": True
        }
    ]
}
```

## Interfacing with pyenergenie 

Pyenergenie isn't trying to solve all of the problems of the smart home, in fact we want to keep things pretty simple in general. Obviously, because we're listening for things like door opens, motion, and temperatures we need a daemon running. Our daemon outputs by sending the current state information to an MQTT server, and subscribing to state changes on that server. 

It is also possible to add a webhook which will perform a GET request on the URL to get a configuration, and a POST request on a URL to set a configuration. 

Pyenergenie can also write to a unix socket or file JSON dumps of it's incoming signals, but it cannot receive instructions in this way.

Obviously pyenergenie is a python library and can be integrated into other services, such as flask, cherrypy, django, etc... 

### API usage

```
def my_main_loop():
    pyenergenie.iter()

    # Do my other main loop things
    
def main():
    while True:
        my_main_loop()
        
 if __name__ == '__main__':
     main()
```

```
# create a background thread with a callback in cherrypy 
```

```
# create a background thread with a callback in django 
```

```
# create a background thread with a callback in flask
```

```
# Examples of doing things 

# Discover everything and add it, this thread will continue until stopped
discover = pyenergenie.Discover(callback=pyenergenie.add)
discover.start()
# Do some other stuff
time.sleep(60)
discover.stop()

# Other functions to mirror what's going on
pyenergenie.learn()
pyenergenie.teach()
pyenergenie.list()
pyenergenie.remove()
pyenergenie.debug()
```

