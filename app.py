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

# Configure Gemini API Key (Fallback to provided key if not in secrets)
GEMINI_KEY = st.secrets.get("gemini", {}).get("API_KEY", "AQ.Ab8RN6LSbEW6T2CoSOi--DHQqOUw5J3EomhnroE7H6uH9tl5_A")
try:
    genai.configure(api_key=GEMINI_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
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
                        with st.popover("✏️ Edit"):
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
                        with st.popover("🗑️ Delete"):
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
                        with st.popover("✏️ Edit"):
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
                        with st.popover("🗑️ Delete"):
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
                    col1, col2, col3 = st.columns([0.74, 0.13, 0.13])
                    with col1:
                        st.subheader(item["title"])
                        if item.get("note"):
                            st.caption(f"📌 {item['note']}")
                        if item.get("code"):
                            st.code(item["code"], language="cpp")
                    with col2:
                        with st.popover("✏️ Edit"):
                            with st.form(f"edit_cpp_form_{item['id']}"):
                                edit_title = st.text_input("Title", value=item.get("title", ""))
                                edit_note = st.text_input("Note", value=item.get("note", ""))
                                edit_code = st.text_area("C++ Code", value=item.get("code", ""), height=150)
                                if st.form_submit_button("Save Changes"):
                                    if update_entry(item["id"], {
                                        "title": edit_title,
                                        "note": edit_note,
                                        "code": edit_code
                                    }):
                                        st.success("Updated!")
                                        st.rerun()
                    with col3:
                        with st.popover("🗑️ Delete"):
                            st.write("Confirm deletion?")
                            if st.button("Delete Now", key=f"del_cpp_{item['id']}"):
                                if delete_entry(item["id"]):
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
                if add_entry({
                    "category": "ielts",
                    "title": word,
                    "word_type": word_type,
                    "definition": definition,
                    "example": example
                }):
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
                    col1, col2, col3 = st.columns([0.74, 0.13, 0.13])
                    with col1:
                        st.markdown(f"### **{item['title']}** *({item.get('word_type', 'N/A')})*")
                        if item.get("definition"):
                            st.write(f"**Meaning:** {item['definition']}")
                        if item.get("example"):
                            st.write(f"*Example:* {item['example']}")
                    with col2:
                        with st.popover("✏️ Edit"):
                            with st.form(f"edit_ielts_form_{item['id']}"):
                                edit_word = st.text_input("Word / Phrase", value=item.get("title", ""))
                                type_options = ["noun", "verb", "adjective", "adverb", "phrase", "idiom"]
                                current_type = item.get("word_type", "noun")
                                default_idx = type_options.index(current_type) if current_type in type_options else 0
                                edit_type = st.selectbox("Type", type_options, index=default_idx)
                                edit_def = st.text_input("Definition", value=item.get("definition", ""))
                                edit_ex = st.text_input("Example", value=item.get("example", ""))
                                if st.form_submit_button("Save Changes"):
                                    if update_entry(item["id"], {
                                        "title": edit_word,
                                        "word_type": edit_type,
                                        "definition": edit_def,
                                        "example": edit_ex
                                    }):
                                        st.success("Updated!")
                                        st.rerun()
                    with col3:
                        with st.popover("🗑️ Delete"):
                            st.write("Confirm deletion?")
                            if st.button("Delete Now", key=f"del_ielts_{item['id']}"):
                                if delete_entry(item["id"]):
                                    st.rerun()

# ==========================================
# TAB 5: PHYSICS EXPERIMENTS & AI
# ==========================================
with tab_lab:
    st.header("🧪 Physics Lab, Simulations & AI Generator")

    # SECTION 1: INTERACTIVE SIMULATION
    st.subheader("1. 🎮 Interactive Simulator: 1D Collision & Momentum Conservation")
    st.caption("Interactive experiment to verify Momentum ($p = mv$) and Kinetic Energy ($E_k = \\frac{1}{2}mv^2$) before and after collision.")

    sim_col1, sim_col2 = st.columns(2)

    with sim_col1:
        st.markdown("**Object 1 ($m_1$)**")
        m1 = st.slider("Mass m1 (kg)", 0.5, 10.0, 2.0, 0.5)
        v1 = st.slider("Initial Velocity v1 (m/s)", -10.0, 10.0, 5.0, 0.5)

    with sim_col2:
        st.markdown("**Object 2 ($m_2$)**")
        m2 = st.slider("Mass m2 (kg)", 0.5, 10.0, 3.0, 0.5)
        v2 = st.slider("Initial Velocity v2 (m/s)", -10.0, 10.0, -2.0, 0.5)

    col_type, _ = st.columns([0.5, 0.5])
    with col_type:
        collision_type = st.radio("Collision Type", ["Elastic Collision", "Inelastic Collision"], horizontal=True)

    # Physics calculations
    p_initial = m1 * v1 + m2 * v2
    ek_initial = 0.5 * m1 * (v1 ** 2) + 0.5 * m2 * (v2 ** 2)

    if "elastic" in collision_type.lower():
        v1_final = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
        v2_final = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)
    else:  # Perfectly Inelastic
        v_common = p_initial / (m1 + m2)
        v1_final = v_common
        v2_final = v_common

    p_final = m1 * v1_final + m2 * v2_final
    ek_final = 0.5 * m1 * (v1_final ** 2) + 0.5 * m2 * (v2_final ** 2)

    # Simulation results metrics
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Final Velocity v1'", f"{v1_final:.2f} m/s")
    m_col2.metric("Final Velocity v2'", f"{v2_final:.2f} m/s")
    m_col3.metric("Momentum (Initial / Final)", f"{p_initial:.2f} / {p_final:.2f}", delta=f"{p_final - p_initial:.2f}")
    m_col4.metric("Kinetic Energy (Initial / Final)", f"{ek_initial:.2f} / {ek_final:.2f} J", delta=f"{ek_final - ek_initial:.2f} J")

    # Plot trajectories x(t)
    t_collision = 2.0
    time_before = np.linspace(0, t_collision, 20)
    time_after = np.linspace(t_collision, 5.0, 30)

    x1_0, x2_0 = 0.0, 10.0
    x1_before = x1_0 + v1 * time_before
    x2_before = x2_0 + v2 * time_before

    x_collision = x1_before[-1]
    x1_after = x_collision + v1_final * (time_after - t_collision)
    x2_after = x_collision + v2_final * (time_after - t_collision)

    df_sim = pd.DataFrame({
        "Time (s)": np.concatenate([time_before, time_after]),
        "Position Object 1 (m)": np.concatenate([x1_before, x1_after]),
        "Position Object 2 (m)": np.concatenate([x2_before, x2_after])
    }).set_index("Time (s)")

    st.line_chart(df_sim)

    st.divider()

    # SECTION 2: AI EXPERIMENT GENERATOR (NEW)
    st.subheader("2. 🤖 AI Experiment Generator (Gemini Powered)")
    st.caption("Enter any topic or concept, and AI will automatically draft a structured lab experiment setup for you.")

    ai_prompt = st.text_input(
        "💡 What experiment would you like to design?",
        placeholder="e.g., Conservation of Mechanical Energy, Measuring Planck's Constant, RLC Circuits..."
    )

    if st.button("✨ Generate Experiment with AI", use_container_width=True):
        if not ai_prompt:
            st.warning("Please enter an experiment topic!")
        elif not gemini_model:
            st.error("Gemini API is not configured properly.")
        else:
            with st.spinner("AI is designing the experiment setup..."):
                prompt_template = f"""
                You are an expert Physics Professor and Experimentalist. Design a complete lab experiment for the topic: "{ai_prompt}".
                Return ONLY a valid JSON object matching this schema:
                {{
                  "title": "Experiment Title",
                  "equipment": "List of required apparatus and tools",
                  "theory": "Theoretical foundation and key equations (LaTeX format where applicable)",
                  "procedure": "Step-by-step procedure, data collection, and error analysis guidance"
                }}
                """
                try:
                    response = gemini_model.generate_content(
                        prompt_template,
                        generation_config={"response_mime_type": "application/json"}
                    )
                    exp_data = json.loads(response.text)
                    st.session_state["last_ai_exp"] = exp_data
                    st.success("Experiment generated successfully!")
                except Exception as e:
                    st.error(f"Error generating experiment with AI: {e}")

    # Display generated AI experiment if available
    if "last_ai_exp" in st.session_state:
        exp_data = st.session_state["last_ai_exp"]
        with st.container(border=True):
            st.markdown(f"### 🧪 {exp_data.get('title')}")
            st.markdown(f"**🛠️ Equipment:** {exp_data.get('equipment')}")
            st.markdown(f"**📐 Theory & Formulas:**\n{exp_data.get('theory')}")
            st.markdown(f"**📝 Procedure & Analysis:**\n{exp_data.get('procedure')}")

            if st.button("💾 Save Generated Experiment to Supabase Log", use_container_width=True):
                payload = {
                    "category": "lab",
                    "title": exp_data.get("title", "AI Experiment"),
                    "formula": exp_data.get("equipment", ""),
                    "description": f"THEORY:\n{exp_data.get('theory')}\n\nPROCEDURE:\n{exp_data.get('procedure')}"
                }
                if add_entry(payload):
                    st.success("Saved to Supabase database!")
                    del st.session_state["last_ai_exp"]
                    st.rerun()

    st.divider()

    # SECTION 3: LAB EXPERIMENT LOG (SUPABASE CRUD)
    st.subheader("3. 📝 Lab Experiment Log & History (Supabase)")

    with st.expander("➕ Add New Manual Experiment Entry"):
        with st.form("lab_form", clear_on_submit=True):
            exp_title = st.text_input("Experiment Title", placeholder="e.g., Verifying Conservation of Linear Momentum")
            equipment = st.text_input("Equipment & Tools", placeholder="e.g., Air track, photogates, gliders")
            description = st.text_area("Description, Procedure & Conclusion", placeholder="Record observations, calculations, error analysis...")
            submitted = st.form_submit_button("Save Experiment")

            if submitted and exp_title:
                if add_entry({
                    "category": "lab",
                    "title": exp_title,
                    "formula": equipment,
                    "description": description
                }):
                    st.success("Experiment saved to Supabase!")
                    st.rerun()

    search_lab = st.text_input("🔍 Search experiments...", key="search_lab")

    if not lab_data:
        st.info("No experiments recorded yet.")
    else:
        filtered_lab = [
            item for item in lab_data
            if not search_lab or search_lab.lower() in item["title"].lower() or search_lab.lower() in (item.get("description") or "").lower()
        ]

        if not filtered_lab:
            st.warning("No matching experiments found.")
        else:
            for item in filtered_lab:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([0.74, 0.13, 0.13])
                    with col1:
                        st.subheader(f"🧪 {item['title']}")
                        if item.get("formula"):
                            st.caption(f"🛠️ Equipment: {item['formula']}")
                        if item.get("description"):
                            st.write(item["description"])
                    with col2:
                        with st.popover("✏️ Edit"):
                            with st.form(f"edit_lab_form_{item['id']}"):
                                edit_title = st.text_input("Title", value=item.get("title", ""))
                                edit_equip = st.text_input("Equipment", value=item.get("formula", ""))
                                edit_desc = st.text_area("Content & Results", value=item.get("description", ""))
                                if st.form_submit_button("Save Changes"):
                                    if update_entry(item["id"], {
                                        "title": edit_title,
                                        "formula": edit_equip,
                                        "description": edit_desc
                                    }):
                                        st.success("Updated!")
                                        st.rerun()
                    with col3:
                        with st.popover("🗑️ Delete"):
                            st.write("Confirm deletion?")
                            if st.button("Delete Now", key=f"del_lab_{item['id']}"):
                                if delete_entry(item["id"]):
                                    st.rerun()
