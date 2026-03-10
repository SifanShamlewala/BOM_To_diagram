"""
DeltaV DCS Architecture Engine
Stage 2: Semantic JSON → Architecture JSON

Deterministic. No coordinates. No rendering logic.

Key design decisions:
- FOPP is standalone (outside all cabinets) — inter-room fiber connector
- FOPP connects to all cabinets within its own room
- FOPP ↔ FOPP links are the inter-room connections
- CIOC is auto-inserted into IO cabinets (1 CIOC per 8 baseplates = 1 tower, 3 towers per cabinet)
- No intra-cabinet connection detail yet
"""

import json
from dataclasses import dataclass
from typing import Optional


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

@dataclass
class ArchitectureConfig:
    baseplates_per_tower: int = 8        # CHARMs per CIOC
    towers_per_io_cabinet: int = 3       # towers per IO cabinet → 24 baseplates/cabinet


# ─────────────────────────────────────────────
# Architecture Engine
# ─────────────────────────────────────────────

class ArchitectureEngine:

    def __init__(self, config: Optional[ArchitectureConfig] = None):
        self.config = config or ArchitectureConfig()

    @property
    def baseplates_per_io_cabinet(self) -> int:
        return self.config.baseplates_per_tower * self.config.towers_per_io_cabinet

    # ── Main entry point ───────────────────────

    def build(self, semantic_json: dict) -> dict:
        output_rooms = []
        fopp_ids_by_room = []

        for room in semantic_json["rooms"]:
            room_type = room["room_type"]
            if room_type == "OTHER":
                built = self._build_other_room(room)
            elif room_type == "OPERATOR":
                built = self._build_operator_room(room)
            else:
                raise ValueError(f"Unknown room_type: {room_type}")

            output_rooms.append(built)

            for fopp in built.get("fopp_nodes", []):
                fopp_ids_by_room.append({
                    "room_type": room_type,
                    "fopp_id": fopp["node_id"]
                })

        inter_room_connections = self._build_inter_room_connections(fopp_ids_by_room)

        return {
            "rooms": output_rooms,
            "inter_room_connections": inter_room_connections
        }

    # ── OTHER room ─────────────────────────────

    def _build_other_room(self, room: dict) -> dict:
        cabinets = []
        fopp_nodes = []
        intra_room_connections = []

        # SERVER cabinet
        srv_devices = []
        cntr_data = room.get("CNTR", {})
        cntr_qty = cntr_data.get("quantity", 0)
        redundant = cntr_data.get("redundant", False)

        if cntr_qty > 0:
            num_controllers = 2 if redundant else cntr_qty
            for i in range(num_controllers):
                role = ("PRIMARY" if i == 0 else "SECONDARY") if redundant else None
                dev_id = (f"CNTR-{'PRI' if i == 0 else 'SEC'}") if redundant else f"CNTR-{i+1:02d}"
                srv_devices.append({"device_id": dev_id, "type": "CNTR", "redundant_role": role})

        for comp in room.get("ENC_COMP", []):
            for i in range(comp["quantity"]):
                slug = comp["part_name"].replace(" ", "_").upper()
                srv_devices.append({
                    "device_id": f"ENC-{slug}-{i+1:02d}",
                    "type": "ENC_COMP",
                    "part_name": comp["part_name"]
                })

        if srv_devices:
            cabinets.append({"cabinet_id": "SRV-01", "type": "SERVER", "devices": srv_devices})

        # IO cabinets — with auto-inserted CIOCs
        charm_baseplates = room.get("CHARM", {}).get("baseplates", 0)
        if charm_baseplates > 0:
            io_cabinets = self._build_io_cabinets(charm_baseplates)
            cabinets.extend(io_cabinets)

        # FOPP — standalone, outside cabinets
        fopp_qty = room.get("FOPP", {}).get("quantity", 0)
        for f in range(fopp_qty):
            fopp_id = f"FOPP-OTHER-{f+1:02d}"
            fopp_nodes.append({"node_id": fopp_id, "type": "FOPP"})
            for cab in cabinets:
                intra_room_connections.append({
                    "from": fopp_id,
                    "to": cab["cabinet_id"],
                    "link_type": "FOPP_TO_CABINET"
                })

        return {
            "room_type": "OTHER",
            "cabinets": cabinets,
            "fopp_nodes": fopp_nodes,
            "intra_room_connections": intra_room_connections
        }

    # ── IO cabinet builder (with CIOC insertion) ──

    def _build_io_cabinets(self, total_baseplates: int) -> list:
        """
        Groups baseplates into IO cabinets.
        Each cabinet has up to towers_per_io_cabinet towers.
        Each tower = 1 CIOC (auto-inserted) + baseplates_per_tower CHARM baseplates.
        """
        n = self.baseplates_per_io_cabinet
        total_cabinets = (total_baseplates + n - 1) // n  # ceiling division

        cabinets = []
        bp_index = 1
        cioc_index = 1

        for cab_idx in range(total_cabinets):
            remaining_in_cab = min(n, total_baseplates - cab_idx * n)
            towers_in_cab = (remaining_in_cab + self.config.baseplates_per_tower - 1) // self.config.baseplates_per_tower

            towers = []
            for t in range(towers_in_cab):
                bps_in_tower = min(
                    self.config.baseplates_per_tower,
                    total_baseplates - (cab_idx * n + t * self.config.baseplates_per_tower)
                )
                baseplates = [
                    {"device_id": f"CHARM-BP-{bp_index + j:02d}", "type": "CHARM"}
                    for j in range(bps_in_tower)
                ]
                towers.append({
                    "tower_index": t,
                    "cioc": {
                        "device_id": f"CIOC-{cioc_index:02d}",
                        "type": "CIOC"
                    },
                    "baseplates": baseplates
                })
                bp_index += bps_in_tower
                cioc_index += 1

            cabinets.append({
                "cabinet_id": f"IO-{cab_idx+1:02d}",
                "type": "IO",
                "towers": towers
            })

        return cabinets

    # ── OPERATOR room ──────────────────────────

    def _build_operator_room(self, room: dict) -> dict:
        cabinets = []
        fopp_nodes = []
        intra_room_connections = []

        wd_devices = []
        for comp in room.get("ENC_COMP", []):
            for i in range(comp["quantity"]):
                slug = comp["part_name"].replace(" ", "_").upper()
                wd_devices.append({
                    "device_id": f"WD-{slug}-{i+1:02d}",
                    "type": "ENC_COMP",
                    "part_name": comp["part_name"]
                })

        if wd_devices:
            cabinets.append({"cabinet_id": "WD-01", "type": "WORKDESK", "devices": wd_devices})

        fopp_qty = room.get("FOPP", {}).get("quantity", 0)
        for f in range(fopp_qty):
            fopp_id = f"FOPP-OPR-{f+1:02d}"
            fopp_nodes.append({"node_id": fopp_id, "type": "FOPP"})
            for cab in cabinets:
                intra_room_connections.append({
                    "from": fopp_id,
                    "to": cab["cabinet_id"],
                    "link_type": "FOPP_TO_CABINET"
                })

        return {
            "room_type": "OPERATOR",
            "cabinets": cabinets,
            "fopp_nodes": fopp_nodes,
            "intra_room_connections": intra_room_connections
        }

    # ── Inter-room connections (FOPP ↔ FOPP) ──

    def _build_inter_room_connections(self, fopp_ids_by_room: list) -> list:
        connections = []
        other_fopps = [f["fopp_id"] for f in fopp_ids_by_room if f["room_type"] == "OTHER"]
        opr_fopps   = [f["fopp_id"] for f in fopp_ids_by_room if f["room_type"] == "OPERATOR"]
        for of in other_fopps:
            for opf in opr_fopps:
                connections.append({"from": of, "to": opf, "link_type": "INTER_ROOM_FIBER"})
        return connections


# ─────────────────────────────────────────────
# Test harness
# ─────────────────────────────────────────────

# SEMANTIC_JSON = {
#     "rooms": [
#         {
#             "room_type": "OTHER",
#             "CNTR": {"quantity": 1, "redundant": True},
#             "CHARM": {"baseplates": 31},
#             "FOPP": {"quantity": 1},
#             "ENC_COMP": [
#                 {"part_name": "DeltaV Rack Workstation", "quantity": 1},
#                 {"part_name": "DeltaV Smart Switch", "quantity": 1},
#                 {"part_name": "19 inch Sliding Screen", "quantity": 1},
#                 {"part_name": "APC UPS", "quantity": 1},
#                 {"part_name": "Hirschmann Industrial Switch", "quantity": 1}
#             ]
#         },
#         {
#             "room_type": "OPERATOR",
#             "CNTR": {"quantity": 0, "redundant": False},
#             "CHARM": {"baseplates": 0},
#             "FOPP": {"quantity": 1},
#             "ENC_COMP": [
#                 {"part_name": "DeltaV Full-sized Tower Workstation", "quantity": 1},
#                 {"part_name": "24-inch Monitor", "quantity": 1},
#                 {"part_name": "Printer", "quantity": 1}
#             ]
#         }
#     ]
# }
# with open('handmade_demo.json', 'r') as file:
#     SEMANTIC_JSON = json.load(file)
# if __name__ == "__main__":
#     engine = ArchitectureEngine()
#     architecture = engine.build(SEMANTIC_JSON)
#     print(type(architecture), type(SEMANTIC_JSON))
#     print (json.dumps(SEMANTIC_JSON, indent=2))
#     print(json.dumps(architecture, indent=2))