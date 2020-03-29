from energenie.Devices.MiHomeDevice import MiHomeDevice
import energenie.OpenThings as OpenThings


SWITCH = {
    "recs": [
        {
            "wr": True,
            "paramid": OpenThings.PARAM_SWITCH_STATE,
            "typeid": OpenThings.Value.UINT,
            "length": 1,
            "value": 0  # FILL IN
        }
    ]
}


class MIHO005(MiHomeDevice):
    _product_id = 0x02
    _product_name = "Socket Adapter Plus"
    _product_description = "The Adapter Plus allows you to monitor the power being used and control of the attached device."
    _product_rf = "FSK(tx,rx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/MIHO005"

    """An Energenie MiHome Adaptor Plus"""
    def __init__(self, **kw_args):
        MiHomeDevice.__init__(self, **kw_args)

        class Readings():
            switch         = None
            voltage        = None
            frequency      = None
            current        = None
            apparent_power = None
            reactive_power = None
            real_power     = None
        self.readings = Readings()

        self.radio_config.inner_times = 4

    @staticmethod
    def get_join_req(deviceid):
        """Get a synthetic join request from this device, for testing"""
        return MiHomeDevice.get_join_req(MIHO005._manufacturer_id, MIHO005._product_id, deviceid)

    def handle_message(self, payload):
        # print("MIHO005 new data %s %s" % (self.device_id, payload))
        for rec in payload["recs"]:
            paramid = rec["paramid"]
            # TODO: consider making this table driven and allowing our base class to fill our readings in for us
            #  then just define the mapping table in __init__ (i.e. paramid->Readings field name)
            value = rec["value"]
            if paramid == OpenThings.PARAM_SWITCH_STATE:
                self.readings.switch = ((value is True) or (value != 0))
            elif paramid == OpenThings.PARAM_VOLTAGE:
                self.readings.voltage = value
            elif paramid == OpenThings.PARAM_CURRENT:
                self.readings.current = value
            elif paramid == OpenThings.PARAM_REAL_POWER:
                self.readings.real_power = value
            elif paramid == OpenThings.PARAM_APPARENT_POWER:
                self.readings.apparent_power = value
            elif paramid == OpenThings.PARAM_REACTIVE_POWER:
                self.readings.reactive_power = value
            elif paramid == OpenThings.PARAM_FREQUENCY:
                self.readings.frequency = value
            else:
                try:
                    param_name = OpenThings.param_info[paramid]['n']  # name
                except:
                    param_name = "UNKNOWN_%s" % str(hex(paramid))
                print("unwanted paramid: %s" % param_name)

    def turn_on(self):
        # TODO: header construction should be in MiHomeDevice as it is shared?
        payload = OpenThings.Message(SWITCH)
        payload.set(header_productid=self.__class__._product_id,
                    header_sensorid=self.device_id,
                    recs_SWITCH_STATE_value=True)
        self.send_message(payload)

    def turn_off(self):
        # TODO: header construction should be in MiHomeDevice as it is shared?
        payload = OpenThings.Message(SWITCH, header=self.__class__.header())
        payload.set(header_productid=self.__class__._product_id,
                    header_sensorid=self.device_id,
                    recs_SWITCH_STATE_value=False)
        self.send_message(payload)

    def set_switch_state(self, state: bool):
        if state:
            self.turn_on()
        else:
            self.turn_off()

    def get_switch_state(self) -> bool:
        """Last stored state of the switch, might be None if unknown"""
        return self.readings.switch

    # TODO: difference between 'is on and 'is requested on'
    # TODO: difference between 'is off' and 'is requested off'
    # TODO: switch state might be 'unknown' if not heard.
    # TODO: switch state might be 'turning_on' or 'turning_off' if send request and not heard response yet

    def is_on(self):  # -> boolean
        """True, False, or None if unknown"""
        s = self.get_switch_state()
        if s is None: return None
        return s

    def is_off(self):  # -> boolean
        """True, False, or None if unknown"""
        s = self.get_switch_state()
        if s is None: return None
        return not s

    def get_voltage(self) -> float:  # -> voltage:float
        """Last stored state of voltage reading, None if unknown"""
        if self.readings.voltage is None:
            raise RuntimeError("No voltage reading received yet")
        return self.readings.voltage

    def get_frequency(self) -> float:  # -> frequency:float
        """Last stored state of frequency reading, None if unknown"""
        if self.readings.frequency is None:
            raise RuntimeError("No frequency reading received yet")
        return self.readings.frequency

    def get_apparent_power(self) -> float:  # ->power:float
        """Last stored state of apparent power reading, None if unknown"""
        if self.readings.apparent_power is None:
            raise RuntimeError("No apparent power reading received yet")
        return self.readings.apparent_power

    def get_reactive_power(self) -> float:  # -> power:float
        """Last stored state of reactive power reading, None if unknown"""
        if self.readings.reactive_power is None:
            raise RuntimeError("No reactive power reading received yet")
        return self.readings.reactive_power

    def get_real_power(self) -> float:  # -> power:float
        """Last stored state of real power reading, None if unknown"""
        if self.readings.real_power is None:
            raise RuntimeError("No real power reading received yet")
        return self.readings.real_power
