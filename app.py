import json
import os
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="PhysEng Study Core", page_icon="⚡", layout="wide"
)

DATA_FILE = "knowledge.json"


# Functions to Load and Save Data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"physics": [], "cpp": [], "ielts": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Initialize Data
data = load_data()

# App Header
st.title("⚡ PhysEng Study Core v1.0")
st.caption(
    "Personal Knowledge Hub for Physics, C++ Engineering, and IELTS Preparation"
)
st.divider()

# Tabs
tab_physics, tab_cpp, tab_ielts = st.tabs(
    ["📐 Physics & Chemistry", "💻 C++ Code Snippets", "🇬🇧 IELTS Vocabulary"]
)

# ==========================================
# TAB 1: PHYSICS & CHEMISTRY
# ==========================================
with tab_physics:
    st.header("Physics & Chemistry Knowledge Base")

    # Form to add new formula
    with st.expander("➕ Add New Formula / Concept"):
        with st.form("physics_form", clear_on_submit=True):
            topic = st.text_input("Topic / Title", placeholder="e.g., Work Done")
            formula = st.text_input(
                "LaTeX Formula (optional)", placeholder=r"e.g., W = F \cdot s \cdot \cos(\alpha)"
            )
            description = st.text_area(
                "Description / Notes",
                placeholder="Explain variables and meaning...",
            )
            submitted = st.form_submit_button("Save Entry")

            if submitted and topic:
                data["physics"].append(
                    {
                        "topic": topic,
                        "formula": formula,
                        "description": description,
                    }
                )
                save_data(data)
                st.success("Successfully added to Physics database!")
                st.rerun()

    # Display entries
    if not data["physics"]:
        st.info("No formulas added yet. Use the form above to add your first entry!")
    else:
        for idx, item in enumerate(data["physics"]):
            with st.container(border=True):
                col1, col2 = st.columns([0.85, 0.15])
                with col1:
                    st.subheader(item["topic"])
                    if item["formula"]:
                        st.latex(item["formula"])
                    if item["description"]:
                        st.write(item["description"])
                with col2:
                    if st.button("Delete", key=f"del_phys_{idx}"):
                        data["physics"].pop(idx)
                        save_data(data)
                        st.rerun()

# ==========================================
# TAB 2: C++ CODE SNIPPETS
# ==========================================
with tab_cpp:
    st.header("C++ Code Snippets")

    # Form to add new code
    with st.expander("➕ Add New C++ Snippet"):
        with st.form("cpp_form", clear_on_submit=True):
            title = st.text_input(
                "Snippet Title", placeholder="e.g., Read Sensor Data"
            )
            code = st.text_area(
                "C++ Code", placeholder="void setup() {\n  ...\n}", height=150
            )
            note = st.text_input("Notes / Hardware Pin", placeholder="e.g., Pin 13 LED")
            submitted = st.form_submit_button("Save Code")

            if submitted and title and code:
                data["cpp"].append({"title": title, "code": code, "note": note})
                save_data(data)
                st.success("Successfully added C++ snippet!")
                st.rerun()

    # Display entries
    if not data["cpp"]:
        st.info("No C++ snippets added yet.")
    else:
        for idx, item in enumerate(data["cpp"]):
            with st.container(border=True):
                col1, col2 = st.columns([0.85, 0.15])
                with col1:
                    st.subheader(item["title"])
                    if item["note"]:
                        st.caption(f"📌 {item['note']}")
                    st.code(item["code"], language="cpp")
                with col2:
                    if st.button("Delete", key=f"del_cpp_{idx}"):
                        data["cpp"].pop(idx)
                        save_data(data)
                        st.rerun()

# ==========================================
# TAB 3: IELTS VOCABULARY
# ==========================================
with tab_ielts:
    st.header("IELTS Vocabulary & Phrases")

    # Form to add new word
    with st.expander("➕ Add New Word / Phrase"):
        with st.form("ielts_form", clear_on_submit=True):
            word = st.text_input("Word / Phrase", placeholder="e.g., Perseverance")
            word_type = st.selectbox(
                "Type", ["noun", "verb", "adjective", "adverb", "phrase", "idiom"]
            )
            definition = st.text_input(
                "Definition", placeholder="e.g., Continued effort to achieve something"
            )
            example = st.text_input(
                "Example Sentence", placeholder="e.g., It takes perseverance to learn C++."
            )
            submitted = st.form_submit_button("Save Word")

            if submitted and word:
                data["ielts"].append(
                    {
                        "word": word,
                        "type": word_type,
                        "definition": definition,
                        "example": example,
                    }
                )
                save_data(data)
                st.success("Successfully added word!")
                st.rerun()

    # Display entries
    if not data["ielts"]:
        st.info("No words added yet.")
    else:
        for idx, item in enumerate(data["ielts"]):
            with st.container(border=True):
                col1, col2 = st.columns([0.85, 0.15])
                with col1:
                    st.markdown(f"### **{item['word']}** *({item['type']})*")
                    if item["definition"]:
                        st.write(f"**Meaning:** {item['definition']}")
                    if item["example"]:
                        st.write(f"*Example:* {item['example']}")
                with col2:
                    if st.button("Delete", key=f"del_ielts_{idx}"):
                        data["ielts"].pop(idx)
                        save_data(data)
                        st.rerun()