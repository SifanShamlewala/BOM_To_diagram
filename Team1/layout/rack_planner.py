from dataclasses import dataclass
from typing import List
from semantic.classifier import CabinetPlan

@dataclass
class RackItemLayout:
    role: str
    x: int
    y: int
    width: int
    height: int
    label: str

def plan_server_cabinet(cabinet: CabinetPlan, cab_x: int, cab_y: int, cab_width: int, cab_height: int) -> List[RackItemLayout]:
    interior_x = cab_x + 8
    interior_y = cab_y + 8
    interior_width = cab_width - 16
    u_height_px = 22
    
    layouts = []
    current_y = interior_y
    gap = 25
    
    role_to_label = {
        "pullout_screen": '19" Pullout Screen',
        "engineering_workstation": "EWS / PROPlus",
        "controller": "PK Controller",
        "deltav_switch": "Red. DCS Switches",
        "hirschmann_switch": "PIN Switch",
        "ups": "UPS"
    }
    
    for item in cabinet.items:
        h = item.u_height * u_height_px
        layouts.append(RackItemLayout(
            role=item.role,
            x=interior_x + interior_width // 2,
            y=current_y + h // 2,
            width=interior_width,
            height=h,
            label=role_to_label.get(item.role, item.role.replace('_', ' ').title())
        ))
        current_y += h + gap
        
    return layouts
