import svgwrite

class BaseIcon:
    def draw(self, dwg: svgwrite.Drawing, cx: float, cy: float, width: float, height: float, label: str = None) -> svgwrite.container.Group:
        """
        dwg    = svgwrite.Drawing
        cx, cy = center of bounding box
        width/height = bounding box dimensions
        All sub-shapes defined as fractions of width/height → scale-safe
        Returns: SVG group element
        """
        raise NotImplementedError
