from energenie.Devices.MiHomeDevice import MiHomeDevice
import energenie.OpenThings as OpenThings
import random
import copy
import time
import logging

MIHO013_IDENTIFY = {
    "recs": [
        {
            "wr": True,
            "paramid": OpenThings.PARAM_IDENTIFY,
            "typeid": OpenThings.Value.UINT,
            "length": 0,
        }
    ]
}

MIHO013_EXERCISE = {
    "recs": [
        {
            "wr": True,
            "paramid": OpenThings.PARAM_EXERCISE,
            "typeid": OpenThings.Value.UINT,
            "length": 0
        }
    ]
}

MIHO013_BATTERY_LEVEL = {
    "recs": [
        {
            "wr": True,
            "paramid": OpenThings.PARAM_BATTERY_LEVEL,  # OpenThings.PARAM_IDENTIFY,
            "typeid": OpenThings.Value.UINT,
            "length": 0,
        }
    ]
}

MIHO013_DIAGNOSTICS = {
    "recs": [
        {
            "wr": True,
            "paramid": OpenThings.PARAM_DIAGNOSTICS,
            "typeid": OpenThings.Value.UINT,
            "length": 0
        }
    ]
}

MIHO013_SET_TEMPERATURE = {
    "recs": [
        {
            "wr": True,
            "paramid": OpenThings.PARAM_TEMPERATURE,
            "typeid": OpenThings.Value.SINT_BP8,
            "length": 2,
            "value": 0
        }
    ]
}

MIHO013_SET_VALVE_POSITION = {
    "recs": [
        {
            "wr": True,
            "paramid": OpenThings.PARAM_VALVE_POSITION,
            "typeid": 0x01,
            "length": 1,
            "value": 0
        }
    ]
}


class MIHO013(MiHomeDevice):
    _product_id = 0x03
    _product_name = "eTRV"
    _product_description = "Electronic, Thermostatic Radiator Valve"
    _product_rf = "FSK(tx, rx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/MIHO013"

    """An Energenie MiHome eTRV Radiator Valve"""
    def __init__(self, **kw_args):
        MiHomeDevice.__init__(self, **kw_args)

        class Readings():
            battery_voltage      = None
            ambient_temperature  = None
            pipe_temperature     = None
            setpoint_temperature = None
            valve_position       = None
            diagnostic_flags     = None
        self.readings = Readings()

        self.radio_config.inner_times = 4
        self.radio_config.outer_times = 4
        self.send_queue = []
        self.lastVoltageReading = None
        self.lastDiagnosticsReading = None
        self.voltageReadingPeriod = 3600
        self.diagnosticsReadingPeriod = 3600
        self._valvePosition = None

    def handle_message(self, payload):
        # send a message whilst receive window is open, this MUST be done first
        if len(self.send_queue) > 0:
            message = self.send_queue.pop(0)
            self.send_message(message)
            logging.debug("MIHO013 send %s (%s)" % (self.device_id, len(self.send_queue)))
            logging.debug("Sent message %s" % str(message))

        # check if it's time to refresh readings
        now = time.time()
        if self.voltageReadingPeriod is not None and (self.lastVoltageReading is None or now - self.lastVoltageReading > self.voltageReadingPeriod):
            self.queue_message(OpenThings.Message(MIHO013_BATTERY_LEVEL, header=self.__class__.header()))
            self.lastVoltageReading = now

        if self.diagnosticsReadingPeriod is not None and (self.lastDiagnosticsReading is None or now - self.lastDiagnosticsReading > self.diagnosticsReadingPeriod):
            self.queue_message(OpenThings.Message(MIHO013_DIAGNOSTICS, header=self.__class__.header()))
            self.lastDiagnosticsReading = now

        # extract data from message
        for rec in payload["recs"]:
            paramid = rec["paramid"]
            if "value" in rec:
                value = rec["value"]
                logging.debug("MIHO013 new data %s %s %s" % (self.device_id, OpenThings.paramid_to_paramname(paramid), value))
                if paramid == OpenThings.PARAM_TEMPERATURE:
                    self.readings.ambient_temperature = value
                if paramid == OpenThings.PARAM_VOLTAGE:
                    self.readings.battery_voltage = value
                if paramid == OpenThings.PARAM_DIAGNOSTICS:
                    self.readings.diagnostic_flags = value

    def queue_message(self, message):
        message.set(
            header_productid=self.__class__._product_id,
            header_sensorid=self.device_id,
            header_encryptPIP=int(random.randrange(0xFFFF))
        )
        logging.debug("Queuing message %s " % str(message))
        self.send_queue.append(copy.copy(message))

    def get_battery_voltage(self) -> float:  # ->voltage:float
        return self.readings.battery_voltage

    def get_ambient_temperature(self) -> float:  # -> temperature:float
        return self.readings.ambient_temperature

    def get_diagnostics(self):
        return self.readings.diagnostic_flags

    def get_setpoint_temperature(self) -> float:  # -> temperature:float
        return self.readings.setpoint_temperature

    def set_setpoint_temperature(self, temperature: float):
        self.readings.setpoint_temperature = temperature
        payload = OpenThings.Message(MIHO013_SET_TEMPERATURE, header=self.__class__.header()).copyof()
        if temperature < 0:
            temperature = 0
        if temperature > 30:
            temperature = 30
        payload.set(recs_TEMPERATURE_value=int(temperature * 256))
        self.queue_message(payload)

    def set_temperature(self, temperature: float):
        self.enable_thermostat()
        self.set_setpoint_temperature(temperature)

    def get_temperature(self) -> float:
        return self.get_ambient_temperature()

    def set_valve_position(self, position: int):
        payload = OpenThings.Message(MIHO013_SET_VALVE_POSITION, header=self.__class__.header()).copyof()
        payload.set(recs_VALVE_POSITION_value=position)
        self._valvePosition = position
        self.queue_message(payload)

    def get_valve_position(self) -> int:
        return self._valvePosition

    def set_identify(self):
        self.queue_message(OpenThings.Message(MIHO013_IDENTIFY, header=self.__class__.header()).copyof())

    def turn_on(self):
        self.set_valve_position(0)

    def turn_off(self):
        self.set_valve_position(1)

    def enable_thermostat(self):
        self.set_valve_position(2)
