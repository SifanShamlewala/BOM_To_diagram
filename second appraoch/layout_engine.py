class LayoutEngine:
    def __init__(self):
        self.room_padding = 40
        self.rack_width = 220
        self.rack_height = 600
        self.rack_spacing = 40

    def layout_rooms(self, rooms):
        x = 50
        y = 50
        for room in rooms:
            room["x"] = x
            room["y"] = y
            room["width"] = 1200
            room["height"] = 800
            x += room["width"] + 100

    def layout_enclosures(self, rooms, enclosures):
        encl_by_id = {e["id"]: e for e in enclosures}

        for room in rooms:
            x = room["x"] + self.room_padding
            y = room["y"] + 100

            for encl_id in room["enclosures"]:
                encl = encl_by_id[encl_id]
                encl["x"] = x
                encl["y"] = y
                encl["width"] = self.rack_width
                encl["height"] = self.rack_height

                x += self.rack_width + self.rack_spacing

    def layout_devices(self, enclosures, devices):
        dev_by_id = {d["id"]: d for d in devices}

        for encl in enclosures:
            if encl["type"] in ["server_cabinet", "io_cabinet"]:
                self._layout_rack_devices(encl, dev_by_id)
            elif encl["type"] == "operator_workstation":
                self._layout_operator_devices(encl, dev_by_id)

    def _layout_rack_devices(self, encl, dev_by_id):
        y = encl["y"] + 40
        for dev_id in encl["devices"]:
            dev = dev_by_id[dev_id]
            dev["x"] = encl["x"] + 20
            dev["y"] = y
            dev["width"] = encl["width"] - 40
            dev["height"] = 30
            y += 40

    def _layout_operator_devices(self, encl, dev_by_id):
        base_x = encl["x"]
        base_y = encl["y"]

        for dev_id in encl["devices"]:
            dev = dev_by_id[dev_id]

            if dev["type"] == "monitor":
                dev["x"] = base_x + 20
                dev["y"] = base_y + 20
            elif dev["type"] == "workstation":
                dev["x"] = base_x + 60
                dev["y"] = base_y + 200
            elif dev["type"] == "printer":
                dev["x"] = base_x + 150
                dev["y"] = base_y + 200
