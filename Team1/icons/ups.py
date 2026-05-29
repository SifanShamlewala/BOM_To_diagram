import svgwrite
from .base_icon import BaseIcon

class UPSIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="ups")
        x = cx - width / 2
        y = cy - height / 2

        # Body: rect(#282828 fill, #111 border)
        group.add(dwg.rect(insert=(x, y), size=(width, height), fill='#282828', stroke='#111111', stroke_width=1))
        
        # APC stripe: rect(h=4, full width, y=top, fill=#2244CC)
        group.add(dwg.rect(insert=(x, y), size=(width, 4), fill='#2244CC'))
        
        # Display: rect(50×16, centered-left at x=20, y=cy-8, fill=#1A2A1A, border #00CC44 2px glow-ish)
        group.add(dwg.rect(insert=(x + 20, cy - 8), size=(50, 16), fill='#1A2A1A', stroke='#00CC44', stroke_width=2))
        
        # Battery bar: 5 segments(8×8 each, x from 80, y=cy-4):
        # Segments 1-4: fill=#00CC44, Segment 5: fill=#444 (80% full)
        for i in range(4):
            group.add(dwg.rect(insert=(x + 80 + i * 10, cy - 4), size=(8, 8), fill='#00CC44'))
        group.add(dwg.rect(insert=(x + 80 + 40, cy - 4), size=(8, 8), fill='#444444'))
        
        # Outlet dots: 3 circles(r=4, fill=#111, border #666) at right side
        for i in range(3):
            group.add(dwg.circle(center=(x + width - 15 - i * 15, cy), r=4, fill='#111111', stroke='#666666', stroke_width=1))
            
        # Label: "UPS" at (cx, bottom+10), font-size=8
        if not label:
            label = "UPS"
        group.add(dwg.text(label, insert=(cx, y + height + 10), text_anchor="middle", font_size=8, font_family="sans-serif", fill='#FFFFFF'))
        
        return group
