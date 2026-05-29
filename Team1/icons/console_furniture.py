import svgwrite
from .base_icon import BaseIcon

class ConsoleFurnitureIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="console_furniture")
        x = cx - width / 2
        y = cy - height / 2
        
        # Work surface: rect(w=350, h=12, y=top, fill=#909090)
        group.add(dwg.rect(insert=(x, y), size=(width, 12), fill='#909090'))
        
        # Left support panel: rect(w=18, h=88, x=left, y=top+12, fill=#A0A0A0)
        group.add(dwg.rect(insert=(x, y + 12), size=(18, 88), fill='#A0A0A0'))
        
        # Right support panel: rect(w=18, h=88, x=right-18, y=top+12, fill=#A0A0A0)
        group.add(dwg.rect(insert=(x + width - 18, y + 12), size=(18, 88), fill='#A0A0A0'))
        
        # Under-desk void: we'll leave it empty so the room background shows through naturally.
        
        # Label: "OWS Console" at (cx, bottom+14), font-size=9
        if not label:
            label = "OWS Console"
        group.add(dwg.text(label, insert=(cx, y + height + 14), text_anchor="middle", font_size=9, font_family="sans-serif", fill='#000000'))
        
        return group
