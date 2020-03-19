from Devices.OOKSwitch import OOKSwitch


class ENER002(OOKSwitch):
    _product_name = "Socket Switch (Green Button)"
    _product_description = "Receive-only socket switch, featuring a green button."
    _product_rf = "OOK(rx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/ENER002"

    """A green button switch"""
    def __repr__(self):
        return "ENER002(%s,%s)" % (str(hex(self.device_id[0])), str(hex(self.device_id[1])))
