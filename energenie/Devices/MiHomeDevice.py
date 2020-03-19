from Devices.EnergenieDevice import EnergenieDevice
import OpenThings


JOIN_REQ = {
    "recs": [
        {
            "wr": False,
            "paramid": OpenThings.PARAM_JOIN,
            "typeid": OpenThings.Value.UINT,
            "length": 0
        }
    ]
}

JOIN_ACK = {
    "recs": [
        {
            "wr": False,
            "paramid": OpenThings.PARAM_JOIN,
            "typeid": OpenThings.Value.UINT,
            "length": 0
        }
    ]
}


class MiHomeDevice(EnergenieDevice):
    _product_rf = "FSK()"

    """An abstraction for Energenie new style MiHome FSK devices"""
    def __init__(self, name=None, device_id=None):
        EnergenieDevice.__init__(self, name, device_id)
        # TODO: These are now implied by the air_interface adaptor
        # self.radio_config.frequency  = 433.92
        # self.radio_config.modulation = "FSK"
        # self.radio_config.codec      = "OpenThings"

        # Different devices might have different PIP's
        # if we are cycling codes on each message?
        # self.config.encryptPID = CRYPT_PID
        # self.config.encryptPIP = CRYPT_PIP

    def get_config(self):
        """Get the persistable config, enough to reconstruct this class from a factory"""
        return {
            "type": self.__class__.__name__,
            # "manufacturer_id": self.__class__._manufacturer_id,  # Redundant data
            # "product_id": self.__class__._product_id, # Redundant data
            "device_id": self.device_id
        }

    def __repr__(self):
        return "MiHomeDevice(%s,%s,%s)" % (str(self.__class__.__manufacturer_id), str(self.__class__.__product_id), str(self.device_id))

    @classmethod
    def get_join_req(cls, mfrid, productid, deviceid):
        """Used for testing, synthesises a JOIN_REQ message from this device"""
        msg = OpenThings.Message(JOIN_REQ, header=cls.header())
        msg["header_mfrid"]     = mfrid
        msg["header_productid"] = productid
        msg["header_sensorid"]  = deviceid
        return msg

    def join_ack(self):
        """Send a join-ack to the real device"""
        print ("send join ack")
        # msg = OpenThings.Message(header_mfrid=MFRID_ENERGENIE, header_productid=self.product_id, header_sensorid=self.device_id)
        # msg[OpenThings.PARAM_JOIN] = {"wr":False, "typeid":OpenThings.Value.UINT, "length":0}
        # self.send_message(msg)

        payload = OpenThings.Message(JOIN_ACK, self.__class__.header())
        payload.set(header_productid=self.__class__._product_id,
                    header_sensorid=self.device_id)
        self.send_message(payload)

    # def handle_message(self, payload):
    # override for any specific handling

    def send_message(self, payload, encoded=False):
        # TODO: interface with air_interface
        # is payload a pydict with header at this point, and we have to call OpenThings.encode?
        # should the encode be done here, or in the air_interface adaptor?

        # TODO: at what point is the payload turned into a pydict?
        # TODO: We know it's going over OpenThings,
        # do we call OpenThings.encode(payload) here?
        # also OpenThings.encrypt() - done by encode() as default
        if self.air_interface is not None:
            # TODO: might want to send the config, either as a send parameter,
            # or by calling air_interface.configure() first?
            self.air_interface.send(payload, encoded=encoded, radio_config=self.radio_config)
        else:
            m = self.__class__._manufacturer_id
            p = self.__class__._product_id
            d = self.device_id
            print("send_message(mock[%s %s %s]):%s" % (str(m), str(p), str(d), payload))
