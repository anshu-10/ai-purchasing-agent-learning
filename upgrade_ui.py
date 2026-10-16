from pathlib import Path
import shutil

ROOT = Path.cwd()
DASHBOARD = ROOT / "frontend" / "dashboard.py"
STREAMLIT_DIR = ROOT / ".streamlit"
CONFIG = STREAMLIT_DIR / "config.toml"

if not DASHBOARD.exists():
    raise SystemExit(
        f"Could not find {DASHBOARD}. Run this script from the repository root."
    )

STREAMLIT_DIR.mkdir(exist_ok=True)

CONFIG.write_text(
    '[theme]\n'
    'base = "dark"\n'
    'primaryColor = "#00C2A8"\n'
    'backgroundColor = "#0B0F14"\n'
    'secondaryBackgroundColor = "#111821"\n'
    'textColor = "#E8EEF5"\n'
    'font = "sans serif"\n'
    'baseRadius = "medium"\n'
    '\n'
    '[theme.sidebar]\n'
    'backgroundColor = "#0F151D"\n'
    'secondaryBackgroundColor = "#111821"\n'
    'borderColor = "#253241"\n',
    encoding="utf-8",
)

source = DASHBOARD.read_text(encoding="utf-8")
marker = "# === PROCUREMENT UI UPGRADE ==="

if marker in source:
    print("UI upgrade is already installed. No changes made.")
    raise SystemExit(0)

backup = DASHBOARD.with_suffix(".py.ui-backup")
shutil.copy2(DASHBOARD, backup)

css = (
    '<style>\n'
    '.block-container { max-width: 1500px; padding-top: 2rem; padding-bottom: 3rem; }\n'
    '[data-testid="stHeader"] { background: transparent; }\n'
    '[data-testid="stToolbar"] { right: 1rem; }\n'
    'section[data-testid="stSidebar"] { border-right: 1px solid #253241; }\n'
    'section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }\n'
    'div[data-testid="stVerticalBlockBorderWrapper"] { border: 1px solid #253241; border-radius: 14px; background: linear-gradient(145deg,#111821,#0D131A); }\n'
    'div[data-testid="stMetric"] { background: #111821; border: 1px solid #253241; padding: 1rem 1.1rem; border-radius: 12px; }\n'
    'div[data-testid="stMetricLabel"] { color: #91A1B2; }\n'
    'div[data-testid="stMetricValue"] { font-weight: 700; }\n'
    '.stButton > button { border-radius: 10px; min-height: 2.7rem; font-weight: 650; border: 1px solid #2A3949; transition: all .15s ease; }\n'
    '.stButton > button:hover { border-color: #00C2A8; box-shadow: 0 0 0 1px #00C2A8; }\n'
    'button[kind="primary"] { background: linear-gradient(90deg,#00A98F,#00C2A8); color: #06110F; border: 0; }\n'
    'div[data-baseweb="select"] > div, div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input { border-radius: 9px; }\n'
    'details { border: 1px solid #253241 !important; border-radius: 10px !important; background: #0F151D !important; }\n'
    '[data-testid="stDataFrame"] { border: 1px solid #253241; border-radius: 10px; overflow: hidden; }\n'
    'div[data-testid="stAlert"] { border-radius: 10px; }\n'
    'h1 { letter-spacing: -.035em; } h2,h3 { letter-spacing: -.02em; }\n'
    '.procurement-hero { padding: 1.35rem 1.5rem; margin: 0 0 1.5rem 0; border: 1px solid #253241; border-radius: 16px; background: radial-gradient(circle at 85% 20%,rgba(0,194,168,.12),transparent 30%),linear-gradient(135deg,#111A23,#0B1118); }\n'
    '.procurement-kicker { color: #00C2A8; font-size: .78rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }\n'
    '.procurement-subtitle { color: #91A1B2; margin-top: .35rem; font-size: .98rem; }\n'
    '</style>'
)

banner = (
    '<div class="procurement-hero">'
    '<div class="procurement-kicker">PROCUREMENT INTELLIGENCE CONSOLE</div>'
    '<div class="procurement-subtitle">Investigate → Constrain → Decide → Approve → Execute → Validate</div>'
    '</div>'
)

injected = (
    '\n# === PROCUREMENT UI UPGRADE ===\n'
    '# Presentation layer only. Agent, database, constraints and workflow are unchanged.\n'
    f'st.markdown({css!r}, unsafe_allow_html=True)\n'
    f'st.markdown({banner!r}, unsafe_allow_html=True)\n'
    '# === END PROCUREMENT UI UPGRADE ===\n'
)

lines = source.splitlines(keepends=True)

insert_at = None
for i, line in enumerate(lines):
    if "st.set_page_config(" in line:
        insert_at = i + 1
        break

if insert_at is None:
    last_import = -1
    for i, line in enumerate(lines):
        if line.startswith(("import ", "from ")):
            last_import = i
    insert_at = last_import + 1

lines.insert(insert_at, injected)
DASHBOARD.write_text("".join(lines), encoding="utf-8")

print("UI upgrade installed successfully.")
print(f"Changed: {DASHBOARD}")
print(f"Created: {CONFIG}")
print(f"Backup:  {backup}")
print()
print("Run:")
print("  streamlit run frontend/dashboard.py")
