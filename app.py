"""
Hong Kong Scam Watch
A data story for the paper "What the Public Searches vs. What the Government Warns:
Emerging Scam Types in Hong Kong, 2020-2025"

Run locally:  python3.11 -m streamlit run app.py
Folder layout:
    app.py
    .streamlit/config.toml   (colours and settings)
    data/                    (8 csv files)
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

st.set_page_config(page_title="Hong Kong Scam Watch", page_icon="🔍", layout="wide")

DATA = Path(__file__).parent / "data"
YEARS = list(range(2020, 2026))

# ---- Edit these two lines ----
AUTHORS = "New Media and Communication 5507"
PUBLISHED = "November 2026"


# ===========================================================================
# 1. STYLE
# ===========================================================================
SEARCH = "#9B6BF2"       # public searches (purple)
SEARCH_DARK = "#6A28D0"
GOV = "#5FD9AE"          # government warnings (mint)
GOV_LIGHT = "#A8EED5"
GOV_TXT = "#2E9E74"
GREY = "#D3D4D9"         # everything we are not pointing at
BLUE, ORANGE = SEARCH, GOV   # older names still used in a few places
PAPER = "#FFFFFF"        # chart background (charts sit on white cards)
INK = "#14181F"          # masthead
SOURCE_NOTE = "Source: Google Trends (region: Hong Kong); HKSAR Government press releases (info.gov.hk)"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Geist:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap');

/* ---------- base ---------- */
[data-testid="stMarkdownContainer"], label, button, input, textarea, [data-testid="stDataFrame"],
[data-testid="stWidgetLabel"], [data-testid="stCaptionContainer"], [data-testid="stTab"],
[data-testid="stExpander"] summary {
    font-family: 'Geist', 'Noto Sans TC', -apple-system, 'PingFang HK', sans-serif !important;
}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {
    font-size: 1rem; line-height: 1.65; color: #1B1C1F;
}
h1, h2, h3 { font-family: 'Geist', 'Noto Sans TC', sans-serif !important; color: #121315; }
h3 { font-size: 1.5rem !important; font-weight: 600 !important; margin-top: 2rem !important; }

.stApp { background: #EFF0F2; overflow-x: hidden; }
[data-testid="stHeader"] { display: none; }
.block-container { max-width: 1160px; padding-top: 0 !important; padding-bottom: 7rem; }

/* ---------- masthead (top bar, unchanged) ---------- */
.masthead { background: #14181F; width: 100vw; margin-left: calc(50% - 50vw); margin-bottom: 1.4rem;
            border-bottom: 4px solid #E5652E; }
.masthead .inner { max-width: 1160px; margin: 0 auto; padding: 1.25rem 1rem 0 1rem; }
.masthead .brand { display: flex; align-items: baseline; gap: 0.9rem; flex-wrap: wrap; }
.masthead .name { font-family: 'Archivo', sans-serif; font-weight: 800; font-size: 1.7rem;
                  letter-spacing: -0.01em; color: #FFFFFF; }
.masthead .name span { color: #E5652E; }
.masthead .tag { font-family: 'Geist', sans-serif; font-size: 0.82rem; color: #9AA3AF; }
.masthead nav { display: flex; gap: 1.8rem; margin-top: 0.9rem; flex-wrap: wrap; }
.masthead nav a { font-family: 'Archivo', sans-serif; font-weight: 600; font-size: 0.84rem;
                  letter-spacing: 0.07em; text-transform: uppercase; text-decoration: none !important;
                  color: #C9CFD6 !important; padding: 0.5rem 0 0.75rem 0; border-bottom: 3px solid transparent; }
.masthead nav a:hover { color: #FFFFFF !important; }
.masthead nav a.on { color: #FFFFFF !important; border-bottom-color: #FFFFFF; }
@media (max-width: 700px) { .masthead nav { gap: 1.1rem; } .masthead .name { font-size: 1.35rem; } }

/* ---------- breadcrumb and filter chips ---------- */
.crumb { font-size: 0.95rem; color: #121315; }
.crumb .sep { color: #C2C3C9; margin: 0 0.45rem; }
.updated { font-size: 0.92rem; color: #6B6C74; margin: 0.45rem 0 1.1rem 0; }
.updated .bolt { color: #B48CF2; margin-right: 0.3rem; }
.chips { display: flex; gap: 0.7rem; flex-wrap: wrap; margin-bottom: 1.3rem; }
.chip { display: inline-flex; align-items: center; gap: 0.5rem; border: 1.5px solid #121315; border-radius: 999px;
        padding: 0.45rem 1.1rem; font-size: 0.95rem; color: #121315; background: transparent; }
.chip svg { width: 17px; height: 17px; }

/* ---------- white section cards ---------- */
[class*="st-key-sec_"] { background: #FFFFFF; border-radius: 16px; padding: 1.8rem 1.9rem 1.6rem 1.9rem !important;
                         gap: 0.9rem; margin-bottom: 0.4rem; }
[class*="st-key-box_"] { background: #FFFFFF; border: 1px solid #D9DADF; border-radius: 10px;
                         padding: 1.1rem 1.3rem 0.8rem 1.3rem !important; gap: 0.5rem; }
.anchor { position: relative; top: -12px; }

/* hero */
.hero { display: flex; align-items: center; gap: 1.2rem; }
.hero .logo { width: 56px; height: 56px; border-radius: 6px; background: #EADCFD; display: flex;
              align-items: center; justify-content: center; flex: none; }
.hero .logo svg { width: 36px; height: 36px; }
.hero .site { font-weight: 600; font-size: 2.6rem; letter-spacing: -0.03em; color: #121315; line-height: 1.05; }
.hero-sub { font-weight: 600; font-size: 1.55rem; letter-spacing: -0.02em; color: #121315; margin-top: 0.9rem; }
.tags { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.4rem; }
.tag2 { background: #F0F1F3; border-radius: 8px; padding: 0.35rem 0.7rem; font-size: 0.92rem; color: #1B1C1F; }

/* rank row */
.ranks { display: flex; flex-wrap: wrap; margin: 0.6rem 0 0.4rem 0; }
.rk { padding: 0 1.6rem; border-left: 1px solid #D9DADF; }
.rk:first-child { padding-left: 0; border-left: none; }
.rk .l1 { font-size: 0.95rem; color: #121315; }
.rk .l2 { font-size: 0.95rem; color: #2C59E8; font-weight: 500; }
.rk .big { font-weight: 600; font-size: 1.9rem; letter-spacing: -0.02em; color: #121315; margin-top: 0.1rem; }
.rk .arr-up { color: #2E9E74; font-size: 1.4rem; margin-left: 0.2rem; }
.rk .arr-dn { color: #EF4E4E; font-size: 1.4rem; margin-left: 0.2rem; }

/* metric boxes with a thick top bar */
.mgrid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.9rem; margin-top: 0.3rem; }
.mbox { border: 1px solid #D9DADF; border-top: 7px solid #6E6E78; border-radius: 8px; padding: 0.8rem 1rem 0.9rem 1rem;
        background: #FFFFFF; }
.mbox.light { border-top-color: #D3D4D9; }
.mbox .ml { font-size: 0.92rem; color: #2C59E8; font-weight: 500; }
.mbox .ml i { font-style: italic; font-family: Georgia, serif; font-size: 0.85rem; margin-left: 0.2rem; }
.mbox .mv { font-weight: 600; font-size: 1.95rem; letter-spacing: -0.03em; color: #121315; margin-top: 0.15rem;
            display: flex; align-items: center; gap: 0.5rem; }
.mbox .mn { font-size: 0.8rem; color: #6B6C74; margin-top: 0.15rem; }
.pillr { font-size: 0.82rem; font-weight: 500; color: #FFFFFF; background: #EF5A5A; border-radius: 999px;
         padding: 0.12rem 0.5rem; letter-spacing: 0; }
.pillg { font-size: 0.82rem; font-weight: 500; color: #FFFFFF; background: #34B385; border-radius: 999px;
         padding: 0.12rem 0.5rem; letter-spacing: 0; }
@media (max-width: 800px) { .mgrid { grid-template-columns: 1fr 1fr; } }

/* section headings */
.big-h { text-align: center; font-weight: 600; font-size: 2.4rem; letter-spacing: -0.03em; color: #121315;
         margin: 2.6rem 0 0.4rem 0; line-height: 1.15; }
.big-sub { text-align: center; font-size: 1.12rem; color: #2A2B30; margin: 0 auto 1.6rem auto; max-width: 820px;
           line-height: 1.5; }
.sec-h { font-weight: 600; font-size: 1.8rem; letter-spacing: -0.02em; color: #121315; line-height: 1.2; }
.lav { color: #B48CF2; }
.sec-p { font-size: 1.08rem; line-height: 1.6; color: #1B1C1F; margin-top: 0.4rem; max-width: 980px; }
.box-h { font-weight: 600; font-size: 1.15rem; color: #121315; }
.box-s { font-size: 0.85rem; color: #6B6C74; }
.legend { font-size: 0.9rem; color: #1B1C1F; display: flex; gap: 1.2rem; flex-wrap: wrap; }
.legend .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 0.4rem; }
.source { font-size: 0.76rem; color: #8B8C94; margin-top: 0.1rem; }

/* findings with check marks */
.checks { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.6rem; margin-bottom: 1.6rem; }
.check svg { width: 30px; height: 30px; }
.check .t1 { font-size: 0.78rem; color: #6B6C74; margin-top: 0.4rem; font-weight: 500; }
.check .t2 { font-size: 1.12rem; line-height: 1.4; color: #121315; margin-top: 0.2rem; }
@media (max-width: 900px) { .checks { grid-template-columns: 1fr 1fr; } }

/* share bar */
.share { border: 1px solid #D9DADF; border-radius: 10px; padding: 1rem 1.2rem 1.1rem 1.2rem; }
.share .bar { display: flex; height: 20px; border-radius: 5px; overflow: hidden; margin-top: 0.8rem; }
.share .bar i { display: block; height: 100%; }

/* sparkline list */
.spark { width: 100%; border-collapse: collapse; }
.spark td { padding: 0.45rem 0; vertical-align: middle; }
.spark .nm { font-size: 1.1rem; color: #121315; width: 30%; }
.spark .nm small { display: block; font-size: 0.78rem; color: #6B6C74; }
.spark .sv { width: 45%; }
.spark .sv svg { width: 100%; height: 46px; display: block; }
.spark .vv { font-size: 1.25rem; font-weight: 500; color: #121315; text-align: right; padding-left: 1rem; white-space: nowrap; }
.spark .vv small { display: block; font-size: 0.74rem; color: #6B6C74; font-weight: 400; }

/* horizontal bars (like "visits, last 3 months") */
.hbars { display: flex; flex-direction: column; gap: 0.55rem; }
.hb { display: flex; align-items: center; gap: 0.8rem; }
.hb i { display: block; height: 30px; border-radius: 0 6px 6px 0; background: #B892F5; }
.hb .lab { font-size: 0.82rem; color: #121315; line-height: 1.2; }
.hb .lab b { display: block; font-weight: 600; font-size: 0.95rem; }

/* tables */
.tbl { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
.tbl th { text-align: left; font-weight: 500; color: #121315; border-bottom: 1.5px solid #121315;
          padding: 0.55rem 0.7rem 0.55rem 0; white-space: nowrap; }
.tbl td { border-bottom: 1px solid #E3E4E8; padding: 0.75rem 0.7rem 0.75rem 0; color: #1B1C1F; vertical-align: middle; }
.tbl .num { text-align: right; font-variant-numeric: tabular-nums; }
.tbl .lnk { color: #2C59E8; }
.tbl .grey { color: #6B6C74; }
.tbl .pur { color: #7A2FE0; } .tbl .grn { color: #2E9E74; }
.tbl.compact td { padding: 0.45rem 0.6rem 0.45rem 0; font-size: 0.88rem; }
.tblwrap { overflow-x: auto; margin-top: 0.4rem; }

/* override Streamlit's own table styles (grid lines, outer frame) */
[data-testid="stMarkdownContainer"] table.tbl, [data-testid="stMarkdownContainer"] table.spark {
    border: none !important; border-collapse: collapse !important; margin: 0 !important; width: 100% !important;
    display: table !important; }
[data-testid="stMarkdownContainer"] table.tbl th, [data-testid="stMarkdownContainer"] table.tbl td,
[data-testid="stMarkdownContainer"] table.spark td {
    border-top: none !important; border-left: none !important; border-right: none !important;
    background: transparent !important; }
[data-testid="stMarkdownContainer"] table.tbl th { border-bottom: 1.5px solid #121315 !important;
    padding: 0.55rem 0.9rem 0.55rem 0 !important; font-weight: 500 !important; }
[data-testid="stMarkdownContainer"] table.tbl td { border-bottom: 1px solid #E3E4E8 !important;
    padding: 0.7rem 0.9rem 0.7rem 0 !important; }
[data-testid="stMarkdownContainer"] table.tbl.compact td { padding: 0.5rem 0.9rem 0.5rem 0 !important; }
[data-testid="stMarkdownContainer"] table.tbl th:last-child,
[data-testid="stMarkdownContainer"] table.tbl td:last-child { padding-right: 0 !important; }
[data-testid="stMarkdownContainer"] table.tbl tr:last-child td { border-bottom: none !important; }
[data-testid="stMarkdownContainer"] table.spark td { border-bottom: none !important; padding: 0.45rem 0 !important; }
.tbl .term { white-space: nowrap; }
.tbl .term small { display: block; font-size: 0.8rem; color: #6B6C74; white-space: normal; }
.tbl .badge { white-space: nowrap; }
.box-s { margin-bottom: 0.2rem; }
.blk { padding-bottom: 1rem; }
.legend { line-height: 1.6; }
.badge { display: inline-block; font-size: 0.78rem; font-weight: 500; border-radius: 6px; padding: 0.12rem 0.5rem; }
.badge.pur { color: #6A28D0; background: #F1E8FE; } .badge.grn { color: #23825F; background: #E1F7EE; }
.badge.grey { color: #4A4B52; background: #F0F1F3; } .badge.red { color: #C8302F; background: #FDE7E7; }

/* legend list next to donut */
.dl { list-style: none; padding: 0; margin: 0.6rem 0 0 0; }
.dl li { font-size: 1rem !important; margin: 0 0 0.75rem 0; display: flex; align-items: center; gap: 0.6rem; }
.dl .d { width: 14px; height: 14px; border-radius: 50%; flex: none; }
.dl b { font-weight: 600; }

/* dark pill buttons */
.btns { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; margin-top: 0.6rem; }
.btn { display: inline-block; background: #1D1F1C; color: #FFFFFF !important; text-decoration: none !important;
       border-radius: 999px; padding: 0.75rem 1.5rem; font-size: 1rem; font-weight: 500; }
.btn:hover { background: #000000; }
.btn-note { color: #6B6C74; font-size: 0.95rem; }

/* sticky section bar at the bottom */
.secbar { position: fixed; left: 0; right: 0; bottom: 0; background: #FFFFFF; border-top: 1px solid #E3E4E8;
          z-index: 999; box-shadow: 0 -2px 12px rgba(0,0,0,0.04); }
.secbar .in { max-width: 1160px; margin: 0 auto; display: flex; justify-content: space-around; padding: 0.55rem 1rem; }
.secbar a { display: flex; flex-direction: column; align-items: center; gap: 0.2rem; font-size: 0.82rem;
            color: #6B6C74 !important; text-decoration: none !important; text-align: center; }
.secbar a:hover { color: #121315 !important; }
.secbar svg { width: 20px; height: 20px; }
@media (max-width: 700px) { .secbar a span { display: none; } }

/* ---------- other pages ---------- */
.hed { font-family: 'Geist', 'Noto Sans TC', sans-serif; font-weight: 600; font-size: 2.3rem;
       line-height: 1.15; letter-spacing: -0.03em; color: #121315; margin: 0.4rem 0 0.6rem 0; }
.dek { font-size: 1.05rem; line-height: 1.55; color: #2A2B30; margin-bottom: 1.2rem; max-width: 780px; }
.note { font-size: 0.95rem; line-height: 1.6; background: #FFFFFF; border-radius: 10px;
        border-left: 5px solid #B48CF2; padding: 0.8rem 1.1rem; margin: 0.6rem 0 1.2rem 0; color: #1B1C1F; }
[data-testid="stExpander"] { background: #FFFFFF; border-radius: 10px; }
.footer { border-top: 1px solid #D9DADF; margin-top: 3rem; padding-top: 0.8rem; font-size: 0.8rem;
          color: #8B8C94; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

pio.templates["paper"] = go.layout.Template(layout=dict(
    font=dict(family="Geist, 'Noto Sans TC', sans-serif", size=13, color="#4A4B52"),
    paper_bgcolor=PAPER, plot_bgcolor=PAPER,
    xaxis=dict(showgrid=False, linecolor="#D9DADF", ticks="", automargin=True),
    yaxis=dict(gridcolor="#ECECEF", zeroline=False, showline=False, automargin=True),
    hoverlabel=dict(bgcolor="white", font_size=13),
    legend=dict(title_text=""),
    margin=dict(l=0, r=10, t=10, b=0),
))
pio.templates.default = "plotly_white+paper"


def show_chart(fig):
    st.plotly_chart(fig, width="stretch", theme=None, config={"displayModeBar": False})


def chart_header(title, sub=None):
    html = f'<div class="chart-title">{title}</div>'
    if sub:
        html += f'<div class="chart-sub">{sub}</div>'
    st.markdown(html, unsafe_allow_html=True)


def source(extra=""):
    st.markdown(f'<div class="source">{SOURCE_NOTE}{extra}</div>', unsafe_allow_html=True)


def key(color):
    """A small coloured square used inside chart subtitles as a legend."""
    return f'<span class="key" style="background:{color}"></span>'


def footer():
    st.markdown(f'<div class="footer">By {AUTHORS}. Data: Google Trends (Hong Kong) and HKSAR Government '
                'press releases, 2020–2025. Search terms and press-release titles are quoted in their '
                'original language.</div>', unsafe_allow_html=True)


NAV = [("The story", "./"), ("Explore the data", "./explore"),
       ("How to spot a scam", "./guide"), ("Methodology", "./methodology")]


def masthead(active):
    links = "".join(f'<a href="{href}" target="_self" class="{"on" if name == active else ""}">{name}</a>'
                    for name, href in NAV)
    st.markdown(f'''<div class="masthead"><div class="inner">
<div class="brand"><div class="name">Hong Kong <span>Scam</span> Watch</div>
<div class="tag">Public searches vs. government warnings, 2020–2025</div></div>
<nav>{links}</nav></div></div>''', unsafe_allow_html=True)


# Shorter names for chart axes
SHORT = {
    "Government/law enforcement impersonation": "Fake officials / police",
    "Logistics/public service impersonation": "Fake courier / public services",
    "Insurance/financial impersonation": "Fake insurers / banks",
    "Account/messaging app takeover": "Account / app takeover",
    "Health/consumer product scams": "Health / product scams",
    "Investment/cryptocurrency": "Investment / crypto",
    "Cross-border scam compounds": "Scam compounds",
    "Online shopping/trading": "Online shopping",
    "Charity impersonation": "Fake charities",
    "Romance/social": "Romance / social",
    "Job/part-time work": "Job / part-time work",
    "AI/deepfake": "AI / deepfake",
}


def short(cat):
    return SHORT.get(cat, cat)


# ===========================================================================
# 2. DATA
# ===========================================================================
@st.cache_data
def load_data():
    def read(name):
        return pd.read_csv(DATA / name, encoding="utf-8-sig", keep_default_na=False)

    codebook = read("codebook_en.csv").sort_values("display_order")

    searches = read("classified_data.csv")
    for col in ["is_generic", "is_first", "is_breakout"]:
        searches[col] = searches[col].astype(str) == "True"

    trends = read("interest_over_time.csv")
    trends["date"] = pd.to_datetime(trends["date"])

    press = read("press_scam.csv")
    for col in ["is_relevant", "is_template"]:
        press[col] = press[col].astype(str) == "True"
    titles = read("press_titles.csv")              # full titles (some were cut off when scraped)
    press = press.merge(titles, on="release_id", how="left")
    press["title_full"] = press["title_full"].fillna("")
    press["title"] = press["title_full"].where(press["title_full"] != "", press["title"])
    press = press.drop(columns="title_full")
    press["date"] = pd.to_datetime(press["date"])

    monthly = read("press_monthly_totals.csv")
    return codebook, searches, trends, press, monthly


codebook, searches, trends, press, monthly = load_data()

rising = searches[(searches["type"] == "rising") & searches["is_first"] & ~searches["is_generic"]]
press_rel = press[press["is_relevant"]]               # scam-related releases
press_core = press_rel[~press_rel["is_template"]]     # without routine HKMA bank notices

CAT_ORDER = codebook["category_en"].tolist()
COMP_CATS = [c for c in CAT_ORDER if c not in ("Non-specific", "Other")]

TERM_EN = {
    "JPEX 詐騙": "JPEX",
    "WhatsApp 詐騙": "WhatsApp",
    "carousell 騙案": "Carousell",
    "易通行 詐騙": "HKeToll",
    "微信 保險 詐騙": "WeChat insurance",
}
TERM_BY_EN = {v: k for k, v in TERM_EN.items()}
TERM_COLORS = {"JPEX": "#9B6BF2", "WhatsApp": "#3FCB9B", "Carousell": "#7C93F2",
               "HKeToll": "#F2B53A", "WeChat insurance": "#A9AC93"}
TERM_PRESS_PATTERN = {
    "微信 保險 詐騙": "微保|騰訊.*保險|微信.*保險|WeSure",
    "易通行 詐騙": "易通行|HKeToll",
    "WhatsApp 詐騙": "WhatsApp",
    "carousell 騙案": "Carousell|旋轉拍賣",
    "JPEX 詐騙": "JPEX",
}
# Top three fast-rising search terms each year (by growth), leaving out terms we could not
# place in a scam type. Checked against classified_data.csv.
RISERS = {
    2020: [("口罩詐騙", "Face-mask scam"), ("pi幣騙局", "Pi Network coin scam"), ("炒股騙局", "Stock-trading scam")],
    2021: [("助養兒童騙局", "Child-sponsorship scam"), ("bitcoin code騙局", "Bitcoin Code scam"),
           ("nft騙局", "NFT scam")],
    2022: [("柬埔寨詐騙", "Cambodia scam compounds"), ("tinder詐騙王", "The Tinder Swindler"),
           ("nmn騙局", "NMN supplement scam")],
    2023: [("龐氏騙局jpex", "JPEX Ponzi scheme"), ("facetime詐騙", "FaceTime scam"), ("ai騙案", "AI scam")],
    2024: [("微信保險詐騙", "WeChat insurance scam"), ("騰訊保險詐騙", "Tencent insurance scam"),
           ("picc詐騙", "PICC insurance scam")],
    2025: [("deepseek騙局", "DeepSeek scam"), ("myanmar scam", "Myanmar scam compounds"),
           ("binance", "Binance")],
}
TYPE_EN = {"警示": "Warning", "执法": "Enforcement", "统计": "Statistics",
           "宣传/政策": "Publicity / policy", "其他": "Other"}


def compare_shares(gov):
    pub = rising["category_en"].value_counts(normalize=True).reindex(COMP_CATS, fill_value=0) * 100
    gv = gov["category_en"].value_counts(normalize=True).reindex(COMP_CATS, fill_value=0) * 100
    comp = pd.DataFrame({"Scam type": COMP_CATS, "Public": pub.values.round(1), "Government": gv.values.round(1)})
    rho = comp["Public"].rank().corr(comp["Government"].rank())     # Spearman's rho
    return comp, rho


def matched_press(term):
    pattern = TERM_PRESS_PATTERN[term]
    m = press_rel[press_rel["title"].str.contains(pattern, case=False, regex=True)
                  | press_rel["entity"].str.contains(pattern, case=False, regex=True)]
    return m.sort_values("date")


def persistence(term):
    """% of months with interest after the first month with interest."""
    g = trends[trends["term"] == term].sort_values("date")
    first = g.loc[g["interest"] > 0, "date"].min()
    return (g.loc[g["date"] >= first, "interest"] > 0).mean() * 100


WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def word(n, capital=False):
    """Newspaper style: write numbers below 10 as words."""
    w = WORDS[n] if 0 <= n < 10 else f"{n:,}"
    return w.capitalize() if capital else w


def signed(x):
    """Use a proper minus sign for negative numbers."""
    return f"{x:.2f}".replace("-", "−")


def months_between(a, b):
    return (b.year - a.year) * 12 + b.month - a.month


# ===========================================================================
# 3. THE STORY (layout modelled on a Semrush overview page)
# ===========================================================================
# ---------- small building blocks ----------
ICONS = {
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "cal": '<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/>',
    "check": '<path d="M4 12.5 9.5 18 20 6"/>',
    "chart": '<path d="M4 4v16h16"/><path d="M7 15l4-5 3 3 5-6"/>',
    "bell": '<path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
    "scale": '<path d="M12 4v16M5 20h14M5 8h14"/><path d="M5 8l-2.5 6h5zM19 8l-2.5 6h5z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
    "grid": '<rect x="4" y="4" width="7" height="7" rx="1"/><rect x="13" y="4" width="7" height="7" rx="1"/>'
            '<rect x="4" y="13" width="7" height="7" rx="1"/><rect x="13" y="13" width="7" height="7" rx="1"/>',
}


def icon(name, color="currentColor", width=1.8):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


def html(s):
    # Streamlit pulls every text block 1rem up (a negative bottom margin meant for paragraphs);
    # the padding in .blk cancels that so legends and boxes are not covered by the next element.
    st.markdown(f'<div class="blk">{s}</div>', unsafe_allow_html=True)


def section_card(name):
    html(f'<div id="{name}" class="anchor"></div>')
    return st.container(key=f"sec_{name}")


def box(name):
    return st.container(key=f"box_{name}")


def box_head(title, sub=""):
    html(f'<div class="box-h">{title}</div>' + (f'<div class="box-s">{sub}</div>' if sub else ""))


def src(text):
    html(f'<div class="source">Source: {text}</div>')


def legend(items):
    """items = [(label, color, extra_text_or_None)]"""
    html('<div class="legend">' + "".join(
        f'<span><span class="dot" style="background:{c}"></span>{lab}'
        + (f' <span style="color:{c};font-weight:500">{x}</span>' if x else "") + "</span>"
        for lab, c, x in items) + "</div>")


def mbox(label, value, note="", pill=None, light=False):
    p = f'<span class="{pill[1]}">{pill[0]}</span>' if pill else ""
    n = f'<div class="mn">{note}</div>' if note else ""
    return (f'<div class="mbox{" light" if light else ""}"><div class="ml">{label}<i>i</i></div>'
            f'<div class="mv">{value}{p}</div>{n}</div>')


def mgrid(items):
    html(f'<div class="mgrid">{"".join(items)}</div>')


def sparkline(values, color, fill):
    v = list(values)
    top = max(v) or 1
    n = len(v)
    pts = [(i / (n - 1) * 300, 46 - x / top * 42) for i, x in enumerate(v)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"0,48 {line} 300,48"
    return (f'<svg viewBox="0 0 300 48" preserveAspectRatio="none"><polygon points="{area}" fill="{fill}"/>'
            f'<polyline points="{line}" fill="none" stroke="{color}" stroke-width="2" '
            f'vector-effect="non-scaling-stroke"/></svg>')


YEAR_TICKS = dict(tick0="2020-01-01", dtick="M12", tickformat="%Y")


def rgba(hexcolor, a):
    h = hexcolor.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


def page_story():
    masthead("The story")
    html('<div id="top"></div>')

    # ---------- numbers ----------
    comp, rho = compare_shares(press_core)
    c = comp.set_index("Scam type")
    counts = pd.crosstab(rising["category_en"], rising["year"]).reindex(columns=YEARS, fill_value=0)
    lead = counts.drop(index=["Other"], errors="ignore").idxmax()
    inv_lead_years = int((lead == "Investment/cryptocurrency").sum())
    n_all = int(monthly["n_all_releases"].sum())
    n_tpl = int(press_rel["is_template"].sum())
    gov_imp = int((press_core["category_en"] == "Government/law enforcement impersonation").sum())
    gov_imp_pct = gov_imp / len(press_core) * 100
    per_year = press_core.groupby("year").size().reindex(YEARS, fill_value=0)
    growth = (per_year[2025] / per_year[2020] - 1) * 100
    m = monthly.groupby("year")[["n_all_releases", "n_scam_nontemplate"]].sum()
    pct20 = m.loc[2020, "n_scam_nontemplate"] / m.loc[2020, "n_all_releases"] * 100
    pct25 = m.loc[2025, "n_scam_nontemplate"] / m.loc[2025, "n_all_releases"] * 100
    hk = matched_press("易通行 詐騙")
    hk_tr = trends[trends["term"] == "易通行 詐騙"]
    hk_peak = hk_tr.loc[hk_tr["interest"].idxmax(), "date"]
    hk_lead = months_between(hk["date"].min(), hk_peak)
    jp = trends[trends["term"] == "JPEX 詐騙"]
    jp_peak = jp.loc[jp["interest"].idxmax(), "date"]
    no_press = [TERM_EN[t] for t in TERM_EN if len(matched_press(t)) == 0]
    no_press_txt = ", ".join(no_press[:-1]) + " and " + no_press[-1] if len(no_press) > 1 else "".join(no_press)
    top_gov = comp.sort_values("Government", ascending=False).iloc[0]
    n_rising = rising["query_clean"].nunique()

    # ---------- breadcrumb, chips ----------
    html(f'<div class="crumb">Main<span class="sep">/</span>Hong Kong scams</div>'
         f'<div class="updated"><span class="bolt">⚡</span>Last updated: {PUBLISHED} &nbsp;·&nbsp; By {AUTHORS}</div>'
         f'<div class="chips"><span class="chip">{icon("globe")}Hong Kong</span>'
         f'<span class="chip">{icon("cal")}Jan 2020 – Dec 2025</span></div>')

    # ---------- hero card ----------
    with st.container(key="sec_hero"):
        html(f'<div class="hero"><div class="logo">{icon("search", "#121315", 2.2)}</div>'
             f'<div class="site">Hong Kong scams</div></div>'
             f'<div class="hero-sub">2020–2025 Attention Stats</div>'
             f'<div class="tags"><span class="tag2">Google Trends</span><span class="tag2">Government press releases</span>'
             f'<span class="tag2">Online fraud</span><span class="tag2">Public communication</span></div>')
        html(f'<div class="ranks">'
             f'<div class="rk"><div class="l1">Top search type:</div><div class="l2">Investment / crypto</div>'
             f'<div class="big">{c.loc["Investment/cryptocurrency", "Public"]:g}%</div></div>'
             f'<div class="rk"><div class="l1">Top warning type:</div><div class="l2">{short(top_gov["Scam type"])}</div>'
             f'<div class="big">{top_gov["Government"]:g}%</div></div>'
             f'<div class="rk"><div class="l1">Rank correlation:</div><div class="l2">Searches vs. warnings</div>'
             f'<div class="big">{signed(rho)}</div></div></div>')
        mgrid([
            mbox("Search terms", f"{len(searches):,}", "4 seed keywords × 6 years"),
            mbox("Fast-rising terms", f"{n_rising}", "distinct, general terms removed"),
            mbox("Press releases scanned", f"{n_all:,}", "every release, 2,192 days"),
            mbox("Scam-related releases", f"{len(press_rel):,}", "found by title keywords, checked by hand"),
            mbox("Scam warnings", f"{len(press_core)}", "2025 vs 2020", (f"+{growth:.0f}%", "pillg")),
            mbox("Routine bank notices", f"{n_tpl:,}", "set aside in most comparisons", light=True),
        ])

    # ---------- headline findings ----------
    html('<div class="big-h"><span class="lav">Hong Kong</span> Scam Attention Statistics</div>'
         '<div class="big-sub">A snapshot of what the public searched for and what the government warned '
         'about, with the four answers this study set out to find</div>')
    ck = icon("check", "#B48CF2", 2.4)
    html(f"""<div class="checks">
<div class="check">{ck}<div class="t1">RQ1 · What people searched for</div>
<div class="t2">Investment and crypto scams led fast-rising searches in {word(inv_lead_years)} of six years</div></div>
<div class="check">{ck}<div class="t1">RQ2 · What the government warned about</div>
<div class="t2">{gov_imp_pct:.0f}% of warnings were about scammers posing as officials</div></div>
<div class="check">{ck}<div class="t1">RQ3 · Do they match?</div>
<div class="t2">Hardly: ranked by scam type, the two lists are unrelated (ρ = {signed(rho)})</div></div>
<div class="check">{ck}<div class="t1">RQ4 · Who came first?</div>
<div class="t2">It depends: HKeToll warnings came {hk_lead} months early; {no_press_txt} got none</div></div>
</div>""")

    # ================= searches =================
    with section_card("searches"):
        html(f'<div class="sec-h"><span class="lav">Hong Kong</span> Public Search Attention</div>'
             f'<div class="sec-p">Between 2020 and 2025, Google Trends listed {len(searches):,} scam-related search '
             f'terms for Hong Kong, {n_rising} of them fast-rising. Investment and cryptocurrency scams led in '
             f'{word(inv_lead_years)} of the six years, and in {jp_peak:%B %Y} searches for JPEX reached the highest '
             f'level of the five scams we followed month by month.</div>')
        mgrid([
            mbox("Fast-rising terms", f"{n_rising}"),
            mbox("Investment / crypto share", f"{c.loc['Investment/cryptocurrency', 'Public']:g}%"),
            mbox("Busiest month", f"{jp_peak:%b %Y}", "JPEX scam, interest = 100"),
        ])
        with box("lines"):
            legend([(TERM_EN[t], TERM_COLORS[TERM_EN[t]], None) for t in TERM_EN])
            tr = trends.copy()
            tr["Scam"] = tr["term"].map(TERM_EN)
            fig = px.line(tr, x="date", y="interest", color="Scam", color_discrete_map=TERM_COLORS,
                          category_orders={"Scam": list(TERM_EN.values())}, labels={"date": "", "interest": ""},
                          line_shape="spline")
            fig.update_traces(line_width=2.4)
            fig.update_layout(height=330, showlegend=False, hovermode="x unified",
                              yaxis=dict(side="right", gridcolor="#ECECEF"),
                              xaxis=dict(showline=True, linecolor="#D9DADF", ticks="", **YEAR_TICKS))
            show_chart(fig)
            src("Google Trends, Hong Kong. Monthly interest, 0–100; 100 = the busiest month of any of the five terms")

        left, right = st.columns([1, 1], gap="medium")
        with left:
            with box("spark"):
                box_head("Five scams, month by month", "Search interest 2020–2025 and its peak")
                rows = ""
                for t in TERM_EN:
                    name = TERM_EN[t]
                    g = trends[trends["term"] == t].sort_values("date")
                    col = TERM_COLORS[name]
                    peak = g.loc[g["interest"].idxmax()]
                    rows += (f'<tr><td class="nm">{name}<small>{t.replace(" ", "")}</small></td>'
                             f'<td class="sv">{sparkline(g["interest"], col, rgba(col, 0.25))}</td>'
                             f'<td class="vv">{int(peak["interest"])}<small>peak {peak["date"]:%b %Y}</small></td></tr>')
                html(f'<table class="spark">{rows}</table>')
        with right:
            with box("types"):
                box_head("Fast-rising searches by scam type", "Share of all fast-rising terms, 2020–2025")
                top = comp.sort_values("Public", ascending=False).head(7)
                n_by = rising["category_en"].value_counts()
                trs = "".join(f'<tr><td class="lnk">{short(r["Scam type"])}</td>'
                              f'<td class="num grey">{r["Public"]:.1f}%</td>'
                              f'<td class="num">{int(n_by.get(r["Scam type"], 0))}</td></tr>'
                              for _, r in top.iterrows())
                html(f'<div class="tblwrap"><table class="tbl"><tr><th>Scam type</th><th class="num">Share</th>'
                     f'<th class="num">Terms</th></tr>{trs}</table></div>')

    # ================= types by year =================
    with section_card("years"):
        html('<div class="sec-h"><span class="lav">Hong Kong</span> Scam Searches by Type and Year</div>'
             '<div class="sec-p">Which kinds of scams appeared in Google’s “rising” lists each year, and the '
             'biggest single risers. Fake insurer messages appeared only from 2024; scam-compound searches '
             'rose in 2022 and again in 2025.</div>')
        left, right = st.columns([1.2, 1], gap="medium")
        with left:
            with box("heat"):
                box_head("Fast-rising terms by type and year", "Number of distinct terms")
                rows = [r for r in CAT_ORDER if r != "Non-specific"]
                heat = counts.reindex(index=rows, fill_value=0)
                heat.index = [short(r) for r in heat.index]
                fig = px.imshow(heat, text_auto=True, aspect="auto",
                                color_continuous_scale=[[0, "#FFFFFF"], [0.08, "#F8DCD3"], [0.45, "#E36B5A"],
                                                        [1, "#9E1622"]],
                                labels=dict(x="", y="", color="Terms"))
                fig.update_xaxes(side="top", type="category", showline=False, ticks="")
                fig.update_yaxes(showline=False, ticks="")
                fig.update_traces(xgap=2, ygap=2, hovertemplate="%{y}, %{x}: %{z} terms<extra></extra>")
                fig.update_layout(height=520, coloraxis_showscale=False)
                show_chart(fig)
                src("Google Trends, Hong Kong. Counts are small; read single-year changes with care")
        with right:
            with box("risers"):
                box_head("Biggest risers each year", "Top three per year. All grew by more than 5,000%.")
                cat_of = rising.drop_duplicates("query_clean").set_index("query_clean")["category_en"]
                trs = ""
                for y, items in RISERS.items():
                    for i, (zh, en) in enumerate(items):
                        trs += (f'<tr><td>{"<b>" + str(y) + "</b>" if i == 0 else ""}</td>'
                                f'<td class="term"><span class="lnk">{zh}</span><small>{en}</small></td>'
                                f'<td><span class="badge pur">{short(cat_of.get(zh, "Other"))}</span></td></tr>')
                html(f'<div class="tblwrap"><table class="tbl compact"><tr><th>Year</th><th>Search term</th>'
                     f'<th>Scam type</th></tr>{trs}</table></div>')

    # ================= government =================
    mo = monthly.copy()
    mo["date"] = pd.to_datetime(dict(year=mo["year"], month=mo["month"], day=1))
    mo["Routine bank notices"] = mo["n_scam_releases"] - mo["n_scam_nontemplate"]
    busiest = mo.loc[mo["n_scam_nontemplate"].idxmax()]
    warn_share = len(press_core) / len(press_rel) * 100
    with section_card("warnings"):
        html(f'<div class="sec-h"><span class="lav">Hong Kong</span> Government Warnings</div>'
             f'<div class="sec-p">We read all {n_all:,} government press releases from 2020 to 2025 and found '
             f'{len(press_rel):,} about scams. {n_tpl:,} of them were near-identical HKMA notices about fake bank '
             f'websites, a reporting routine rather than a choice of what to warn about, so we set them aside. '
             f'The remaining {len(press_core)} warnings rose from {per_year[2020]} in 2020 to {per_year[2025]} '
             f'in 2025, and {gov_imp_pct:.0f}% of them were about scammers posing as officials.</div>')
        html(f'<div class="share"><div class="legend">'
             f'<span><span class="dot" style="background:{GOV}"></span>Scam warnings '
             f'<span style="color:{GOV_TXT};font-weight:500">{warn_share:.1f}%</span></span>'
             f'<span><span class="dot" style="background:{GREY}"></span>Routine bank notices '
             f'<span style="color:#6B6C74;font-weight:500">{100 - warn_share:.1f}%</span></span></div>'
             f'<div class="bar"><i style="width:{warn_share:.1f}%;background:{GOV}"></i>'
             f'<i style="width:{100 - warn_share:.1f}%;background:{GREY}"></i></div></div>')
        mgrid([
            mbox("Scam warnings", f"{len(press_core)}", "2025 vs 2020", (f"+{growth:.0f}%", "pillg")),
            mbox("Share of all releases", f"{pct25:.2f}%", f"2025; it was {pct20:.2f}% in 2020",
                 (f"+{pct25 - pct20:.2f} pts", "pillg")),
            mbox("Busiest month", f"{busiest['date']:%b %Y}", f"{int(busiest['n_scam_nontemplate'])} warnings"),
        ])
        with box("monthly"):
            legend([("Scam warnings", GOV, None), ("Routine bank notices", GREY, None)])
            fig = go.Figure()
            fig.add_bar(x=mo["date"], y=mo["n_scam_nontemplate"], name="Scam warnings", marker_color=GOV,
                        hovertemplate="%{x|%b %Y}: %{y} warnings<extra></extra>")
            fig.add_bar(x=mo["date"], y=mo["Routine bank notices"], name="Routine bank notices", marker_color=GREY,
                        hovertemplate="%{x|%b %Y}: %{y} bank notices<extra></extra>")
            fig.update_layout(barmode="stack", height=290, showlegend=False, bargap=0.18,
                              yaxis=dict(side="right", gridcolor="#ECECEF"),
                              xaxis=dict(showline=True, linecolor="#D9DADF", ticks="", **YEAR_TICKS))
            fig.update_traces(marker_line_width=0)
            show_chart(fig)
            src("HKSAR Government press releases (info.gov.hk), monthly")

        left, right = st.columns([1, 1], gap="medium")
        with left:
            with box("yearly"):
                box_head("Scam warnings per year", "Routine bank notices excluded")
                top = per_year.max()
                bars = "".join(
                    f'<div class="hb"><i style="width:{v / top * 72:.0f}%;background:{GOV_LIGHT}"></i>'
                    f'<div class="lab">{y}<b>{v}</b></div></div>' for y, v in per_year.items())
                html(f'<div class="hbars">{bars}</div>')
        with right:
            with box("donut"):
                box_head("Warnings by scam type", "Share of the scam warnings, 2020–2025")
                share = press_core["category_en"].value_counts()
                top4 = share.head(4)
                labels = [short(x) for x in top4.index] + ["Other types"]
                values = list(top4.values) + [int(share.iloc[4:].sum())]
                cols = [GOV, "#B892F5", "#7C93F2", "#F2C14E", "#D3D4D9"]
                a, b = st.columns([1, 1.3])
                with a:
                    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.64, sort=False, direction="clockwise",
                                           marker=dict(colors=cols, line=dict(color="white", width=2)),
                                           textinfo="none",
                                           hovertemplate="%{label}: %{value} (%{percent})<extra></extra>"))
                    fig.update_layout(height=200, showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
                    show_chart(fig)
                with b:
                    tot = sum(values)
                    html('<ul class="dl">' + "".join(
                        f'<li><span class="d" style="background:{col}"></span>{lab} '
                        f'<b style="color:{GOV_TXT if i == 0 else "#4A4B52"}">{v / tot * 100:.1f}%</b></li>'
                        for i, (lab, v, col) in enumerate(zip(labels, values, cols))) + "</ul>")

    # ================= comparison =================
    with section_card("compare"):
        html('<div class="sec-h"><span class="lav">Hong Kong</span> Searches vs. Warnings</div>'
             f'<div class="sec-p">Both sources sorted into the same scam types. Investment scams were '
             f'{c.loc["Investment/cryptocurrency", "Public"]:g}% of fast-rising searches but none of the warnings; '
             f'impersonation of officials was {c.loc["Government/law enforcement impersonation", "Government"]:g}% '
             f'of warnings but only {c.loc["Government/law enforcement impersonation", "Public"]:g}% of searches.</div>')
        include_tpl = st.toggle("Include the routine bank notices", value=False)
        comp_v, rho_v = compare_shares(press_rel if include_tpl else press_core)
        comp_v["gap"] = comp_v["Public"] - comp_v["Government"]
        comp_v = comp_v.sort_values("gap", ascending=False)
        comp_v["label"] = comp_v["Scam type"].map(short)
        both = len(set(comp_v.nlargest(5, "Public")["Scam type"]) & set(comp_v.nlargest(5, "Government")["Scam type"]))
        big_gap = comp_v.iloc[-1]
        html(f'<div class="ranks">'
             f'<div class="rk"><div class="l1">Rank correlation:</div><div class="l2">Spearman’s ρ</div>'
             f'<div class="big">{signed(rho_v)}</div></div>'
             f'<div class="rk"><div class="l1">Shared top-5 types:</div><div class="l2">Searches and warnings</div>'
             f'<div class="big">{both} of 5</div></div>'
             f'<div class="rk"><div class="l1">Largest gap:</div><div class="l2">{big_gap["label"]}</div>'
             f'<div class="big">{abs(big_gap["gap"]):.1f} pts</div></div></div>')
        left, right = st.columns([1.35, 1], gap="medium")
        with left:
            with box("bars"):
                legend([("Fast-rising searches", SEARCH, None), ("Government warnings", GOV, None)])
                fig = go.Figure()
                fig.add_bar(y=comp_v["label"], x=comp_v["Public"], orientation="h", name="Searches",
                            marker_color=SEARCH, text=comp_v["Public"].map(lambda v: f"{v:.0f}%"),
                            textposition="outside", cliponaxis=False,
                            hovertemplate="%{y}<br>Searches: %{x:.1f}%<extra></extra>")
                fig.add_bar(y=comp_v["label"], x=comp_v["Government"], orientation="h", name="Warnings",
                            marker_color=GOV, text=comp_v["Government"].map(lambda v: f"{v:.0f}%"),
                            textposition="outside", cliponaxis=False,
                            hovertemplate="%{y}<br>Warnings: %{x:.1f}%<extra></extra>")
                fig.update_traces(textfont=dict(size=11, color="#6B6C74"), marker_line_width=0)
                fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.1, height=600, showlegend=False,
                                  xaxis=dict(ticksuffix="%", showgrid=True, gridcolor="#ECECEF", rangemode="tozero"),
                                  yaxis=dict(showgrid=False, autorange="reversed"))
                show_chart(fig)
                src(f"Google Trends; info.gov.hk. ‘Non-specific’ and ‘Other’ not shown")
        with right:
            with box("gaps"):
                box_head("Scam type comparison", "Share of each source, percentage points")
                trs = "".join(
                    f'<tr><td class="lnk">{r["label"]}</td><td class="num pur">{r["Public"]:.1f}%</td>'
                    f'<td class="num grn">{r["Government"]:.1f}%</td>'
                    f'<td class="num"><span class="badge {"pur" if r["gap"] > 0 else "grn"}">'
                    f'{"+" if r["gap"] > 0 else "−"}{abs(r["gap"]):.1f}</span></td></tr>'
                    for _, r in comp_v.iterrows())
                html(f'<div class="tblwrap"><table class="tbl compact"><tr><th>Scam type</th><th class="num">Searches</th>'
                     f'<th class="num">Warnings</th><th class="num">Gap</th></tr>{trs}</table></div>')
                html('<div class="box-s">Purple gap: the public paid more attention. Green: the government did.</div>')

    # ================= timing =================
    rows_t = []
    for name in ["HKeToll", "WhatsApp", "JPEX", "WeChat insurance", "Carousell"]:
        t = TERM_BY_EN[name]
        g = trends[trends["term"] == t].sort_values("date")
        mp = matched_press(t)
        rows_t.append(dict(name=name, first=g.loc[g["interest"] > 0, "date"].min(),
                           peak=g.loc[g["interest"].idxmax(), "date"],
                           press=mp["date"].min() if len(mp) else None, n=len(mp), persist=persistence(t)))
    with section_card("timing"):
        html('<div class="sec-h"><span class="lav">Hong Kong</span> Who Came First?</div>'
             f'<div class="sec-p">For five scams we compared when searches began and peaked with the date of the '
             f'first government press release naming them. The government warned about fake HKeToll texts in '
             f'{hk["date"].min():%B %Y}, {hk_lead} months before searches peaked; {no_press_txt} never appeared '
             f'in a press release title.</div>')
        with box("timeline"):
            legend([("First searches", SEARCH, None), ("Search peak", SEARCH_DARK, None),
                    ("First press release", GOV_TXT, None)])
            fig = go.Figure()
            for r in rows_t:
                pts = [r["first"], r["peak"]] + ([r["press"]] if r["press"] is not None else [])
                fig.add_scatter(x=[min(pts), max(pts)], y=[r["name"]] * 2, mode="lines", hoverinfo="skip",
                                line=dict(color="#E3E4E8", width=3), showlegend=False)
                fig.add_scatter(x=[r["first"]], y=[r["name"]], mode="markers", showlegend=False,
                                marker=dict(symbol="circle", size=12, color="white", line=dict(color=SEARCH, width=2.5)),
                                hovertemplate=f"{r['name']}: first searches %{{x|%b %Y}}<extra></extra>")
                fig.add_scatter(x=[r["peak"]], y=[r["name"]], mode="markers", showlegend=False,
                                marker=dict(symbol="circle", size=13, color=SEARCH_DARK),
                                hovertemplate=f"{r['name']}: search peak %{{x|%b %Y}}<extra></extra>")
                if r["press"] is not None:
                    fig.add_scatter(x=[r["press"]], y=[r["name"]], mode="markers", showlegend=False,
                                    marker=dict(symbol="diamond", size=14, color=GOV_TXT),
                                    hovertemplate=f"{r['name']}: first press release %{{x|%b %Y}}<extra></extra>")
                else:
                    fig.add_annotation(x=max(pts), y=r["name"], text="  no press release", showarrow=False,
                                       xanchor="left", font=dict(size=12, color="#8B8C94"))
            fig.update_layout(height=280, xaxis=dict(range=["2019-12-01", "2026-03-01"], showgrid=True,
                                                     gridcolor="#ECECEF", **YEAR_TICKS),
                              yaxis=dict(showgrid=False, autorange="reversed"))
            show_chart(fig)
            src("Google Trends; info.gov.hk. Press releases matched to a scam by name in the title")

        trs = ""
        for r in rows_t:
            if r["press"] is None:
                lead_txt, lead_cls = "No press release", "grey"
            else:
                d = months_between(r["press"], r["peak"])
                lead_txt, lead_cls = ((f"Warning {d} mo before peak", "grn") if d > 0
                                      else (f"Searches {-d} mo ahead", "pur"))
            pat, pcls = ("Sustained", "pur") if r["persist"] >= 50 else ("Short-lived", "grey")
            press_txt = f'{r["press"]:%b %Y}' if r["press"] is not None else "—"
            trs += (f'<tr><td class="lnk">{r["name"]}</td><td class="grey">{r["first"]:%b %Y}</td>'
                    f'<td class="pur">{r["peak"]:%b %Y}</td><td class="grn">{press_txt}</td>'
                    f'<td class="num">{r["n"]}</td><td><span class="badge {lead_cls}">{lead_txt}</span></td>'
                    f'<td><span class="badge {pcls}">{pat}</span> <span class="grey">{r["persist"]:.0f}%</span></td></tr>')
        html('<div class="tblwrap"><table class="tbl"><tr><th>Scam</th><th>First searches</th><th>Search peak</th>'
             '<th>First press release</th><th class="num">Releases</th><th>Who came first</th>'
             f'<th>Search pattern</th></tr>{trs}</table></div>'
             '<div class="box-s">Search pattern: share of months with measurable interest after the first '
             'appearance; 50% or more counts as sustained.</div>')

        with box("detail"):
            names = {TERM_EN[t]: t for t in TERM_EN}
            a, b = st.columns([2, 1])
            with a:
                box_head("One scam in detail", "Monthly search interest and every matching press release (◆)")
            with b:
                pick = st.selectbox("Scam", list(names), index=list(names).index("HKeToll"),
                                    label_visibility="collapsed")
            term = names[pick]
            t_df = trends[trends["term"] == term].sort_values("date")
            matched = matched_press(term)
            col = TERM_COLORS[pick]
            fig = go.Figure()
            fig.add_scatter(x=t_df["date"], y=t_df["interest"], mode="lines", fill="tozeroy", line_shape="spline",
                            line=dict(color=col, width=2.2), fillcolor=rgba(col, 0.22),
                            hovertemplate="%{x|%b %Y}: %{y}<extra></extra>", showlegend=False)
            if len(matched):
                fig.add_scatter(x=matched["date"], y=[-7] * len(matched), mode="markers", showlegend=False,
                                marker=dict(symbol="diamond", size=10, color=GOV_TXT), text=matched["title"],
                                hovertemplate="%{x|%d %b %Y}<br>%{text}<extra></extra>")
            fig.update_layout(height=290, yaxis=dict(range=[-14, 105], side="right", gridcolor="#ECECEF"),
                              xaxis=YEAR_TICKS)
            show_chart(fig)
            if len(matched):
                src(f"Google Trends; info.gov.hk. {len(matched)} matching press releases; hover over ◆ for the title")
            else:
                src("Google Trends. No press release names this scam; warnings may have gone out through the "
                    "SFC or police social media")

    # ================= limits =================
    with section_card("limits"):
        html('<div class="sec-h"><span class="lav">Hong Kong</span> What the Numbers Can’t Tell Us</div>'
             '<div class="sec-p">Search data show what people were curious or worried about, not how many were '
             'cheated, and Google Trends reports relative interest, not counts. On the government side we read only '
             'the official press release website; the Securities and Futures Commission, the police and the '
             'Anti-Deception Coordination Centre publish many warnings elsewhere. A scam missing from press '
             'releases is not necessarily one the government ignored.</div>'
             '<div class="btns"><a class="btn" href="./methodology" target="_self">Read the methodology →</a>'
             '<a class="btn" href="./explore" target="_self">Explore the data →</a>'
             '<span class="btn-note">Every search term and press release, searchable.</span></div>')
    footer()

    # sticky section bar
    links = [("top", "grid", "Overview"), ("searches", "chart", "Searches"), ("years", "search", "By year"),
             ("warnings", "bell", "Warnings"), ("compare", "scale", "Comparison"), ("timing", "clock", "Timing"),
             ("limits", "info", "Limits")]
    html('<div class="secbar"><div class="in">' + "".join(
        f'<a href="#{a}" target="_self">{icon(i)}<span>{lab}</span></a>' for a, i, lab in links) + "</div></div>")


# ===========================================================================
# 4. OTHER PAGES
# ===========================================================================
def page_explorer():
    masthead("Explore the data")
    st.markdown('<div class="hed">Explore the data</div>'
                '<div class="dek">Search every term and press release behind the story. Terms and titles are '
                'in their original language; type Chinese or English, e.g. 易通行, WhatsApp, 銀行.</div>',
                unsafe_allow_html=True)
    tab_search, tab_press = st.tabs(["Google searches", "Government press releases"])

    with tab_search:
        f1, f2 = st.columns(2)
        yr = f1.slider("Years", 2020, 2025, (2020, 2025), key="s_years")
        cats = f2.multiselect("Scam types", CAT_ORDER, key="s_cats", placeholder="All scam types")
        keyword = st.text_input("Keyword", key="s_kw", placeholder="e.g. 易通行 or whatsapp")
        o1, o2 = st.columns(2)
        only_rising = o1.toggle("Fast-rising terms only", value=False)
        show_generic = o2.toggle("Include general terms (e.g. ‘scam meaning’)", value=False)

        df = searches[searches["year"].between(*yr)]
        if cats:
            df = df[df["category_en"].isin(cats)]
        if only_rising:
            df = df[df["type"] == "rising"]
        if not show_generic:
            df = df[~df["is_generic"]]
        if keyword:
            kw = keyword.strip().lower()
            no_space = df["query"].str.replace(" ", "", regex=False).str.lower()   # "易 通行" -> "易通行"
            df = df[no_space.str.contains(kw.replace(" ", ""), regex=False)
                    | df["query_clean"].str.lower().str.contains(kw, regex=False)
                    | df["entity"].str.lower().str.contains(kw, regex=False)]

        st.caption(f"{len(df):,} results")
        st.dataframe(
            df.sort_values(["year", "type", "value"], ascending=[True, True, False])[
                ["year", "type", "query_clean", "value", "category_en", "keyword"]],
            hide_index=True, width="stretch",
            column_config={
                "year": st.column_config.NumberColumn("Year", format="%d"),
                "type": st.column_config.TextColumn("List", help="top = most searched; rising = fastest growing"),
                "query_clean": st.column_config.TextColumn("Search term"),
                "value": st.column_config.NumberColumn(
                    "Value", help="top: relative popularity (0–100); rising: % growth on the previous year"),
                "category_en": st.column_config.TextColumn("Scam type"),
                "keyword": st.column_config.TextColumn("Seed keyword"),
            },
        )
        st.caption("Values are relative indices from Google Trends, not search counts, and cannot be "
                   "compared across seed keywords.")

    with tab_press:
        g1, g2 = st.columns(2)
        pyr = g1.slider("Years", 2020, 2025, (2020, 2025), key="p_years")
        pcats = g2.multiselect("Scam types", CAT_ORDER, key="p_cats", placeholder="All scam types")
        pkw = st.text_input("Keyword in title", key="p_kw", placeholder="e.g. 易通行 or 銀行")
        show_template = st.toggle(f"Include routine bank notices ({int(press_rel['is_template'].sum()):,})",
                                  value=False)
        pdf = press_rel if show_template else press_core
        pdf = pdf[pdf["year"].between(*pyr)].copy()
        pdf["release_type_en"] = pdf["release_type"].map(TYPE_EN).fillna(pdf["release_type"])
        if pcats:
            pdf = pdf[pdf["category_en"].isin(pcats)]
        if pkw:
            k = pkw.strip().lower()
            pdf = pdf[pdf["title"].str.lower().str.contains(k, regex=False)
                      | pdf["entity"].str.lower().str.contains(k, regex=False)]
        st.caption(f"{len(pdf):,} press releases")
        st.dataframe(
            pdf.sort_values("date", ascending=False)[["date", "url", "title", "category_en", "release_type_en"]],
            hide_index=True, width="stretch",
            column_config={
                "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "url": st.column_config.LinkColumn("Link", display_text="Open ↗", width="small"),
                "title": st.column_config.TextColumn("Title", width="medium"),
                "category_en": st.column_config.TextColumn("Scam type"),
                "release_type_en": st.column_config.TextColumn("Type"),
            },
        )
    footer()


def page_guide():
    masthead("How to spot a scam")
    st.markdown('<div class="hed">How to spot a scam</div>'
                '<div class="dek">What each type of scam in this study looks like, and what to do about it, '
                'summarised from official Hong Kong anti-scam information.</div>', unsafe_allow_html=True)
    st.markdown('<div class="note"><b>Suspect a scam?</b> Call the Anti-Deception Coordination Centre’s '
                'Anti-Scam Helpline <b>18222</b>, or check a phone number, website or account with '
                '<b>Scameter</b> before you pay. In an emergency, call <b>999</b>.</div>',
                unsafe_allow_html=True)

    for _, row in codebook[~codebook["category_en"].isin(["Non-specific", "Other"])].iterrows():
        cat = row["category_en"]
        with st.expander(cat):
            st.markdown(f"{row['definition_en']} {row['how_it_works_en']}")
            if row["warning_signs_en"]:
                st.markdown("**Warning signs**\n" + "\n".join(f"- {s}" for s in row["warning_signs_en"].split(";")))
            if row["advice_en"]:
                st.markdown("**What to do**\n" + "\n".join(f"- {s}" for s in row["advice_en"].split(";")))
            examples = (rising[rising["category_en"] == cat]
                        .sort_values("value", ascending=False)["query_clean"].unique()[:6])
            if len(examples):
                st.caption("Searched for in Hong Kong: " + "、".join(examples))
            links = [u.strip() for u in row["source"].split(";") if u.strip()]
            if links:
                st.caption("Sources: " + " · ".join(f"[{u}]({u})" for u in links))
    footer()


def page_methods():
    masthead("Methodology")
    st.markdown('<div class="hed">Methodology</div>', unsafe_allow_html=True)
    st.markdown("### Google searches")
    st.markdown(
        "We used the Python library *pytrends* to collect Google Trends’ related queries for four seed "
        "keywords (詐騙, 騙案, 騙局 and *scam*), region Hong Kong, one request per calendar year from 2020 to "
        "2025. Each request returns up to 25 *top* (most searched) and 25 *rising* (fastest growing) terms. "
        "We standardised the text (lower case, traditional Chinese, no spaces between Chinese characters), "
        f"merged spellings such as 易通行 and hketoll, removed 22 rows of sanctions-screening template strings "
        f"(641 → {len(searches)} rows), and marked general terms, films and games as non-specific. Monthly "
        "interest for five representative scams was collected in a single request, so the five share one "
        "0–100 scale."
    )
    st.markdown("### Government press releases")
    st.markdown(
        "We scraped the daily Chinese index pages of the HKSAR Government press release website "
        f"(info.gov.hk) for all 2,192 days from 2020 to 2025, {int(monthly['n_all_releases'].sum()):,} "
        "releases in total, with 1.5–3 seconds between requests and in line with the site’s robots.txt. "
        f"Releases whose titles contained scam-related keywords ({len(press):,}) were downloaded in full and "
        f"checked by hand; {len(press_rel):,} were about scams. {int(press_rel['is_template'].sum()):,} of these "
        "are routine HKMA notices about fake bank websites or emails and are excluded from most comparisons."
    )
    st.markdown("### Classification")
    st.markdown(
        "Search terms and press releases were sorted into the same 15 scam types using a shared codebook, "
        "with keyword rules followed by manual review. In the HKeToll and WhatsApp comparison, press releases "
        "were matched to a scam by keywords in their titles. A scam counts as *sustained* if, after its first "
        "month with measurable search interest, at least half of the following months still show interest."
    )
    st.markdown("### Limitations")
    st.markdown(
        "- Google Trends values are relative indices from a sample of searches, not counts, and values from "
        "different requests cannot be compared directly.\n"
        "- Searches show public attention, not the number of victims.\n"
        "- Press releases were selected by title keywords, so releases that mention scams only in the body are missed.\n"
        "- Warnings issued outside the press release website (Securities and Futures Commission, police social "
        "media, Anti-Deception Coordination Centre) are not included.\n"
        "- Yearly counts are small."
    )
    st.markdown("### Data")
    d1, d2 = st.columns(2)
    d1.download_button("Search terms (CSV)", searches.to_csv(index=False).encode("utf-8-sig"),
                       "classified_data.csv", "text/csv", width="stretch")
    d2.download_button("Monthly search interest (CSV)", trends.to_csv(index=False).encode("utf-8-sig"),
                       "interest_over_time.csv", "text/csv", width="stretch")
    d1.download_button("Press releases (CSV)", press.to_csv(index=False).encode("utf-8-sig"),
                       "press_scam.csv", "text/csv", width="stretch")
    d2.download_button("Codebook (CSV)", codebook.to_csv(index=False).encode("utf-8-sig"),
                       "codebook_en.csv", "text/csv", width="stretch")
    footer()


# ===========================================================================
# 5. NAVIGATION (plain text links at the top)
# ===========================================================================
P_STORY = st.Page(page_story, title="The story", default=True)
P_EXPLORER = st.Page(page_explorer, title="Explore the data", url_path="explore")
P_GUIDE = st.Page(page_guide, title="How to spot a scam", url_path="guide")
P_METHODS = st.Page(page_methods, title="Methodology", url_path="methodology")

st.navigation([P_STORY, P_EXPLORER, P_GUIDE, P_METHODS], position="hidden").run()
