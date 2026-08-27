import json
import numpy as np
import pandas as pd
import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

# Page Configuration
st.set_page_config(
    page_title="PhysEng Study Core", page_icon="⚡", layout="wide"
)

# Configure Gemini API Key (Safely fetch from Streamlit secrets)
GEMINI_KEY = st.secrets.get("gemini", {}).get("API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
try:
    if GEMINI_KEY:
        genai.configure(api_key=GEMINI_KEY)
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    else:
        gemini_model = None
except Exception as e:
    gemini_model = None

# Initialize Supabase Client
@st.cache_resource
def init_supabase() -> Client:
    try:
        url = st.secrets["supabase"]["SUPABASE_URL"]
        key = st.secrets["supabase"]["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("Supabase Secrets not configured in .streamlit/secrets.toml!")
        st.stop()

supabase = init_supabase()

# Helper Functions for Supabase Operations
def fetch_entries(category: str):
    try:
        res = supabase.table("knowledge_base").select("*").eq("category", category).order("id", desc=True).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Error fetching data ({category}): {e}")
        return []

def add_entry(payload: dict):
    try:
        supabase.table("knowledge_base").insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Error adding entry: {e}")
        return False

def delete_entry(item_id: int):
    try:
        supabase.table("knowledge_base").delete().eq("id", item_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting entry: {e}")
        return False

def update_entry(item_id: int, payload: dict):
    try:
        supabase.table("knowledge_base").update(payload).eq("id", item_id).execute()
        return True
    except Exception as e:
        st.error(f"Error updating entry: {e}")
        return False

# Fetch data for all categories
physics_data = fetch_entries("physics")
math_data = fetch_entries("math")
cpp_data = fetch_entries("cpp")
ielts_data = fetch_entries("ielts")
lab_data = fetch_entries("lab")

# ==========================================
# SIDEBAR: STATS & DATA MANAGEMENT
# ==========================================
with st.sidebar:
    st.header("📊 Supabase Statistics")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Physics", len(physics_data))
        st.metric("C++ Code", len(cpp_data))
        st.metric("Experiments", len(lab_data))
    with col_s2:
        st.metric("Math", len(math_data))
        st.metric("IELTS Words", len(ielts_data))
    
    st.divider()
    st.subheader("💾 Data Management")
    
    # Export current database to JSON format
    all_data = {
        "physics": physics_data,
        "math": math_data,
        "cpp": cpp_data,
        "ielts": ielts_data,
        "lab": lab_data,
    }
    st.download_button(
        label="📥 Export JSON Backup",
        data=json.dumps(all_data, ensure_ascii=False, indent=4),
        file_name="knowledge_backup.json",
        mime="application/json",
        use_container_width=True
    )

    # Import JSON Backup
    uploaded_file = st.file_uploader("📤 Import JSON Backup (Restore)", type=["json"], key="json_uploader")
    if uploaded_file is not None:
        if st.button("🔄 Perform Restore", use_container_width=True):
            try:
                imported_json = json.load(uploaded_file)
                count = 0
                for cat, items in imported_json.items():
                    for entry in items:
                        clean_payload = {k: v for k, v in entry.items() if k not in ["id", "created_at"]}
                        if add_entry(clean_payload):
                            count += 1
                st.success(f"Successfully restored {count} entries!")
                st.rerun()
            except Exception as err:
                st.error(f"Invalid JSON file: {err}")

# App Header
st.title("⚡ PhysEng Study Core v3.0")
st.caption("Personal Knowledge Hub for Physics, Mathematics, C++ Engineering, IELTS Preparation, and AI Experiments")
st.divider()

# Tabs
tab_physics, tab_math, tab_cpp, tab_ielts, tab_lab = st.tabs(
    [
        "📐 Physics & Chemistry",
        "🧮 Mathematics",
        "💻 C++ Code Snippets",
        "🇬🇧 IELTS Vocabulary",
        "🧪 Physics Experiments & AI",
    ]
)

# ==========================================
# TAB 1: PHYSICS & CHEMISTRY
# ==========================================
with tab_physics:
    st.header("Physics & Chemistry Knowledge Base")

    with st.expander("➕ Add New Formula / Concept"):
        with st.form("physics_form", clear_on_submit=True):
            topic = st.text_input("Topic / Title", placeholder="e.g., Work Done")
            formula = st.text_input("LaTeX Formula (optional)", placeholder=r"e.g., W = F \cdot s \cdot \cos(\alpha)")
            description = st.text_area("Description / Notes", placeholder="Explain variables and meaning...")
            submitted = st.form_submit_button("Save Entry")

            if submitted and topic:
                if add_entry({
                    "category": "physics",
                    "title": topic,
                    "formula": formula,
                    "description": description
                }):
                    st.success("Successfully saved to Supabase!")
                    st.rerun()

    search_phys = st.text_input("🔍 Search Physics entries...", key="search_phys")

    if not physics_data:
        st.info("No formulas added yet. Use the form above to add your first entry!")
    else:
        filtered = [
            item for item in physics_data
            if not search_phys or search_phys.lower() in item["title"].lower() or search_phys.lower() in (item.get("description") or "").lower()
        ]
        
        if not filtered:
            st.warning("No matching entries found.")
        else:
            for item in filtered:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([0.74, 0.13, 0.13])
                    with col1:
                        st.subheader(item["title"])
                        if item.get("formula"):
                            clean_formula = item["formula"].strip("$ ")
                            if clean_formula:
                                st.latex(clean_formula)
                        if item.get("description"):
                            st.write(item["description"])
                    with col2:
                        with st.popover("✏️ Edit", key=f"pop_edit_phys_{item['id']}"):
                            with st.form(f"edit_phys_form_{item['id']}"):
                                edit_title = st.text_input("Title", value=item.get("title", ""))
                                edit_formula = st.text_input("Formula (LaTeX)", value=item.get("formula", ""))
                                edit_desc = st.text_area("Description", value=item.get("description", ""))
                                if st.form_submit_button("Save Changes"):
                                    if update_entry(item["id"], {
                                        "title": edit_title,
                                        "formula": edit_formula,
                                        "description": edit_desc
                                    }):
                                        st.success("Updated!")
                                        st.rerun()
                    with col3:
                        with st.popover("🗑️ Delete", key=f"pop_del_phys_{item['id']}"):
                            st.write("Confirm deletion?")
                            if st.button("Delete Now", key=f"del_phys_{item['id']}"):
                                if delete_entry(item["id"]):
                                    st.rerun()

# ==========================================
# TAB 2: MATHEMATICS
# ==========================================
with tab_math:
    st.header("Mathematics Knowledge Base")

    with st.expander("➕ Add New Math Formula / Theorem"):
        with st.form("math_form", clear_on_submit=True):
            topic = st.text_input("Topic / Title", placeholder="e.g., Differential Equation of Motion")
            formula = st.text_input("LaTeX Formula", placeholder=r"e.g., \frac{d^2x}{dt^2} + \omega^2 x = 0")
            description = st.text_area("Description / Notes", placeholder="Explain concept, proof steps...")
            submitted = st.form_submit_button("Save Entry")

            if submitted and topic:
                if add_entry({
                    "category": "math",
                    "title": topic,
                    "formula": formula,
                    "description": description
                }):
                    st.success("Successfully saved to Supabase!")
                    st.rerun()

    search_math = st.text_input("🔍 Search Math entries...", key="search_math")

    if not math_data:
        st.info("No math formulas added yet.")
    else:
        filtered = [
            item for item in math_data
            if not search_math or search_math.lower() in item["title"].lower() or search_math.lower() in (item.get("description") or "").lower()
        ]

        if not filtered:
            st.warning("No matching entries found.")
        else:
            for item in filtered:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([0.74, 0.13, 0.13])
                    with col1:
                        st.subheader(item["title"])
                        if item.get("formula"):
                            clean_formula = item["formula"].strip("$ ")
                            if clean_formula:
                                st.latex(clean_formula)
                        if item.get("description"):
                            st.write(item["description"])
                    with col2:
                        with st.popover("✏️ Edit", key=f"pop_edit_math_{item['id']}"):
                            with st.form(f"edit_math_form_{item['id']}"):
                                edit_title = st.text_input("Title", value=item.get("title", ""))
                                edit_formula = st.text_input("Formula (LaTeX)", value=item.get("formula", ""))
                                edit_desc = st.text_area("Description", value=item.get("description", ""))
                                if st.form_submit_button("Save Changes"):
                                    if update_entry(item["id"], {
                                        "title": edit_title,
                                        "formula": edit_formula,
                                        "description": edit_desc
                                    }):
                                        st.success("Updated!")
                                        st.rerun()
                    with col3:
                        with st.popover("🗑️ Delete", key=f"pop_del_math_{item['id']}"):
                            st.write("Confirm deletion?")
                            if st.button("Delete Now", key=f"del_math_{item['id']}"):
                                if delete_entry(item["id"]):
                                    st.rerun()

# ==========================================
# TAB 3: C++ CODE SNIPPETS
# ==========================================
with tab_cpp:
    st.header("C++ Code Snippets")

    with st.expander("➕ Add New C++ Snippet"):
        with st.form("cpp_form", clear_on_submit=True):
            title = st.text_input("Snippet Title", placeholder="e.g., Read Sensor Data")
            code = st.text_area("C++ Code", placeholder="void setup() {\n  ...\n}", height=150)
            note = st.text_input("Notes / Hardware Pin", placeholder="e.g., Pin 13 LED")
            submitted = st.form_submit_button("Save Code")

            if submitted and title and code:
                if add_entry({
                    "category": "cpp",
                    "title": title,
                    "code": code,
                    "note": note
                }):
                    st.success("Successfully saved C++ snippet!")
                    st.rerun()

    search_cpp = st.text_input("🔍 Search C++ snippets...", key="search_cpp")

    if not cpp_data:
        st.info("No C++ snippets added yet.")
    else:
        filtered = [
            item for item in cpp_data
            if not search_cpp or search_cpp.lower() in item["title"].lower() or search_cpp.lower() in (item.get("code") or "").lower() or search_cpp.lower() in (item.get("note") or "").lower()
        ]

        if not filtered:
            st.warning("No matching snippets found.")
        else:
            for item in filtered:
                with st.container(border=True):
