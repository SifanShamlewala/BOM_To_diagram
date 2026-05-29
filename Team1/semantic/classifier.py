import math
from dataclasses import dataclass
from typing import List, Optional
from parser.bom_parser import ComponentDTO

@dataclass
class StackItem:
    role: str
    u_height: int
    dto: ComponentDTO

@dataclass
class CabinetPlan:
    items: List[StackItem]

@dataclass
class TowerPlan:
    slot: int
    baseplate_count: int
    has_cioc: bool

@dataclass
class IOCabinetPlan:
    index: int
    towers: List[TowerPlan]

@dataclass
class FOPPNode:
    id: str
    room: str

@dataclass
class Connection:
    source: str
    target: str
    style: str
    color_a: str
    color_b: Optional[str] = None

@dataclass
class OperatorPlan:
    console: bool
    monitors: int
    tower_workstation: bool
    printer: bool
    firewall: bool

@dataclass
class PlacementPlan:
    server_cabinet: CabinetPlan
    io_cabinets: List[IOCabinetPlan]
    fopp_nodes: List[FOPPNode]
    operator_room: OperatorPlan
    connections: List[Connection]

def classify(components: List[ComponentDTO]) -> PlacementPlan:
    server_items = []
    
    opr_console = False
    opr_monitors = 0
    opr_ws = False
    opr_printer = False
    opr_firewall = False
    
    baseplate_count = 0
    
    for dto in components:
        desc = dto.description.upper()
        cat = dto.category.upper()
        
        if dto.room == "PDC_ROOM":
            if cat == "SCR":
                server_items.append(StackItem("pullout_screen", 1, dto))
            elif cat == "WS" and ("RACK" in desc or "PROPLUS" in desc or "PROFESSIONAL" in desc or "PLUS" in desc or "PREMIUM" in desc):
                if not any(item.role == "engineering_workstation" for item in server_items):
                    server_items.append(StackItem("engineering_workstation", 2, dto))
            elif cat == "CNTR" and "PK750" in desc:
                server_items.append(StackItem("controller", 4, dto))
            elif cat == "SWT" and "DELTAV" in desc:
                server_items.append(StackItem("deltav_switch", 1, dto))
            elif cat == "SWT" and ("HIRSHMAN" in desc or "HIRSCHMANN" in desc):
                server_items.append(StackItem("hirschmann_switch", 1, dto))
            elif cat == "UPS":
                server_items.append(StackItem("ups", 2, dto))
            elif cat == "CHARM" and "BASEPLATE ASSEMBLY" in desc:
                baseplate_count += dto.quantity
        elif dto.room == "OPERATOR_ROOM":
            if cat == "CON":
                opr_console = True
            elif cat == "MON":
                opr_monitors += dto.quantity
            elif cat == "WS" and ("TOWER" in desc or "FULL-SIZED" in desc):
                opr_ws = True
            elif cat == "PRT":
                opr_printer = True
            elif cat == "FW":
                opr_firewall = True

    role_order = {
        "pullout_screen": 1,
        "engineering_workstation": 2,
        "controller": 3,
        "deltav_switch": 4,
        "hirschmann_switch": 5,
        "ups": 6
    }
    server_items.sort(key=lambda x: role_order.get(x.role, 99))

    BASEPLATES_PER_TOWER = 8
    TOWERS_PER_CABINET = 3
    
    full_towers = baseplate_count // BASEPLATES_PER_TOWER
    remainder = baseplate_count % BASEPLATES_PER_TOWER
    
    tower_bp_counts = [BASEPLATES_PER_TOWER] * full_towers
    if remainder > 0:
        tower_bp_counts.append(remainder)
        
    io_cabinet_count = math.ceil(len(tower_bp_counts) / TOWERS_PER_CABINET)
    io_cabinets = []
    
    for cab_idx in range(io_cabinet_count):
        start = cab_idx * TOWERS_PER_CABINET
        assigned = tower_bp_counts[start : start + TOWERS_PER_CABINET]
        while len(assigned) < TOWERS_PER_CABINET:
            assigned.append(None)
            
        towers = []
        for slot, count in enumerate(assigned):
            if count is None:
                towers.append(TowerPlan(slot=slot, baseplate_count=0, has_cioc=False))
            else:
                towers.append(TowerPlan(slot=slot, baseplate_count=count, has_cioc=True))
                
        io_cabinets.append(IOCabinetPlan(index=cab_idx + 1, towers=towers))

    fopp_nodes = [
        FOPPNode(id="fopp_pdc", room="PDC_ROOM"),
        FOPPNode(id="fopp_opr", room="OPERATOR_ROOM")
    ]
    
    connections = [
        Connection("server_cabinet", "fopp_pdc", "dual", "#2244CC", "#CC44AA"),
        Connection("io_cabinet_1",   "fopp_pdc", "dual", "#2244CC", "#CC44AA"),
        Connection("io_cabinet_2",   "fopp_pdc", "dual", "#2244CC", "#CC44AA"),
        Connection("fopp_pdc",       "fopp_opr", "single", "#CC2200")
    ]
    
    opr_plan = OperatorPlan(
        console=opr_console,
        monitors=opr_monitors,
        tower_workstation=opr_ws,
        printer=opr_printer,
        firewall=opr_firewall
    )
    
    return PlacementPlan(
        server_cabinet=CabinetPlan(items=server_items),
        io_cabinets=io_cabinets,
        fopp_nodes=fopp_nodes,
        operator_room=opr_plan,
        connections=connections
    )
