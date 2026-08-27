import json
import numpy as np
import pandas as pd
import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="PhysEng Study Core", 
    page_icon="⚡", 
    layout="wide"
)

# ==========================================
# INITIALIZATION & SECRETS MANAGEMENT
# ==========================================

# Configure Gemini API Key safely
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("gemini", {}).get("API_KEY")
gemini_model = None

if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        st.sidebar.warning(f"Gemini Init Warning: {e}")
else:
    st.sidebar.info("💡 Tip: Add `GEMINI_API_KEY` to `.streamlit/secrets.toml` to enable AI tools.")

# Initialize Supabase Client
@st.cache_resource
def init_supabase() -> Client:
    try:
        url = st.secrets["supabase"]["SUPABASE_URL"]
        key = st.secrets["supabase"]["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        st.error("⚠️ Supabase credentials not found in `.streamlit/secrets.toml`!")
        st.stop()

supabase = init_supabase()

# ==========================================
# DATABASE CRUD HELPERS
# ==========================================
def fetch_entries(category: str):
    try:
        res = supabase.table("knowledge_base").select("*").eq("category", category).order("id", desc=True).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Error fetching {category}: {e}")
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

# Fetch initial data (Added 'ai' category)
categories = ["physics", "math", "cpp", "ielts", "lab", "ai"]
data_store = {cat: fetch_entries(cat) for cat in categories}

# ==========================================
# REUSABLE UI COMPONENT: ENTRY CARD
# ==========================================
def render_entry_card(item: dict, card_type: str):
    """Generic card renderer with Edit & Delete popovers."""
    item_id = item["id"]
    
    with st.container(border=True):
        col1, col2, col3 = st.columns([0.74, 0.13, 0.13])
        
        # --- Content View ---
        with col1:
            if card_type in ["physics", "math"]:
                st.subheader(item.get("title", ""))
                if item.get("formula"):
                    clean_formula = item["formula"].strip("$ ")
                    if clean_formula:
                        st.latex(clean_formula)
                if item.get("description"):
                    st.write(item["description"])
                    
            elif card_type == "cpp":
                st.subheader(item.get("title", ""))
                if item.get("note"):
                    st.caption(f"📌 {item['note']}")
                if item.get("code"):
                    st.code(item["code"], language="cpp")
                    
            elif card_type == "ielts":
                st.markdown(f"### **{item.get('title')}** *({item.get('word_type', 'N/A')})*")
                if item.get("definition"):
                    st.write(f"**Meaning:** {item['definition']}")
                if item.get("example"):
                    st.write(f"*Example:* {item['example']}")
                    
            elif card_type == "lab":
                st.subheader(f"🧪 {item.get('title')}")
                if item.get("formula"):
                    st.caption(f"🛠️ Equipment: {item['formula']}")
                if item.get("description"):
                    st.write(item["description"])

            elif card_type == "ai":
                st.subheader(f"🤖 {item.get('title')}")
                if item.get("formula"):
                    st.caption(f"🔗 Link / Tag: {item['formula']}")
                if item.get("description"):
                    st.write(item["description"])

        # --- Edit Popover ---
        with col2:
            with st.popover("✏️ Edit"):
                with st.form(f"edit_form_{card_type}_{item_id}"):
                    updated_payload = {}
                    
                    if card_type in ["physics", "math"]:
                        updated_payload["title"] = st.text_input("Title", value=item.get("title", ""))
                        updated_payload["formula"] = st.text_input("Formula (LaTeX)", value=item.get("formula", ""))
                        updated_payload["description"] = st.text_area("Description", value=item.get("description", ""))
                        
                    elif card_type == "cpp":
                        updated_payload["title"] = st.text_input("Title", value=item.get("title", ""))
                        updated_payload["note"] = st.text_input("Note", value=item.get("note", ""))
                        updated_payload["code"] = st.text_area("C++ Code", value=item.get("code", ""), height=150)
                        
                    elif card_type == "ielts":
                        updated_payload["title"] = st.text_input("Word / Phrase", value=item.get("title", ""))
                        type_opts = ["noun", "verb", "adjective", "adverb", "phrase", "idiom"]
                        curr_type = item.get("word_type", "noun")
                        idx = type_opts.index(curr_type) if curr_type in type_opts else 0
                        updated_payload["word_type"] = st.selectbox("Type", type_opts, index=idx)
                        updated_payload["definition"] = st.text_input("Definition", value=item.get("definition", ""))
                        updated_payload["example"] = st.text_input("Example", value=item.get("example", ""))
                        
                    elif card_type == "lab":
                        updated_payload["title"] = st.text_input("Title", value=item.get("title", ""))
                        updated_payload["formula"] = st.text_input("Equipment", value=item.get("formula", ""))
                        updated_payload["description"] = st.text_area("Content & Results", value=item.get("description", ""))

                    elif card_type == "ai":
                        updated_payload["title"] = st.text_input("Tool / Prompt Title", value=item.get("title", ""))
                        updated_payload["formula"] = st.text_input("URL / Category / Tag", value=item.get("formula", ""))
                        updated_payload["description"] = st.text_area("Description / Prompt / Notes", value=item.get("description", ""))

                    if st.form_submit_button("Save Changes"):
                        if update_entry(item_id, updated_payload):
                            st.success("Updated!")
                            st.rerun()

        # --- Delete Popover ---
        with col3:
            with st.popover("🗑️ Delete"):
                st.write("Confirm deletion?")
                if st.button("Delete Now", key=f"del_{card_type}_{item_id}"):
                    if delete_entry(item_id):
                        st.rerun()

# ==========================================
# SIDEBAR: STATS & DATA MANAGEMENT
# ==========================================
with st.sidebar:
    st.header("📊 Supabase Statistics")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Physics", len(data_store["physics"]))
        st.metric("C++ Code", len(data_store["cpp"]))
        st.metric("Experiments", len(data_store["lab"]))
    with col_s2:
        st.metric("Math", len(data_store["math"]))
        st.metric("IELTS Words", len(data_store["ielts"]))
        st.metric("AI Tools", len(data_store["ai"]))
    
    st.divider()
    st.subheader("💾 Data Management")
    
    # Backup
    st.download_button(
        label="📥 Export JSON Backup",
        data=json.dumps(data_store, ensure_ascii=False, indent=4),
        file_name="knowledge_backup.json",
        mime="application/json",
        use_container_width=True
    )

    # Restore
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

# ==========================================
# APP HEADER
# ==========================================
st.title("⚡ PhysEng Study Core v3.0")
st.caption("Personal Knowledge Hub for Physics, Mathematics, C++ Engineering, IELTS Preparation, AI Tools & Experiments")
st.divider()

# ==========================================
# MAIN TABS
# ==========================================
tab_physics, tab_math, tab_cpp, tab_ielts, tab_lab, tab_ai = st.tabs([
    "📐 Physics & Chemistry",
    "🧮 Mathematics",
    "💻 C++ Code Snippets",
    "🇬🇧 IELTS Vocabulary",
    "🧪 Physics Experiments & AI",
    "🤖 AI Tools & Prompts"
])

# ------------------------------------------
# TAB 1: PHYSICS & CHEMISTRY
# ------------------------------------------
with tab_physics:
    st.header("Physics & Chemistry Knowledge Base")

    with st.expander("➕ Add New Formula / Concept"):
        with st.form("physics_form", clear_on_submit=True):
            topic = st.text_input("Topic / Title", placeholder="e.g., Work Done")
            formula = st.text_input("LaTeX Formula (optional)", placeholder=r"e.g., W = F \cdot s \cdot \cos(\alpha)")
            description = st.text_area("Description / Notes", placeholder="Explain variables and meaning...")
            if st.form_submit_button("Save Entry") and topic:
                if add_entry({"category": "physics", "title": topic, "formula": formula, "description": description}):
                    st.success("Successfully saved!")
                    st.rerun()

    search = st.text_input("🔍 Search Physics entries...", key="search_phys")
    items = [
        item for item in data_store["physics"]
        if not search or search.lower() in item["title"].lower() or search.lower() in (item.get("description") or "").lower()
    ]
    if not items:
        st.info("No matching entries found.")
    else:
        for item in items:
            render_entry_card(item, "physics")

# ------------------------------------------
# TAB 2: MATHEMATICS
# ------------------------------------------
with tab_math:
    st.header("Mathematics Knowledge Base")

    with st.expander("➕ Add New Math Formula / Theorem"):
        with st.form("math_form", clear_on_submit=True):
            topic = st.text_input("Topic / Title", placeholder="e.g., Differential Equation of Motion")
            formula = st.text_input("LaTeX Formula", placeholder=r"e.g., \frac{d^2x}{dt^2} + \omega^2 x = 0")
            description = st.text_area("Description / Notes", placeholder="Explain concept, proof steps...")
            if st.form_submit_button("Save Entry") and topic:
                if add_entry({"category": "math", "title": topic, "formula": formula, "description": description}):
                    st.success("Successfully saved!")
                    st.rerun()

    search = st.text_input("🔍 Search Math entries...", key="search_math")
    items = [
        item for item in data_store["math"]
        if not search or search.lower() in item["title"].lower() or search.lower() in (item.get("description") or "").lower()
    ]
    if not items:
        st.info("No matching entries found.")
    else:
        for item in items:
            render_entry_card(item, "math")

# ------------------------------------------
# TAB 3: C++ CODE SNIPPETS
# ------------------------------------------
with tab_cpp:
    st.header("C++ Code Snippets")

    with st.expander("➕ Add New C++ Snippet"):
        with st.form("cpp_form", clear_on_submit=True):
            title = st.text_input("Snippet Title", placeholder="e.g., Read Sensor Data")
            code = st.text_area("C++ Code", placeholder="void setup() {\n  ...\n}", height=150)
            note = st.text_input("Notes / Hardware Pin", placeholder="e.g., Pin 13 LED")
            if st.form_submit_button("Save Code") and title and code:
                if add_entry({"category": "cpp", "title": title, "code": code, "note": note}):
                    st.success("Successfully saved!")
                    st.rerun()

    search = st.text_input("🔍 Search C++ snippets...", key="search_cpp")
    items = [
        item for item in data_store["cpp"]
        if not search or search.lower() in item["title"].lower() or search.lower() in (item.get("code") or "").lower() or search.lower() in (item.get("note") or "").lower()
    ]
    if not items:
        st.info("No matching snippets found.")
    else:
        for item in items:
            render_entry_card(item, "cpp")

# ------------------------------------------
# TAB 4: IELTS VOCABULARY
# ------------------------------------------
with tab_ielts:
    st.header("IELTS Vocabulary & Phrases")

    with st.expander("➕ Add New Word / Phrase"):
        with st.form("ielts_form", clear_on_submit=True):
            word = st.text_input("Word / Phrase", placeholder="e.g., Perseverance")
            word_type = st.selectbox("Type", ["noun", "verb", "adjective", "adverb", "phrase", "idiom"])
            definition = st.text_input("Definition", placeholder="e.g., Continued effort to achieve something")
            example = st.text_input("Example Sentence", placeholder="e.g., It takes perseverance to learn C++.")
            if st.form_submit_button("Save Word") and word:
                if add_entry({"category": "ielts", "title": word, "word_type": word_type, "definition": definition, "example": example}):
                    st.success("Successfully saved!")
                    st.rerun()

    search = st.text_input("🔍 Search Vocabulary...", key="search_ielts")
    items = [
        item for item in data_store["ielts"]
        if not search or search.lower() in item["title"].lower() or search.lower() in (item.get("definition") or "").lower()
    ]
    if not items:
        st.info("No matching words found.")
    else:
        for item in items:
            render_entry_card(item, "ielts")

# ------------------------------------------
# TAB 5: PHYSICS EXPERIMENTS & AI
# ------------------------------------------
with tab_lab:
    st.header("🧪 Physics Lab, Simulations & AI Generator")

    # 1. INTERACTIVE SIMULATOR
    st.subheader("1. 🎮 Interactive Simulator: 1D Collision & Momentum Conservation")
    st.caption(r"Interactive experiment to verify Momentum ($p = mv$) and Kinetic Energy ($E_k = \frac{1}{2}mv^2$).")

    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        st.markdown("**Object 1 ($m_1$)**")
        m1 = st.slider("Mass m1 (kg)", 0.5, 10.0, 2.0, 0.5)
        v1 = st.slider("Initial Velocity v1 (m/s)", -10.0, 10.0, 5.0, 0.5)

    with sim_col2:
        st.markdown("**Object 2 ($m_2$)**")
        m2 = st.slider("Mass m2 (kg)", 0.5, 10.0, 3.0, 0.5)
        v2 = st.slider("Initial Velocity v2 (m/s)", -10.0, 10.0, -2.0, 0.5)

    collision_type = st.radio("Collision Type", ["Elastic Collision", "Inelastic Collision"], horizontal=True)

    # Calculations
    p_initial = m1 * v1 + m2 * v2
    ek_initial = 0.5 * m1 * (v1 ** 2) + 0.5 * m2 * (v2 ** 2)

    if "elastic" in collision_type.lower():
        v1_final = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
        v2_final = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)
    else:
        v_common = p_initial / (m1 + m2)
        v1_final = v2_final = v_common

    p_final = m1 * v1_final + m2 * v2_final
    ek_final = 0.5 * m1 * (v1_final ** 2) + 0.5 * m2 * (v2_final ** 2)

    # Display Metrics
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Final Velocity v1'", f"{v1_final:.2f} m/s")
    m_col2.metric("Final Velocity v2'", f"{v2_final:.2f} m/s")
    m_col3.metric("Momentum (Init / Final)", f"{p_initial:.2f} / {p_final:.2f}", delta=f"{p_final - p_initial:.2f}")
    m_col4.metric("Kinetic Energy (Init / Final)", f"{ek_initial:.2f} / {ek_final:.2f} J", delta=f"{ek_final - ek_initial:.2f} J")

    # Chart Trajectories
    t_collision = 2.0
    time_before = np.linspace(0, t_collision, 20)
    time_after = np.linspace(t_collision, 5.0, 30)

    x1_before, x2_before = 0.0 + v1 * time_before, 10.0 + v2 * time_before
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

    # 2. AI EXPERIMENT GENERATOR
    st.subheader("2. 🤖 AI Experiment Generator (Gemini Powered)")
    st.caption("Enter any topic or concept, and AI will automatically draft a structured lab experiment setup for you.")

    ai_prompt = st.text_input("💡 What experiment would you like to design?", placeholder="e.g., Conservation of Mechanical Energy...")

    if st.button("✨ Generate Experiment with AI", use_container_width=True):
        if not ai_prompt:
            st.warning("Please enter an experiment topic!")
        elif not gemini_model:
            st.error("Gemini API key is not configured in secrets.")
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
                    st.session_state["last_ai_exp"] = json.loads(response.text)
                    st.success("Experiment generated successfully!")
                except Exception as e:
                    st.error(f"Error generating experiment with AI: {e}")

    # Display AI Result
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

    # 3. LAB EXPERIMENT LOG (SUPABASE CRUD)
    st.subheader("3. 📝 Lab Experiment Log & History (Supabase)")

    with st.expander("➕ Add New Manual Experiment Entry"):
        with st.form("lab_form", clear_on_submit=True):
            exp_title = st.text_input("Experiment Title", placeholder="e.g., Verifying Conservation of Linear Momentum")
            equipment = st.text_input("Equipment & Tools", placeholder="e.g., Air track, photogates, gliders")
            description = st.text_area("Description, Procedure & Conclusion", placeholder="Record observations...")
            if st.form_submit_button("Save Experiment") and exp_title:
                if add_entry({"category": "lab", "title": exp_title, "formula": equipment, "description": description}):
                    st.success("Experiment saved to Supabase!")
                    st.rerun()

    search = st.text_input("🔍 Search experiments...", key="search_lab")
    items = [
        item for item in data_store["lab"]
        if not search or search.lower() in item["title"].lower() or search.lower() in (item.get("description") or "").lower()
    ]
    if not items:
        st.info("No experiments recorded yet.")
    else:
        for item in items:
            render_entry_card(item, "lab")

# ------------------------------------------
# TAB 6: AI TOOLS & PROMPTS
# ------------------------------------------
with tab_ai:
    st.header("🤖 AI Tools, Workflows & Prompts Library")

    with st.expander("➕ Add New AI Tool / Prompt"):
        with st.form("ai_form", clear_on_submit=True):
            ai_title = st.text_input("Tool / Prompt Title", placeholder="e.g., Jeff Su AI Productivity Prompt / ChatGPT Code Reviewer")
            ai_tag = st.text_input("URL / Category / Tag", placeholder="e.g., https://... or Productivity, Coding, Physics Helper")
            ai_desc = st.text_area("Description / Prompt Template / Notes", placeholder="Paste prompt or details here...", height=150)
            if st.form_submit_button("Save AI Entry") and ai_title:
                if add_entry({"category": "ai", "title": ai_title, "formula": ai_tag, "description": ai_desc}):
                    st.success("AI entry saved successfully!")
                    st.rerun()

    search = st.text_input("🔍 Search AI tools or prompts...", key="search_ai")
    items = [
        item for item in data_store["ai"]
        if not search or search.lower() in item["title"].lower() or search.lower() in (item.get("description") or "").lower() or search.lower() in (item.get("formula") or "").lower()
    ]
    if not items:
        st.info("No AI entries found.")
    else:
        for item in items:
            render_entry_card(item, "ai")
