import svgwrite
from .base_icon import BaseIcon

class PulloutScreenIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="pullout_screen")
        x = cx - width / 2
        y = cy - height / 2

        # Main bezel: thin rect (#1A1A1A border, 2px), fills bounding box
        group.add(dwg.rect(insert=(x, y), size=(width, height), fill='none', stroke='#1A1A1A', stroke_width=2))
        
        # Screen area: inset 3px each side, fill #C8D0D8
        group.add(dwg.rect(insert=(x + 3, y + 3), size=(width - 6, height - 6), fill='#C8D0D8'))
        
        # Scanline texture: 4 thin horizontal lines (#B0B8C0, 1px)
        for i in range(1, 5):
            ly = y + 3 + (height - 6) * (i / 5)
            group.add(dwg.line(start=(x + 3, ly), end=(x + width - 3, ly), stroke='#B0B8C0', stroke_width=1))
            
        # Hinge left
        group.add(dwg.circle(center=(x + 6, cy), r=3, fill='#666666'))
        # Hinge right
        group.add(dwg.circle(center=(x + width - 6, cy), r=3, fill='#666666'))
        
        # Label
        if not label:
            label = "19″ Pullout Screen"
        group.add(dwg.text(label, insert=(cx, y + height + 10), text_anchor="middle", font_size=8, font_family="sans-serif", fill='#FFFFFF'))
        
        return group
