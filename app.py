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

st.set_page_config(page_title="Hong Kong Scam Watch", page_icon="🔍", layout="centered")

DATA = Path(__file__).parent / "data"
YEARS = list(range(2020, 2026))

# ---- Edit these two lines ----
AUTHORS = "New Media and Communication 5507"
PUBLISHED = "November 2026"


# ===========================================================================
# 1. STYLE
# ===========================================================================
BLUE = "#1F5A96"      # public searches
ORANGE = "#E5652E"    # government warnings
GREY = "#C4BDB2"      # everything we are not pointing at
PAPER = "#F7F3EC"     # page background (same as .streamlit/config.toml)
INK = "#14181F"       # masthead
SOURCE_NOTE = "Source: Google Trends (region: Hong Kong); HKSAR Government press releases (info.gov.hk)"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800&family=Inter:wght@400;500;600&family=Noto+Sans+TC:wght@400;500;700&display=swap');

/* one modern sans everywhere */
[data-testid="stMarkdownContainer"], label, button, input, textarea, [data-testid="stDataFrame"],
[data-testid="stWidgetLabel"], [data-testid="stCaptionContainer"], [data-testid="stTab"],
[data-testid="stExpander"] summary {
    font-family: 'Inter', 'Noto Sans TC', -apple-system, 'PingFang HK', sans-serif !important;
}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {
    font-size: 1.06rem; line-height: 1.75; color: #1A1A1A;
}
h1, h2, h3 {
    font-family: 'Archivo', 'Noto Sans TC', sans-serif !important;
    font-weight: 800 !important; color: #111111; letter-spacing: -0.01em;
}
h3 { font-size: 1.6rem !important; margin-top: 2.6rem !important; }

.block-container { max-width: 940px; padding-top: 4.5rem; padding-bottom: 3rem; }

/* headline block */
.kicker { font-family: 'Archivo', sans-serif; font-weight: 700; font-size: 0.82rem; letter-spacing: 0.08em;
          text-transform: uppercase; color: #E5652E; margin-top: 0.4rem; }
.hed {
    font-family: 'Archivo', 'Noto Sans TC', sans-serif; font-weight: 800;
    font-size: 3.2rem; line-height: 1.04; letter-spacing: -0.02em; color: #111111; margin: 0.4rem 0 1rem 0;
}
.dek { font-size: 1.25rem; line-height: 1.55; color: #444444; margin-bottom: 1.1rem; }
.byline {
    font-size: 0.86rem; color: #666666;
    border-top: 1px solid #DDDDDD; border-bottom: 1px solid #DDDDDD;
    padding: 0.55rem 0; margin-bottom: 1.6rem;
}
.byline b { color: #111111; font-weight: 600; }

/* the numbers strip under the headline */
.nums { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0 1.6rem; margin: 0.4rem 0 2.2rem 0; }
.num { border-top: 3px solid #111111; padding-top: 0.6rem; }
.num .big { font-family: 'Archivo', sans-serif; font-weight: 800; font-size: 2.3rem; line-height: 1.05;
            letter-spacing: -0.02em; }
.num .lbl { font-size: 0.86rem; line-height: 1.4; color: #555555; margin-top: 0.35rem; }
@media (max-width: 700px) { .nums { grid-template-columns: repeat(2, 1fr); gap: 1.2rem 1.2rem; } }

/* four findings */
.findings { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.3rem 2rem; margin: 0.6rem 0 1.2rem 0; }
.finding .rq { font-family: 'Archivo', sans-serif; font-weight: 700; font-size: 0.78rem; letter-spacing: 0.06em;
               text-transform: uppercase; color: #888888; }
.finding .h { font-family: 'Archivo', sans-serif; font-weight: 700; font-size: 1.12rem; line-height: 1.3;
              margin: 0.2rem 0 0.3rem 0; color: #111111; }
.finding .t { font-size: 0.95rem; line-height: 1.6; color: #333333; }
@media (max-width: 700px) { .findings { grid-template-columns: 1fr; } }

/* biggest risers each year */
.risers { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem 1.8rem; margin: 0.6rem 0 0.8rem 0; }
.yr { border-top: 1px solid #111111; padding-top: 0.45rem; }
.yr .y { font-family: 'Archivo', sans-serif; font-weight: 800; font-size: 1.35rem; }
.yr ol { margin: 0.3rem 0 0 1.1rem; padding: 0; }
.yr li { font-size: 0.92rem !important; line-height: 1.45 !important; margin-bottom: 0.35rem; }
.yr .zh { font-weight: 600; color: #111111; }
.yr .en { color: #666666; font-size: 0.84rem; display: block; }
@media (max-width: 700px) { .risers { grid-template-columns: repeat(2, 1fr); } }

/* chart header and source line */
.chart-title { font-family: 'Archivo', 'Noto Sans TC', sans-serif; font-weight: 700; font-size: 1.12rem;
               color: #111111; margin-top: 1.6rem; }
.chart-sub { font-size: 0.9rem; color: #555555; margin-bottom: 0.2rem; }
.source { font-size: 0.76rem; color: #888888;
          border-top: 1px solid #E5E5E5; padding-top: 0.35rem; margin: -0.4rem 0 1.4rem 0; }
.key { display: inline-block; width: 11px; height: 11px; border-radius: 2px; margin: 0 4px 0 2px; vertical-align: -1px; }

/* notes */
.note { font-size: 0.95rem; line-height: 1.6;
        border-left: 3px solid #111111; padding: 0.3rem 0 0.3rem 0.9rem; margin: 0.8rem 0 1.4rem 0; color: #222222; }
.footer { border-top: 1px solid #DDDDDD; margin-top: 3rem;
          padding-top: 0.8rem; font-size: 0.8rem; color: #777777; line-height: 1.6; }

/* page background and Streamlit's own top bar */
.stApp { background: #F7F3EC; overflow-x: hidden; }
[data-testid="stHeader"] { display: none; }
.block-container { padding-top: 0 !important; }

/* masthead: full-width dark band with the site name and the page links */
.masthead { background: #14181F; width: 100vw; margin-left: calc(50% - 50vw); margin-bottom: 2.4rem;
            border-bottom: 4px solid #E5652E; }
.masthead .inner { max-width: 940px; margin: 0 auto; padding: 1.25rem 1rem 0 1rem; }
.masthead .brand { display: flex; align-items: baseline; gap: 0.9rem; flex-wrap: wrap; }
.masthead .name { font-family: 'Archivo', sans-serif; font-weight: 800; font-size: 1.7rem;
                  letter-spacing: -0.01em; color: #FFFFFF; }
.masthead .name span { color: #E5652E; }
.masthead .tag { font-family: 'Inter', sans-serif; font-size: 0.82rem; color: #9AA3AF; }
.masthead nav { display: flex; gap: 1.8rem; margin-top: 0.9rem; flex-wrap: wrap; }
.masthead nav a { font-family: 'Archivo', sans-serif; font-weight: 600; font-size: 0.84rem;
                  letter-spacing: 0.07em; text-transform: uppercase; text-decoration: none !important;
                  color: #C9CFD6 !important; padding: 0.5rem 0 0.75rem 0; border-bottom: 3px solid transparent; }
.masthead nav a:hover { color: #FFFFFF !important; }
.masthead nav a.on { color: #FFFFFF !important; border-bottom-color: #FFFFFF; }
@media (max-width: 700px) { .masthead nav { gap: 1.1rem; } .masthead .name { font-size: 1.35rem; } }
</style>
""", unsafe_allow_html=True)

pio.templates["paper"] = go.layout.Template(layout=dict(
    font=dict(family="Inter, 'Noto Sans TC', sans-serif", size=13, color="#333333"),
    paper_bgcolor=PAPER, plot_bgcolor=PAPER,
    xaxis=dict(showgrid=False, linecolor="#999999", ticks="outside", tickcolor="#999999", automargin=True),
    yaxis=dict(gridcolor="#E3DCD0", zeroline=False, showline=False, automargin=True),
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
TERM_COLORS = {"JPEX": ORANGE, "WhatsApp": BLUE, "Carousell": "#7FA7CE",
               "HKeToll": "#3A9E7E", "WeChat insurance": "#9B7BB5"}
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
# 3. THE STORY
# ===========================================================================
def page_story():
    masthead("The story")
    # ---------- numbers used in the text ----------
    jp = trends[trends["term"] == "JPEX 詐騙"]
    jp_peak = jp.loc[jp["interest"].idxmax(), "date"]
    jp_press = len(matched_press("JPEX 詐騙"))
    comp, rho = compare_shares(press_core)
    c = comp.set_index("Scam type")

    counts = pd.crosstab(rising["category_en"], rising["year"]).reindex(columns=YEARS, fill_value=0)
    lead = counts.drop(index=["Other"], errors="ignore").idxmax()           # top scam type each year
    inv = counts.loc["Investment/cryptocurrency"]
    inv_lead_years = int((lead == "Investment/cryptocurrency").sum())
    ins24, tot24 = int(counts.loc["Insurance/financial impersonation", 2024]), int(counts[2024].sum())

    n_tpl = int(press_rel["is_template"].sum())
    gov_imp = int((press_core["category_en"] == "Government/law enforcement impersonation").sum())
    m = monthly.groupby("year")[["n_all_releases", "n_scam_nontemplate"]].sum()
    pct20 = m.loc[2020, "n_scam_nontemplate"] / m.loc[2020, "n_all_releases"] * 100
    pct25 = m.loc[2025, "n_scam_nontemplate"] / m.loc[2025, "n_all_releases"] * 100

    hk = matched_press("易通行 詐騙")
    hk_tr = trends[trends["term"] == "易通行 詐騙"]
    hk_peak = hk_tr.loc[hk_tr["interest"].idxmax(), "date"]
    hk_lead = months_between(hk["date"].min(), hk_peak)
    wa_persist = persistence("WhatsApp 詐騙")

    n_all = int(monthly["n_all_releases"].sum())
    gov_imp_pct = gov_imp / len(press_core) * 100
    no_press = [TERM_EN[t] for t in TERM_EN if len(matched_press(t)) == 0]

    # ---------- headline ----------
    st.markdown(f"""
    <div class="kicker">Hong Kong · Scams · 2020–2025</div>
    <div class="hed">What Hong Kong searches for is not what it is warned about</div>
    <div class="dek">Six years of Google searches and government press releases show the public
    and the government paying attention to different scams.</div>
    <div class="byline">By <b>{AUTHORS}</b> &nbsp;|&nbsp; {PUBLISHED}</div>
    """, unsafe_allow_html=True)

    # ---------- the numbers ----------
    st.markdown(f"""
    <div class="nums">
      <div class="num"><div class="big" style="color:{BLUE}">{len(searches):,}</div>
        <div class="lbl">scam-related search terms from Google Trends, Hong Kong</div></div>
      <div class="num"><div class="big">{n_all:,}</div>
        <div class="lbl">government press releases scanned, one day at a time</div></div>
      <div class="num"><div class="big" style="color:{ORANGE}">{len(press_core):,}</div>
        <div class="lbl">scam warnings left after removing routine bank notices</div></div>
      <div class="num"><div class="big">{signed(rho)}</div>
        <div class="lbl">rank correlation between the two. 0 means no relationship</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"In {jp_peak:%B %Y}, Hong Kong searches for “JPEX 詐騙” (JPEX scam) reached the highest level of "
        f"any of the five scam terms we followed month by month. In the six years from 2020 to 2025, "
        f"{'not one government press release' if jp_press == 0 else f'only {jp_press} government press releases'} "
        f"carried the name JPEX in its title."
    )
    st.markdown(
        f"That gap is not unusual. We compared {len(searches):,} scam-related search terms that Google "
        f"Trends recorded for Hong Kong between 2020 and 2025 with all {int(monthly['n_all_releases'].sum()):,} "
        f"press releases the government issued in the same period. When both are sorted into the same "
        f"scam types, they rank those types in almost unrelated order (Spearman’s ρ = {signed(rho)})."
    )

    chart_header("Searches for five scams, month by month",
                 "Google search interest in Hong Kong. 100 = the busiest month of any of the five terms.")
    tr = trends.copy()
    tr["Scam"] = tr["term"].map(TERM_EN)
    fig = px.line(tr, x="date", y="interest", color="Scam", color_discrete_map=TERM_COLORS,
                  category_orders={"Scam": list(TERM_EN.values())},
                  labels={"date": "", "interest": ""})
    fig.update_traces(line_width=2)
    fig.update_layout(height=380, legend=dict(orientation="h", y=1.1, x=0), hovermode="x unified")
    show_chart(fig)
    source()

    # ---------- four findings ----------
    st.markdown("### Four findings")
    st.markdown(f"""
    <div class="findings">
      <div class="finding"><div class="rq">1 · What people searched for</div>
        <div class="h">Money scams dominate searches</div>
        <div class="t">Investment and crypto scams topped the fast-rising searches in {word(inv_lead_years)} of six
        years. Fake insurer messages took over in 2024; AI and scam-compound searches grew in 2025.</div></div>
      <div class="finding"><div class="rq">2 · What the government warned about</div>
        <div class="h">Warnings focus on fake officials</div>
        <div class="t">{gov_imp_pct:.0f}% of non-routine scam press releases were about scammers posing as
        government departments or officials.</div></div>
      <div class="finding"><div class="rq">3 · Do they match?</div>
        <div class="h">Hardly at all</div>
        <div class="t">Investment scams were {c.loc['Investment/cryptocurrency', 'Public']:g}% of searches but
        0% of press releases. Ranked by scam type, the two lists are unrelated (ρ = {signed(rho)}).</div></div>
      <div class="finding"><div class="rq">4 · Who came first?</div>
        <div class="h">It depends on the scam</div>
        <div class="t">The government warned about HKeToll texts {hk_lead} months before searches peaked.
        For {', '.join(no_press[:-1]) + ' and ' + no_press[-1] if len(no_press) > 1 else ''.join(no_press)},
        no press release appeared at all.</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ---------- what people searched for ----------
    st.markdown("### What people searched for")
    st.markdown(
        "Each year, Google Trends lists the terms whose searches grew fastest alongside 詐騙, 騙案, 騙局 "
        f"and “scam”. We sorted these {rising['query_clean'].nunique()} fast-rising terms by scam type. "
        f"Investment and cryptocurrency scams led the list in {word(inv_lead_years)} of the six years, with "
        f"{word(int(inv.max()))} rising terms at their peak, from fake trading platforms to coins such as "
        "Pi Network and USDT."
    )
    st.markdown(
        f"In 2024 the pattern changed. {word(ins24, capital=True)} of that year’s {tot24} rising terms were about fake messages "
        "in the name of insurers and payment companies, such as 微信保險詐騙 (WeChat insurance scam) and "
        "picc詐騙. Searches about scam compounds in Cambodia and Myanmar rose in 2022 and again in 2025."
    )
    chart_header("Fast-rising scam searches, by type and year",
                 "Number of distinct search terms in Google Trends’ “rising” lists for Hong Kong")
    rows = [r for r in CAT_ORDER if r != "Non-specific"]
    heat = counts.reindex(index=rows, fill_value=0)
    heat.index = [short(r) for r in heat.index]
    fig = px.imshow(heat, text_auto=True, aspect="auto",
                    color_continuous_scale=[[0, PAPER], [0.08, "#F8DCD3"], [0.45, "#E36B5A"], [1, "#9E1622"]],
                    labels=dict(x="", y="", color="Terms"))
    fig.update_xaxes(side="top", type="category", showline=False, ticks="")
    fig.update_yaxes(showline=False, ticks="")
    fig.update_traces(xgap=2, ygap=2, hovertemplate="%{y}, %{x}: %{z} terms<extra></extra>")
    fig.update_layout(height=520, coloraxis_showscale=False)
    show_chart(fig)
    source(". Counts are small; read single-year changes with care.")

    chart_header("The biggest risers each year",
                 "Fastest-growing scam searches in Hong Kong, as listed by Google Trends")
    cells = []
    for y, items in RISERS.items():
        lis = "".join(f'<li><span class="zh">{zh}</span><span class="en">{en}</span></li>' for zh, en in items)
        cells.append(f'<div class="yr"><div class="y">{y}</div><ol>{lis}</ol></div>')
    st.markdown(f'<div class="risers">{"".join(cells)}</div>', unsafe_allow_html=True)
    source(". All of these were ‘breakout’ terms, meaning searches grew by more than 5,000%.")

    # ---------- what the government warned about ----------
    st.markdown("### What the government warned about")
    st.markdown(
        f"Government press releases tell a different story. Of the {len(press_rel):,} scam-related releases "
        f"we found, {n_tpl:,} were near-identical notices from the Hong Kong Monetary Authority, one for "
        "each fake bank website or email it was told about. They show a reporting routine more than a "
        "choice of what to warn about, so we set them aside."
    )
    st.markdown(
        f"Of the remaining {len(press_core)} releases, {gov_imp} ({gov_imp / len(press_core) * 100:.0f}%) warned "
        "about scammers pretending to be government officials or departments: fake websites in the name of "
        "the Water Supplies Department, WhatsApp messages claiming to come from a bureau secretary, phone "
        f"calls said to be from the Department of Health or the Immigration Department. Scam warnings also grew as a share of all releases, from "
        f"{pct20:.2f}% in 2020 to {pct25:.2f}% in 2025."
    )
    focus = {"Government/law enforcement impersonation": ORANGE, "Anti-scam resources": "#F3B897",
             "Logistics/public service impersonation": BLUE}
    by_year = press_core.groupby(["year", "category_en"]).size().reset_index(name="Releases")
    by_year["Type"] = by_year["category_en"].where(by_year["category_en"].isin(focus), "All other types")
    by_year = by_year.groupby(["year", "Type"], as_index=False)["Releases"].sum()
    by_year["year"] = by_year["year"].astype(str)
    chart_header("Government scam warnings by year",
                 f"Press releases, excluding routine bank notices. {key(ORANGE)}Impersonating officials "
                 f"{key('#F3B897')}Anti-scam campaigns and tools {key(BLUE)}Fake courier and toll messages "
                 f"{key(GREY)}All other types")
    fig = px.bar(by_year, x="year", y="Releases", color="Type",
                 color_discrete_map={**focus, "All other types": GREY},
                 category_orders={"Type": list(focus) + ["All other types"], "year": [str(y) for y in YEARS]},
                 labels={"year": "", "Releases": ""})
    fig.update_layout(height=360, showlegend=False, bargap=0.3)
    show_chart(fig)
    source()

    mo = monthly.copy()
    mo["date"] = pd.to_datetime(dict(year=mo["year"], month=mo["month"], day=1))
    mo["Routine bank notices"] = mo["n_scam_releases"] - mo["n_scam_nontemplate"]
    busiest = mo.loc[mo["n_scam_nontemplate"].idxmax()]
    chart_header("Scam press releases, month by month",
                 f"{key(ORANGE)}Scam warnings &nbsp; {key(GREY)}Routine bank notices (set aside)")
    fig = go.Figure()
    fig.add_bar(x=mo["date"], y=mo["n_scam_nontemplate"], name="Scam warnings", marker_color=ORANGE,
                hovertemplate="%{x|%b %Y}: %{y} warnings<extra></extra>")
    fig.add_bar(x=mo["date"], y=mo["Routine bank notices"], name="Routine bank notices", marker_color=GREY,
                hovertemplate="%{x|%b %Y}: %{y} bank notices<extra></extra>")
    fig.update_layout(barmode="stack", height=320, showlegend=False, bargap=0.15)
    show_chart(fig)
    source(f". Busiest month for warnings: {busiest['date']:%B %Y} ({int(busiest['n_scam_nontemplate'])}).")

    # ---------- where they diverge ----------
    st.markdown("### Where the two diverge")
    st.markdown(
        f"Put side by side, the gaps are large. Investment scams made up {c.loc['Investment/cryptocurrency', 'Public']:g}% "
        "of fast-rising searches but none of the press releases. Romance scams "
        f"({c.loc['Romance/social', 'Public']:g}% of searches) and online-shopping scams "
        f"({c.loc['Online shopping/trading', 'Public']:g}%) show a similar gap. In the other direction, "
        f"impersonation of officials took up {c.loc['Government/law enforcement impersonation', 'Government']:g}% "
        f"of press releases but only {c.loc['Government/law enforcement impersonation', 'Public']:g}% of rising searches."
    )
    include_tpl = st.toggle("Include the routine bank notices", value=False)
    comp_v, rho_v = compare_shares(press_rel if include_tpl else press_core)
    comp_v["gap"] = comp_v["Public"] - comp_v["Government"]
    chart_header("Share of attention by scam type",
                 f"{key(BLUE)}Share of fast-rising searches &nbsp; {key(ORANGE)}Share of government press releases")
    comp_v = comp_v.sort_values("gap", ascending=False)
    comp_v["label"] = comp_v["Scam type"].map(short)
    fig = go.Figure()
    fig.add_bar(y=comp_v["label"], x=comp_v["Public"], orientation="h", name="Searches",
                marker_color=BLUE, text=comp_v["Public"].map(lambda v: f"{v:.0f}%"),
                textposition="outside", cliponaxis=False,
                hovertemplate="%{y}<br>Searches: %{x:.1f}%<extra></extra>")
    fig.add_bar(y=comp_v["label"], x=comp_v["Government"], orientation="h", name="Press releases",
                marker_color=ORANGE, text=comp_v["Government"].map(lambda v: f"{v:.0f}%"),
                textposition="outside", cliponaxis=False,
                hovertemplate="%{y}<br>Press releases: %{x:.1f}%<extra></extra>")
    fig.update_traces(textfont=dict(size=11, color="#555555"))
    fig.update_layout(barmode="group", bargap=0.28, bargroupgap=0.08, height=640, showlegend=False,
                      xaxis=dict(ticksuffix="%", showgrid=True, gridcolor="#E3DCD0", rangemode="tozero"),
                      yaxis=dict(showgrid=False, autorange="reversed"))
    show_chart(fig)
    source(f". Spearman’s ρ = {signed(rho_v)}. ‘Non-specific’ and ‘Other’ not shown.")

    # ---------- who came first ----------
    st.markdown("### Sometimes the warnings come first")
    st.markdown(
        f"The two records do not always move in opposite directions. For fake HKeToll toll-payment texts, "
        f"the government was ahead: its first warning came in {hk['date'].min():%B %Y}, followed by "
        f"{len(hk) - 1} more by the end of 2025. Public searches for 易通行詐騙 peaked {hk_lead} months "
        f"after that first warning, in {hk_peak:%B %Y}."
    )
    st.markdown(
        f"WhatsApp scams follow a different pattern. Interest first appeared in 2021 and never fully went away: "
        f"searches showed measurable interest in {wa_persist:.0f}% of the months since. JPEX, by contrast, "
        "flared up for a few months and then disappeared from search."
    )

    chart_header("Who came first?",
                 f"<span style='color:{ORANGE}'>▲</span> First government press release &nbsp; "
                 f"<span style='color:{BLUE}'>●</span> First month with search interest &nbsp; "
                 f"<span style='color:{BLUE}'>◆</span> Search peak")
    fig = go.Figure()
    order = ["HKeToll", "WhatsApp", "JPEX", "WeChat insurance", "Carousell"]
    for name in order:
        t = TERM_BY_EN[name]
        g = trends[trends["term"] == t].sort_values("date")
        first_s = g.loc[g["interest"] > 0, "date"].min()
        peak_s = g.loc[g["interest"].idxmax(), "date"]
        mp = matched_press(t)
        pts = [first_s, peak_s] + ([mp["date"].min()] if len(mp) else [])
        fig.add_scatter(x=[min(pts), max(pts)], y=[name, name], mode="lines", hoverinfo="skip",
                        line=dict(color="#CCCCCC", width=2), showlegend=False)
        fig.add_scatter(x=[first_s], y=[name], mode="markers", showlegend=False,
                        marker=dict(symbol="circle", size=11, color=PAPER, line=dict(color=BLUE, width=2)),
                        hovertemplate=f"{name}: first searches %{{x|%b %Y}}<extra></extra>")
        fig.add_scatter(x=[peak_s], y=[name], mode="markers", showlegend=False,
                        marker=dict(symbol="diamond", size=12, color=BLUE),
                        hovertemplate=f"{name}: search peak %{{x|%b %Y}}<extra></extra>")
        if len(mp):
            fig.add_scatter(x=[mp["date"].min()], y=[name], mode="markers", showlegend=False,
                            marker=dict(symbol="triangle-up", size=13, color=ORANGE),
                            hovertemplate=f"{name}: first press release %{{x|%b %Y}} "
                                          f"({len(mp)} in total)<extra></extra>")
        else:
            fig.add_annotation(x=max(pts), y=name, text="  no press release", showarrow=False,
                               xanchor="left", font=dict(size=12, color="#888888"))
    fig.update_layout(height=300, xaxis=dict(range=["2020-01-01", "2026-03-01"], showgrid=True,
                                             gridcolor="#E3DCD0"),
                      yaxis=dict(showgrid=False, autorange="reversed"))
    show_chart(fig)
    source(". Press releases matched to a scam by name in the title.")
    names = {TERM_EN[t]: t for t in TERM_EN}
    pick = st.selectbox("Choose a scam", list(names), index=list(names).index("HKeToll"))
    term = names[pick]
    t_df = trends[trends["term"] == term].sort_values("date")
    matched = matched_press(term)
    chart_header(f"{pick}: searches and government warnings",
                 f"{key(TERM_COLORS[pick])}Monthly search interest &nbsp; "
                 f"<span style='color:{ORANGE}'>▲</span> Government press release on this scam "
                 f"({len(matched)} in total)")
    fig = go.Figure()
    fig.add_scatter(x=t_df["date"], y=t_df["interest"], mode="lines", line=dict(color=TERM_COLORS[pick], width=2.2),
                    hovertemplate="%{x|%b %Y}: %{y}<extra></extra>", showlegend=False)
    if len(matched):
        fig.add_scatter(x=matched["date"], y=[-6] * len(matched), mode="markers", showlegend=False,
                        marker=dict(symbol="triangle-up", size=10, color=ORANGE), text=matched["title"],
                        hovertemplate="%{x|%d %b %Y}<br>%{text}<extra></extra>")
    fig.update_layout(height=340, yaxis=dict(range=[-12, 105]))
    show_chart(fig)
    source()
    if not len(matched):
        st.markdown('<div class="note">No government press release with this scam in its title was found. '
                    'Warnings may have gone out through other channels, such as the Securities and Futures '
                    'Commission or police social media, which this study does not cover.</div>',
                    unsafe_allow_html=True)

    # ---------- limits ----------
    st.markdown("### What the numbers can and cannot tell us")
    st.markdown(
        "Search data show what people were curious or worried about, not how many were cheated. Google "
        "Trends reports relative interest from a sample of searches, not counts. On the government side, "
        "we read only the official press release website; the Securities and Futures Commission, the police "
        "and the Anti-Deception Coordination Centre publish many warnings elsewhere. A scam that is missing "
        "from press releases is not necessarily one the government ignored."
    )
    st.page_link(P_METHODS, label="Read the full methodology →")
    footer()


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
