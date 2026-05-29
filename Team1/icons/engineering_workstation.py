import svgwrite
from .base_icon import BaseIcon

class EngineeringWorkstationIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="engineering_workstation")
        x = cx - width / 2
        y = cy - height / 2

        # Body: rect(#3A3A3A fill, #222 border)
        group.add(dwg.rect(insert=(x, y), size=(width, height), fill='#3A3A3A', stroke='#222222', stroke_width=1))
        
        # Rack ears: rect(3px wide, full height) at left and right edges (#4A4A4A)
        group.add(dwg.rect(insert=(x, y), size=(3, height), fill='#4A4A4A'))
        group.add(dwg.rect(insert=(x + width - 3, y), size=(3, height), fill='#4A4A4A'))
        
        # Drive bay 1: rect(12×10, x=15, cy-5, fill=#222, border #555)
        group.add(dwg.rect(insert=(x + 15, cy - 5), size=(12, 10), fill='#222222', stroke='#555555', stroke_width=1))
        
        # Drive bay 2: rect(12×10, x=30, cy-5, fill=#222, border #555)
        group.add(dwg.rect(insert=(x + 30, cy - 5), size=(12, 10), fill='#222222', stroke='#555555', stroke_width=1))
        
        # Port holes: 6 circles(r=3, #111, stroke #444) at x=55,65,75,85,95,105 along cy
        for offset in [55, 65, 75, 85, 95, 105]:
            group.add(dwg.circle(center=(x + offset, cy), r=3, fill='#111111', stroke='#444444', stroke_width=1))
            
        # Power LED: circle(r=3, fill=#00CC44) at (width-12, cy-8)
        group.add(dwg.circle(center=(x + width - 12, cy - 8), r=3, fill='#00CC44'))
        
        # Label: "EWS/PROPlus" at (cx, bottom+10), font-size=8
        if not label:
            label = "EWS/PROPlus"
        group.add(dwg.text(label, insert=(cx, y + height + 10), text_anchor="middle", font_size=8, font_family="sans-serif", fill='#FFFFFF'))
        
        return group
