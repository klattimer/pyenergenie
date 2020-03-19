from Devices.MiHomeLight import MiHomeLight


class MIHO026(MiHomeLight):
    _product_name = "Light Switch (Brushed Steel)"
    _product_description = "Receive-only light switch"
    _product_rf = "OOK(rx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/MIHO026"

    """Brushed Steel Finish"""
    def __repr__(self):
        return "MIHO026(%s,%s)" % (str(hex(self.device_id[0])), str(hex(self.device_id[1])))
