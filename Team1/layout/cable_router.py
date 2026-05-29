from dataclasses import dataclass
from typing import List

@dataclass
class PathLine:
    points: List[tuple]
    color: str
    stroke_width: float
    style: str
    label: str = None

def route_cables(canvas, fopp_pdc, fopp_opr) -> List[PathLine]:
    CABLE_TRAY_Y = 835
    paths = []
    
    cabinets = [
        (canvas.server_cabinet.x + canvas.server_cabinet.width // 2, canvas.server_cabinet.y + canvas.server_cabinet.height),
        (canvas.io_cabinet_1.x + canvas.io_cabinet_1.width // 2, canvas.io_cabinet_1.y + canvas.io_cabinet_1.height),
        (canvas.io_cabinet_2.x + canvas.io_cabinet_2.width // 2, canvas.io_cabinet_2.y + canvas.io_cabinet_2.height)
    ]
    
    for cx, bottom_y in cabinets:
        active_x = cx - 3
        redundant_x = cx + 3
        
        # Active line
        paths.append(PathLine(
            points=[
                (active_x, bottom_y),
                (active_x, CABLE_TRAY_Y),
                (fopp_pdc.x + fopp_pdc.width//2 - 3, CABLE_TRAY_Y),
                (fopp_pdc.x + fopp_pdc.width//2 - 3, fopp_pdc.y)
            ],
            color="#2244CC",
            stroke_width=2.5,
            style="solid"
        ))
        
        # Redundant line
        paths.append(PathLine(
            points=[
                (redundant_x, bottom_y),
                (redundant_x, CABLE_TRAY_Y),
                (fopp_pdc.x + fopp_pdc.width//2 + 3, CABLE_TRAY_Y),
                (fopp_pdc.x + fopp_pdc.width//2 + 3, fopp_pdc.y)
            ],
            color="#CC44AA",
            stroke_width=2.5,
            style="solid"
        ))
        
    # Operator room OWS cables
    ows_bottom_x = (1620 + 375) - 120
    ows_bottom_y = 850
    opr_cable_tray_y = 860
    
    # Active line (Operator)
    paths.append(PathLine(
        points=[
            (fopp_opr.x + fopp_opr.width//2 - 3, fopp_opr.y),
            (fopp_opr.x + fopp_opr.width//2 - 3, opr_cable_tray_y),
            (ows_bottom_x - 3, opr_cable_tray_y),
            (ows_bottom_x - 3, ows_bottom_y)
        ],
        color="#2244CC",
        stroke_width=2.5,
        style="solid"
    ))
    
    # Redundant line (Operator)
    paths.append(PathLine(
        points=[
            (fopp_opr.x + fopp_opr.width//2 + 3, fopp_opr.y),
            (fopp_opr.x + fopp_opr.width//2 + 3, opr_cable_tray_y),
            (ows_bottom_x + 3, opr_cable_tray_y),
            (ows_bottom_x + 3, ows_bottom_y)
        ],
        color="#CC44AA",
        stroke_width=2.5,
        style="solid"
    ))
        
    # Fibre line
    fopp_pdc_cx = fopp_pdc.x + fopp_pdc.width // 2
    fopp_pdc_bottom = fopp_pdc.y + fopp_pdc.height
    fopp_opr_cx = fopp_opr.x + fopp_opr.width // 2
    fopp_opr_bottom = fopp_opr.y + fopp_opr.height
    FIBRE_LINE_Y = fopp_pdc_bottom + 10
    
    paths.append(PathLine(
        points=[
            (fopp_pdc_cx, fopp_pdc_bottom),
            (fopp_pdc_cx, FIBRE_LINE_Y),
            (fopp_opr_cx, FIBRE_LINE_Y),
            (fopp_opr_cx, fopp_opr_bottom)
        ],
        color="#CC2200",
        stroke_width=3.0,
        style="solid",
        label="Fibre"
    ))
    
    return paths
