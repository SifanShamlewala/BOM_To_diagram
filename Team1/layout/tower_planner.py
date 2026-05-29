from dataclasses import dataclass
from typing import List, Optional
from semantic.classifier import IOCabinetPlan

@dataclass
class CIOCLayout:
    x: int
    y: int
    width: int
    height: int

@dataclass
class BaseplateLayout:
    x: int
    y: int
    width: int
    height: int
    alt: bool

@dataclass
class TowerLayout:
    slot: int
    x: int
    y: int
    width: int
    height: int
    is_empty: bool
    cioc: Optional[CIOCLayout]
    baseplates: List[BaseplateLayout]

def plan_io_towers(cabinet: IOCabinetPlan, cab_x: int) -> List[TowerLayout]:
    CABINET_ABS_TOP_Y = 250
    CABINET_HEIGHT = 450
    IO_CABINET_INTERIOR_MARGIN_X = 5
    IO_CABINET_INTERIOR_MARGIN_TOP = 10
    TOWER_WIDTH = 100
    TOWER_GAP = 5
    CIOC_HEIGHT = 55
    BASEPLATE_HEIGHT = 18

    interior_x = cab_x + IO_CABINET_INTERIOR_MARGIN_X
    interior_y = CABINET_ABS_TOP_Y + IO_CABINET_INTERIOR_MARGIN_TOP
    tower_height = CABINET_HEIGHT - 20
    
    tower_layouts = []
    for slot_idx, tower_plan in enumerate(cabinet.towers):
        tower_x = interior_x + slot_idx * (TOWER_WIDTH + TOWER_GAP)
        
        if tower_plan.baseplate_count == 0:
            tower_layouts.append(TowerLayout(
                slot=slot_idx,
                x=tower_x + TOWER_WIDTH // 2, y=interior_y + tower_height // 2,
                width=TOWER_WIDTH,
                height=tower_height,
                is_empty=True,
                cioc=None,
                baseplates=[]
            ))
        else:
            cioc_layout = CIOCLayout(
                x=tower_x + TOWER_WIDTH // 2, y=interior_y + CIOC_HEIGHT // 2,
                width=TOWER_WIDTH, height=CIOC_HEIGHT
            )
            baseplates = []
            bp_y_start = interior_y + CIOC_HEIGHT + 3
            for bp_idx in range(tower_plan.baseplate_count):
                baseplates.append(BaseplateLayout(
                    x=tower_x + TOWER_WIDTH // 2,
                    y=bp_y_start + bp_idx * BASEPLATE_HEIGHT + BASEPLATE_HEIGHT // 2,
                    width=TOWER_WIDTH,
                    height=BASEPLATE_HEIGHT,
                    alt=bool(bp_idx % 2)
                ))
            tower_layouts.append(TowerLayout(
                slot=slot_idx, x=tower_x + TOWER_WIDTH // 2, y=interior_y + tower_height // 2,
                width=TOWER_WIDTH, height=tower_height,
                is_empty=False,
                cioc=cioc_layout, baseplates=baseplates
            ))
            
    return tower_layouts
