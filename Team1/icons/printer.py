import svgwrite
from .base_icon import BaseIcon

class PrinterIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="printer")
        x = cx - width / 2
        y = cy - height / 2
        
        # Body: rect(#B0B0B0 fill, #888 border, border-radius=2)
        group.add(dwg.rect(insert=(x, y), size=(width, height), rx=2, ry=2, fill='#B0B0B0', stroke='#888888', stroke_width=1))
        
        # Output tray: rect(w=54, h=6, y=top+2, cx, fill=#A0A0A0) — ledge at top
        group.add(dwg.rect(insert=(cx - 27, y + 2), size=(54, 6), fill='#A0A0A0'))
        
        # Paper input: rect(w=54, h=8, y=bottom-10, cx) — thin slot, fill=#888
        group.add(dwg.rect(insert=(cx - 27, y + height - 10), size=(54, 8), fill='#888888'))
        
        # Status LED: circle(r=3, fill=#00CC44) at (right-8, top+10)
        group.add(dwg.circle(center=(x + width - 8, y + 10), r=3, fill='#00CC44'))
        
        # Label: "Printer" at (cx, bottom+12), font-size=9
        if not label:
            label = "Printer"
        group.add(dwg.text(label, insert=(cx, y + height + 12), text_anchor="middle", font_size=9, font_family="sans-serif", fill='#000000'))
        
        return group
