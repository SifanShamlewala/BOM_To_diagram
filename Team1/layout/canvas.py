from dataclasses import dataclass

@dataclass
class Rect:
    x: int
    y: int
    width: int
    height: int

@dataclass
class Line:
    x1: int
    y1: int
    x2: int
    y2: int
    dash: str
    stroke: str

class CanvasLayout:
    def __init__(self):
        self.width = 2400
        self.height = 1050
        self.title = "CO2 Capture Plant"
        self.title_font_size = 20
        self.title_y = 24
        
        self.pdc_room = Rect(30, 40, 1580, 960)
        self.operator_room = Rect(1620, 40, 750, 960)
        
        self.divider = Line(x1=1610, y1=40, x2=1610, y2=1000, dash="8,4", stroke="#888888")
        
        self.server_cabinet = Rect(70, 250, 220, 450)
        self.io_cabinet_1 = Rect(340, 250, 330, 450)
        self.io_cabinet_2 = Rect(720, 250, 330, 450)
        
        self.cable_tray = Rect(70, 835, 980, 10)
        
        self.fopp_pdc_cx = (180 + 885) // 2
        self.fopp_pdc_cy = 882
        self.fopp_pdc_rect = Rect(self.fopp_pdc_cx - 45, self.fopp_pdc_cy - 27, 90, 54)
        
        self.fopp_opr_cx = 1720
        self.fopp_opr_cy = 900
        self.fopp_opr_rect = Rect(self.fopp_opr_cx - 45, self.fopp_opr_cy - 27, 90, 54)
