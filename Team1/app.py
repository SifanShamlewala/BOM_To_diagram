"""
PROJECT TRACKER

[x] Step 1 - Basic Streamlit skeleton
[x] Step 2 - File upload
[x] Step 3 - BOM preview table
[x] Step 4 - Hierarchical grouping display
[x] Step 5 - Confirmation dialog before SVG
[x] Step 6 - SVG generation
[x] Step 7 - SVG display
[x] Step 8 - State management cleanup
[x] Step 9 - Code polish and structure cleanup

Current Phase: COMPLETED
"""

import streamlit as st
import pandas as pd
import tempfile
import os
from parser.bom_parser import parse_bom
from semantic.classifier import classify
from renderer.svg_composer import compose_svg

def init_state():
    if "bom_df" not in st.session_state:
        st.session_state.bom_df = None
    if "hierarchy_data" not in st.session_state:
        st.session_state.hierarchy_data = None
    if "svg_output" not in st.session_state:
        st.session_state.svg_output = None
    if "confirmed" not in st.session_state:
        st.session_state.confirmed = False

def render_upload():
    uploaded_file = st.file_uploader("Upload BOM Excel File", type=["xlsx", "xls"])
    if uploaded_file is not None:
        try:
            # We only read the excel if it's new or state is empty
            df = pd.read_excel(uploaded_file)
            if st.session_state.bom_df is None:
                st.session_state.bom_df = df
                st.session_state.hierarchy_data = None
                st.session_state.svg_output = None
                st.session_state.confirmed = False
            return uploaded_file
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
    return None

def render_bom_preview():
    if st.session_state.bom_df is not None:
        st.subheader("BOM Preview")
        st.dataframe(st.session_state.bom_df, use_container_width=True)

def render_hierarchy(uploaded_file):
    if st.session_state.bom_df is not None and uploaded_file is not None:
        if st.button("Generate Hierarchical Grouping"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            try:
                components = parse_bom(tmp_path)
                plan = classify(components)
                st.session_state.hierarchy_data = plan
                # Reset downstream state
                st.session_state.svg_output = None
                st.session_state.confirmed = False
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

    if st.session_state.hierarchy_data is not None:
        plan = st.session_state.hierarchy_data
        st.subheader("Hierarchical Grouping")
        
        # FUTURE FEATURE: This section will later support item movement between cabinets.
        # For now, it is display-only.
        
        with st.expander("Server Cabinet", expanded=True):
            for item in plan.server_cabinet.items:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;├── {item.role.replace('_', ' ').title()}")
        
        for io_cab in plan.io_cabinets:
            with st.expander(f"I/O Cabinet #{io_cab.index}", expanded=True):
                for tower in io_cab.towers:
                    status = "Active" if tower.has_cioc else "Spare"
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;├── Tower {tower.slot} ({status})")
                    if tower.baseplate_count > 0:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── {tower.baseplate_count} Baseplates")

        with st.expander("Operator Room", expanded=True):
            opr = plan.operator_room
            if opr.console: st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;├── Operator Console")
            if opr.monitors: st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;├── {opr.monitors} Monitors")
            if opr.tower_workstation: st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;├── Tower Workstation")
            if opr.printer: st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;├── Printer")
            if opr.firewall: st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;├── Firewall")

def render_confirmation():
    if st.session_state.hierarchy_data is not None:
        st.markdown("---")
        st.subheader("Finalize Layout")
        st.warning("Please confirm before generating SVG. This action will finalize layout.")
        confirm = st.checkbox("I confirm the hierarchy is correct", value=st.session_state.confirmed)
        st.session_state.confirmed = confirm

def render_svg():
    if st.session_state.confirmed:
        if st.button("Generate SVG"):
            os.makedirs("output", exist_ok=True)
            output_path = "output/diagram.svg"
            try:
                svg = compose_svg(st.session_state.hierarchy_data, output_path)
                svg.saveas(output_path)
                st.session_state.svg_output = output_path
                st.success("SVG generated successfully!")
            except Exception as e:
                st.error(f"Error generating SVG: {e}")

    if st.session_state.svg_output is not None:
        st.subheader("Generated Layout (SVG)")
        try:
            with open(st.session_state.svg_output, "r", encoding="utf-8") as f:
                svg_content = f.read()
            st.components.v1.html(svg_content, height=800, scrolling=True)
            st.download_button(label="Download SVG", data=svg_content, file_name="diagram.svg", mime="image/svg+xml")
        except Exception as e:
            st.error(f"Error displaying SVG: {e}")

def main():
    st.set_page_config(page_title="BOM Hierarchy Viewer", layout="wide")
    st.title("BOM Hierarchical Grouping & SVG Generator")
    
    init_state()
    uploaded_file = render_upload()
    render_bom_preview()
    render_hierarchy(uploaded_file)
    render_confirmation()
    render_svg()

if __name__ == "__main__":
    main()
