from energenie.Devices.MiHomeLight import MiHomeLight


class MIHO025(MiHomeLight):
    _product_name = "Light Switch (Chrome)"
    _product_description = "Receive-only light switch"
    _product_rf = "OOK(rx)"
    _product_url = "https://energenie4u.co.uk/catalogue/product/MIHO025"

    """Chrome Finish"""
    def __repr__(self):
        return "MIHO025(%s,%s)" % (str(hex(self.device_id[0])), str(hex(self.device_id[1])))
