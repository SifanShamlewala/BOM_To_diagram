import svgwrite
from .base_icon import BaseIcon

class ControllerIcon(BaseIcon):
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        group = dwg.g(id="pk750_controller")
        x = cx - width / 2
        y = cy - height / 2

        # Body: rect(#1A2A4A fill — dark navy, #0A1A3A border)
        group.add(dwg.rect(insert=(x, y), size=(width, height), fill='#1A2A4A', stroke='#0A1A3A', stroke_width=1))
        
        # Center divider: vertical line at cx, y+4 to y+h-4, stroke=#4466AA, 1px
        group.add(dwg.line(start=(cx, y + 4), end=(cx, y + height - 4), stroke='#4466AA', stroke_width=1))
        
        # LEFT sub-module (x to cx):
        # Status LED column: 4 circles(r=3) at x=15, evenly y-spaced; colors: green,amber,green,green
        led_y_spacing = (height - 20) / 3
        for i, color in enumerate(['#00CC44', '#FFBF00', '#00CC44', '#00CC44']):
            group.add(dwg.circle(center=(x + 15, y + 10 + i * led_y_spacing), r=3, fill=color))
        
        # Port row: 4 rects(8×5, border-radius=1) at bottom-left, spaced evenly
        port_spacing = (cx - x - 30) / 4
        for i in range(4):
            group.add(dwg.rect(insert=(x + 25 + i * port_spacing, y + height - 15), size=(8, 5), rx=1, ry=1, fill='#222222', stroke='#555555', stroke_width=1))

        # RIGHT sub-module (cx to right): Same mirrored pattern
        for i, color in enumerate(['#00CC44', '#FFBF00', '#00CC44', '#00CC44']):
            group.add(dwg.circle(center=(cx + 15, y + 10 + i * led_y_spacing), r=3, fill=color))
            
        for i in range(4):
            group.add(dwg.rect(insert=(cx + 25 + i * port_spacing, y + height - 15), size=(8, 5), rx=1, ry=1, fill='#222222', stroke='#555555', stroke_width=1))
            
        # "REDUNDANT" text: centered between modules at cy, font-size=7, fill=#AABBDD, letter-spacing=1
        text = dwg.text("REDUNDANT", insert=(cx, cy), text_anchor="middle", font_size=7, font_family="sans-serif", fill='#AABBDD')
        text['style'] = "letter-spacing: 1px"
        group.add(text)
        
        # Label: "PK Controller" at (cx, bottom+10), font-size=8
        if not label:
            label = "PK Controller"
        group.add(dwg.text(label, insert=(cx, y + height + 10), text_anchor="middle", font_size=8, font_family="sans-serif", fill='#FFFFFF'))
        
        return group
