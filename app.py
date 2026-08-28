import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import pandas as pd
import numpy as np
import json
import datetime

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="OmniNote & AI Lab",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 2. DARK LUXURY CUSTOM CSS
# ============================================================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --bg-main: #0E1117;
  --bg-sidebar: #161922;
  --bg-card: #1E222D;
  --border-color: #2D323F;
  --text-color: #E0E0E0;
  --gold: #D4AF37;
  --cyan: #00ADB5;
  --muted: #9AA0AC;
}

html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
  background-color: var(--bg-main);
  color: var(--text-color);
}

[data-testid="stHeader"] {
  background-color: transparent;
}

[data-testid="stToolbar"] {
  right: 1rem;
}

.block-container {
  padding-top: 2rem;
  padding-bottom: 3rem;
  max-width: 1300px;
}

[data-testid="stSidebar"] {
  background-color: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
}

[data-testid="stSidebar"] * {
  color: var(--text-color);
}

[data-testid="stSidebar"] .stRadio > label {
  color: var(--gold);
  font-weight: 600;
  letter-spacing: 0.3px;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
  padding: 0.35rem 0.6rem;
  border-radius: 8px;
  margin-bottom: 0.1rem;
  font-size: 0.92rem;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
}

h1, h2, h3, h4 {
  color: var(--text-color) !important;
  font-weight: 600;
}

h1 {
  background: linear-gradient(90deg, var(--gold), var(--cyan));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
}

.stExpander {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color) !important;
  border-radius: 10px !important;
  margin-bottom: 0.6rem;
  overflow: hidden;
}

[data-testid="stExpander"] summary {
  font-weight: 500;
}

.stButton > button {
  border-radius: 10px !important;
  background-color: var(--bg-card);
  color: var(--text-color);
  border: 1px solid var(--border-color) !important;
  transition: all 0.2s ease;
}

.stButton > button:hover {
  border-color: var(--gold) !important;
  color: var(--gold);
  box-shadow: 0 0 10px rgba(212, 175, 55, 0.15);
}

.stTextInput input, .stTextArea textarea {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 10px !important;
  color: var(--text-color) !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--cyan) !important;
}

.stSelectbox div[data-baseweb="select"] > div {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 10px !important;
  color: var(--text-color) !important;
}

[data-testid="stForm"] {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 1.2rem 1.2rem 0.8rem 1.2rem;
}

[data-testid="stSlider"] > div > div > div {
  color: var(--gold);
}

.stCaption, [data-testid="stCaptionContainer"] p {
  color: var(--muted);
}

.sidebar-brand {
  text-align: center;
  padding: 0.8rem 0 0.2rem 0;
}

.brand-title {
  font-size: 1.4rem;
  font-weight: 700;
  background: linear-gradient(90deg, var(--gold), var(--cyan));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-subtitle {
  font-size: 0.78rem;
  color: var(--muted);
  letter-spacing: 3px;
  margin-top: 0.15rem;
  text-transform: uppercase;
}

.divider-gold {
  height: 2px;
  background: linear-gradient(90deg, var(--gold), var(--cyan));
  border-radius: 2px;
  margin: 0.7rem 0 1rem 0;
}

.category-header {
  border-left: 4px solid var(--gold);
  padding-left: 1rem;
  margin-bottom: 0.5rem;
}

.category-header h2 {
  margin-bottom: 0.1rem;
}

.ai-lab-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 1rem 1.2rem 1.2rem 1.2rem;
  margin-bottom: 1.2rem;
}

.lab-title {
  font-weight: 600;
  font-size: 1.02rem;
  margin-bottom: 0.3rem;
}

.badge {
  display: inline-block;
  padding: 0.2rem 0.8rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 500;
  border: 1px solid var(--gold);
  color: var(--gold);
  margin-bottom: 0.4rem;
}

.status-badge {
  font-size: 0.78rem;
  margin-top: 0.8rem;
  padding: 0.5rem 0.9rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background-color: var(--bg-card);
}

.status-badge .status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 0.4rem;
}

.status-dot-green { background-color: #4CAF50; }
.status-dot-yellow { background-color: #FFC107; }
.status-dot-grey { background-color: #6C757D; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================
# 3. CATEGORY DEFINITIONS
# ============================================================
CATEGORIES = {
    "vat_ly": {
        "label": "⚛️ Vật Lý",
        "icon": "⚛️",
        "ai_lab": True,
        "subtitle": "Công thức, định luật & Mô phỏng thí nghiệm AI",
    },
    "hoa_hoc": {
        "label": "🧪 Hóa Học",
        "icon": "🧪",
        "ai_lab": True,
        "subtitle": "Phản ứng, động học & Mô phỏng nhiệt độ AI",
    },
    "toan_hoc": {
        "label": "📐 Toán Học",
        "icon": "📐",
        "ai_lab": False,
        "subtitle": "Công thức, định lý & chứng minh LaTeX",
    },
    "cpp": {
        "label": "💻 C++ & CS",
        "icon": "💻",
        "ai_lab": False,
        "subtitle": "Code snippet, thuật toán & cấu trúc dữ liệu",
    },
    "ielts": {
        "label": "📚 IELTS Vocabulary",
        "icon": "📚",
        "ai_lab": False,
        "subtitle": "Bộ thẻ từ vựng & cụm từ học thuật",
    },
}

# ============================================================
# 4. SAMPLE DATA
# ============================================================
SAMPLE_NOTES = {
    "vat_ly": [
        {
            "title": "Công thức chuyển động ném ngang",
            "content": (
                "- **Vận tốc phương ngang:** $v_x = v_0$ (không đổi)\n"
                "- **Vận tốc phương thẳng đứng:** $v_y = g \\cdot t$\n"
                "- **Tầm xa:** $L = v_0 \\cdot \\sqrt{\\frac{2h}{g}}$\n"
                "- **Phương trình quỹ đạo:** $y = h - \\frac{g}{2v_0^2}x^2$\n\n"
                "> 💡 Dùng **AI Experiment Lab** bên phải để mô phỏng quỹ đạo ném ngang với vận tốc ban đầu tùy chỉnh."
            ),
        },
        {
            "title": "Định luật II Newton",
            "content": (
                "$$\\vec{F} = m \\cdot \\vec{a}$$\n\n"
                "- Lực tổng hợp tác dụng lên vật bằng tích khối lượng và gia tốc.\n"
                "- Đơn vị: **Newton (N)** = kg·m/s².\n"
                "- Áp dụng: **$$F = m \\cdot \\frac{\\Delta v}{\\Delta t}$$**"
            ),
        },
    ],
    "hoa_hoc": [
        {
            "title": "Tốc độ phản ứng bậc 1",
            "content": (
                "- Phương trình tốc độ: $v = k \\cdot [A]$\n"
                "- Chu kỳ bán hủy: $t_{1/2} = \\frac{\\ln 2}{k}$\n"
                "- Nồng độ theo thời gian: $[A]_t = [A]_0 \\cdot e^{-kt}$\n\n"
                "> 🔬 Dùng **AI Experiment Lab** bên phải để mô phỏng sự suy giảm nồng độ theo nhiệt độ."
            ),
        },
    ],
    "toan_hoc": [
        {
            "title": "PTVP dao động điều hòa",
            "content": (
                "**Phương trình vi phân dao động điều hòa:**\n\n"
                "$$x''(t) + \\omega^2 x(t) = 0$$\n\n"
                "**Nghiệm tổng quát:**\n\n"
                "$$x(t) = A\\cos(\\omega t + \\varphi)$$\n\n"
                "- $A$: biên độ dao động\n"
                "- $\\omega$: tần số góc (rad/s)\n"
                "- $\\varphi$: pha ban đầu"
            ),
            "extra": {
                "formula": r"x''(t) + \omega^2 x(t) = 0 \Rightarrow x(t) = A\cos(\omega t + \varphi)"
            },
        },
    ],
    "cpp": [
        {
            "title": "Đọc cảm biến nhiệt độ LM35",
            "content": (
                "Đọc giá trị analog từ cảm biến LM35, chuyển đổi sang độ Celsius "
                "và in ra Serial Monitor mỗi giây."
            ),
            "extra": {
                "language": "cpp",
                "tags": "Arduino, Sensor, AnalogRead",
                "code": (
                    "const int sensorPin = A0;\n"
                    "void setup() {\n"
                    "  Serial.begin(9600);\n"
                    "}\n"
                    "void loop() {\n"
                    "  int reading = analogRead(sensorPin);\n"
                    "  float voltage = reading * (5.0 / 1023.0);\n"
                    "  float celsius = voltage * 100.0;\n"
                    "  Serial.print(\"Nhiet do: \");\n"
                    "  Serial.print(celsius);\n"
                    "  Serial.println(\" *C\");\n"
                    "  delay(1000);\n"
                    "}"
                ),
            },
        },
    ],
    "ielts": [
        {
            "title": "Perseverance",
            "content": (
                "Từ vựng học thuật mô tả phẩm chất kiên trì — thường xuất hiện trong "
                "chủ đề Education & Success của IELTS Writing Task 2."
            ),
            "extra": {
                "type": "noun",
                "definition": "Sự kiên trì, bền bỉ theo đuổi mục tiêu dù gặp khó khăn.",
                "example": "It takes perseverance to master a new language.",
            },
        },
    ],
}

# ============================================================
# 5. SESSION STATE INITIALIZATION & FALLBACK DATABASE SYSTEM
# ============================================================
def _generate_id():
    now = datetime.datetime.now()
    return f"note_{now.strftime('%Y%m%d%H%M%S%f')}_{np.random.randint(1000, 9999)}"


def _get_supabase_config():
    try:
        config = st.secrets.get("supabase", {})
        return dict(config)
    except Exception:
        return {}


def _get_gemini_config():
    try:
        gemini_key = st.secrets.get("gemini", {}).get("api_key", "")
        google_key = st.secrets.get("google", {}).get("api_key", "")
        root_key = st.secrets.get("GEMINI_API_KEY", "")
        return gemini_key or google_key or root_key
    except Exception:
        return ""


def init_session_state():
    if "notes" not in st.session_state:
        local_notes = {key: [] for key in CATEGORIES.keys()}
        for cat_key, note_list in SAMPLE_NOTES.items():
            for sample in note_list:
                local_notes[cat_key].append(
                    {
                        "id": _generate_id(),
                        "category": cat_key,
                        "title": sample["title"],
                        "content": sample["content"],
                        "created_at": datetime.datetime.now().isoformat(),
                        "extra": sample.get("extra", {}),
                    }
                )
        st.session_state.notes = local_notes

    if "supabase_available" not in st.session_state:
        supabase_config = _get_supabase_config()
        is_ready = bool(supabase_config.get("url") and supabase_config.get("key"))
        st.session_state.supabase_available = False
        st.session_state.supabase_client = None
        if is_ready:
            try:
                client: Client = create_client(
                    supabase_config["url"], supabase_config["key"]
                )
                st.session_state.supabase_client = client
                st.session_state.supabase_available = True
            except Exception:
                st.session_state.supabase_client = None
                st.session_state.supabase_available = False

    if "gemini_available" not in st.session_state:
        gemini_key = _get_gemini_config()
        st.session_state.gemini_available = bool(gemini_key)
        st.session_state.gemini_api_key = gemini_key


init_session_state()

# ============================================================
# 6. CRUD FUNCTIONS (Supabase-first, Local Session fallback)
# ============================================================
def _normalize_note(row):
    extra = {}
    raw_extra = row.get("meta") or row.get("extra")
    if raw_extra:
        try:
            if isinstance(raw_extra, str):
                extra = json.loads(raw_extra)
            else:
                extra = raw_extra
        except Exception:
            extra = {}
    normalized = dict(row)
    normalized["extra"] = extra
    return normalized


def get_notes(category_key):
    if st.session_state.supabase_available and st.session_state.supabase_client:
        try:
            response = (
                st.session_state.supabase_client.table("notes")
                .select("*")
                .eq("category", category_key)
                .order("created_at")
                .execute()
            )
            if response and response.data:
                return [_normalize_note(row) for row in response.data]
            return []
        except Exception:
            return st.session_state.notes.get(category_key, [])
    return st.session_state.notes.get(category_key, [])


def add_note(category_key, title, content, extra=None):
    extra = extra or {}
    note_id = _generate_id()
    created_at = datetime.datetime.now().isoformat()
    if st.session_state.supabase_available and st.session_state.supabase_client:
        try:
            st.session_state.supabase_client.table("notes").insert(
                {
                    "id": note_id,
                    "category": category_key,
                    "title": title,
                    "content": content,
                    "created_at": created_at,
                    "meta": json.dumps(extra, ensure_ascii=False),
                }
            ).execute()
            return True
        except Exception:
            pass
    st.session_state.notes.setdefault(category_key, []).append(
        {
            "id": note_id,
            "category": category_key,
            "title": title,
            "content": content,
            "created_at": created_at,
            "extra": extra,
        }
    )
    return True


def delete_note(category_key, note_id):
    if st.session_state.supabase_available and st.session_state.supabase_client:
        try:
            (
                st.session_state.supabase_client.table("notes")
                .delete()
                .eq("id", note_id)
                .execute()
            )
            return True
        except Exception:
            pass
    st.session_state.notes.setdefault(category_key, [])
    st.session_state.notes[category_key] = [
        note
        for note in st.session_state.notes[category_key]
        if note.get("id") != note_id
    ]
    return True


def count_notes(category_key):
    try:
        return len(get_notes(category_key))
    except Exception:
        return 0

# ============================================================
# 7. AI SIMULATION ENGINE (Gemini + Fallback Generator)
# ============================================================
def detect_simulation_type(query):
    q = query.lower()
    if any(
        keyword in q
        for keyword in [
            "ném ngang",
            "parabol",
            "projectile",
            "parabola",
            "quỹ đạo",
            "quy dao",
            "trajectory",
        ]
    ):
        return "parabola"
    if any(
        keyword in q
        for keyword in [
            "phản ứng",
            "phan ung",
            "reaction",
            "mũ",
            "mu",
            "exponential",
            "tăng trưởng",
            "tang truong",
            "phân rã",
            "phan ra",
            "decay",
            "nồng độ",
            "nong do",
        ]
    ):
        return "exponential"
    return "sine"


def fallback_simulation(query):
    sim_type = detect_simulation_type(query)
    x = np.linspace(0, 10, 80)
    if sim_type == "parabola":
        y = -0.5 * (x - 5.0) ** 2 + 8.0
        label = "Quỹ đạo Parabol (Ném ngang)"
    elif sim_type == "exponential":
        y = 2.0 * np.exp(0.3 * x)
        label = "Hàm mũ — Tốc độ phản ứng / Tăng trưởng"
    else:
        y = 2.0 * np.sin(x)
        label = "Sóng Sine — Dao động điều hòa"
    df = pd.DataFrame({"x": x, "y": y})
    return df, label, sim_type


def run_gemini_simulation(query):
    api_key = st.session_state.get("gemini_api_key", "")
    if not api_key:
        raise RuntimeError("Gemini API key is missing.")
    genai.configure(api_key=api_key)
    prompt = (
        "Bạn là chuyên gia mô phỏng vật lý / hóa học. "
        f'Dựa trên câu hỏi: "{query}". '
        "Hãy tạo dữ liệu mô phỏng cho đồ thị. "
        "Trả về DUY NHẤT một JSON hợp lệ (không markdown, không giải thích thêm) với cấu trúc: "
        '{"label": "Tên đồ thị ngắn gọn", "sim_type": "sine" | "parabola" | "exponential", '
        '"x": [25 đến 45 số thực tăng dần], "y": [25 đến 45 số thực tương ứng]}.'
    )
    last_error = None
    for model_name in ["gemini-2.0-flash", "gemini-1.5-flash"]:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()
            payload = json.loads(raw_text)
            x_vals = payload["x"]
            y_vals = payload["y"]
            label = payload.get("label", "Mô phỏng từ Gemini AI")
            sim_type = payload.get("sim_type", "sine")
            if not x_vals or not y_vals or len(x_vals) != len(y_vals):
                raise ValueError("Invalid simulation payload from Gemini.")
            df = pd.DataFrame({"x": x_vals, "y": y_vals})
            return df, label, sim_type
        except Exception as exc:
            last_error = exc
            continue
    raise RuntimeError(str(last_error))


def apply_simulation_parameters(x, base_y, sim_type, amplitude, frequency, phase, baseline):
    x = np.asarray(x, dtype=float)
    base_y = np.asarray(base_y, dtype=float)
    center = float(np.mean(x)) if len(x) else 5.0
    offset = float(np.max(base_y)) if len(base_y) else 0.0
    frequency = max(frequency, 0.2)
    if sim_type == "parabola":
        y = offset + baseline - amplitude * (((x - center) / frequency) ** 2)
    elif sim_type == "exponential":
        y = amplitude * base_y + baseline
    else:
        y = offset + baseline + amplitude * np.sin(frequency * x + phase)
    return y

# ============================================================
# 8. NOTE RENDER FUNCTIONS
# ============================================================
def render_note_card(note, category_key):
    note_id = note.get("id", "")
    title = note.get("title", "Chưa có tiêu đề")
    content = note.get("content", "")
    extra = note.get("extra", {})
    created_raw = note.get("created_at", "")
    try:
        created = (
            datetime.datetime.fromisoformat(created_raw).strftime("%d/%m/%Y %H:%M")
            if created_raw
            else "Không rõ"
        )
    except Exception:
        created = created_raw
    with st.expander(f"📌 {title}", expanded=False):
        st.caption(f"🕒 {created}")
        if category_key == "ielts":
            word_type = extra.get("type", "")
            definition = extra.get("definition", "")
            example = extra.get("example", "")
            if word_type:
                st.caption(f"🏷️ {word_type}")
            if definition:
                st.write(f"**Nghĩa:** {definition}")
            if example:
                st.write(f"*Ví dụ:* {example}")
        if category_key == "cpp":
            code = extra.get("code", "")
            language = extra.get("language", "cpp")
            tags = extra.get("tags", "")
            if tags:
                st.caption(f"🏷️ {tags}")
            if code:
                try:
                    st.code(code, language=language)
                except Exception:
                    st.code(code, language=None)
        if category_key == "toan_hoc":
            formula = extra.get("formula", "")
            if formula:
                try:
                    st.latex(formula)
                except Exception:
                    st.markdown(formula)
        if content:
            st.markdown(content)
        if st.button("🗑️ Xóa Note", key=f"note_del_{category_key}_{note_id}"):
            delete_note(category_key, note_id)
            st.rerun()


def render_note_viewer(category_key):
    notes = get_notes(category_key)
    st.markdown('<div class="ai-lab-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="lab-title" style="color: var(--cyan);">🗂️ Note Viewer — Thư viện Ghi Chú</div>',
        unsafe_allow_html=True,
    )
    search_query = st.text_input(
        "🔍 Tìm kiếm ghi chú...",
        key=f"note_search_{category_key}",
        placeholder="Nhập từ khóa để lọc theo tiêu đề hoặc nội dung...",
    )
    if search_query:
        try:
            filtered = [
                note
                for note in notes
                if search_query.lower() in note.get("title", "").lower()
                or search_query.lower() in note.get("content", "").lower()
            ]
        except Exception:
            filtered = notes
    else:
        filtered = notes
    if not notes:
        st.info("📭 Chưa có ghi chú nào trong danh mục này.")
    else:
        st.caption(f"📊 Hiển thị {len(filtered)} / {len(notes)} ghi chú")
        if not filtered:
            st.warning("Không tìm thấy ghi chú phù hợp với từ khóa tìm kiếm.")
        for note in filtered:
            try:
                render_note_card(note, category_key)
            except Exception:
                continue
    st.markdown('</div>', unsafe_allow_html=True)


def render_note_editor(category_key):
    st.markdown('<div class="ai-lab-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="lab-title" style="color: var(--gold);">📝 Note Editor — Tạo Ghi Chú Mới</div>',
        unsafe_allow_html=True,
    )
    st.caption("Nội dung hỗ trợ **Markdown** và **LaTeX** (viết công thức trong `$...$` hoặc `$$...$$`).")
    with st.form(f"note_form_{category_key}", clear_on_submit=True):
        note_title = st.text_input(
            "📌 Tiêu đề ghi chú",
            key=f"note_title_{category_key}",
            placeholder="Nhập tiêu đề ghi chú...",
        )
        note_content = st.text_area(
            "📄 Nội dung (Markdown / LaTeX)",
            key=f"note_content_{category_key}",
            height=180,
            placeholder=(
                "Hỗ trợ Markdown và LaTeX, ví dụ:\n\n"
                "$E = mc^2$\n\n"
                "- Điểm 1\n"
                "- Điểm 2"
            ),
        )
        submitted = st.form_submit_button("💾 Lưu Ghi Chú")
        if submitted:
            if note_title.strip() and note_content.strip():
                add_note(category_key, note_title.strip(), note_content.strip())
                st.success("✅ Đã lưu ghi chú thành công!")
                st.rerun()
            else:
                st.warning("Vui lòng nhập đầy đủ tiêu đề và nội dung ghi chú.")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 9. AI EXPERIMENT LAB (splits for Vật Lý & Hóa Học)
# ============================================================
def render_ai_lab(category_key):
    st.markdown('<div class="ai-lab-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="lab-title" style="color: var(--cyan);">🧪 AI Experiment Lab</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Hỏi Gemini mô phỏng hiện tượng Vật Lý / Hóa Học. "
        "Nếu thiếu API key hoặc API lỗi, bộ sinh dữ liệu dự phòng sẽ tự động tạo số liệu — UI không bao giờ đứt đoạn."
    )
    query = st.text_input(
        "🎯 Câu hỏi mô phỏng",
        key=f"sim_query_{category_key}",
        placeholder='VD: "Mô phỏng ném ngang v0=15m/s" hoặc "Tốc độ phản ứng bậc 1 theo nhiệt độ"',
    )
    if st.button("⚡ Kích hoạt Mô phỏng Gemini", key=f"sim_run_{category_key}"):
        if not query.strip():
            st.warning("⚠️ Hãy nhập câu hỏi mô phỏng trước khi kích hoạt.")
        else:
            sim_data = None
            source = "🛡️ Bộ sinh dữ liệu dự phòng"
            used_gemini = False
            if st.session_state.get("gemini_available", False):
                with st.spinner("⏳ Gemini AI đang xử lý mô phỏng..."):
                    try:
                        df, label, sim_type = run_gemini_simulation(query)
                        sim_data = {
                            "x": df["x"].tolist(),
                            "y": df["y"].tolist(),
                            "label": label,
                            "sim_type": sim_type,
                        }
                        used_gemini = True
                        source = "✨ Gemini AI"
                    except Exception:
                        sim_data = None
                        used_gemini = False
            if sim_data is None:
                try:
                    df, label, sim_type = fallback_simulation(query)
                    sim_data = {
                        "x": df["x"].tolist(),
                        "y": df["y"].tolist(),
                        "label": label,
                        "sim_type": sim_type,
                    }
                    source = "🛡️ Bộ sinh dữ liệu dự phòng"
                except Exception:
                    sim_data = None
            if sim_data is None:
                st.error("❌ Không thể tạo mô phỏng. Vui lòng thử lại với câu hỏi khác.")
            else:
                st.session_state[f"sim_data_{category_key}"] = sim_data
                st.session_state[f"sim_source_{category_key}"] = source
                st.session_state[f"sim_query_{category_key}_last"] = query.strip()
                st.rerun()
    sim_data = st.session_state.get(f"sim_data_{category_key}")
    if sim_data is not None:
        source = st.session_state.get(f"sim_source_{category_key}", "🛡️ Bộ sinh dữ liệu dự phòng")
        st.markdown(f'<span class="badge">{source}</span>', unsafe_allow_html=True)
        st.markdown(f"### {sim_data.get('label', 'Mô phỏng')}")
        last_query = st.session_state.get(f"sim_query_{category_key}_last", "")
        if last_query:
            st.caption(f"📝 Câu hỏi: {last_query}")
        amplitude = st.slider(
            "🎚️ Biên độ (Amplitude)", 0.2, 5.0, 1.0, 0.1, key=f"sim_amp_{category_key}"
        )
        frequency = st.slider(
            "🎚️ Tần số (Frequency)", 0.2, 3.0, 1.0, 0.1, key=f"sim_freq_{category_key}"
        )
        phase = st.slider(
            "🎚️ Pha ban đầu (Phase)", 0.0, 6.28, 0.0, 0.05, key=f"sim_phase_{category_key}"
        )
        baseline = st.slider(
            "🎚️ Dịch chuyển nền (Baseline)", -5.0, 5.0, 0.0, 0.1, key=f"sim_base_{category_key}"
        )
        try:
            x = np.asarray(sim_data["x"], dtype=float)
            base_y = np.asarray(sim_data["y"], dtype=float)
            sim_type = sim_data.get("sim_type", "sine")
            y = apply_simulation_parameters(
                x, base_y, sim_type, amplitude, frequency, phase, baseline
            )
            chart_df = pd.DataFrame({"x": x, "y": y})
            st.line_chart(chart_df.set_index("x"), height=320)
        except Exception:
            try:
                chart_df = pd.DataFrame({"x": sim_data["x"], "y": sim_data["y"]})
                st.line_chart(chart_df.set_index("x"), height=320)
            except Exception:
                st.warning("⚠️ Không thể vẽ đồ thị cho mô phỏng này.")
    else:
        st.info("👆 Nhập câu hỏi mô phỏng và bấm **Kích hoạt Mô phỏng Gemini** để xem số liệu + đồ thị tương tác.")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 10. SPLIT LAYOUT (VẬT LÝ & HÓA HỌC)
# ============================================================
def render_split_layout(category_key):
    category_info = CATEGORIES[category_key]
    st.markdown(
        f'<div class="category-header"><h2>{category_info["label"]} '
        f'<span style="color:#9AA0AC; font-size:0.9rem;">— {category_info["subtitle"]}</span></h2></div>',
        unsafe_allow_html=True,
    )
    left_col, right_col = st.columns([1, 1], gap="large")
    with left_col:
        render_note_editor(category_key)
        render_note_viewer(category_key)
    with right_col:
        render_ai_lab(category_key)

# ============================================================
# 11. FULL-WIDTH LAYOUT (TOÁN, C++, IELTS)
# ============================================================
def render_full_width(category_key):
    category_info = CATEGORIES[category_key]
    st.markdown(
        f'<div class="category-header"><h2>{category_info["label"]} '
        f'<span style="color:#9AA0AC; font-size:0.9rem;">— {category_info["subtitle"]}</span></h2></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="ai-lab-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="lab-title" style="color: var(--gold);">📝 Note Editor — Tạo Ghi Chú Mới</div>',
        unsafe_allow_html=True,
    )
    if category_key == "ielts":
        st.caption("Tạo thẻ từ vựng IELTS với từ, loại từ, định nghĩa, ví dụ và ghi chú bổ sung.")
        with st.form(f"note_form_{category_key}", clear_on_submit=True):
            word = st.text_input("🔤 Từ / Cụm từ", key=f"ielts_word_{category_key}", placeholder="e.g. Perseverance")
            word_type = st.selectbox(
                "🏷️ Loại từ",
                ["noun", "verb", "adjective", "adverb", "phrase", "idiom"],
                key=f"ielts_type_{category_key}",
            )
            definition = st.text_input("📖 Định nghĩa", key=f"ielts_definition_{category_key}", placeholder="e.g. Continued effort to achieve something")
            example = st.text_input("✍️ Ví dụ câu", key=f"ielts_example_{category_key}", placeholder="e.g. It takes perseverance to learn C++.")
            content = st.text_area(
                "📄 Ghi chú bổ sung (Markdown / LaTeX) — tùy chọn",
                key=f"ielts_content_{category_key}",
                height=100,
                placeholder="Viết thêm tips, collocations, synonyms...",
            )
            submitted = st.form_submit_button("💾 Lưu Ghi Chú")
            if submitted:
                if not word.strip():
                    st.warning("Vui lòng nhập từ / cụm từ.")
                elif not (content.strip() or definition.strip() or example.strip()):
                    st.warning("Vui lòng nhập ít nhất định nghĩa, ví dụ hoặc ghi chú bổ sung.")
                else:
                    add_note(
                        category_key,
                        word.strip(),
                        content.strip(),
                        {
                            "type": word_type,
                            "definition": definition.strip(),
                            "example": example.strip(),
                        },
                    )
                    st.success("✅ Đã lưu thẻ từ vựng IELTS!")
                    st.rerun()
    elif category_key == "cpp":
        st.caption("Lưu code snippet với ngôn ngữ, đoạn code và mô tả Markdown/LaTeX.")
        with st.form(f"note_form_{category_key}", clear_on_submit=True):
            title = st.text_input("💻 Tiêu đề snippet", key=f"cpp_title_{category_key}", placeholder="e.g. Đọc cảm biến LM35")
            language = st.selectbox(
                "🌐 Ngôn ngữ",
                ["cpp", "python", "javascript", "sql", "bash", "java", "csharp"],
                key=f"cpp_lang_{category_key}",
            )
            code = st.text_area("👨‍💻 Code", key=f"cpp_code_{category_key}", height=180, placeholder="void setup() {\n  // code...\n}")
            content = st.text_area(
                "📄 Mô tả / Ghi chú (Markdown / LaTeX)",
                key=f"cpp_content_{category_key}",
                height=100,
                placeholder="Mô tả chức năng, thuật toán, hardware pin...",
            )
            submitted = st.form_submit_button("💾 Lưu Ghi Chú")
            if submitted:
                if title.strip() and code.strip() and content.strip():
                    add_note(
                        category_key,
                        title.strip(),
                        content.strip(),
                        {"language": language, "code": code.strip()},
                    )
                    st.success("✅ Đã lưu C++ snippet!")
                    st.rerun()
                else:
                    st.warning("Vui lòng nhập đầy đủ tiêu đề, đoạn code và mô tả.")
    else:
        st.caption("Soạn thảo nội dung Markdown dài kèm công thức LaTeX trong `$...$` hoặc ô công thức riêng.")
        with st.form(f"note_form_{category_key}", clear_on_submit=True):
            title = st.text_input("📐 Tiêu đề công thức / định lý", key=f"math_title_{category_key}", placeholder="e.g. PTVP dao động điều hòa")
            formula = st.text_input(
                "📝 Công thức LaTeX (tùy chọn)",
                key=f"math_formula_{category_key}",
                placeholder=r"e.g. \int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}",
            )
            content = st.text_area(
                "📄 Nội dung (Markdown / LaTeX)",
                key=f"math_content_{category_key}",
                height=200,
                placeholder="Viết chứng minh, lý thuyết, ví dụ...\n\n$x^2 + y^2 = z^2$",
            )
            submitted = st.form_submit_button("💾 Lưu Ghi Chú")
            if submitted:
                if title.strip() and content.strip():
                    extra = {}
                    if formula.strip():
                        extra["formula"] = formula.strip()
                    add_note(category_key, title.strip(), content.strip(), extra)
                    st.success("✅ Đã lưu ghi chú Toán Học!")
                    st.rerun()
                else:
                    st.warning("Vui lòng nhập đầy đủ tiêu đề và nội dung.")
    st.markdown('</div>', unsafe_allow_html=True)
    render_note_viewer(category_key)

# ============================================================
# 12. SIDEBAR & MAIN ROUTING
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-title">🧠 OmniNote</div>
            <div class="brand-subtitle">& AI Lab v5.0</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)
    selected_category = st.radio(
        "📚 CHUYÊN MỤC",
        options=list(CATEGORIES.keys()),
        format_func=lambda key: CATEGORIES[key]["label"],
    )
    try:
        total_notes = sum(count_notes(key) for key in CATEGORIES.keys())
    except Exception:
        total_notes = 0
    st.markdown(
        f'<div class="status-badge">📦 Tổng ghi chú: <b>{total_notes}</b></div>',
        unsafe_allow_html=True,
    )
    if st.session_state.get("supabase_available", False):
        st.markdown(
            '<div class="status-badge"><span class="status-dot status-dot-green"></span>🟢 Supabase: Đã kết nối</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-badge"><span class="status-dot status-dot-yellow"></span>🟡 Supabase: Local Session</div>',
            unsafe_allow_html=True,
        )
    if st.session_state.get("gemini_available", False):
        st.markdown(
            '<div class="status-badge"><span class="status-dot status-dot-green"></span>🔑 Gemini: API Ready</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-badge"><span class="status-dot status-dot-grey"></span>⚪ Gemini: Fallback Mode</div>',
            unsafe_allow_html=True,
        )

st.title("OmniNote & AI Lab v5.0")
st.caption(
    "💎 Trung tâm ghi chú học thuật cá nhân — Vật Lý · Hóa Học · Toán Học · C++ & CS · IELTS Vocabulary — "
    "tích hợp AI Simulation Lab."
)
st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)

if CATEGORIES[selected_category]["ai_lab"]:
    render_split_layout(selected_category)
else:
    render_full_width(selected_category)

st.divider()
st.caption("© 2026 OmniNote & AI Lab v5.0 — Streamlit · Supabase-ready · Gemini Fallback Engine")
