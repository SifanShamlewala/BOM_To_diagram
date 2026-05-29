import svgwrite
from .base_icon import BaseIcon

class DeltaVSwitchIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="deltav_switch")
        x = cx - width / 2
        y = cy - height / 2

        # Body: rect(#4A4A4A fill)
        group.add(dwg.rect(insert=(x, y), size=(width, height), fill='#4A4A4A'))
        
        # DV stripe: rect(w=6, full height, x=0, fill=#2244CC)
        group.add(dwg.rect(insert=(x, y), size=(6, height), fill='#2244CC'))
        
        # 8 port rects: (8×6px each, y-centered, fill=#222, border #555) from x=20 spaced 14px apart
        for i in range(8):
            px = x + 20 + i * 14
            group.add(dwg.rect(insert=(px, cy - 3), size=(8, 6), fill='#222222', stroke='#555555', stroke_width=1))
            # Activity dots: circle(r=2, #00CC44) above each port, y=cy-8
            group.add(dwg.circle(center=(px + 4, cy - 8), r=2, fill='#00CC44'))
            
        # Label: "DV Switch" at (cx, bottom+10), font-size=8
        if not label:
            label = "DV Switch"
        group.add(dwg.text(label, insert=(cx, y + height + 10), text_anchor="middle", font_size=8, font_family="sans-serif", fill='#FFFFFF'))
        
        return group
