import svgwrite
from layout.canvas import CanvasLayout
from layout.rack_planner import plan_server_cabinet
from layout.tower_planner import plan_io_towers
from layout.room_planner import plan_operator_room
from layout.cable_router import route_cables
from icons import *

def compose_svg(plan, output_path: str = "output/diagram.svg"):
    canvas = CanvasLayout()
    dwg = svgwrite.Drawing(output_path, size=(canvas.width, canvas.height), profile='full')
    
    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=(canvas.width, canvas.height), fill="#FFFFFF"))
    
    # Title
    dwg.add(dwg.text(canvas.title, insert=(canvas.width // 2, canvas.title_y), text_anchor="middle", font_size=canvas.title_font_size, font_family="sans-serif", font_weight="bold", fill="#000000"))
    
    # Rooms
    dwg.add(dwg.rect(insert=(canvas.pdc_room.x, canvas.pdc_room.y), size=(canvas.pdc_room.width, canvas.pdc_room.height), fill="#F5F5F5", stroke="#999999", stroke_width=1))
    dwg.add(dwg.text("PDC ROOM", insert=(canvas.pdc_room.x + canvas.pdc_room.width // 2, canvas.pdc_room.y + 20), text_anchor="middle", font_size=16, font_family="sans-serif", font_weight="bold", fill="#333333"))

    dwg.add(dwg.rect(insert=(canvas.operator_room.x, canvas.operator_room.y), size=(canvas.operator_room.width, canvas.operator_room.height), fill="#F5F5F5", stroke="#999999", stroke_width=1))
    dwg.add(dwg.text("OPERATOR ROOM", insert=(canvas.operator_room.x + canvas.operator_room.width // 2, canvas.operator_room.y + 20), text_anchor="middle", font_size=16, font_family="sans-serif", font_weight="bold", fill="#333333"))

    # Room divider
    line = dwg.line(start=(canvas.divider.x1, canvas.divider.y1), end=(canvas.divider.x2, canvas.divider.y2), stroke=canvas.divider.stroke, stroke_width=1)
    line['stroke-dasharray'] = canvas.divider.dash
    dwg.add(line)
    
    # Cable Tray
    dwg.add(dwg.rect(insert=(canvas.cable_tray.x, canvas.cable_tray.y), size=(canvas.cable_tray.width, canvas.cable_tray.height), fill="#404040"))
    
    # Cabinets
    cabinets = [
        (canvas.server_cabinet, "SERVER CABINET"),
        (canvas.io_cabinet_1, "I/O CABINET #1"),
        (canvas.io_cabinet_2, "I/O CABINET #2")
    ]
    for cab, label in cabinets:
        dwg.add(dwg.rect(insert=(cab.x, cab.y), size=(cab.width, cab.height), fill="#2B2B2B", stroke="#111111", stroke_width=2))
        dwg.add(dwg.text(label, insert=(cab.x + cab.width // 2, cab.y - 10), text_anchor="middle", font_size=12, font_family="sans-serif", font_weight="bold", fill="#000000"))

    # Server Cabinet Items
    server_items = plan_server_cabinet(plan.server_cabinet, canvas.server_cabinet.x, canvas.server_cabinet.y, canvas.server_cabinet.width, canvas.server_cabinet.height)
    for item in server_items:
        icon_class = None
        if item.role == "pullout_screen": icon_class = PulloutScreenIcon
        elif item.role == "engineering_workstation": icon_class = EngineeringWorkstationIcon
        elif item.role == "controller": icon_class = ControllerIcon
        elif item.role == "deltav_switch": icon_class = DeltaVSwitchIcon
        elif item.role == "hirschmann_switch": icon_class = HirschmannSwitchIcon
        elif item.role == "ups": icon_class = UPSIcon
        
        if icon_class:
            icon = icon_class()
            dwg.add(icon.draw(dwg, item.x, item.y, item.width, item.height, item.label))

    # I/O Cabinets
    for i, cab_plan in enumerate(plan.io_cabinets):
        cab_rect = canvas.io_cabinet_1 if i == 0 else canvas.io_cabinet_2
        towers = plan_io_towers(cab_plan, cab_rect.x)
        
        # Draw tower labels
        for idx, t in enumerate(towers):
            dwg.add(dwg.text(f"Tower {chr(65+idx)}", insert=(t.x, t.y - 5), text_anchor="middle", font_size=10, font_family="sans-serif", fill="#DDDDDD"))
            if t.is_empty:
                dwg.add(EmptyTowerSlotIcon().draw(dwg, t.x, t.y, t.width, t.height))
                dwg.add(dwg.text("SPARE", insert=(t.x, t.y), text_anchor="middle", font_size=8, font_family="sans-serif", fill="#DDDDDD"))
            else:
                if t.cioc:
                    dwg.add(CIOCIcon().draw(dwg, t.cioc.x, t.cioc.y, t.cioc.width, t.cioc.height))
                for bp in t.baseplates:
                    dwg.add(CharmBaseplateIcon().draw(dwg, bp.x, bp.y, bp.width, bp.height, "alt" if bp.alt else ""))

    # Operator Room Items
    operator_items = plan_operator_room(plan.operator_room)
    for item in operator_items:
        icon_class = None
        if item.role == "operator_console": icon_class = ConsoleFurnitureIcon
        elif item.role == "monitor": icon_class = MonitorIcon
        elif item.role == "tower_workstation": icon_class = TowerWorkstationIcon
        elif item.role == "printer": icon_class = PrinterIcon
        elif item.role == "firewall": icon_class = FirewallIcon
        
        if icon_class:
            dwg.add(icon_class().draw(dwg, item.cx, item.cy, item.width, item.height))

    # Cables
    paths = route_cables(canvas, canvas.fopp_pdc_rect, canvas.fopp_opr_rect)
    for p in paths:
        if len(p.points) > 1:
            d = f"M {p.points[0][0]} {p.points[0][1]}"
            for pt in p.points[1:]:
                d += f" L {pt[0]} {pt[1]}"
            path = dwg.path(d=d, fill="none", stroke=p.color, stroke_width=p.stroke_width)
            dwg.add(path)
            
            if p.label:
                mid_x = (p.points[1][0] + p.points[2][0]) // 2
                mid_y = p.points[1][1]
                dwg.add(dwg.text(p.label, insert=(mid_x, mid_y - 5), text_anchor="middle", font_size=9, font_family="sans-serif", font_weight="bold", fill=p.color))

    # FOPP Nodes
    dwg.add(FoppMcIcon().draw(dwg, canvas.fopp_pdc_cx, canvas.fopp_pdc_cy, canvas.fopp_pdc_rect.width, canvas.fopp_pdc_rect.height, "[PDC]"))
    dwg.add(FoppMcIcon().draw(dwg, canvas.fopp_opr_cx, canvas.fopp_opr_cy, canvas.fopp_opr_rect.width, canvas.fopp_opr_rect.height, "[OPR]"))
    
    return dwg
