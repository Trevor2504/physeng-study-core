import json
import streamlit as st
from supabase import create_client, Client

# Page Configuration
st.set_page_config(
    page_title="PhysEng Study Core", page_icon="⚡", layout="wide"
)

# Initialize Supabase Client
@st.cache_resource
def init_supabase() -> Client:
    try:
        url = st.secrets["supabase"]["SUPABASE_URL"]
        key = st.secrets["supabase"]["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("Chưa cấu hình Supabase Secrets trong .streamlit/secrets.toml!")
        st.stop()

supabase = init_supabase()

# Helper Functions for Supabase Operations
def fetch_entries(category: str):
    res = supabase.table("knowledge_base").select("*").eq("category", category).order("id", desc=True).execute()
    return res.data or []

def add_entry(payload: dict):
    supabase.table("knowledge_base").insert(payload).execute()

def delete_entry(item_id: int):
    supabase.table("knowledge_base").delete().eq("id", item_id).execute()

# Fetch data for all categories
physics_data = fetch_entries("physics")
math_data = fetch_entries("math")
cpp_data = fetch_entries("cpp")
ielts_data = fetch_entries("ielts")

# ==========================================
# SIDEBAR: STATS & DATA MANAGEMENT
# ==========================================
with st.sidebar:
    st.header("📊 Thống kê Supabase")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Physics", len(physics_data))
        st.metric("C++ Code", len(cpp_data))
    with col_s2:
        st.metric("Math", len(math_data))
        st.metric("IELTS Words", len(ielts_data))
    
    st.divider()
    st.subheader("💾 Tải dữ liệu về máy")
    
    # Export current database to JSON format
    all_data = {
        "physics": physics_data,
        "math": math_data,
        "cpp": cpp_data,
        "ielts": ielts_data,
    }
    st.download_button(
        label="📥 Xuất dữ liệu JSON",
        data=json.dumps(all_data, ensure_ascii=False, indent=4),
        file_name="knowledge_backup.json",
        mime="application/json",
        use_container_width=True
    )

# App Header
st.title("⚡ PhysEng Study Core v2.0 (Supabase Powered)")
st.caption("Personal Knowledge Hub for Physics, Mathematics, C++ Engineering, and IELTS Preparation")
st.divider()

# Tabs
tab_physics, tab_math, tab_cpp, tab_ielts = st.tabs(
    [
        "📐 Physics & Chemistry",
        "🧮 Mathematics",
        "💻 C++ Code Snippets",
        "🇬🇧 IELTS Vocabulary",
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
                add_entry({
                    "category": "physics",
                    "title": topic,
                    "formula": formula,
                    "description": description
                })
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
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.subheader(item["title"])
                        if item.get("formula"):
                            st.latex(item["formula"])
                        if item.get("description"):
                            st.write(item["description"])
                    with col2:
                        if st.button("Delete", key=f"del_phys_{item['id']}"):
                            delete_entry(item["id"])
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
                add_entry({
                    "category": "math",
                    "title": topic,
                    "formula": formula,
                    "description": description
                })
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
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.subheader(item["title"])
                        if item.get("formula"):
                            st.latex(item["formula"])
                        if item.get("description"):
                            st.write(item["description"])
                    with col2:
                        if st.button("Delete", key=f"del_math_{item['id']}"):
                            delete_entry(item["id"])
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
                add_entry({
                    "category": "cpp",
                    "title": title,
                    "code": code,
                    "note": note
                })
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
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.subheader(item["title"])
                        if item.get("note"):
                            st.caption(f"📌 {item['note']}")
                        if item.get("code"):
                            st.code(item["code"], language="cpp")
                    with col2:
                        if st.button("Delete", key=f"del_cpp_{item['id']}"):
                            delete_entry(item["id"])
                            st.rerun()

# ==========================================
# TAB 4: IELTS VOCABULARY
# ==========================================
with tab_ielts:
    st.header("IELTS Vocabulary & Phrases")

    with st.expander("➕ Add New Word / Phrase"):
        with st.form("ielts_form", clear_on_submit=True):
            word = st.text_input("Word / Phrase", placeholder="e.g., Perseverance")
            word_type = st.selectbox("Type", ["noun", "verb", "adjective", "adverb", "phrase", "idiom"])
            definition = st.text_input("Definition", placeholder="e.g., Continued effort to achieve something")
            example = st.text_input("Example Sentence", placeholder="e.g., It takes perseverance to learn C++.")
            submitted = st.form_submit_button("Save Word")

            if submitted and word:
                add_entry({
                    "category": "ielts",
                    "title": word,
                    "word_type": word_type,
                    "definition": definition,
                    "example": example
                })
                st.success("Successfully saved word!")
                st.rerun()

    search_ielts = st.text_input("🔍 Search Vocabulary...", key="search_ielts")

    if not ielts_data:
        st.info("No words added yet.")
    else:
        filtered = [
            item for item in ielts_data
            if not search_ielts or search_ielts.lower() in item["title"].lower() or search_ielts.lower() in (item.get("definition") or "").lower()
        ]

        if not filtered:
            st.warning("No matching words found.")
        else:
            for item in filtered:
                with st.container(border=True):
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.markdown(f"### **{item['title']}** *({item.get('word_type', 'N/A')})*")
                        if item.get("definition"):
                            st.write(f"**Meaning:** {item['definition']}")
                        if item.get("example"):
                            st.write(f"*Example:* {item['example']}")
                    with col2:
                        if st.button("Delete", key=f"del_ielts_{item['id']}"):
                            delete_entry(item["id"])
                            st.rerun()
