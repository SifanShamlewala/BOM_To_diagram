import svgwrite
from .base_icon import BaseIcon

class FirewallIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="firewall")
        x = cx - width / 2
        y = cy - height / 2
        
        # Body: rect(#3A3A3A fill, #222 border)
        group.add(dwg.rect(insert=(x, y), size=(width, height), fill='#3A3A3A', stroke='#222222', stroke_width=1))
        
        # Amber stripe: rect(w=8, full height, x=0, fill=#CC7700)
        group.add(dwg.rect(insert=(x, y), size=(8, height), fill='#CC7700'))
        
        # Shield icon: small SVG path (shield shape, w=14, h=16) at x=30, cy, fill=none, stroke=#FFFFFF, 1.5px
        shield_path = f"M{x+30},{cy-8} L{x+37},{cy-8} L{x+37},{cy} C{x+37},{cy+5} {x+33},{cy+8} {x+30},{cy+8} C{x+27},{cy+8} {x+23},{cy+5} {x+23},{cy} L{x+23},{cy-8} Z"
        group.add(dwg.path(d=shield_path, fill='none', stroke='#FFFFFF', stroke_width=1.5))
        
        # Port row: 4 rects(8×6, fill=#222, border #555) at right side, x from 120 spaced 12px
        for i in range(4):
            group.add(dwg.rect(insert=(x + 120 + i * 12, cy - 3), size=(8, 6), fill='#222222', stroke='#555555', stroke_width=1))
            
        # Label: "Firewall" at (cx, bottom+10), font-size=8
        if not label:
            label = "Firewall"
        group.add(dwg.text(label, insert=(cx, y + height + 10), text_anchor="middle", font_size=8, font_family="sans-serif", fill='#000000'))
        
        return group
