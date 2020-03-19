from Devices.MiHomeLight import MiHomeLight


class MIHO008(MiHomeLight):
    _product_name = "Light Switch (White)"
    _product_description = "Receive-only light switch"
    _product_rf = "OOK(rx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/MIHO008"

    """White finish"""
    def __repr__(self):
        return "MIHO008(%s,%s)" % (str(hex(self.device_id[0])), str(hex(self.device_id[1])))
