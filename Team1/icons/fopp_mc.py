import svgwrite
from .base_icon import BaseIcon

class FoppMcIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="fopp_mc")
        x = cx - width / 2
        y = cy - height / 2
        
        # Bounding box: 90 × 54px
        # Outer rect: fill=none, stroke=#111111, stroke-width=1.5
        group.add(dwg.rect(insert=(x, y), size=(width, height), fill='none', stroke='#111111', stroke_width=1.5))
        
        # Upper-left triangle: polygon(top-left, top-right, bottom-left), fill=#2244CC
        group.add(dwg.polygon(points=[(x, y), (x + width, y), (x, y + height)], fill='#2244CC'))
        
        # Lower-right triangle: polygon(top-right, bottom-right, bottom-left), fill=#CC44AA
        group.add(dwg.polygon(points=[(x + width, y), (x + width, y + height), (x, y + height)], fill='#CC44AA'))
        
        # Diagonal line on top: stroke=#111, width=1px
        group.add(dwg.line(start=(x, y + height), end=(x + width, y), stroke='#111111', stroke_width=1))
        
        # Connection stubs: short horizontal lines (6px) protruding from left and right edges at cy
        group.add(dwg.line(start=(x - 6, cy), end=(x, cy), stroke='#111111', stroke_width=1.5))
        group.add(dwg.line(start=(x + width, cy), end=(x + width + 6, cy), stroke='#111111', stroke_width=1.5))
        
        # "FOPP" label: below rect, font-size=9, font-weight=bold, fill=#333
        if not label:
            label = "FOPP"
        text = dwg.text(label, insert=(cx, y + height + 15), text_anchor="middle", font_size=9, font_family="sans-serif", fill='#333333')
        text['font-weight'] = "bold"
        group.add(text)
        
        return group
