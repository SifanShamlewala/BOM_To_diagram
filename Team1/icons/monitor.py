import svgwrite
from .base_icon import BaseIcon

class MonitorIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="monitor")
        x = cx - width / 2
        y = cy - height / 2
        
        # Bezel: rect(w=70, h=42, fill=#1A1A1A, border-radius=3)
        group.add(dwg.rect(insert=(x, y), size=(width, 42), rx=3, ry=3, fill='#1A1A1A'))
        
        # Screen: rect inset 4px each side, fill=#4488BB, border-radius=1
        group.add(dwg.rect(insert=(x + 4, y + 4), size=(width - 8, 42 - 8), rx=1, ry=1, fill='#4488BB'))
        
        # Stand: trapezoid(top-width=8, bottom-width=16, height=10) centered below bezel
        stand_y = y + 42
        group.add(dwg.polygon(points=[
            (cx - 4, stand_y),
            (cx + 4, stand_y),
            (cx + 8, stand_y + 10),
            (cx - 8, stand_y + 10)
        ], fill='#1A1A1A'))
        
        # Base foot: rect(w=40, h=4, y=bottom-4) centered
        group.add(dwg.rect(insert=(cx - 20, y + height - 4), size=(40, 4), fill='#1A1A1A'))
        
        # Label: "Monitor" at (cx, bottom+14), font-size=8
        if not label:
            label = "Monitor"
        group.add(dwg.text(label, insert=(cx, y + height + 14), text_anchor="middle", font_size=8, font_family="sans-serif", fill='#000000'))
        
        return group
