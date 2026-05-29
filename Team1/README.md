#BOM to DCS Diagram Generator

A PoC tool that reads a DCS hardware Bill of Materials (BOM) from an Excel file and automatically generates a visual architecture diagram of the control system layout — no manual drawing required.

---

## What It Does

1. You upload a BOM Excel file through a browser-based UI
2. The tool parses and filters the hardware list
3. It calculates cabinet counts, tower layouts, and component placement
4. It generates a downloadable **SVG diagram** showing the full DCS architecture — rooms, cabinets, racks, icons, and cable connections

---

## Project Structure

```
├── app.py                  # Streamlit web application (entry point)
├── parser/
│   └── bom_parser.py       # Reads Excel BOM, filters components, detects rooms
├── semantic/
│   └── classifier.py       # Maps components to roles, calculates layout plan
├── layout/
│   ├── canvas.py           # SVG canvas dimensions and coordinate constants
│   ├── room_planner.py     # Positions rooms and cabinets on the canvas
│   ├── rack_planner.py     # Stacks items inside the server cabinet
│   ├── tower_planner.py    # Lays out CHARM towers inside I/O cabinets
│   └── cable_router.py     # Computes cable paths between cabinets and FOPP nodes
├── renderer/
│   └── svg_composer.py     # Assembles all elements into the final SVG file
├── icons/
│   ├── base_icon.py        # Shared interface for all icon classes
│   ├── cioc.py             # CIOC controller icon
│   ├── charm_baseplate.py  # CHARM baseplate icon
│   ├── controller.py       # PK750 controller icon
│   ├── deltav_switch.py    # DeltaV smart switch icon
│   ├── hirschmann_switch.py
│   ├── engineering_workstation.py
│   ├── tower_workstation.py
│   ├── fopp_mc.py          # Fibre Optic Patch Panel + Media Converter icon
│   ├── ups.py
│   ├── pullout_screen.py
│   ├── console_furniture.py
│   ├── monitor.py
│   ├── printer.py
│   ├── firewall.py
│   └── empty_tower_slot.py # Placeholder for unused tower slots
└── output/
    └── diagram.svg         # Generated output (created at runtime)
```

---

## Setup & Installation

**Requirements:** Python 3.9+

```bash
# Clone the repo and install dependencies
pip install -r requirements.txt
```

No other setup needed. The tool has no database or external services.

---

## Running the App

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## How to Use

The UI walks you through 5 steps:

| Step | Action |
|------|--------|
| 1 | Upload your BOM `.xlsx` file |
| 2 | Review the raw BOM table |
| 3 | Click **Generate Hierarchical Grouping** to see the parsed layout |
| 4 | Check the confirmation box to finalise |
| 5 | Click **Generate SVG** — view and download the diagram |

---

## BOM File Format

The Excel file must follow this column structure:

| Column | Content |
|--------|---------|
| A | Sr. No. |
| B | Item Description |
| C | Quantity |
| D | Category Code |
| E | Part Number |

Room sections are detected by header rows containing `PDC` or `OPERATOR` in column A (with no serial number). The tool currently expects exactly this format.

### Supported Category Codes

| Code | Hardware | Behaviour |
|------|----------|-----------|
| `CHARM` | CHARM Baseplates + CIOC | Used for tower/cabinet math |
| `CNTR` | PK750 Controller | Drawn in Server Cabinet |
| `SWT` | Network Switches | Drawn in Server Cabinet (type detected by description) |
| `WS` | Workstations | Rack type → Server Cabinet; Tower type → Operator Room |
| `UPS` | UPS | Drawn in Server Cabinet |
| `SCR` | Pullout Screen | Drawn in Server Cabinet |
| `FOPP` | Fibre Optic Patch Panel | Drawn as FOPP+MC icon, one per room |
| `MON` | Monitor | Drawn in Operator Room |
| `CON` | Operator Console | Drawn in Operator Room |
| `PRT` | Printer | Drawn in Operator Room |
| `FW` | Firewall | Drawn in Operator Room |
| `CAB`, `MC`, `SW`, `SWK`, `FBR`, `GEN` | Cabinets, media converters, software, fibre | Excluded from diagram |
| `PWR` | Power supplies | Excluded unless description contains `UPS` |

---

## How the Layout Is Calculated

### CHARM Tower Math

The number of I/O cabinets is derived automatically from the BOM baseplate quantity:

- **8 baseplates per tower** (1 CIOC on top + 8 baseplates below)
- **3 towers per I/O cabinet**
- Remaining/unused tower slots are drawn with a dashed border

*Example: 31 baseplates → 4 towers → 2 I/O cabinets (Cabinet 1: 3 towers, Cabinet 2: 1 active + 2 empty)*

### Server Cabinet Stack Order

Items are placed top-to-bottom in fixed U-height order:

```
Pullout Screen      (1U)
Engineering WS      (2U)
PK750 Controller    (4U)
DeltaV Switch       (1U)
Hirschmann Switch   (1U)
UPS                 (2U)
[blank panel]
```

### Cable Connections

| Connection | Style | Colour |
|------------|-------|--------|
| Each cabinet → PDC FOPP | Dual lines (active + redundant) | Blue + Magenta |
| PDC FOPP → Operator FOPP | Single line (inter-room fibre) | Red |

---

## Output

The generated SVG (`output/diagram.svg`) is a 2400 × 1050 px scalable diagram split into two room zones:

- **PDC Room** (left) — Server Cabinet, I/O Cabinets, PDC FOPP node
- **Operator Room** (right) — Console, monitors, workstation, printer, Operator FOPP node

A legend in the bottom-right explains cable colour coding.

---

## Known Limitations (PoC Scope)

- Only specified BOM format is supported — different column layouts will break parsing
- Adding a new hardware type requires writing a new icon class and a classifier rule
- The hierarchy view is display-only; drag-to-rearrange is not yet implemented
- No PDF or PowerPoint export at this stage
- No input validation feedback for malformed or missing BOM data

---


