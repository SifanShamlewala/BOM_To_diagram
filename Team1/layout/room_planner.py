from dataclasses import dataclass
from semantic.classifier import OperatorPlan

@dataclass
class PositionedItem:
    role: str
    cx: int
    cy: int
    width: int
    height: int

def plan_operator_room(plan: OperatorPlan) -> list:
    items = []
    base_x = 1620 + 375
    
    # Grounded positions
    desk_cy = 750
    desk_h = 100
    desk_top = desk_cy - desk_h // 2  # 700
    
    if plan.console:
        items.append(PositionedItem("operator_console", base_x, desk_cy, 350, desk_h))
    if plan.monitors > 0:
        monitor_h = 55
        items.append(PositionedItem("monitor", base_x, desk_top - monitor_h // 2, 70, monitor_h))
    if plan.tower_workstation:
        tower_h = 140
        # Under the desk
        items.append(PositionedItem("tower_workstation", base_x - 120, desk_top + 10 + tower_h // 2, 55, tower_h))
    if plan.printer:
        printer_h = 65
        items.append(PositionedItem("printer", base_x + 120, desk_top - printer_h // 2, 70, printer_h))
    if plan.firewall:
        items.append(PositionedItem("firewall", base_x + 220, desk_cy, 180, 22))
        
    return items
