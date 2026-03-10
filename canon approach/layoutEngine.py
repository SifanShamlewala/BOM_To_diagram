"""
DeltaV DCS Layout Engine
Stage 3: Architecture JSON → Layout JSON

Deterministic. No coordinates (no pixels/inches).
Assigns only: row, col, col_span, tower_col, stack_index.

Layout rules:
- Each room has its own independent col space starting at 0
- Rooms are placed side by side (OTHER left, OPERATOR right) — tracked via room_index
- Within a room:
    row=0 → cabinets (SRV, IO, WORKDESK)
    row=1 → FOPP node (bottom-right corner of room)
- Cabinet col assignment:
    SRV  → col_span = 1
    IO   → col_span = number of towers
    WD   → col_span = 1
- IO towers → tower_col = 0, 1, 2 ... (within cabinet)
- FOPP col → last col of the room (col_span_total - 1), row=1
- Devices inside SERVER/WORKDESK → stack_index = position in devices list
- Devices inside IO tower → stack_index 0 = CIOC, 1..N = baseplates
"""

import json
from typing import Optional


class LayoutEngine:

    def build(self, architecture_json: dict) -> dict:
        elements = []

        for room_index, room in enumerate(architecture_json["rooms"]):
            room_type = room["room_type"]
            room_elements, total_cols = self._layout_room(room, room_index)
            elements.extend(room_elements)

        # Connections pass-through (unchanged from architecture JSON)
        connections = self._collect_connections(architecture_json)

        return {
            "elements": elements,
            "connections": connections
        }

    # ── Room layout ────────────────────────────

    def _layout_room(self, room: dict, room_index: int) -> tuple:
        """
        Returns (elements, total_col_span_of_room).
        room_index is used only as metadata — col space is independent per room.
        """
        elements = []
        current_col = 0

        for cabinet in room.get("cabinets", []):
            cab_type = cabinet["type"]
            cab_id = cabinet["cabinet_id"]

            if cab_type == "IO":
                col_span = len(cabinet["towers"])
            else:
                col_span = 1

            # Cabinet element
            elements.append({
                "id": cab_id,
                "element_type": "CABINET",
                "cabinet_type": cab_type,
                "room_type": room["room_type"],
                "room_index": room_index,
                "row": 0,
                "col": current_col,
                "col_span": col_span
            })

            # Devices inside cabinet
            if cab_type == "IO":
                for tower in cabinet["towers"]:
                    tower_col = tower["tower_index"]  # relative col within cabinet

                    # CIOC at stack_index=0
                    cioc = tower["cioc"]
                    elements.append({
                        "id": cioc["device_id"],
                        "element_type": "DEVICE",
                        "device_type": cioc["type"],
                        "room_index": room_index,
                        "parent": cab_id,
                        "tower_col": tower_col,
                        "stack_index": 0
                    })

                    # Baseplates at stack_index=1..N
                    for bp_idx, bp in enumerate(tower["baseplates"]):
                        elements.append({
                            "id": bp["device_id"],
                            "element_type": "DEVICE",
                            "device_type": bp["type"],
                            "room_index": room_index,
                            "parent": cab_id,
                            "tower_col": tower_col,
                            "stack_index": bp_idx + 1   # +1 because CIOC occupies 0
                        })

            else:
                # SERVER or WORKDESK — flat device list
                for stack_idx, device in enumerate(cabinet.get("devices", [])):
                    elements.append({
                        "id": device["device_id"],
                        "element_type": "DEVICE",
                        "device_type": device["type"],
                        "room_index": room_index,
                        "parent": cab_id,
                        "stack_index": stack_idx
                    })

            current_col += col_span

        total_cols = current_col  # total col width of this room

        # FOPP nodes — row=1, col=last col of room (bottom-right)
        fopp_col = max(0, total_cols - 1)
        for fopp in room.get("fopp_nodes", []):
            elements.append({
                "id": fopp["node_id"],
                "element_type": "FOPP",
                "device_type": "FOPP",
                "room_type": room["room_type"],
                "room_index": room_index,
                "row": 1,
                "col": fopp_col
            })

        return elements, total_cols

    # ── Connections pass-through ───────────────

    def _collect_connections(self, architecture_json: dict) -> list:
        connections = []

        for room in architecture_json["rooms"]:
            for conn in room.get("intra_room_connections", []):
                connections.append({
                    "from": conn["from"],
                    "to": conn["to"],
                    "link_type": conn["link_type"],
                    "scope": "INTRA_ROOM"
                })

        for conn in architecture_json.get("inter_room_connections", []):
            connections.append({
                "from": conn["from"],
                "to": conn["to"],
                "link_type": conn["link_type"],
                "scope": "INTER_ROOM"
            })

        return connections


# ─────────────────────────────────────────────
# Test harness — uses architecture JSON directly
# ─────────────────────────────────────────────
#
# ARCHITECTURE_JSON = {
#   "rooms": [
#     {
#       "room_type": "OTHER",
#       "cabinets": [
#         {
#           "cabinet_id": "SRV-01",
#           "type": "SERVER",
#           "devices": [
#             {"device_id": "CNTR-PRI", "type": "CNTR", "redundant_role": "PRIMARY"},
#             {"device_id": "CNTR-SEC", "type": "CNTR", "redundant_role": "SECONDARY"},
#             {"device_id": "ENC-DELTAV_RACK_WORKSTATION-01", "type": "ENC_COMP", "part_name": "DeltaV Rack Workstation"},
#             {"device_id": "ENC-DELTAV_SMART_SWITCH-01", "type": "ENC_COMP", "part_name": "DeltaV Smart Switch"},
#             {"device_id": "ENC-19_INCH_SLIDING_SCREEN-01", "type": "ENC_COMP", "part_name": "19 inch Sliding Screen"},
#             {"device_id": "ENC-APC_UPS-01", "type": "ENC_COMP", "part_name": "APC UPS"},
#             {"device_id": "ENC-HIRSCHMANN_INDUSTRIAL_SWITCH-01", "type": "ENC_COMP", "part_name": "Hirschmann Industrial Switch"}
#           ]
#         },
#         {
#           "cabinet_id": "IO-01",
#           "type": "IO",
#           "towers": [
#             {
#               "tower_index": 0,
#               "cioc": {"device_id": "CIOC-01", "type": "CIOC"},
#               "baseplates": [
#                 {"device_id": "CHARM-BP-01", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-02", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-03", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-04", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-05", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-06", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-07", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-08", "type": "CHARM"}
#               ]
#             },
#             {
#               "tower_index": 1,
#               "cioc": {"device_id": "CIOC-02", "type": "CIOC"},
#               "baseplates": [
#                 {"device_id": "CHARM-BP-09", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-10", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-11", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-12", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-13", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-14", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-15", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-16", "type": "CHARM"}
#               ]
#             },
#             {
#               "tower_index": 2,
#               "cioc": {"device_id": "CIOC-03", "type": "CIOC"},
#               "baseplates": [
#                 {"device_id": "CHARM-BP-17", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-18", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-19", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-20", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-21", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-22", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-23", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-24", "type": "CHARM"}
#               ]
#             }
#           ]
#         },
#         {
#           "cabinet_id": "IO-02",
#           "type": "IO",
#           "towers": [
#             {
#               "tower_index": 0,
#               "cioc": {"device_id": "CIOC-04", "type": "CIOC"},
#               "baseplates": [
#                 {"device_id": "CHARM-BP-25", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-26", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-27", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-28", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-29", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-30", "type": "CHARM"},
#                 {"device_id": "CHARM-BP-31", "type": "CHARM"}
#               ]
#             }
#           ]
#         }
#       ],
#       "fopp_nodes": [{"node_id": "FOPP-OTHER-01", "type": "FOPP"}],
#       "intra_room_connections": [
#         {"from": "FOPP-OTHER-01", "to": "SRV-01", "link_type": "FOPP_TO_CABINET"},
#         {"from": "FOPP-OTHER-01", "to": "IO-01", "link_type": "FOPP_TO_CABINET"},
#         {"from": "FOPP-OTHER-01", "to": "IO-02", "link_type": "FOPP_TO_CABINET"}
#       ]
#     },
#     {
#       "room_type": "OPERATOR",
#       "cabinets": [
#         {
#           "cabinet_id": "WD-01",
#           "type": "WORKDESK",
#           "devices": [
#             {"device_id": "WD-DELTAV_FULL-SIZED_TOWER_WORKSTATION-01", "type": "ENC_COMP", "part_name": "DeltaV Full-sized Tower Workstation"},
#             {"device_id": "WD-24-INCH_MONITOR-01", "type": "ENC_COMP", "part_name": "24-inch Monitor"},
#             {"device_id": "WD-PRINTER-01", "type": "ENC_COMP", "part_name": "Printer"}
#           ]
#         }
#       ],
#       "fopp_nodes": [{"node_id": "FOPP-OPR-01", "type": "FOPP"}],
#       "intra_room_connections": [
#         {"from": "FOPP-OPR-01", "to": "WD-01", "link_type": "FOPP_TO_CABINET"}
#       ]
#     }
#   ],
#   "inter_room_connections": [
#     {"from": "FOPP-OTHER-01", "to": "FOPP-OPR-01", "link_type": "INTER_ROOM_FIBER"}
#   ]
# }
#
#
# if __name__ == "__main__":
#     engine = LayoutEngine()
#     layout = engine.build(ARCHITECTURE_JSON)
#     print(json.dumps(layout, indent=2))
#
#     # ── Human-readable summary ──
#     print("\n─── LAYOUT SUMMARY ───")
#     cabinets = [e for e in layout["elements"] if e["element_type"] == "CABINET"]
#     fopps    = [e for e in layout["elements"] if e["element_type"] == "FOPP"]
#     devices  = [e for e in layout["elements"] if e["element_type"] == "DEVICE"]
#
#     print(f"\nCABINETS ({len(cabinets)}):")
#     for c in cabinets:
#         print(f"  [{c['room_type']} room_index={c['room_index']}] "
#               f"{c['id']:30s}  row={c['row']}  col={c['col']}  col_span={c['col_span']}")
#
#     print(f"\nFOPP NODES ({len(fopps)}):")
#     for f in fopps:
#         print(f"  [{f['room_type']} room_index={f['room_index']}] "
#               f"{f['id']:30s}  row={f['row']}  col={f['col']}")
#
#     print(f"\nCONNECTIONS ({len(layout['connections'])}):")
#     for conn in layout["connections"]:
#         print(f"  [{conn['scope']:12s}] {conn['from']:25s} → {conn['to']:25s}  ({conn['link_type']})")