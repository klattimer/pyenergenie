from Devices.MiHomeLight import MiHomeLight


class MIHO024(MiHomeLight):
    __product_name = "Light Switch (Black Nickel)"
    __product_description = "Receive-only light switch"
    __product_rf = "OOK(rx)"
    __product_url = "https://energenie4u.co.uk/catalogue/product/MIHO024"

    """Black Nickel Finish"""
    def __repr__(self):
        return "MIHO024(%s,%s)" % (str(hex(self.device_id[0])), str(hex(self.device_id[1])))
