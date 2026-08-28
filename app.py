import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import pandas as pd
import numpy as np
import json
import datetime
import streamlit.components.v1 as components

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
        "label": "⚛️ Physics",
        "icon": "⚛️",
        "ai_lab": True,
        "subtitle": "Formulas, Laws & AI Experiment Lab",
        "sim_placeholder": "e.g., Projectile motion with v0 = 30 m/s at 55°",
    },
    "hoa_hoc": {
        "label": "🧪 Chemistry",
        "icon": "🧪",
        "ai_lab": True,
        "subtitle": "Reactions, Kinetics & Temperature Simulations",
        "sim_placeholder": "e.g., First-order reaction rate vs temperature",
    },
    "toan_hoc": {
        "label": "📐 Mathematics",
        "icon": "📐",
        "ai_lab": False,
        "subtitle": "Formulas, Theorems & LaTeX Proofs",
    },
    "cpp": {
        "label": "💻 C++ & CS",
        "icon": "💻",
        "ai_lab": False,
        "subtitle": "Code Snippets, Algorithms & Data Structures",
    },
    "ielts": {
        "label": "📚 IELTS Vocabulary",
        "icon": "📚",
        "ai_lab": False,
        "subtitle": "Flashcards & Academic Word Bank",
    },
}

# ============================================================
# 4. SAMPLE DATA
# ============================================================
SAMPLE_NOTES = {
    "vat_ly": [
        {
            "title": "Projectile Motion — Key Formulas",
            "content": (
                "- **Horizontal velocity:** $v_x = v_0$ (constant)\n"
                "- **Vertical velocity:** $v_y = g \\cdot t$\n"
                "- **Range:** $L = v_0 \\cdot \\sqrt{\\frac{2h}{g}}$\n"
                "- **Trajectory equation:** $y = h - \\frac{g}{2v_0^2}x^2$\n\n"
                "> 💡 Use the **AI Experiment Lab** on the right to simulate a projectile with a custom initial velocity."
            ),
        },
        {
            "title": "Newton's Second Law",
            "content": (
                "$$\\vec{F} = m \\cdot \\vec{a}$$\n\n"
                "- The net force acting on an object equals the product of its mass and acceleration.\n"
                "- Unit: **Newton (N)** = kg·m/s².\n"
                "- Alternate form: **$$F = m \\cdot \\frac{\\Delta v}{\\Delta t}$$**"
            ),
        },
    ],
    "hoa_hoc": [
        {
            "title": "First-Order Reaction Kinetics",
            "content": (
                "- Rate law: $v = k \\cdot [A]$\n"
                "- Half-life: $t_{1/2} = \\frac{\\ln 2}{k}$\n"
                "- Concentration over time: $[A]_t = [A]_0 \\cdot e^{-kt}$\n\n"
                "> 🔬 Use the **AI Experiment Lab** on the right to simulate reactant decay at different temperatures (Arrhenius equation)."
            ),
        },
    ],
    "toan_hoc": [
        {
            "title": "Harmonic Oscillator ODE",
            "content": (
                "**Differential equation of the harmonic oscillator:**\n\n"
                "$$x''(t) + \\omega^2 x(t) = 0$$\n\n"
                "**General solution:**\n\n"
                "$$x(t) = A\\cos(\\omega t + \\varphi)$$\n\n"
                "- $A$: oscillation amplitude\n"
                "- $\\omega$: angular frequency (rad/s)\n"
                "- $\\varphi$: initial phase"
            ),
            "extra": {
                "formula": r"x''(t) + \omega^2 x(t) = 0 \Rightarrow x(t) = A\cos(\omega t + \varphi)"
            },
        },
    ],
    "cpp": [
        {
            "title": "Read LM35 Temperature Sensor",
            "content": (
                "Reads the analog output of the LM35 temperature sensor, converts the "
                "reading to degrees Celsius, and prints it to the Serial Monitor every second."
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
                    "  Serial.print(\"Temperature: \");\n"
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
                "Academic vocabulary describing the quality of persisting — commonly seen "
                "in Education & Success topics for IELTS Writing Task 2."
            ),
            "extra": {
                "type": "noun",
                "definition": "Continued effort to achieve a goal despite difficulties.",
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
# 7. SIMULATION ENGINE — MODELS & PARAMETER DEFINITIONS
# ============================================================
SIM_MODELS = {
    "projectile": {
        "title": "Projectile Motion",
        "emoji": "🚀",
        "default_params": {
            "v0": 20.0,
            "angle": 45.0,
            "gravity": 9.8,
            "drag": 0.05,
        },
        "param_defs": [
            {"key": "v0", "label": "Initial Velocity (m/s)", "min": 5.0, "max": 50.0, "step": 1.0, "live": True},
            {"key": "angle", "label": "Launch Angle (deg)", "min": 5.0, "max": 85.0, "step": 1.0, "live": True},
            {"key": "gravity", "label": "Gravity (m/s²)", "min": 1.0, "max": 25.0, "step": 0.1, "live": True},
            {"key": "drag", "label": "Air Drag Coefficient", "min": 0.0, "max": 0.5, "step": 0.01, "live": False},
        ],
    },
    "pendulum": {
        "title": "Simple Pendulum",
        "emoji": "🕰️",
        "default_params": {
            "length": 2.5,
            "theta0": 45.0,
            "gravity": 9.8,
            "damping": 0.05,
        },
        "param_defs": [
            {"key": "length", "label": "Rod Length (m)", "min": 1.0, "max": 5.0, "step": 0.1, "live": True},
            {"key": "theta0", "label": "Initial Angle (deg)", "min": 5.0, "max": 90.0, "step": 1.0, "live": True},
            {"key": "gravity", "label": "Gravity (m/s²)", "min": 1.0, "max": 20.0, "step": 0.1, "live": True},
            {"key": "damping", "label": "Damping Coefficient", "min": 0.0, "max": 0.5, "step": 0.01, "live": False},
        ],
    },
    "bouncing": {
        "title": "Bouncing Ball",
        "emoji": "🏀",
        "default_params": {
            "height": 6.0,
            "gravity": 9.8,
            "restitution": 0.75,
        },
        "param_defs": [
            {"key": "height", "label": "Drop Height (m)", "min": 1.0, "max": 8.0, "step": 0.5, "live": True},
            {"key": "gravity", "label": "Gravity (m/s²)", "min": 1.0, "max": 20.0, "step": 0.1, "live": True},
            {"key": "restitution", "label": "Restitution (0–1)", "min": 0.3, "max": 0.95, "step": 0.05, "live": True},
        ],
    },
    "particles": {
        "title": "Gas Particle Kinetics",
        "emoji": "💨",
        "default_params": {
            "particleCount": 40,
            "temperature": 450.0,
        },
        "param_defs": [
            {"key": "particleCount", "label": "Particle Count", "min": 5, "max": 60, "step": 1, "live": True},
            {"key": "temperature", "label": "Temperature (K)", "min": 200.0, "max": 1000.0, "step": 10.0, "live": True},
        ],
    },
    "reaction": {
        "title": "First-Order Chemical Reaction",
        "emoji": "🧪",
        "default_params": {
            "temperature": 450.0,
            "reactantCount": 36,
            "Ea": 4000.0,
            "k0": 0.6,
        },
        "param_defs": [
            {"key": "temperature", "label": "Temperature (K)", "min": 300.0, "max": 1000.0, "step": 10.0, "live": True},
            {"key": "reactantCount", "label": "Initial Reactant Particles", "min": 10, "max": 60, "step": 2, "live": True},
            {"key": "Ea", "label": "Activation Energy (J/mol)", "min": 500.0, "max": 12000.0, "step": 100.0, "live": False},
            {"key": "k0", "label": "Pre-exponential Factor", "min": 0.1, "max": 2.0, "step": 0.05, "live": False},
        ],
    },
}


def build_sim_config(sim_type, overrides=None, description=""):
    model = SIM_MODELS.get(sim_type)
    if model is None:
        model = SIM_MODELS["projectile"]
        sim_type = "projectile"
    params = dict(model["default_params"])
    if overrides:
        valid_keys = {d["key"] for d in model["param_defs"]}
        for key, value in overrides.items():
            if key in valid_keys:
                try:
                    params[key] = float(value)
                except Exception:
                    pass
    for d in model["param_defs"]:
        lo, hi = d["min"], d["max"]
        try:
            clamped = min(max(float(params[d["key"]]), float(lo)), float(hi))
        except Exception:
            clamped = float(lo)
        if isinstance(d["step"], int):
            params[d["key"]] = int(round(clamped))
        else:
            params[d["key"]] = round(clamped, 6)
    return {
        "sim_type": sim_type,
        "simType": sim_type,
        "params": params,
        "title": model["title"],
        "emoji": model["emoji"],
        "description": description,
    }


def detect_fallback_sim_type(query, category_key):
    q = (query or "").lower()
    if any(
        keyword in q
        for keyword in [
            "projectile",
            "throw",
            "launch",
            "cannon",
            "ballistic",
            "trajectory",
            "parabola",
            "nem ngang",
            "quỹ đạo",
            "quy dao",
        ]
    ):
        return "projectile"
    if any(keyword in q for keyword in ["pendulum", "swing", "clock", "con lac"]):
        return "pendulum"
    if any(keyword in q for keyword in ["bounc", "restitution", "ball drop"]):
        return "bouncing"
    if any(
        keyword in q
        for keyword in ["gas", "molecule", "kinetic theory", "diffusion", "pressure"]
    ):
        return "particles"
    if any(
        keyword in q
        for keyword in [
            "reaction",
            "chemical",
            "concentration",
            "arrhenius",
            "kinetics",
            "catalyst",
            "hoá",
            "hoa hoc",
            "phản ứng",
            "phan ung",
            "nồng độ",
            "nong do",
        ]
    ):
        return "reaction"
    if category_key == "hoa_hoc":
        return "reaction"
    return "projectile"


def _init_sim_states():
    for cat_key in ["vat_ly", "hoa_hoc"]:
        if f"sim_config_{cat_key}" not in st.session_state:
            default_type = "reaction" if cat_key == "hoa_hoc" else "projectile"
            default_desc = (
                "Arrhenius model: reactant particles (cyan) convert into product particles "
                "(green). Increase temperature to accelerate the reaction."
                if cat_key == "hoa_hoc"
                else "Classic projectile launched from ground level. Tune velocity, angle and gravity, then observe the trajectory."
            )
            st.session_state[f"sim_config_{cat_key}"] = build_sim_config(
                default_type, {}, default_desc
            )
            st.session_state[f"sim_source_{cat_key}"] = "🎯 Preset Scenario"
            st.session_state[f"sim_desc_{cat_key}"] = default_desc
            st.session_state[f"sim_query_{cat_key}_last"] = ""


init_session_state()
_init_sim_states()


# ============================================================
# 8. SIMULATION ENGINE — GEMINI INTEGRATION
# ============================================================
def run_gemini_sim_config(query, category_key):
    api_key = st.session_state.get("gemini_api_key", "")
    if not api_key:
        raise RuntimeError("Gemini API key is missing.")
    genai.configure(api_key=api_key)
    prompt = (
        "You are a physics & chemistry simulation configurator. "
        f'Knowledge query: "{query}". '
        "Return ONLY a valid JSON object (no markdown fences, no extra text) with exactly this schema: "
        '{"sim_type": "projectile"|"pendulum"|"bouncing"|"particles"|"reaction", '
        '"description": "one concise sentence in English describing the simulated phenomenon", '
        '"params": {optional numeric overrides for known parameter keys}}. '
        "Known parameter keys: v0, angle, gravity, drag, length, theta0, damping, height, "
        "restitution, particleCount, temperature, reactantCount, Ea, k0."
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
            if not isinstance(payload, dict):
                raise ValueError("Gemini returned a non-object payload.")
            sim_type = payload.get("sim_type", detect_fallback_sim_type(query, category_key))
            description = payload.get("description", "")
            if description is None:
                description = ""
            params = payload.get("params", {})
            if not isinstance(params, dict):
                params = {}
            return sim_type, description, params
        except Exception as exc:
            last_error = exc
            continue
    raise RuntimeError(str(last_error))


# ============================================================
# 9. HTML5 CANVAS SIMULATION BUILDER
# ============================================================
CANVAS_TEMPLATE = """
<style>
#sim-root{font-family:'Inter',-apple-system,'Segoe UI',sans-serif;background:#0E1117;border:1px solid #2D323F;border-radius:10px;padding:10px 12px 12px;}
#sim-root h4{margin:0 0 8px;color:#D4AF37;font-weight:600;font-size:14px;}
#sim-canvas{width:100%;display:block;background:radial-gradient(1200px 500px at 50% -10%,#131A26 0%,#0A0E15 70%);border:1px solid #2D323F;border-radius:8px;}
#sim-controls{display:flex;gap:8px;margin-top:10px;}
#sim-controls button{flex:1;padding:8px 6px;border:1px solid #2D323F;border-radius:8px;background:#1E222D;color:#E0E0E0;font-size:12.5px;cursor:pointer;transition:all .15s;}
#sim-controls button:hover{border-color:#D4AF37;color:#D4AF37;}
#sim-controls button.active{border-color:#00ADB5;color:#00ADB5;}
.live-row{margin-top:8px;}
.live-row label{display:flex;justify-content:space-between;font-size:11.5px;color:#9AA0AC;margin-bottom:2px;}
.live-row input[type=range]{width:100%;accent-color:#00ADB5;height:16px;cursor:pointer;}
#sim-status{margin-top:8px;font-size:12px;color:#9AA0AC;font-family:Consolas,monospace;background:#161922;border:1px solid #2D323F;border-radius:6px;padding:6px 10px;}
</style>
<div id="sim-root">
<h4>🚀 Simulation</h4>
<canvas id="sim-canvas"></canvas>
<div id="sim-controls">
<button id="btn-play" class="active">⏸ Pause</button>
<button id="btn-reset">↺ Reset Experiment</button>
<button id="btn-clear">🧹 Clear Canvas</button>
</div>
<div id="live-controls"></div>
<div id="sim-status">• Ready</div>
</div>
<script>
(function(){
const CONFIG=__CONFIG_JSON__;
const LIVE=__LIVE_JSON__;
const canvas=document.getElementById('sim-canvas');
const ctx=canvas.getContext('2d');
const W=760,H=430;
canvas.width=W;canvas.height=H;
const GROUND=H-46;
const R=8.314;
let running=true;
let lastT=performance.now();
let traces=[];
let sim={};
let PX=1;

function fmt(v,d){const n=parseFloat(v);if(isNaN(n))return '0';return n.toFixed(d===undefined?1:d);}
function rr(x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}
function circle(x,y,r){ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);}
function rand(a,b){return a+Math.random()*(b-a);}

function reset(){
  traces=[];
  const p=CONFIG.params;
  if(CONFIG.simType==='projectile'){
    const ang=p.angle*Math.PI/180;
    const range=(p.v0*p.v0*Math.sin(2*ang)/Math.max(p.gravity,0.1));
    PX=(W-150)/Math.max(range,10);
    sim={x:70,y:GROUND,vx:p.v0*Math.cos(ang),vy:-p.v0*Math.sin(ang),gravity:p.gravity,drag:p.drag,t:0,landed:false};
  }else if(CONFIG.simType==='pendulum'){
    PX=78;
    sim={theta:p.theta0*Math.PI/180,omega:0,pivot:{x:W/2,y:46},bob:{x:0,y:0}};
    sim.bob.x=sim.pivot.x+p.length*PX*Math.sin(sim.theta);
    sim.bob.y=sim.pivot.y+p.length*PX*Math.cos(sim.theta);
  }else if(CONFIG.simType==='bouncing'){
    PX=(H-80)/Math.max(p.height,1);
    sim={y:-p.height*PX,vy:0,gravity:p.gravity,e:p.restitution,t:0,bounces:0};
  }else if(CONFIG.simType==='particles'||CONFIG.simType==='reaction'){
    sim.box={x:50,y:56,w:W-100,h:H-160};
    sim.temperature=p.temperature;
    const n=CONFIG.simType==='particles'?Math.round(p.particleCount):Math.round(p.reactantCount);
    sim.particles=[];
    for(let i=0;i<n;i++){
      sim.particles.push({x:rand(sim.box.x+16,sim.box.x+sim.box.w-16),y:rand(sim.box.y+16,sim.box.y+sim.box.h-16),vx:0,vy:0,isB:false});
    }
    if(CONFIG.simType==='reaction'){sim.aCount=n;sim.bCount=0;}
  }
  updateStatus();
}

function stepProjectile(dt){
  const sp=Math.hypot(sim.vx,sim.vy);
  if(sp>1e-6){const f=Math.max(1-sim.drag*dt,0.0);sim.vx*=f;sim.vy*=f;}
  sim.vy+=sim.gravity*dt;
  sim.x+=sim.vx*PX*dt;
  sim.y+=sim.vy*PX*dt;
  sim.t+=dt;
  traces.push({x:sim.x,y:sim.y});
  if(traces.length>1500)traces.shift();
  if(sim.y>=GROUND&&sim.vy>0){sim.y=GROUND;sim.vy=0;sim.vx=0;sim.landed=true;}
}

function stepPendulum(dt){
  const p=CONFIG.params;
  const alpha=-(p.gravity/p.length)*Math.sin(sim.theta)-p.damping*sim.omega;
  sim.omega+=alpha*dt;
  sim.theta+=sim.omega*dt;
  sim.bob.x=sim.pivot.x+p.length*PX*Math.sin(sim.theta);
  sim.bob.y=sim.pivot.y+p.length*PX*Math.cos(sim.theta);
  traces.push({x:sim.bob.x,y:sim.bob.y});
  if(traces.length>1200)traces.shift();
}

function stepBouncing(dt){
  sim.vy+=sim.gravity*PX*dt;
  sim.y+=sim.vy*dt;
  sim.t+=dt;
  if(sim.y>=0){
    if(Math.abs(sim.vy)>10){sim.y=0;sim.vy=-sim.vy*sim.e;sim.bounces++;}
    else{sim.y=0;sim.vy=0;}
  }
  if(traces.length===0||Math.abs(traces[traces.length-1].y-sim.y)>4){traces.push({x:sim.t,y:sim.y});}
  if(traces.length>500)traces.shift();
}

function propelParticles(dt){
  const box=sim.box;
  const target=46*Math.sqrt(sim.temperature/300)+8;
  for(const pt of sim.particles){
    const sp=Math.hypot(pt.vx,pt.vy)||1e-6;
    pt.vx=pt.vx/sp*target;pt.vy=pt.vy/sp*target;
    pt.x+=pt.vx*dt;pt.y+=pt.vy*dt;
    if(pt.x<box.x+6){pt.x=box.x+6;pt.vx=Math.abs(pt.vx)*(0.85+Math.random()*0.3);}
    if(pt.x>box.x+box.w-6){pt.x=box.x+box.w-6;pt.vx=-Math.abs(pt.vx)*(0.85+Math.random()*0.3);}
    if(pt.y<box.y+6){pt.y=box.y+6;pt.vy=Math.abs(pt.vy)*(0.85+Math.random()*0.3);}
    if(pt.y>box.y+box.h-6){pt.y=box.y+box.h-6;pt.vy=-Math.abs(pt.vy)*(0.85+Math.random()*0.3);}
  }
}

function stepParticles(dt){
  sim.temperature=CONFIG.params.temperature;
  propelParticles(dt);
}

function stepReaction(dt){
  sim.temperature=CONFIG.params.temperature;
  const p=CONFIG.params;
  const k=p.k0*Math.exp(-p.Ea/(R*sim.temperature));
  const prob=Math.min(k*dt,0.35);
  for(const pt of sim.particles){
    if(!pt.isB&&Math.random()<prob){pt.isB=true;}
  }
  propelParticles(dt);
  let a=0,b=0;
  for(const pt of sim.particles){if(pt.isB)b++;else a++;}
  sim.aCount=a;sim.bCount=b;
}

function drawProjectile(){
  const p=CONFIG.params;
  const ang=p.angle*Math.PI/180;
  ctx.strokeStyle='rgba(45,50,63,0.4)';ctx.lineWidth=1;
  for(let gx=60;gx<W;gx+=60){ctx.beginPath();ctx.moveTo(gx,0);ctx.lineTo(gx,GROUND);ctx.stroke();}
  for(let gy=40;gy<GROUND;gy+=40){ctx.beginPath();ctx.moveTo(0,gy);ctx.lineTo(W,gy);ctx.stroke();}
  ctx.fillStyle='#1E222D';ctx.fillRect(0,GROUND,W,H-GROUND);
  ctx.strokeStyle='#D4AF37';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,GROUND);ctx.lineTo(W,GROUND);ctx.stroke();
  const flight=2*p.v0*Math.sin(ang)/p.gravity;
  ctx.setLineDash([7,7]);ctx.strokeStyle='rgba(0,173,181,0.45)';ctx.lineWidth=2;ctx.beginPath();
  for(let i=0;i<=60;i++){
    const t=i/60*flight;
    const cx=70+p.v0*Math.cos(ang)*PX*t;
    const cy=GROUND-p.v0*Math.sin(ang)*PX*t+0.5*p.gravity*PX*t*t;
    if(i===0)ctx.moveTo(cx,cy);else ctx.lineTo(cx,cy);
  }
  ctx.stroke();ctx.setLineDash([]);
  ctx.strokeStyle='rgba(212,175,55,0.8)';ctx.beginPath();ctx.arc(70,GROUND,42,-ang,0);ctx.stroke();
  if(traces.length>1){
    ctx.strokeStyle='rgba(0,173,181,0.85)';ctx.lineWidth=2.5;ctx.beginPath();
    for(let i=0;i<traces.length;i++){if(i===0)ctx.moveTo(traces[i].x,traces[i].y);else ctx.lineTo(traces[i].x,traces[i].y);}
    ctx.stroke();
  }
  const grd=ctx.createRadialGradient(sim.x-3,sim.y-3,2,sim.x,sim.y,13);
  grd.addColorStop(0,'#FFE9A8');grd.addColorStop(0.4,'#D4AF37');grd.addColorStop(1,'#8C6D1F');
  circle(sim.x,sim.y,12);ctx.fillStyle=grd;ctx.fill();ctx.strokeStyle='#2D323F';ctx.stroke();
  if(!sim.landed){
    ctx.strokeStyle='#FF6B6B';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(sim.x,sim.y);ctx.lineTo(sim.x+sim.vx*22,sim.y+sim.vy*22);ctx.stroke();
  }
}

function drawPendulum(){
  const p=CONFIG.params;
  ctx.fillStyle='#1E222D';ctx.fillRect(sim.pivot.x-140,40,280,8);
  ctx.fillStyle='#D4AF37';ctx.fillRect(sim.pivot.x-140,40,280,2);
  circle(sim.pivot.x,sim.pivot.y,5);ctx.fillStyle='#D4AF37';ctx.fill();
  ctx.strokeStyle='#C9CDD4';ctx.lineWidth=2.5;
  ctx.beginPath();ctx.moveTo(sim.pivot.x,sim.pivot.y);ctx.lineTo(sim.bob.x,sim.bob.y);ctx.stroke();
  const a=Math.PI/2-sim.theta;
  ctx.strokeStyle='rgba(212,175,55,0.7)';ctx.lineWidth=1.5;
  ctx.beginPath();ctx.arc(sim.pivot.x,sim.pivot.y,Math.min(p.length*PX*0.22,60),Math.min(a,Math.PI/2),Math.max(a,Math.PI/2));ctx.stroke();
  if(traces.length>1){
    ctx.strokeStyle='rgba(0,173,181,0.8)';ctx.lineWidth=1.8;ctx.beginPath();
    for(let i=0;i<traces.length;i++){if(i===0)ctx.moveTo(traces[i].x,traces[i].y);else ctx.lineTo(traces[i].x,traces[i].y);}
    ctx.stroke();
  }
  const grd=ctx.createRadialGradient(sim.bob.x-3,sim.bob.y-3,2,sim.bob.x,sim.bob.y,14);
  grd.addColorStop(0,'#B0F5FF');grd.addColorStop(0.5,'#00ADB5');grd.addColorStop(1,'#006B70');
  circle(sim.bob.x,sim.bob.y,13);ctx.fillStyle=grd;ctx.fill();ctx.strokeStyle='#2D323F';ctx.stroke();
}

function drawBouncing(){
  const p=CONFIG.params;
  ctx.strokeStyle='rgba(45,50,63,0.5)';ctx.fillStyle='#9AA0AC';ctx.font='11px Consolas';
  for(let m=1;m<=8;m++){
    const yy=GROUND-m*PX;
    if(yy<10)break;
    ctx.beginPath();ctx.moveTo(8,yy);ctx.lineTo(20,yy);ctx.stroke();
    ctx.fillText(m+'m',24,yy+4);
  }
  ctx.fillStyle='#1E222D';ctx.fillRect(0,GROUND,W,H-GROUND);
  ctx.strokeStyle='#D4AF37';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,GROUND);ctx.lineTo(W,GROUND);ctx.stroke();
  for(let i=0;i<traces.length;i++){
    const tr=traces[i];
    const fade=1-i/traces.length;
    circle(60,GROUND+tr.y,10*fade+2);
    ctx.fillStyle='rgba(0,173,181,'+(0.3*fade).toFixed(3)+')';ctx.fill();
  }
  const ballY=GROUND+sim.y;
  const maxH=Math.max(p.height*PX,1);
  const t=Math.min(1,Math.max(0,(p.height*PX+sim.y)/maxH));
  const grd=ctx.createRadialGradient(56,ballY-3,2,60,ballY,13);
  grd.addColorStop(0,'#FFD180');grd.addColorStop(0.5,'#FF6F00');grd.addColorStop(1,'#8C3B00');
  circle(60,ballY,12);ctx.fillStyle=grd;ctx.fill();ctx.strokeStyle='#2D323F';ctx.stroke();
}

function drawParticles(){
  const box=sim.box;
  rr(box.x,box.y,box.w,box.h,10);ctx.fillStyle='rgba(19,26,38,0.6)';ctx.fill();
  ctx.strokeStyle='#2D323F';ctx.lineWidth=2;ctx.stroke();
  ctx.strokeStyle='rgba(0,173,181,0.35)';ctx.lineWidth=1;
  rr(box.x-3,box.y-3,box.w+6,box.h+6,12);ctx.stroke();
  const speedAvg=46*Math.sqrt(sim.temperature/300)+8;
  for(const pt of sim.particles){
    const sp=Math.hypot(pt.vx,pt.vy);
    const tt=Math.min(sp/speedAvg,1);
    const hue=200-200*tt;
    ctx.fillStyle='hsla('+hue+',85%,62%,0.85)';
    circle(pt.x,pt.y,2.8);ctx.fill();
  }
}

function drawReaction(){
  const box=sim.box;
  rr(box.x,box.y,box.w,box.h,8);ctx.fillStyle='rgba(30,34,45,0.85)';ctx.fill();
  ctx.strokeStyle='rgba(0,173,181,0.5)';ctx.lineWidth=2;ctx.stroke();
  ctx.fillStyle='#2D323F';ctx.fillRect(box.x-8,box.y-8,box.w+16,10);
  for(const pt of sim.particles){
    ctx.fillStyle=pt.isB?'#66BB6A':'#26C6DA';
    circle(pt.x,pt.y,3.0);ctx.fill();
  }
  const total=Math.max(sim.aCount+sim.bCount,1);
  const frac=sim.aCount/total;
  ctx.fillStyle='#161922';ctx.fillRect(box.x,box.y+box.h+14,box.w,10);
  ctx.fillStyle='#26C6DA';ctx.fillRect(box.x,box.y+box.h+14,box.w*frac,10);
  ctx.strokeStyle='#2D323F';ctx.strokeRect(box.x,box.y+box.h+14,box.w,10);
}

function updateStatus(){
  const el=document.getElementById('sim-status');
  if(CONFIG.simType==='projectile'){
    const sp=Math.hypot(sim.vx,sim.vy);
    const xm=(sim.x-70)/PX;
    el.textContent='⏱ t='+fmt(sim.t,2)+'s   📏 x='+fmt(xm,1)+' m   🚀 v='+fmt(sp,2)+' m/s'+(sim.landed?'   🎯 Landed':'');
  }else if(CONFIG.simType==='pendulum'){
    el.textContent='θ = '+fmt(sim.theta*180/Math.PI,1)+'°   ω = '+fmt(sim.omega,2)+' rad/s   T ≈ '+fmt(2*Math.PI*Math.sqrt(CONFIG.params.length/CONFIG.params.gravity),2)+' s';
  }else if(CONFIG.simType==='bouncing'){
    el.textContent='⏱ t='+fmt(sim.t,2)+'s   📏 h='+fmt(-sim.y/PX,2)+' m   🔁 Bounces='+sim.bounces;
  }else if(CONFIG.simType==='particles'){
    const speedAvg=46*Math.sqrt(sim.temperature/300)+8;
    el.textContent='🌡 Temperature = '+fmt(sim.temperature,0)+' K   ⚡ Avg speed = '+fmt(speedAvg,0)+' px/s   n = '+sim.particles.length;
  }else if(CONFIG.simType==='reaction'){
    const k=CONFIG.params.k0*Math.exp(-CONFIG.params.Ea/(R*sim.temperature));
    el.textContent='A = '+sim.aCount+'  →  B = '+sim.bCount+'   ⚗ k = '+fmt(k,3)+' s⁻¹   t½ = '+fmt(Math.LN2/k,1)+' s';
  }
}

const btnPlay=document.getElementById('btn-play');
const btnReset=document.getElementById('btn-reset');
const btnClear=document.getElementById('btn-clear');
btnPlay.addEventListener('click',function(){
  running=!running;
  btnPlay.textContent=running?'⏸ Pause':'▶ Play';
  btnPlay.classList.toggle('active',running);
});
btnReset.addEventListener('click',function(){reset();});
btnClear.addEventListener('click',function(){traces=[];});

function setParam(key,val){
  CONFIG.params[key]=parseFloat(val);
  const el=document.getElementById('lbl-'+key);
  if(el){let digits=0;for(const d of LIVE){if(d.key===key&&d.step<1){digits=2;break;}}el.textContent=fmt(val,digits);}
  applyLive(key);
}
function applyLive(key){
  if(CONFIG.simType==='projectile'){
    if(key==='gravity'){sim.gravity=CONFIG.params.gravity;}
    else{reset();}
  }else if(CONFIG.simType==='pendulum'){
    if(key==='length'||key==='theta0'){reset();}
  }else if(CONFIG.simType==='bouncing'){
    if(key==='restitution'){sim.e=CONFIG.params.restitution;}
    else{reset();}
  }else if(CONFIG.simType==='particles'||CONFIG.simType==='reaction'){
    sim.temperature=CONFIG.params.temperature;
  }
}

const liveWrap=document.getElementById('live-controls');
LIVE.forEach(function(d){
  const row=document.createElement('div');row.className='live-row';
  const lab=document.createElement('label');
  const digits=(d.step<1)?2:0;
  lab.innerHTML='<span>'+d.label+'</span><span id="lbl-'+d.key+'">'+fmt(CONFIG.params[d.key],digits)+'</span>';
  const inp=document.createElement('input');
  inp.type='range';inp.min=d.min;inp.max=d.max;inp.step=d.step;inp.value=CONFIG.params[d.key];
  inp.addEventListener('input',function(){setParam(d.key,this.value);});
  row.appendChild(lab);row.appendChild(inp);
  liveWrap.appendChild(row);
});

function loop(t){
  const dt=Math.min((t-lastT)/1000,0.05);
  lastT=t;
  if(running){
    if(CONFIG.simType==='projectile')stepProjectile(dt);
    else if(CONFIG.simType==='pendulum')stepPendulum(dt);
    else if(CONFIG.simType==='bouncing')stepBouncing(dt);
    else if(CONFIG.simType==='particles')stepParticles(dt);
    else if(CONFIG.simType==='reaction')stepReaction(dt);
    updateStatus();
  }
  if(CONFIG.simType==='projectile')drawProjectile();
  else if(CONFIG.simType==='pendulum')drawPendulum();
  else if(CONFIG.simType==='bouncing')drawBouncing();
  else if(CONFIG.simType==='particles')drawParticles();
  else if(CONFIG.simType==='reaction')drawReaction();
  requestAnimationFrame(loop);
}

document.querySelector('#sim-root h4').textContent=CONFIG.emoji+' '+CONFIG.title;
reset();
requestAnimationFrame(loop);
})();
</script>
"""


def _safe_json(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")


def build_simulation_html(config, live_defs):
    js_config = dict(config)
    js_config["simType"] = config.get("sim_type", "projectile")
    html = CANVAS_TEMPLATE
    html = html.replace("__CONFIG_JSON__", _safe_json(js_config))
    html = html.replace("__LIVE_JSON__", _safe_json(live_defs))
    return html

# ============================================================
# 10. NOTE RENDER FUNCTIONS
# ============================================================
def render_note_card(note, category_key):
    note_id = note.get("id", "")
    title = note.get("title", "Untitled note")
    content = note.get("content", "")
    extra = note.get("extra", {})
    created_raw = note.get("created_at", "")
    try:
        created = (
            datetime.datetime.fromisoformat(created_raw).strftime("%d/%m/%Y %H:%M")
            if created_raw
            else "Unknown"
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
                st.write(f"**Meaning:** {definition}")
            if example:
                st.write(f"*Example:* {example}")
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
        if st.button("🗑️ Delete Note", key=f"note_del_{category_key}_{note_id}"):
            delete_note(category_key, note_id)
            st.rerun()


def render_note_viewer(category_key):
    notes = get_notes(category_key)
    st.markdown('<div class="ai-lab-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="lab-title" style="color: var(--cyan);">🗂️ Note Viewer — Note Library</div>',
        unsafe_allow_html=True,
    )
    search_query = st.text_input(
        "🔍 Search notes...",
        key=f"note_search_{category_key}",
        placeholder="Filter by title or content...",
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
        st.info("📭 No notes saved in this category yet.")
    else:
        st.caption(f"📊 Showing {len(filtered)} / {len(notes)} notes")
        if not filtered:
            st.warning("No notes match your search keyword.")
        for note in filtered:
            try:
                render_note_card(note, category_key)
            except Exception:
                continue
    st.markdown('</div>', unsafe_allow_html=True)


def render_note_editor(category_key):
    st.markdown('<div class="ai-lab-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="lab-title" style="color: var(--gold);">📝 Note Editor — Create New Note</div>',
        unsafe_allow_html=True,
    )
    st.caption("Content supports **Markdown** and **LaTeX** (use `$...$` or `$$...$$`).")
    with st.form(f"note_form_{category_key}", clear_on_submit=True):
        note_title = st.text_input(
            "📌 Note title",
            key=f"note_title_{category_key}",
            placeholder="Enter a note title...",
        )
        note_content = st.text_area(
            "📄 Content (Markdown / LaTeX)",
            key=f"note_content_{category_key}",
            height=180,
            placeholder=(
                "Supports Markdown and LaTeX, e.g.:\n\n"
                "$E = mc^2$\n\n"
                "- Point 1\n"
                "- Point 2"
            ),
        )
        submitted = st.form_submit_button("💾 Save Note")
        if submitted:
            if note_title.strip() and note_content.strip():
                add_note(category_key, note_title.strip(), note_content.strip())
                st.success("✅ Note saved successfully!")
                st.rerun()
            else:
                st.warning("Please fill in both title and content.")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 11. AI EXPERIMENT LAB (HTML5 Canvas + Gemini)
# ============================================================
def render_ai_lab(category_key):
    category_info = CATEGORIES[category_key]
    st.markdown('<div class="ai-lab-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="lab-title" style="color: var(--cyan);">🧪 AI Experiment Lab</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Ask Gemini to configure an interactive HTML5 Canvas simulation for Physics & Chemistry. "
        "When Gemini is offline or fails, a built-in scenario generator (Projectile, Pendulum, "
        "Chemical Reaction) takes over automatically — the lab always works, right on app load."
    )
    query = st.text_input(
        "🎯 Simulation prompt",
        key=f"sim_query_{category_key}",
        placeholder=category_info["sim_placeholder"],
    )
    if st.button("⚡ Activate Gemini Simulation", key=f"sim_run_{category_key}"):
        if not query.strip():
            st.warning("⚠️ Enter a simulation prompt before activating.")
        else:
            sim_type = None
            description = ""
            params_override = {}
            source = "🛡️ Built-in Scenario"
            used_gemini = False
            if st.session_state.get("gemini_available", False):
                with st.spinner("⏳ Gemini AI is configuring the simulation..."):
                    try:
                        sim_type, description, params_override = run_gemini_sim_config(
                            query, category_key
                        )
                        used_gemini = True
                        source = "✨ Gemini AI"
                    except Exception:
                        sim_type = None
                        used_gemini = False
            if not used_gemini or sim_type not in SIM_MODELS:
                sim_type = detect_fallback_sim_type(query, category_key)
                source = "🛡️ Built-in Scenario"
                if not description:
                    description = SIM_MODELS[sim_type]["title"]
            config = build_sim_config(sim_type, params_override, description)
            st.session_state[f"sim_config_{category_key}"] = config
            st.session_state[f"sim_source_{category_key}"] = source
            st.session_state[f"sim_desc_{category_key}"] = description or config["title"]
            st.session_state[f"sim_query_{category_key}_last"] = query.strip()
            st.rerun()

    config = st.session_state.get(f"sim_config_{category_key}")
    if config is None:
        config = build_sim_config("projectile", {}, "")
        st.session_state[f"sim_config_{category_key}"] = config
        st.session_state[f"sim_source_{category_key}"] = "🎯 Preset Scenario"
        st.session_state[f"sim_desc_{category_key}"] = config["title"]

    source = st.session_state.get(f"sim_source_{category_key}", "🎯 Preset Scenario")
    description = st.session_state.get(f"sim_desc_{category_key}", "")
    last_query = st.session_state.get(f"sim_query_{category_key}_last", "")
    model = SIM_MODELS[config["sim_type"]]
    params = config["params"]
    param_defs = model["param_defs"]

    st.markdown(f'<span class="badge">{source}</span>', unsafe_allow_html=True)
    st.markdown(f"### {model['emoji']} {model['title']}")
    if last_query:
        st.caption(f"📝 Prompt: {last_query}")
    if description:
        st.info(description)

    col_a, col_b = st.columns(2)
    for index, pdef in enumerate(param_defs):
        target_col = col_a if index % 2 == 0 else col_b
        with target_col:
            try:
                value = params[pdef["key"]]
            except Exception:
                value = pdef["min"]
            sim_type_key = config.get("sim_type", "projectile")
            widget_value = st.slider(
                pdef["label"],
                min_value=pdef["min"],
                max_value=pdef["max"],
                value=value,
                step=pdef["step"],
                key=f"slider_{category_key}_{sim_type_key}_{pdef['key']}",
            )
            params[pdef["key"]] = widget_value
    st.session_state[f"sim_config_{category_key}"] = config

    live_defs = [d for d in param_defs if d.get("live", False)]
    sim_html = build_simulation_html(config, live_defs)
    component_height = 560 + 52 * len(live_defs)
    components.html(sim_html, height=component_height, scrolling=False)

    try:
        param_rows = [
            {
                "Parameter": pdef["label"],
                "Value": params[pdef["key"]],
                "Range": f"{pdef['min']} – {pdef['max']}",
            }
            for pdef in param_defs
        ]
        param_df = pd.DataFrame(param_rows)
        st.caption("⚙️ Experiment Parameters (current values)")
        st.dataframe(param_df, hide_index=True, use_container_width=True)
    except Exception:
        pass
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 12. LAYOUT RENDERERS
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


def render_full_width(category_key):
    category_info = CATEGORIES[category_key]
    st.markdown(
        f'<div class="category-header"><h2>{category_info["label"]} '
        f'<span style="color:#9AA0AC; font-size:0.9rem;">— {category_info["subtitle"]}</span></h2></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="ai-lab-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="lab-title" style="color: var(--gold);">📝 Note Editor — Create New Note</div>',
        unsafe_allow_html=True,
    )
    if category_key == "ielts":
        st.caption("Create an IELTS vocabulary flashcard with word, type, definition, example and extra notes.")
        with st.form(f"note_form_{category_key}", clear_on_submit=True):
            word = st.text_input("🔤 Word / Phrase", key=f"ielts_word_{category_key}", placeholder="e.g., Perseverance")
            word_type = st.selectbox(
                "🏷️ Word type",
                ["noun", "verb", "adjective", "adverb", "phrase", "idiom"],
                key=f"ielts_type_{category_key}",
            )
            definition = st.text_input("📖 Definition", key=f"ielts_definition_{category_key}", placeholder="e.g., Continued effort to achieve something")
            example = st.text_input("✍️ Example sentence", key=f"ielts_example_{category_key}", placeholder="e.g., It takes perseverance to learn C++.")
            content = st.text_area(
                "📄 Additional notes (Markdown / LaTeX) — optional",
                key=f"ielts_content_{category_key}",
                height=100,
                placeholder="Add tips, collocations, synonyms...",
            )
            submitted = st.form_submit_button("💾 Save Note")
            if submitted:
                if not word.strip():
                    st.warning("Please enter a word / phrase.")
                elif not (content.strip() or definition.strip() or example.strip()):
                    st.warning("Please enter at least one of: definition, example or additional notes.")
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
                    st.success("✅ IELTS vocabulary card saved!")
                    st.rerun()
    elif category_key == "cpp":
        st.caption("Save code snippets with language, source code and a Markdown/LaTeX description.")
        with st.form(f"note_form_{category_key}", clear_on_submit=True):
            title = st.text_input("💻 Snippet title", key=f"cpp_title_{category_key}", placeholder="e.g., Read LM35 sensor")
            language = st.selectbox(
                "🌐 Language",
                ["cpp", "python", "javascript", "sql", "bash", "java", "csharp"],
                key=f"cpp_lang_{category_key}",
            )
            code = st.text_area("👨‍💻 Code", key=f"cpp_code_{category_key}", height=180, placeholder="void setup() {\n  // code...\n}")
            content = st.text_area(
                "📄 Description / Notes (Markdown / LaTeX)",
                key=f"cpp_content_{category_key}",
                height=100,
                placeholder="Describe the function, algorithm, hardware pins...",
            )
            submitted = st.form_submit_button("💾 Save Note")
            if submitted:
                if title.strip() and code.strip() and content.strip():
                    add_note(
                        category_key,
                        title.strip(),
                        content.strip(),
                        {"language": language, "code": code.strip()},
                    )
                    st.success("✅ C++ snippet saved!")
                    st.rerun()
                else:
                    st.warning("Please fill in title, code and description.")
    else:
        st.caption("Long-form Markdown editor with LaTeX formulas in `$...$` or a dedicated formula field.")
        with st.form(f"note_form_{category_key}", clear_on_submit=True):
            title = st.text_input("📐 Theorem / Formula title", key=f"math_title_{category_key}", placeholder="e.g., Harmonic oscillator ODE")
            formula = st.text_input(
                "📝 LaTeX formula (optional)",
                key=f"math_formula_{category_key}",
                placeholder=r"e.g., \int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}",
            )
            content = st.text_area(
                "📄 Content (Markdown / LaTeX)",
                key=f"math_content_{category_key}",
                height=200,
                placeholder="Write the proof, theory, examples...\n\n$x^2 + y^2 = z^2$",
            )
            submitted = st.form_submit_button("💾 Save Note")
            if submitted:
                if title.strip() and content.strip():
                    extra = {}
                    if formula.strip():
                        extra["formula"] = formula.strip()
                    add_note(category_key, title.strip(), content.strip(), extra)
                    st.success("✅ Mathematics note saved!")
                    st.rerun()
                else:
                    st.warning("Please fill in both title and content.")
    st.markdown('</div>', unsafe_allow_html=True)
    render_note_viewer(category_key)

# ============================================================
# 13. SIDEBAR & MAIN ROUTING
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-title">🧠 OmniNote</div>
            <div class="brand-subtitle">& AI LAB v5.0</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)
    selected_category = st.radio(
        "📚 CATEGORIES",
        options=list(CATEGORIES.keys()),
        format_func=lambda key: CATEGORIES[key]["label"],
    )
    try:
        total_notes = sum(count_notes(key) for key in CATEGORIES.keys())
    except Exception:
        total_notes = 0
    st.markdown(
        f'<div class="status-badge">📦 Total notes: <b>{total_notes}</b></div>',
        unsafe_allow_html=True,
    )
    if st.session_state.get("supabase_available", False):
        st.markdown(
            '<div class="status-badge"><span class="status-dot status-dot-green"></span>🟢 Supabase: Connected</div>',
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
    "💎 Premium personal academic hub — Physics · Chemistry · Mathematics · C++ & CS · IELTS Vocabulary — "
    "powered by the interactive AI Simulation Lab."
)
st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)

if CATEGORIES[selected_category]["ai_lab"]:
    render_split_layout(selected_category)
else:
    render_full_width(selected_category)

st.divider()
st.caption("© 2026 OmniNote & AI Lab v5.0 — Streamlit · Supabase-ready · Gemini Fallback Engine · HTML5 Canvas Simulations")
