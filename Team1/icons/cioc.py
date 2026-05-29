import svgwrite
from .base_icon import BaseIcon

class CIOCIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="cioc")
        x = cx - width / 2
        y = cy - height / 2
        
        # Bounding box: TOWER_WIDTH × 55px (width=100)
        # Body: rect(#3D3D3D fill, #555 border)
        group.add(dwg.rect(insert=(x, y), size=(width, height), fill='#3D3D3D', stroke='#555555', stroke_width=1))
        
        # Two copper port holes: circle(r=6, fill=#885533, border #AA7744) at (cx-14,cy) and (cx+14,cy)
        group.add(dwg.circle(center=(cx - 14, cy), r=6, fill='#885533', stroke='#AA7744', stroke_width=1))
        group.add(dwg.circle(center=(cx + 14, cy), r=6, fill='#885533', stroke='#AA7744', stroke_width=1))
        
        # Status LED pair: circle(r=3, #00CC44) at (cx-6, cy+18), circle(r=3, #00CC44) at (cx+6, cy+18)
        group.add(dwg.circle(center=(cx - 6, cy + 18), r=3, fill='#00CC44'))
        group.add(dwg.circle(center=(cx + 6, cy + 18), r=3, fill='#00CC44'))
        
        # "CIOC" text: centered top, font-size=8, fill=#AAAAAA
        group.add(dwg.text("CIOC", insert=(cx, y + 15), text_anchor="middle", font_size=8, font_family="sans-serif", fill='#AAAAAA'))
        
        return group
