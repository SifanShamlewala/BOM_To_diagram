import svgwrite
from .base_icon import BaseIcon

class HirschmannSwitchIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="hirschmann_switch")
        x = cx - width / 2
        y = cy - height / 2

        # Body: rect(#505050 fill)
        group.add(dwg.rect(insert=(x, y), size=(width, height), fill='#505050'))
        
        # Hirsch stripe: rect(w=6, full height, x=0, fill=#CC6622)
        group.add(dwg.rect(insert=(x, y), size=(6, height), fill='#CC6622'))
        
        # Top row ports: 4 rects(8×5, border-radius=2, fill=#222) at y=cy-7, x from 20, spaced 16px
        for i in range(4):
            group.add(dwg.rect(insert=(x + 20 + i * 16, cy - 7), size=(8, 5), rx=2, ry=2, fill='#222222'))
            
        # Bottom row ports: 4 rects same at y=cy+2
        for i in range(4):
            group.add(dwg.rect(insert=(x + 20 + i * 16, cy + 2), size=(8, 5), rx=2, ry=2, fill='#222222'))
            
        # Label: "Red. DCS Switches" at (cx, bottom+10), font-size=8
        if not label:
            label = "Red. DCS Switches"
        group.add(dwg.text(label, insert=(cx, y + height + 10), text_anchor="middle", font_size=8, font_family="sans-serif", fill='#FFFFFF'))
        
        return group
