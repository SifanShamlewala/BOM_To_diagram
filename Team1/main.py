from parser.bom_parser import parse_bom
from semantic.classifier import classify
from renderer.svg_composer import compose_svg
import os

def generate_diagram(bom_path: str, output_path: str = "output/diagram.svg") -> str:
    # 1. Parse Excel
    components = parse_bom(bom_path)
    
    # 2. Classify Semantic Roles
    plan = classify(components)
    
    # 3. Compute SVG
    svg = compose_svg(plan, output_path)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 4. Save
    svg.saveas(output_path)
    return output_path

if __name__ == "__main__":
    generate_diagram("CO2_Excel_Restored.xlsx")
