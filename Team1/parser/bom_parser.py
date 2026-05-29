from dataclasses import dataclass
from typing import List
import openpyxl

@dataclass
class ComponentDTO:
    id: int
    description: str
    quantity: int
    category: str
    part_number: str
    room: str

def parse_bom(xlsx_path: str) -> List[ComponentDTO]:
    """
    Reads CO2_Excel_Restored.xlsx.
    Tracks current_room by detecting rows with no Sr.No.
    Applies filter rules and returns clean ComponentDTO list.
    """
    DROP_CATEGORIES = {"MC", "CAB", "SWK", "SW", "FBR"}
    
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    sheet = wb.active

    current_room = None
    result = []

    for row in sheet.iter_rows(values_only=True):
        if all(cell is None for cell in row):
            continue

        sr_no = row[0]

        # Section header logic
        val_0 = str(sr_no).strip().upper()
        if val_0 == "SR. NO" or val_0 == "SR.NO":
            continue
            
        if "PDC" in val_0:
            current_room = "PDC_ROOM"
            continue
        elif "OPERATOR" in val_0:
            current_room = "OPERATOR_ROOM"
            continue

        try:
            id_val = int(sr_no)
        except (ValueError, TypeError):
            continue

        description = str(row[1]).strip() if row[1] else ""
        try:
            quantity = int(row[2])
        except (ValueError, TypeError):
            quantity = 1
            
        category = str(row[3]).strip() if row[3] else ""
        part_number = str(row[4]).strip() if row[4] else ""

        dto = ComponentDTO(
            id=id_val,
            description=description,
            quantity=quantity,
            category=category,
            part_number=part_number,
            room=current_room
        )

        # Apply drop rules
        if dto.category in DROP_CATEGORIES:
            continue
        if dto.category == "PWR" and "UPS" not in dto.description.upper():
            continue
        if dto.category in {"MON", "GEN"} and dto.room == "PDC_ROOM":
            continue

        result.append(dto)

    return result
