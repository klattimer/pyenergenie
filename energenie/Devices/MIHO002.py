from Devices.OOKSwitch import OOKSwitch


class MIHO002(OOKSwitch):
    _product_name = "Socket Switch"
    _product_description = "Receive-only socket switch, featuring a purple button"
    _product_rf = "OOK(rx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/MIHO002"

    """A purple button MiHome switch"""
    def __repr__(self):
        return "MIHO002(%s,%s)" % (str(hex(self.device_id[0])), str(hex(self.device_id[1])))
