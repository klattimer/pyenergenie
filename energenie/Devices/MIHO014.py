from Devices.OOKSwitch import OOKSwitch


class MIHO014(OOKSwitch):
    _product_name = "Relay Switch (White)"
    _product_description = "Receive-only relay switch"
    _product_rf = "OOK(rx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/MIHO014"

    """Energenie 3kW switchable relay"""
    def __repr__(self):
        return "MIHO014(%s,%s)" % (str(hex(self.device_id[0])), str(hex(self.device_id[1])))
