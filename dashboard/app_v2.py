"""
🌍 Renewable Energy Readiness Score — v4.0 PERSONALIZED ULTIMATE
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from sklearn.preprocessing import MinMaxScaler

load_dotenv()

def hex_to_rgba(hex_color, alpha=0.15):
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = ''.join([c*2 for c in h])
    r,g,b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

THEMES = {
    "🌌 Sci-Fi Space": {
        "bg":"#020814","bg2":"#050f1e","bg3":"#0a1628","border":"#0d2137",
        "accent1":"#00d4ff","accent2":"#7b2ff7","accent3":"#ff6b35",
        "high":"#00d4ff","medium":"#7b2ff7","low":"#ff6b35",
        "font":"Orbitron","body":"Exo 2",
        "glow":"0 0 20px rgba(0,212,255,0.4)","particle":"rgba(0,212,255,0.6)",
        "grad":"linear-gradient(135deg,#00d4ff,#7b2ff7)",
    },
    "💎 Ultra Luxury": {
        "bg":"#0a0a0f","bg2":"#12121a","bg3":"#1a1a24","border":"#2a2a3a",
        "accent1":"#c9a84c","accent2":"#e8d5a3","accent3":"#8b6914",
        "high":"#c9a84c","medium":"#e8d5a3","low":"#8b6914",
        "font":"Playfair Display","body":"Cormorant Garamond",
        "glow":"0 0 30px rgba(201,168,76,0.3)","particle":"rgba(201,168,76,0.5)",
        "grad":"linear-gradient(135deg,#c9a84c,#e8d5a3)",
    },
    "⚡ Cyberpunk": {
        "bg":"#050005","bg2":"#0d000d","bg3":"#150015","border":"#2d002d",
        "accent1":"#ff00ff","accent2":"#00ffff","accent3":"#ffff00",
        "high":"#00ffff","medium":"#ffff00","low":"#ff00ff",
        "font":"Share Tech Mono","body":"Source Code Pro",
        "glow":"0 0 25px rgba(255,0,255,0.5)","particle":"rgba(0,255,255,0.7)",
        "grad":"linear-gradient(135deg,#ff00ff,#00ffff)",
    },
    "🌿 Clean Future": {
        "bg":"#f0f4f8","bg2":"#ffffff","bg3":"#e8f0fe","border":"#d0dce8",
        "accent1":"#1a73e8","accent2":"#34a853","accent3":"#ea4335",
        "high":"#34a853","medium":"#fbbc04","low":"#ea4335",
        "font":"DM Sans","body":"DM Sans",
        "glow":"0 4px 20px rgba(26,115,232,0.2)","particle":"rgba(26,115,232,0.4)",
        "grad":"linear-gradient(135deg,#1a73e8,#34a853)","light":True,
    },
}

st.set_page_config(
    page_title="⚡ RE Readiness Ultimate",
    page_icon="🌍", layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.markdown("### 🎨 Personalize")
    chosen_theme = st.selectbox("Theme", list(THEMES.keys()), index=0)
    chosen_effects = st.multiselect(
        "Visual Effects",
        ["✨ Glowing Borders","🌊 Animated Background","🎆 Particles","🔮 Glassmorphism"],
        default=["✨ Glowing Borders","🔮 Glassmorphism"],
    )

T           = THEMES[chosen_theme]
is_light    = T.get("light", False)
text_color  = "#1a1a2e" if is_light else "#e8eef4"
muted_color = "#5a6a7a" if is_light else "#4a6a8a"
use_glow    = "✨ Glowing Borders"     in chosen_effects
use_anim    = "🌊 Animated Background" in chosen_effects
use_part    = "🎆 Particles"           in chosen_effects
use_glass   = "🔮 Glassmorphism"       in chosen_effects

glow_css  = f"box-shadow:{T['glow']};" if use_glow else ""
glass_css = (f"backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);"
             f"background:{'rgba(255,255,255,0.08)' if not is_light else 'rgba(255,255,255,0.7)'} !important;"
             ) if use_glass else ""
anim_css  = (f"background:linear-gradient(-45deg,{T['bg']},{T['bg2']},{T['bg3']},{T['bg']});"
             f"background-size:400% 400%;animation:gradientFlow 8s ease infinite;"
             ) if use_anim else f"background-color:{T['bg']};"

FONT_URLS = {
    "Orbitron":         "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap",
    "Playfair Display": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Cormorant+Garamond:wght@300;400;600&display=swap",
    "Share Tech Mono":  "https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Source+Code+Pro:wght@300;400;600&display=swap",
    "DM Sans":          "https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;600;700&display=swap",
}

particles_js = f"""
<canvas id="pc" style="position:fixed;top:0;left:0;width:100%;height:100%;
pointer-events:none;z-index:0;opacity:0.35;"></canvas>
<script>
const cv=document.getElementById('pc');
if(cv){{
  const cx=cv.getContext('2d');
  cv.width=window.innerWidth; cv.height=window.innerHeight;
  const ps=Array.from({{length:55}},()=>({{
    x:Math.random()*cv.width,y:Math.random()*cv.height,
    vx:(Math.random()-.5)*.5,vy:(Math.random()-.5)*.5,
    r:Math.random()*2+.5,a:Math.random()*.5+.2
  }}));
  function draw(){{
    cx.clearRect(0,0,cv.width,cv.height);
    ps.forEach(p=>{{
      p.x+=p.vx;p.y+=p.vy;
      if(p.x<0||p.x>cv.width)p.vx*=-1;
      if(p.y<0||p.y>cv.height)p.vy*=-1;
      cx.beginPath();cx.arc(p.x,p.y,p.r,0,Math.PI*2);
      cx.fillStyle='{T["particle"]}';cx.globalAlpha=p.a;cx.fill();
    }});
    ps.forEach((p,i)=>ps.slice(i+1).forEach(p2=>{{
      const d=Math.hypot(p.x-p2.x,p.y-p2.y);
      if(d<100){{
        cx.beginPath();cx.moveTo(p.x,p.y);cx.lineTo(p2.x,p2.y);
        cx.strokeStyle='{T["particle"]}';cx.globalAlpha=(1-d/100)*.12;
        cx.lineWidth=.5;cx.stroke();
      }}
    }}));
    requestAnimationFrame(draw);
  }}
  draw();
}}
</script>
""" if use_part else ""

st.markdown(f"""
<style>
  @import url('{FONT_URLS.get(T["font"],"") }');
  :root{{
    --bg:{T['bg']};--bg2:{T['bg2']};--bg3:{T['bg3']};--border:{T['border']};
    --a1:{T['accent1']};--a2:{T['accent2']};--a3:{T['accent3']};
    --high:{T['high']};--med:{T['medium']};--low:{T['low']};
    --text:{text_color};--muted:{muted_color};--grad:{T['grad']};
  }}
  @keyframes gradientFlow{{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}
  @keyframes shimmer{{0%{{background-position:-200% 0}}100%{{background-position:200% 0}}}}
  @keyframes floatUp{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
  @keyframes pulseGlow{{0%,100%{{opacity:1}}50%{{opacity:.8}}}}

  html,body,[class*="css"]{{font-family:'{T["body"]}',sans-serif!important;color:{text_color};}}
  .main{{{anim_css}min-height:100vh;}}
  .block-container{{padding:1rem 2rem;position:relative;z-index:1;}}
  [data-testid="stSidebar"]{{background:linear-gradient(180deg,{T['bg2']} 0%,{T['bg']} 100%)!important;border-right:1px solid {T['border']};}}

  .kpi{{
    {glass_css}
    background:linear-gradient(135deg,{T['bg3']} 0%,{T['bg2']} 100%);
    border:1px solid {T['border']};border-radius:16px;padding:18px 16px;
    text-align:center;position:relative;overflow:hidden;
    transition:transform .25s,border-color .25s;
    {'animation:pulseGlow 3s ease infinite;' if use_glow else ''}
  }}
  .kpi:hover{{transform:translateY(-4px) scale(1.02);border-color:{T['accent1']};{glow_css}}}
  .kpi::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
    background:{T['grad']};background-size:200% 100%;animation:shimmer 3s infinite;}}
  .kv{{font-family:'{T["font"]}',monospace;font-size:1.8rem;font-weight:700;line-height:1;margin:6px 0 2px;}}
  .kl{{font-size:.65rem;color:{muted_color};text-transform:uppercase;letter-spacing:2px;font-weight:700;}}
  .ks{{font-size:.65rem;color:{muted_color};margin-top:3px;opacity:.7;}}

  .sh{{font-family:'{T["font"]}',monospace;font-size:.72rem;font-weight:700;
    color:{T['accent1']};text-transform:uppercase;letter-spacing:3px;
    border-bottom:1px solid {T['border']};padding-bottom:8px;margin:22px 0 14px;
    display:flex;align-items:center;gap:8px;}}

  .bh{{background:rgba(0,0,0,.3);color:{T['high']};border:1px solid {T['high']};padding:3px 14px;border-radius:20px;font-size:.72rem;font-weight:700;font-family:'{T["font"]}',monospace;{f'box-shadow:0 0 8px {T["high"]}66;' if use_glow else ''}}}
  .bm{{background:rgba(0,0,0,.3);color:{T['medium']};border:1px solid {T['medium']};padding:3px 14px;border-radius:20px;font-size:.72rem;font-weight:700;font-family:'{T["font"]}',monospace;{f'box-shadow:0 0 8px {T["medium"]}66;' if use_glow else ''}}}
  .bl{{background:rgba(0,0,0,.3);color:{T['low']};border:1px solid {T['low']};padding:3px 14px;border-radius:20px;font-size:.72rem;font-weight:700;font-family:'{T["font"]}',monospace;{f'box-shadow:0 0 8px {T["low"]}66;' if use_glow else ''}}}

  .card{{{glass_css}background:{T['bg2']};border:1px solid {T['border']};border-radius:20px;padding:22px 26px;transition:border-color .2s;}}
  .card:hover{{border-color:{T['accent1']};}}
  .bc{{{glass_css}background:linear-gradient(135deg,{T['bg3']},{T['bg2']});border:1px solid {T['border']};border-radius:20px;padding:24px;text-align:center;transition:all .3s;}}
  .bc:hover{{transform:scale(1.02);{glow_css}}}
  .bscore{{font-family:'{T["font"]}',monospace;font-size:3.2rem;font-weight:900;line-height:1;margin:10px 0;}}

  .lr{{display:flex;align-items:center;gap:12px;padding:10px 14px;border-radius:12px;margin-bottom:5px;
    {glass_css}background:{T['bg3']};border:1px solid {T['border']};transition:all .2s;}}
  .lr:hover{{border-color:{T['accent1']};transform:translateX(5px);{glow_css}}}
  .lr-rank{{font-family:'{T["font"]}',monospace;font-size:.9rem;font-weight:700;min-width:30px;text-align:center;}}
  .lr-name{{flex:1;font-size:.88rem;font-weight:600;}}
  .lr-score{{font-family:'{T["font"]}',monospace;font-size:.88rem;color:{T['accent1']};font-weight:700;}}

  .pc{{background:{T['bg3']};border-left:3px solid {T['accent1']};border-radius:0 14px 14px 0;
    padding:14px 18px;margin-bottom:10px;transition:all .2s;}}
  .pc:hover{{border-left-width:5px;{glow_css}}}

  .tn{{{glass_css}background:{T['bg3']};border:2px solid {T['border']};border-radius:18px;
    padding:20px;text-align:center;transition:all .3s;animation:floatUp 4s ease infinite;}}
  .tn:hover{{border-color:{T['accent1']};{glow_css}}}
  .ty{{font-family:'{T["font"]}',monospace;font-size:1.6rem;font-weight:700;color:{T['accent1']};}}
  .ts{{font-family:'{T["font"]}',monospace;font-size:2.8rem;font-weight:900;margin:6px 0;}}

  .stTabs [data-baseweb="tab-list"]{{gap:3px;background:{T['bg2']};border-radius:14px;padding:4px;border:1px solid {T['border']};}}
  .stTabs [data-baseweb="tab"]{{color:{muted_color};font-weight:600;font-size:.78rem;border-radius:10px;padding:8px 14px;font-family:'{T["font"]}',monospace;letter-spacing:1px;}}
  .stTabs [aria-selected="true"]{{background:linear-gradient(135deg,{T['bg3']},{T['accent1']}22)!important;color:{T['accent1']}!important;border:1px solid {T['accent1']}44!important;}}

  ::-webkit-scrollbar{{width:4px;}}
  ::-webkit-scrollbar-track{{background:{T['bg']};}}
  ::-webkit-scrollbar-thumb{{background:{T['border']};border-radius:2px;}}
  h1,h2,h3{{font-family:'{T["font"]}',sans-serif!important;}}
</style>
{particles_js}
""", unsafe_allow_html=True)

LABEL_COLORS = {"High": T["high"], "Medium": T["medium"], "Low": T["low"]}
LABEL_FILL   = {
    "High":   hex_to_rgba(T["high"],   0.13),
    "Medium": hex_to_rgba(T["medium"], 0.13),
    "Low":    hex_to_rgba(T["low"],    0.13),
}
LABEL_ORDER  = ["Low","Medium","High"]
MONGO_URI    = os.getenv("MONGO_URI","mongodb://localhost:27017/")
MONGO_DB     = os.getenv("MONGO_DB", "renewable_readiness")
RETRAIN_TH   = 50
MEDAL        = {1:"🥇",2:"🥈",3:"🥉"}
FEATURE_COLS = [
    "log_gdp_per_capita","urban_population_pct",
    "log_energy_use_per_capita","electricity_access_pct",
    "renewable_share_pct","energy_pressure_index","infrastructure_score",
]

@st.cache_data
def load_data():
    try:
        c = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        r = list(c[MONGO_DB]["countries"].find({},{"_id":0}))
        c.close()
        if r: return pd.DataFrame(r),"🍃 MongoDB"
    except: pass
    return pd.read_csv("data/raw/predictions.csv"),"📄 CSV"

@st.cache_data
def load_metrics():
    try:
        c = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        r = list(c[MONGO_DB]["model_metrics"].find({},{"_id":0}))
        c.close()
        return pd.DataFrame(r) if r else None
    except: return None

def get_log_count():
    try:
        c = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        n = c[MONGO_DB]["predictions_log"].count_documents({})
        c.close(); return n
    except: return 0

@st.cache_resource
def load_pipeline(): return joblib.load("models/logistic_regression.pkl")
@st.cache_resource
def load_rf():       return joblib.load("models/random_forest.pkl")

df,data_src = load_data()
metrics_df  = load_metrics()
pipeline    = load_pipeline()
rf_pipe     = load_rf()
log_count   = get_log_count()

def badge(label):
    return f'<span class="{"bh" if label=="High" else "bm" if label=="Medium" else "bl"}">{label}</span>'

def norm_row(row):
    return {c:float((row[c]-df[c].min())/(df[c].max()-df[c].min()+1e-9)*100) for c in FEATURE_COLS}

def make_layout(height=None, yrange=None):
    layout = dict(
        paper_bgcolor=T["bg"], plot_bgcolor=T["bg2"],
        font_color=muted_color, title_font_color=T["accent1"],
        xaxis=dict(gridcolor=T["border"]),
        yaxis=dict(gridcolor=T["border"]),
    )
    if height: layout["height"] = height
    if yrange: layout["yaxis"] = dict(gridcolor=T["border"], range=yrange)
    return layout

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:6px 0 18px;border-bottom:1px solid {T["border"]};margin-bottom:14px;'>
      <div style='font-size:2rem;'>🌍</div>
      <div style='font-family:"{T["font"]}",monospace;font-size:.95rem;font-weight:900;
                  background:{T["grad"]};-webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  letter-spacing:3px;'>RE READINESS</div>
      <div style='font-size:.58rem;color:{muted_color};letter-spacing:3px;margin-top:3px;'>ULTIMATE v4.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="kl">Filter</div>', unsafe_allow_html=True)
    label_filter = st.multiselect("Filter",["High","Medium","Low"],
                                  default=["High","Medium","Low"],
                                  label_visibility="collapsed")

    st.markdown(f'<div class="kl" style="margin-top:10px;">Search</div>', unsafe_allow_html=True)
    search = st.text_input("Search",placeholder="Country...",label_visibility="collapsed")

    st.markdown("---")

    # Retrain progress
    pct = min(log_count/RETRAIN_TH*100,100)
    bar_color = T["high"] if pct >= 100 else T["accent1"]
    st.markdown(f"""
    <div style='background:{T["bg3"]};border:1px solid {T["border"]};
                border-radius:10px;padding:12px;margin:6px 0;'>
      <div style='display:flex;justify-content:space-between;'>
        <div style='font-size:.65rem;color:{muted_color};text-transform:uppercase;letter-spacing:1px;'>🔄 Retrain Progress</div>
        <div style='font-family:"{T["font"]}",monospace;font-size:.72rem;color:{bar_color};font-weight:700;'>{log_count}/{RETRAIN_TH}</div>
      </div>
      <div style='background:{T["bg"]};border-radius:4px;height:6px;margin:7px 0;'>
        <div style='width:{pct}%;height:6px;border-radius:4px;
                    background:linear-gradient(90deg,{T["accent1"]},{bar_color});'></div>
      </div>
      <div style='font-size:.62rem;color:{muted_color};'>
        {'✅ Ready to retrain!' if pct>=100 else f'{RETRAIN_TH-log_count} more predictions needed'}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Force retrain button
    if st.button("🔄 Force Retrain Now", use_container_width=True):
        with st.spinner("🔄 Retraining model on all data..."):
            try:
                import sys
                sys.path.insert(0, ".")
                from src.retrain import check_and_retrain
                success = check_and_retrain(force=True)
                if success:
                    st.success("✅ Model retrained successfully!")
                    st.cache_resource.clear()
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Retrain failed — check terminal")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:.65rem;color:{muted_color};text-transform:uppercase;letter-spacing:1px;'>Source</div>
    <div style='color:{T["accent1"]};font-size:.85rem;font-weight:700;'>{data_src}</div>
    <div style='font-size:.65rem;color:{muted_color};margin-top:2px;'>{len(df)} countries</div>
    """, unsafe_allow_html=True)

# ── Filter ─────────────────────────────────────────────────────────────────
fdf = df[df["predicted_label"].isin(label_filter)].copy()
if search:
    fdf = fdf[fdf["country_name"].str.contains(search,case=False,na=False)]

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='padding:6px 0 4px;'>
  <h1 style='font-size:2rem;font-weight:900;margin:0;line-height:1.1;
             background:{T["grad"]};-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
    🌍 Renewable Energy Adoption Readiness Score
  </h1>
  <p style='color:{muted_color};font-size:.78rem;margin-top:6px;
            font-family:"{T["font"]}",monospace;letter-spacing:1px;'>
    ML · World Bank · Kaggle · MongoDB · Theme: {chosen_theme}
  </p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ── KPIs ───────────────────────────────────────────────────────────────────
counts = df["predicted_label"].value_counts()
total  = len(df)
top_c  = df.loc[df["readiness_score"].idxmax(),"country_name"]
kpis   = [
    (total,                                T["accent1"], "COUNTRIES",  "in dataset"),
    (counts.get("High",0),                 T["high"],    "HIGH",       f"{counts.get('High',0)/total*100:.0f}%"),
    (counts.get("Medium",0),               T["medium"],  "MEDIUM",     f"{counts.get('Medium',0)/total*100:.0f}%"),
    (counts.get("Low",0),                  T["low"],     "LOW",        f"{counts.get('Low',0)/total*100:.0f}%"),
    (f"{df['readiness_score'].mean():.1f}",T["accent2"], "AVG SCORE",  "global"),
    (f"{df['readiness_score'].max():.1f}", T["accent1"], "TOP SCORE",  top_c),
]
for col,(val,clr,lbl,sub) in zip(st.columns(6),kpis):
    with col:
        st.markdown(f'<div class="kpi"><div class="kl">{lbl}</div>'
                    f'<div class="kv" style="color:{clr};">{val}</div>'
                    f'<div class="ks">{sub}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9 = st.tabs([
    "🌍 3D Globe","🗺️ Map","🏆 Leaderboard",
    "⚔️ Battle","🔮 Future 2050",
    "🎯 Policy","📄 Report","📊 Analytics","⚡ Predict New",
])

# ══ TAB 1 — 3D GLOBE ══════════════════════════════════════════════════════
with tab1:
    st.markdown(f'<div class="sh">🌍 Interactive 3D Globe — drag · zoom · hover</div>',unsafe_allow_html=True)
    p1=fdf.copy()
    p1["cv"]=p1["predicted_label"].map({"Low":0,"Medium":1,"High":2})
    loc="country_code" if "country_code" in p1.columns else "country_name"
    lm="ISO-3" if loc=="country_code" else "country names"
    fig_globe=go.Figure(go.Choropleth(
        locations=p1[loc],locationmode=lm,z=p1["cv"],text=p1["country_name"],
        customdata=np.stack([p1["readiness_score"],p1["predicted_label"],
                             p1["prediction_confidence"]*100],axis=-1),
        hovertemplate="<b>%{text}</b><br>Score:%{customdata[0]:.1f}<br>%{customdata[1]}<br>Conf:%{customdata[2]:.0f}%<extra></extra>",
        colorscale=[[0,T["low"]],[.5,T["medium"]],[1,T["high"]]],
        zmin=0,zmax=2,showscale=False,
        marker=dict(line=dict(color=T["bg"],width=.5)),
    ))
    frames=[go.Frame(layout=dict(geo=dict(projection_rotation=dict(lon=l,lat=20,roll=0))),name=str(l))
            for l in range(0,360,3)]
    fig_globe.frames=frames
    fig_globe.update_layout(
        geo=dict(showframe=False,bgcolor=T["bg"],
                 showcoastlines=True,coastlinecolor=T["border"],
                 showland=True,landcolor=T["bg2"],
                 showocean=True,oceancolor=T["bg"],
                 showcountries=True,countrycolor=T["border"],
                 projection_type="orthographic",
                 projection_rotation=dict(lon=0,lat=20,roll=0)),
        paper_bgcolor=T["bg"],margin=dict(l=0,r=0,t=0,b=0),height=560,
        updatemenus=[dict(type="buttons",showactive=False,y=.05,x=.5,xanchor="center",
            buttons=[dict(label="▶ Rotate",method="animate",
                args=[None,dict(frame=dict(duration=50,redraw=True),
                               fromcurrent=True,transition=dict(duration=0))])])],
    )
    st.plotly_chart(fig_globe,use_container_width=True)
    g1,g2,g3=st.columns(3)
    for c,(l,cl,d) in zip([g1,g2,g3],[
        ("🟢 High",T["high"],"Score > 61"),
        ("🟡 Medium",T["medium"],"Score 54–61"),
        ("🔴 Low",T["low"],"Score < 54"),
    ]):
        with c:
            st.markdown(f"<div style='color:{cl};font-size:.82rem;font-weight:700;'>{l}</div>"
                        f"<div style='color:{muted_color};font-size:.72rem;'>{d}</div>",
                        unsafe_allow_html=True)

# ══ TAB 2 — MAP ═══════════════════════════════════════════════════════════
with tab2:
    st.markdown(f'<div class="sh">🗺️ Global Readiness Map</div>',unsafe_allow_html=True)
    p2=fdf.copy()
    p2["cv"]=p2["predicted_label"].map({"Low":0,"Medium":1,"High":2})
    loc2="country_code" if "country_code" in p2.columns else "country_name"
    fig_map=px.choropleth(p2,locations=loc2,
        locationmode="ISO-3" if loc2=="country_code" else "country names",
        color="cv",hover_name="country_name",
        hover_data={"readiness_score":":.1f","predicted_label":True,"cv":False},
        color_continuous_scale=[[0,T["low"]],[.5,T["medium"]],[1,T["high"]]],range_color=[0,2])
    fig_map.update_layout(paper_bgcolor=T["bg"],
        geo=dict(bgcolor=T["bg"],showframe=False,showcoastlines=True,coastlinecolor=T["border"],
                 showland=True,landcolor=T["bg2"],showocean=True,oceancolor=T["bg"],
                 showcountries=True,countrycolor=T["border"]),
        coloraxis_showscale=False,margin=dict(l=0,r=0,t=0,b=0),height=500)
    st.plotly_chart(fig_map,use_container_width=True)

# ══ TAB 3 — LEADERBOARD ═══════════════════════════════════════════════════
with tab3:
    st.markdown(f'<div class="sh">🏆 Country Leaderboard</div>',unsafe_allow_html=True)
    lc1,lc2=st.columns([2,1])
    with lc1:
        lbf=st.selectbox("Show:",["🌍 All","🟢 High Only","🟡 Medium Only","🔴 Low Only"])
    with lc2:
        lbn=st.slider("Top N:",10,50,20)
    lbmap={"🌍 All":["High","Medium","Low"],"🟢 High Only":["High"],
           "🟡 Medium Only":["Medium"],"🔴 Low Only":["Low"]}
    lbdf=(df[df["predicted_label"].isin(lbmap[lbf])]
          .sort_values("readiness_score",ascending=False)
          .head(lbn).reset_index(drop=True))
    mx=df["readiness_score"].max()
    if len(lbdf)>=3:
        st.markdown(f'<div class="sh">🏅 Podium</div>',unsafe_allow_html=True)
        p1c,p2c,p3c=st.columns(3)
        for col,idx,medal in zip([p2c,p1c,p3c],[0,1,2],["🥇","🥈","🥉"]):
            r=lbdf.iloc[idx]; clr=LABEL_COLORS[r["predicted_label"]]
            with col:
                st.markdown(f"""
                <div class="bc" style="border-color:{clr}44;">
                  <div style='font-size:2.5rem;'>{medal}</div>
                  <div style='font-size:1rem;font-weight:800;margin:8px 0;'>{r['country_name']}</div>
                  <div class="bscore" style="color:{clr};font-size:2rem;">{r['readiness_score']:.1f}</div>
                  {badge(r['predicted_label'])}
                </div>""",unsafe_allow_html=True)
    st.markdown(f'<div class="sh">📋 Rankings</div>',unsafe_allow_html=True)
    for i,row in lbdf.iterrows():
        rank=i+1; clr=LABEL_COLORS[row["predicted_label"]]
        bw=row["readiness_score"]/mx*100; m=MEDAL.get(rank,f"#{rank}")
        st.markdown(f"""
        <div class="lr">
          <div class="lr-rank" style="color:{clr};">{m}</div>
          <div class="lr-name">{row['country_name']}</div>
          <div style='flex:2;background:{T["bg"]};border-radius:4px;height:5px;'>
            <div style='width:{bw}%;height:5px;border-radius:4px;
                        background:linear-gradient(90deg,{clr}88,{clr});'></div>
          </div>
          <div class="lr-score">{row['readiness_score']:.1f}</div>
          {badge(row['predicted_label'])}
        </div>""",unsafe_allow_html=True)

# ══ TAB 4 — BATTLE MODE ═══════════════════════════════════════════════════
with tab4:
    st.markdown(f'<div class="sh">⚔️ Country Battle Mode</div>',unsafe_allow_html=True)
    cl=sorted(df["country_name"].dropna().unique())
    b1,b2,b3=st.columns([2,1,2])
    with b1:
        ca=st.selectbox("🔵 Country A:",cl,
                        index=cl.index("Germany") if "Germany" in cl else 0,key="ba")
    with b2:
        st.markdown(f"<div style='text-align:center;padding-top:26px;"
                    f"font-family:\"{T['font']}\",monospace;font-size:1.5rem;"
                    f"font-weight:900;color:{T['accent2']};'>VS</div>",
                    unsafe_allow_html=True)
    with b3:
        cb=st.selectbox("🔴 Country B:",cl,
                        index=cl.index("India") if "India" in cl else 1,key="bb")
    if ca!=cb:
        ra=df[df["country_name"]==ca].iloc[0]
        rb=df[df["country_name"]==cb].iloc[0]
        ca_clr=LABEL_COLORS[ra["predicted_label"]]
        cb_clr=LABEL_COLORS[rb["predicted_label"]]
        winner=ca if ra["readiness_score"]>rb["readiness_score"] else cb
        diff=abs(ra["readiness_score"]-rb["readiness_score"])
        s1,s2,s3=st.columns([2,1,2])
        with s1:
            st.markdown(f"""
            <div class="bc" style="border-color:{ca_clr};">
              <div style='font-size:.7rem;color:{muted_color};font-family:"{T["font"]}",monospace;
                          text-transform:uppercase;letter-spacing:2px;'>Country A</div>
              <div style='font-size:1.4rem;font-weight:800;margin:8px 0;'>{ca}</div>
              <div class="bscore" style="color:{ca_clr};">{ra['readiness_score']:.1f}</div>
              {badge(ra['predicted_label'])}
              <div style='margin-top:10px;font-size:.78rem;color:{muted_color};'>
                Confidence: <span style='color:{ca_clr};font-weight:700;'>{ra['prediction_confidence']*100:.0f}%</span>
              </div>
            </div>""",unsafe_allow_html=True)
        with s2:
            st.markdown(f"""
            <div style='text-align:center;padding-top:30px;'>
              <div style='font-size:.65rem;color:{muted_color};text-transform:uppercase;letter-spacing:2px;'>Winner</div>
              <div style='font-size:.95rem;font-weight:800;color:{T["accent1"]};margin:8px 0;'>🏆 {winner}</div>
              <div style='font-size:.7rem;color:{muted_color};'>by {diff:.1f} pts</div>
            </div>""",unsafe_allow_html=True)
        with s3:
            st.markdown(f"""
            <div class="bc" style="border-color:{cb_clr};">
              <div style='font-size:.7rem;color:{muted_color};font-family:"{T["font"]}",monospace;
                          text-transform:uppercase;letter-spacing:2px;'>Country B</div>
              <div style='font-size:1.4rem;font-weight:800;margin:8px 0;'>{cb}</div>
              <div class="bscore" style="color:{cb_clr};">{rb['readiness_score']:.1f}</div>
              {badge(rb['predicted_label'])}
              <div style='margin-top:10px;font-size:.78rem;color:{muted_color};'>
                Confidence: <span style='color:{cb_clr};font-weight:700;'>{rb['prediction_confidence']*100:.0f}%</span>
              </div>
            </div>""",unsafe_allow_html=True)
        st.markdown(f'<div class="sh">📡 Radar Comparison</div>',unsafe_allow_html=True)
        cats=[c.replace("_"," ").replace("log ","").title() for c in FEATURE_COLS]
        va=list(norm_row(ra).values())
        vb=list(norm_row(rb).values())
        fig_r=go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=va+[va[0]],theta=cats+[cats[0]],fill="toself",
            fillcolor=LABEL_FILL[ra["predicted_label"]],
            line=dict(color=ca_clr,width=2),name=ca))
        fig_r.add_trace(go.Scatterpolar(
            r=vb+[vb[0]],theta=cats+[cats[0]],fill="toself",
            fillcolor=LABEL_FILL[rb["predicted_label"]],
            line=dict(color=cb_clr,width=2),name=cb))
        fig_r.update_layout(
            polar=dict(bgcolor=T["bg2"],
                       radialaxis=dict(visible=True,range=[0,100],gridcolor=T["border"]),
                       angularaxis=dict(gridcolor=T["border"],tickfont_color=muted_color)),
            paper_bgcolor=T["bg"],legend=dict(bgcolor=T["bg2"],font_color=text_color),
            height=420,showlegend=True)
        st.plotly_chart(fig_r,use_container_width=True)
        st.markdown(f'<div class="sh">📊 Feature Breakdown</div>',unsafe_allow_html=True)
        fig_b=go.Figure()
        fig_b.add_trace(go.Bar(name=ca,x=cats,y=va,marker_color=ca_clr,opacity=.85))
        fig_b.add_trace(go.Bar(name=cb,x=cats,y=vb,marker_color=cb_clr,opacity=.85))
        fig_b.update_layout(**make_layout(height=350),barmode="group",
                            legend=dict(bgcolor=T["bg2"],font_color=text_color))
        st.plotly_chart(fig_b,use_container_width=True)
        st.markdown(f'<div class="sh">🏅 Feature Winners</div>',unsafe_allow_html=True)
        fw=st.columns(len(FEATURE_COLS))
        for col,feat,a,b_ in zip(fw,cats,va,vb):
            wc=ca_clr if a>=b_ else cb_clr
            wn=ca if a>=b_ else cb
            with col:
                st.markdown(f"""
                <div style='background:{T["bg3"]};border:1px solid {T["border"]};
                            border-radius:10px;padding:10px 6px;text-align:center;'>
                  <div style='font-size:.58rem;color:{muted_color};text-transform:uppercase;
                              letter-spacing:1px;margin-bottom:5px;'>{feat}</div>
                  <div style='font-size:.8rem;font-weight:700;color:{wc};'>{wn}</div>
                  <div style='font-size:.6rem;color:{muted_color};margin-top:2px;'>+{abs(a-b_):.1f}</div>
                </div>""",unsafe_allow_html=True)
    else:
        st.warning("Select two different countries!")

# ══ TAB 5 — FUTURE 2050 ═══════════════════════════════════════════════════
with tab5:
    st.markdown(f'<div class="sh">🔮 Future Readiness Predictor — 2030 · 2040 · 2050</div>',unsafe_allow_html=True)
    fc1,fc2=st.columns([2,1])
    with fc1:
        fc=st.selectbox("Country:",sorted(df["country_name"].dropna().unique()),
                        index=sorted(df["country_name"].dropna().unique()).index("India")
                        if "India" in df["country_name"].values else 0)
    with fc2:
        sc=st.selectbox("Scenario:",["🚀 Optimistic","📈 Moderate","🐢 Pessimistic"])
    fr=df[df["country_name"]==fc].iloc[0]
    GR={"🚀 Optimistic":dict(gdp=.06,urban=.008,elec=.02,renew=.04,energy=.01),
        "📈 Moderate":  dict(gdp=.03,urban=.005,elec=.01,renew=.025,energy=.005),
        "🐢 Pessimistic":dict(gdp=.01,urban=.002,elec=.005,renew=.01,energy=.002)}[sc]

    def project(row,yrs,gr):
        g=np.expm1(row["log_gdp_per_capita"])*(1+gr["gdp"])**yrs
        u=min(row["urban_population_pct"]+gr["urban"]*yrs*100,100)
        e=min(row["electricity_access_pct"]+gr["elec"]*yrs*100,100)
        r=min(row["renewable_share_pct"]+gr["renew"]*yrs*100,100)
        en=np.expm1(row["log_energy_use_per_capita"])*(1+gr["energy"])**yrs
        lg=np.log1p(g); le2=np.log1p(en)
        inf=(e+u)/2
        me=max(df["energy_use_per_capita"].max() if "energy_use_per_capita" in df.columns else 12000,en)
        pr=(en/me)*(1-r/100)
        inp=pd.DataFrame([[lg,u,le2,e,r,pr,inf]],columns=FEATURE_COLS)
        prb=pipeline.predict_proba(inp)[0]
        le3=joblib.load("models/label_encoder.pkl")
        lbl=le3.inverse_transform([pipeline.predict(inp)[0]])[0]
        tmp=df[FEATURE_COLS].copy()
        nr=pd.DataFrame([[lg,u,le2,e,r,pr,inf]],columns=FEATURE_COLS)
        cb2=pd.concat([tmp,nr],ignore_index=True)
        sc2=MinMaxScaler()
        s=(0.30*sc2.fit_transform(cb2[["log_gdp_per_capita"]]).flatten()[-1]+
           0.30*sc2.fit_transform(cb2[["infrastructure_score"]]).flatten()[-1]+
           0.25*sc2.fit_transform(cb2[["renewable_share_pct"]]).flatten()[-1]+
           0.15*(1-sc2.fit_transform(cb2[["energy_pressure_index"]]).flatten()[-1]))*100
        return dict(score=round(s,1),label=lbl,conf=round(prb.max()*100,1),
                    gdp=round(g,0),urban=round(u,1),elec=round(e,1),renew=round(r,1))

    YRS=[0,11,21,31]; YLBLS=["2024","2030","2040","2050"]
    PROJS=[project(fr,y,GR) for y in YRS]
    st.markdown(f'<div class="sh">📅 Timeline</div>',unsafe_allow_html=True)
    tc=st.columns(4)
    for col,proj,yr in zip(tc,PROJS,YLBLS):
        clr=LABEL_COLORS[proj["label"]]
        with col:
            st.markdown(f"""
            <div class="tn" style="border-color:{clr}44;animation-delay:{YLBLS.index(yr)*.5}s;">
              <div class="ty">{yr}</div>
              <div class="ts" style="color:{clr};">{proj['score']}</div>
              <div style='font-size:.68rem;color:{muted_color};margin:3px 0;'>/100</div>
              {badge(proj['label'])}
              <div style='margin-top:8px;font-size:.7rem;color:{muted_color};'>{proj['conf']}% conf</div>
            </div>""",unsafe_allow_html=True)
    st.markdown(f'<div class="sh">📈 Trajectory</div>',unsafe_allow_html=True)
    yns=[2024,2030,2040,2050]
    scs=[p["score"] for p in PROJS]
    fig_t=go.Figure()
    fig_t.add_trace(go.Scatter(
        x=yns,y=scs,fill="tozeroy",
        fillcolor=hex_to_rgba(T["accent1"],0.04),
        line=dict(color=T["accent1"],width=3),
        mode="lines+markers+text",
        marker=dict(size=12,color=[LABEL_COLORS[p["label"]] for p in PROJS],
                    line=dict(width=2,color=T["bg"])),
        text=[f"{s:.1f}" for s in scs],textposition="top center",
        textfont=dict(color=T["accent1"],size=12,family=T["font"]),
    ))
    fig_t.add_hline(y=61,line_dash="dash",line_color=T["high"],
                    annotation_text="High",annotation_font_color=T["high"])
    fig_t.add_hline(y=54,line_dash="dash",line_color=T["medium"],
                    annotation_text="Medium",annotation_font_color=T["medium"])
    fig_t.update_layout(
        **make_layout(height=340,yrange=[0,105]),
        showlegend=False,
        title=dict(text=f"{fc} — {sc}",font_color=T["accent1"],font_size=13),
    )
    st.plotly_chart(fig_t,use_container_width=True)
    st.markdown(f'<div class="sh">📊 Projected Indicators</div>',unsafe_allow_html=True)
    pt=pd.DataFrame({"Year":YLBLS,"Score":[p["score"] for p in PROJS],
                     "Label":[p["label"] for p in PROJS],
                     "GDP($)":[f"{p['gdp']:,.0f}" for p in PROJS],
                     "Urban%":[f"{p['urban']:.1f}" for p in PROJS],
                     "Elec%":[f"{p['elec']:.1f}" for p in PROJS],
                     "Renew%":[f"{p['renew']:.1f}" for p in PROJS]})
    st.dataframe(pt,use_container_width=True,hide_index=True)

# ══ TAB 6 — POLICY ENGINE ═════════════════════════════════════════════════
with tab6:
    st.markdown(f'<div class="sh">🎯 Policy Recommendation Engine</div>',unsafe_allow_html=True)
    pc=st.selectbox("Country:",sorted(df["country_name"].dropna().unique()),key="pol")
    pr=df[df["country_name"]==pc].iloc[0]
    pl=pr["predicted_label"]; pclr=LABEL_COLORS[pl]
    fnorm=norm_row(pr)
    for col,(lbl,val,clr2) in zip(st.columns(4),[
        ("Score",f"{pr['readiness_score']:.1f}/100",pclr),
        ("Status",pl,pclr),
        ("GDP/cap",f"${np.expm1(pr['log_gdp_per_capita']):,.0f}",T["accent2"]),
        ("Renewable",f"{pr['renewable_share_pct']:.1f}%",T["accent1"]),
    ]):
        with col:
            st.markdown(f'<div class="kpi"><div class="kl">{lbl}</div>'
                        f'<div class="kv" style="color:{clr2};font-size:1.4rem;">{val}</div></div>',
                        unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    weaks=[(c,c.replace("_"," ").title(),fnorm[c]) for c in FEATURE_COLS if fnorm[c]<40]
    weaks.sort(key=lambda x:x[2])
    POLICIES={
        "log_gdp_per_capita":[
            dict(p="CRITICAL",t="Attract Clean Energy FDI",d="Establish renewable SEZs. Tax incentives for clean tech. Target Green Climate Fund.",i="HIGH",tl="3-5 yrs"),
            dict(p="HIGH",t="Develop Green Finance Framework",d="Issue sovereign green bonds. Create national green bank. Partner with multilateral banks.",i="HIGH",tl="1-2 yrs"),
        ],
        "electricity_access_pct":[
            dict(p="CRITICAL",t="Rural Electrification via Solar",d="Deploy solar home systems. Target 100% access by 2030. IRENA/UNDP partnerships.",i="VERY HIGH",tl="2-5 yrs"),
            dict(p="HIGH",t="Smart Grid Modernization",d="Upgrade transmission for renewables. Deploy smart meters. Reduce losses.",i="HIGH",tl="3-7 yrs"),
        ],
        "renewable_share_pct":[
            dict(p="CRITICAL",t="National Renewable Energy Target",d="Set 40% renewable target by 2030. Feed-in tariffs. Competitive auctions.",i="VERY HIGH",tl="1-3 yrs"),
            dict(p="HIGH",t="Phase Out Fossil Fuel Subsidies",d="Eliminate coal/oil subsidies. Redirect to renewables. Implement carbon pricing.",i="HIGH",tl="2-4 yrs"),
        ],
        "urban_population_pct":[
            dict(p="HIGH",t="Smart Urban Energy Planning",d="Integrate renewables in urban plans. Mandate solar on buildings. Develop microgrids.",i="MEDIUM",tl="2-4 yrs"),
        ],
        "log_energy_use_per_capita":[
            dict(p="MEDIUM",t="National Energy Efficiency Standards",d="Mandatory efficiency standards. Energy audits. Public awareness.",i="MEDIUM",tl="1-2 yrs"),
        ],
        "infrastructure_score":[
            dict(p="HIGH",t="10-Year Infrastructure Roadmap",d="National energy plan. Priority transmission lines. Tech transfer partnerships.",i="HIGH",tl="5-10 yrs"),
        ],
    }
    PC={"CRITICAL":T["low"],"HIGH":T["medium"],"MEDIUM":T["accent1"]}
    if weaks:
        st.markdown(f'<div class="sh">⚠️ Weak Areas ({len(weaks)})</div>',unsafe_allow_html=True)
        wc1,wc2=st.columns(2)
        with wc1:
            for c,d,v in weaks:
                bc2=T["low"] if v<20 else T["medium"] if v<30 else T["accent1"]
                st.markdown(f"""
                <div style='margin-bottom:10px;'>
                  <div style='display:flex;justify-content:space-between;margin-bottom:3px;'>
                    <div style='font-size:.8rem;font-weight:600;'>{d}</div>
                    <div style='font-family:"{T["font"]}",monospace;font-size:.78rem;color:{bc2};'>{v:.1f}/100</div>
                  </div>
                  <div style='background:{T["bg"]};border-radius:3px;height:5px;'>
                    <div style='width:{v}%;height:5px;border-radius:3px;
                                background:linear-gradient(90deg,{bc2}88,{bc2});'></div>
                  </div>
                </div>""",unsafe_allow_html=True)
        with wc2:
            fig_w=go.Figure(go.Bar(
                x=[w[1] for w in weaks],y=[w[2] for w in weaks],
                marker_color=[T["low"] if v<20 else T["medium"] if v<30 else T["accent1"] for _,_,v in weaks],
                text=[f"{v:.0f}" for _,_,v in weaks],
                textposition="outside",textfont=dict(color=text_color,size=11)))
            fig_w.update_layout(**make_layout(height=240),showlegend=False,
                                margin=dict(t=20,b=10,l=10,r=10))
            st.plotly_chart(fig_w,use_container_width=True)
        st.markdown(f'<div class="sh">📋 Recommendations</div>',unsafe_allow_html=True)
        total=0
        for col,disp,val in weaks:
            if col in POLICIES:
                for pol in POLICIES[col]:
                    total+=1; pc2=PC.get(pol["p"],T["accent1"])
                    st.markdown(f"""
                    <div class="pc" style="border-left-color:{pc2};">
                      <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                        <div>
                          <div style='font-size:.62rem;color:{pc2};text-transform:uppercase;
                                      letter-spacing:2px;font-weight:700;'>{pol["p"]} — {disp}</div>
                          <div style='font-size:.92rem;font-weight:700;margin:4px 0;'>{pol["t"]}</div>
                          <div style='font-size:.78rem;color:{muted_color};line-height:1.5;'>{pol["d"]}</div>
                        </div>
                        <div style='text-align:right;min-width:90px;margin-left:14px;'>
                          <div style='font-size:.62rem;color:{muted_color};text-transform:uppercase;'>Impact</div>
                          <div style='font-size:.78rem;font-weight:700;color:{pc2};'>{pol["i"]}</div>
                          <div style='font-size:.62rem;color:{muted_color};margin-top:5px;text-transform:uppercase;'>Timeline</div>
                          <div style='font-size:.72rem;'>{pol["tl"]}</div>
                        </div>
                      </div>
                    </div>""",unsafe_allow_html=True)
        st.success(f"✅ {total} recommendations for {pc}")
    else:
        st.markdown(f"""
        <div class="card" style="border-color:{T['high']};text-align:center;padding:40px;">
          <div style='font-size:3rem;'>🎉</div>
          <div style='font-size:1.2rem;font-weight:800;color:{T["high"]};margin:12px 0;'>
            {pc} has Strong Performance!</div>
          <div style='color:{muted_color};font-size:.85rem;'>All indicators above threshold.</div>
        </div>""",unsafe_allow_html=True)
    st.markdown(f'<div class="sh">🌐 Strategic Overview</div>',unsafe_allow_html=True)
    STRAT={
        "High":[("🌱","Lead by Example","Share best practices via South-South cooperation"),
                ("💡","Innovation Hub","Invest in green hydrogen and advanced storage R&D"),
                ("🤝","Climate Finance","Contribute to Green Climate Fund")],
        "Medium":[("⚡","Accelerate Transition","Fast-track renewable auctions"),
                  ("🏗️","Infrastructure Push","Prioritize grid modernization"),
                  ("📚","Skills Development","Train workforce for green energy jobs")],
        "Low":[("🆘","Emergency Energy Access","Prioritize basic electricity access first"),
               ("💰","Secure Climate Finance","Apply for GCF and World Bank green grants"),
               ("🤝","International Support","Seek IRENA/UNDP technical assistance")],
    }
    for icon,title,desc in STRAT[pl]:
        st.markdown(f"""
        <div style='display:flex;gap:14px;padding:12px 16px;background:{T["bg3"]};
                    border-radius:10px;margin-bottom:7px;border:1px solid {T["border"]};'>
          <div style='font-size:1.4rem;'>{icon}</div>
          <div>
            <div style='font-size:.88rem;font-weight:700;color:{pclr};'>{title}</div>
            <div style='font-size:.78rem;color:{muted_color};margin-top:2px;'>{desc}</div>
          </div>
        </div>""",unsafe_allow_html=True)

# ══ TAB 7 — REPORT ════════════════════════════════════════════════════════
with tab7:
    st.markdown(f'<div class="sh">📄 Report Generator</div>',unsafe_allow_html=True)
    rc=st.selectbox("Country:",sorted(df["country_name"].dropna().unique()),key="rpt")
    rr=df[df["country_name"]==rc].iloc[0]
    rl=rr["predicted_label"]; rclr=LABEL_COLORS[rl]
    fn=norm_row(rr)
    gr_=df.sort_values("readiness_score",ascending=False).reset_index(drop=True)
    rnk=gr_[gr_["country_name"]==rc].index[0]+1
    st.markdown(f"""
    <div class="card" style="border-color:{rclr}44;">
      <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px;'>
        <div>
          <div style='font-size:.62rem;color:{muted_color};text-transform:uppercase;
                      letter-spacing:3px;font-family:"{T["font"]}",monospace;'>RE READINESS REPORT</div>
          <div style='font-size:1.6rem;font-weight:800;margin:5px 0;'>{rc}</div>
          <div style='font-size:.75rem;color:{muted_color};'>{datetime.now().strftime('%B %d, %Y')}</div>
        </div>
        <div style='text-align:right;'>
          {badge(rl)}
          <div style='font-family:"{T["font"]}",monospace;font-size:2.2rem;font-weight:700;
                      color:{rclr};margin-top:6px;'>{rr['readiness_score']:.1f}</div>
          <div style='font-size:.72rem;color:{muted_color};'>Rank #{rnk}/{len(df)}</div>
        </div>
      </div>
      <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px;'>
        {''.join([f"<div style='background:{T['bg3']};border-radius:8px;padding:10px;text-align:center;'><div style='font-size:.6rem;color:{muted_color};text-transform:uppercase;letter-spacing:1px;'>{lbl}</div><div style='font-size:1rem;font-weight:700;color:{clr};font-family:\"{T['font']}\",monospace;'>{val}</div></div>" for lbl,val,clr in [
            ("GDP/Capita",f"${np.expm1(rr['log_gdp_per_capita']):,.0f}",T["accent2"]),
            ("Electricity",f"{rr['electricity_access_pct']:.1f}%",T["accent1"]),
            ("Renewable",f"{rr['renewable_share_pct']:.1f}%",T["accent1"]),
            ("Urban",f"{rr['urban_population_pct']:.1f}%",T["medium"]),
            ("Confidence",f"{rr['prediction_confidence']*100:.0f}%",rclr),
            ("Global Rank",f"#{rnk}/{len(df)}",T["low"]),
        ]])}
      </div>
      <div style='background:{T["bg3"]};border-radius:10px;padding:14px;'>
        <div style='font-size:.65rem;color:{muted_color};text-transform:uppercase;
                    letter-spacing:2px;margin-bottom:8px;'>Executive Summary</div>
        <div style='font-size:.82rem;line-height:1.7;'>
          {rc} — <strong style='color:{rclr};'>{rl} Readiness</strong>,
          Score <strong style='color:{rclr};'>{rr['readiness_score']:.1f}/100</strong>,
          Rank #{rnk}/{len(df)}, Confidence {rr['prediction_confidence']*100:.0f}%.
          {'Strong foundations support renewable transition.' if rl=='High' else
           'Moderate readiness — targeted investments needed.' if rl=='Medium' else
           'Significant investment and reform needed.'}
        </div>
      </div>
    </div>""",unsafe_allow_html=True)
    st.markdown(f'<div class="sh">📊 Feature Profile</div>',unsafe_allow_html=True)
    for col in FEATURE_COLS:
        v=fn[col]; bc3=T["low"] if v<30 else T["medium"] if v<60 else T["high"]
        st.markdown(f"""
        <div style='margin-bottom:8px;'>
          <div style='display:flex;justify-content:space-between;margin-bottom:3px;'>
            <div style='font-size:.78rem;font-weight:600;'>{col.replace("_"," ").replace("log ","").title()}</div>
            <div style='font-family:"{T["font"]}",monospace;font-size:.75rem;color:{bc3};'>{v:.1f}/100</div>
          </div>
          <div style='background:{T["bg"]};border-radius:4px;height:6px;'>
            <div style='width:{v}%;height:6px;border-radius:4px;
                        background:linear-gradient(90deg,{bc3}88,{bc3});'></div>
          </div>
        </div>""",unsafe_allow_html=True)
    report_txt=f"""
================================================================================
  RENEWABLE ENERGY READINESS REPORT — {rc.upper()}
  Generated: {datetime.now().strftime('%B %d, %Y')} | Theme: {chosen_theme}
================================================================================
Country:      {rc}
Score:        {rr['readiness_score']:.1f}/100
Readiness:    {rl}
Global Rank:  #{rnk} of {len(df)}
Confidence:   {rr['prediction_confidence']*100:.0f}%

INDICATORS
GDP/Capita:   ${np.expm1(rr['log_gdp_per_capita']):,.0f}
Electricity:  {rr['electricity_access_pct']:.1f}%
Renewable:    {rr['renewable_share_pct']:.1f}%
Urban Pop:    {rr['urban_population_pct']:.1f}%

FEATURE SCORES (0-100)
{chr(10).join(["  " + c.replace("_"," ").replace("log ","").title().ljust(35) + " " + str(round(fn[c],1)) for c in FEATURE_COLS])}

SUMMARY
{('STRONG: Well-positioned for renewable transition.') if rl=='High' else
 ('DEVELOPING: Moderate readiness with improvement opportunities.') if rl=='Medium' else
 ('EMERGING: Foundational infrastructure investment needed.')}
================================================================================
"""
    d1,d2,d3=st.columns(3)
    with d1:
        st.download_button("⬇️ TXT Report",report_txt,
            f"RE_{rc.replace(' ','_')}.txt","text/plain",use_container_width=True)
    with d2:
        st.download_button("⬇️ CSV Data",pd.DataFrame([rr]).to_csv(index=False),
            f"RE_{rc.replace(' ','_')}.csv","text/csv",use_container_width=True)
    with d3:
        st.download_button("⬇️ All Countries",df.to_csv(index=False),
            f"RE_All.csv","text/csv",use_container_width=True)

# ══ TAB 8 — ANALYTICS ═════════════════════════════════════════════════════
with tab8:
    st.markdown(f'<div class="sh">📊 Deep Analytics</div>',unsafe_allow_html=True)
    a1,a2=st.columns(2)
    with a1:
        fh=px.histogram(fdf,x="readiness_score",color="predicted_label",
                        color_discrete_map=LABEL_COLORS,nbins=30,
                        barmode="overlay",opacity=.8,title="Score Distribution")
        fh.update_layout(**make_layout())
        st.plotly_chart(fh,use_container_width=True)
    with a2:
        lc2=fdf["predicted_label"].value_counts().reset_index()
        lc2.columns=["label","count"]
        fp=px.pie(lc2,values="count",names="label",color="label",
                  color_discrete_map=LABEL_COLORS,hole=.6,title="Breakdown")
        fp.update_layout(paper_bgcolor=T["bg"],font_color=muted_color,
                         title_font_color=T["accent1"],showlegend=False)
        fp.add_annotation(text=f"<b>{len(fdf)}</b><br>countries",
                          x=.5,y=.5,showarrow=False,font_size=14,font_color=text_color)
        st.plotly_chart(fp,use_container_width=True)
    fs=st.selectbox("Feature:",FEATURE_COLS,key="af")
    fb=px.box(fdf,x="predicted_label",y=fs,color="predicted_label",
              color_discrete_map=LABEL_COLORS,
              category_orders={"predicted_label":LABEL_ORDER},
              points="outliers",title=f"{fs} by Label")
    fb.update_layout(**make_layout(),showlegend=False)
    st.plotly_chart(fb,use_container_width=True)
    st.markdown(f'<div class="sh">🤖 Model Performance</div>',unsafe_allow_html=True)
    rf2=rf_pipe.named_steps["clf"]
    fi=pd.DataFrame({"Feature":FEATURE_COLS,"Importance":rf2.feature_importances_}).sort_values("Importance")
    fi2=px.bar(fi,x="Importance",y="Feature",orientation="h",
               color="Importance",color_continuous_scale=[T["bg3"],T["accent1"]],
               title="Feature Importance")
    fi2.update_layout(**make_layout(height=340),coloraxis_showscale=False)
    st.plotly_chart(fi2,use_container_width=True)
    if metrics_df is not None:
        for col,(_,mr) in zip(st.columns(3),metrics_df.iterrows()):
            with col:
                st.markdown(f'<div class="kpi"><div class="kl">{mr["model"].replace("_"," ").title()}</div>'
                            f'<div class="kv" style="color:{T["accent1"]};">{mr["accuracy"]*100:.1f}%</div>'
                            f'<div class="ks">AUC:{mr["auc_roc"]:.3f}</div></div>',
                            unsafe_allow_html=True)
    st.markdown(f'<div class="sh">🔗 Correlations</div>',unsafe_allow_html=True)
    corr=df[FEATURE_COLS].corr().round(2)
    fc2=px.imshow(corr,text_auto=True,aspect="auto",
                  color_continuous_scale=[T["low"],T["bg"],T["high"]],
                  range_color=[-1,1],title="Feature Correlation")
    fc2.update_layout(paper_bgcolor=T["bg"],font_color=muted_color,
                      title_font_color=T["accent1"],height=400)
    st.plotly_chart(fc2,use_container_width=True)
    st.markdown(f'<div class="sh">📋 Full Table</div>',unsafe_allow_html=True)
    sc3=["country_name","readiness_score","predicted_label",
         "prediction_confidence","electricity_access_pct","renewable_share_pct"]
    sc3=[c for c in sc3 if c in fdf.columns]
    st.dataframe(fdf[sc3].sort_values("readiness_score",ascending=False).reset_index(drop=True),
                 use_container_width=True,hide_index=True,height=380)

# ══ TAB 9 — PREDICT NEW ═══════════════════════════════════════════════════
with tab9:
    st.markdown(f'<div class="sh">⚡ Predict Readiness for Custom Scenario</div>',unsafe_allow_html=True)
    st.markdown(f"""
    <div style='color:{muted_color};font-size:.82rem;margin-bottom:20px;
                font-family:"{T["font"]}",monospace;'>
      Adjust any country indicators and get instant ML prediction.
      Every prediction is logged to MongoDB and contributes to model retraining.
    </div>
    """, unsafe_allow_html=True)

    # Progress bar
    pct2 = min(log_count/RETRAIN_TH*100, 100)
    st.markdown(f"""
    <div style='background:{T["bg3"]};border:1px solid {T["border"]};
                border-radius:12px;padding:14px 18px;margin-bottom:20px;'>
      <div style='display:flex;justify-content:space-between;margin-bottom:6px;'>
        <div style='font-size:.75rem;color:{muted_color};font-weight:600;'>🔄 Retraining Progress</div>
        <div style='font-family:"{T["font"]}",monospace;font-size:.78rem;color:{T["accent1"]};font-weight:700;'>
          {log_count}/{RETRAIN_TH} predictions logged
        </div>
      </div>
      <div style='background:{T["bg"]};border-radius:4px;height:6px;'>
        <div style='width:{pct2}%;height:6px;border-radius:4px;background:{T["grad"]};'></div>
      </div>
      <div style='font-size:.68rem;color:{muted_color};margin-top:5px;'>
        Model automatically retrains when {RETRAIN_TH} new predictions are collected.
        Or use Force Retrain button in sidebar anytime.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Input sliders
    pc1,pc2 = st.columns(2)
    with pc1:
        gdp    = st.slider("💰 GDP per Capita (USD)",        100,  120000, 15000,  500)
        urban  = st.slider("🏙️ Urban Population (%)",          0,     100,    55,    1)
        energy = st.slider("⚡ Energy Use per Capita (kgoe)", 100,   12000,  2000,   50)
    with pc2:
        elec   = st.slider("💡 Electricity Access (%)",        0,     100,    80,    1)
        renew  = st.slider("🌱 Renewable Share (%)",           0,     100,    25,    1)

    # Compute features
    log_gdp    = np.log1p(gdp)
    log_energy = np.log1p(energy)
    infra      = (elec + urban) / 2
    max_e      = float(df["energy_use_per_capita"].max()) if "energy_use_per_capita" in df.columns else 12000.0
    pressure   = (energy / max_e) * (1 - renew / 100)

    preview_inp  = pd.DataFrame([[log_gdp, urban, log_energy, elec, renew, pressure, infra]],
                                columns=FEATURE_COLS)
    preview_prob = pipeline.predict_proba(preview_inp)[0]
    le_          = joblib.load("models/label_encoder.pkl")
    preview_lbl  = le_.inverse_transform([pipeline.predict(preview_inp)[0]])[0]
    preview_conf = float(preview_prob.max())
    preview_clr  = LABEL_COLORS[preview_lbl]

    # Live preview card
    st.markdown(f"""
    <div style='background:{T["bg3"]};border:1px solid {preview_clr}44;
                border-radius:14px;padding:16px 20px;margin:16px 0;'>
      <div style='font-size:.65rem;color:{muted_color};text-transform:uppercase;
                  letter-spacing:2px;margin-bottom:6px;'>⚡ Live Preview (updates as you slide)</div>
      <div style='display:flex;justify-content:space-between;align-items:center;'>
        <div style='display:flex;gap:24px;align-items:center;'>
          <div>
            <div style='font-family:"{T["font"]}",monospace;font-size:1.6rem;
                        font-weight:900;color:{preview_clr};'>{preview_lbl.upper()}</div>
            <div style='font-size:.72rem;color:{muted_color};'>Readiness Level</div>
          </div>
          <div>
            <div style='font-family:"{T["font"]}",monospace;font-size:1.4rem;
                        font-weight:700;color:{T["accent2"]};'>{preview_conf*100:.0f}%</div>
            <div style='font-size:.72rem;color:{muted_color};'>Confidence</div>
          </div>
        </div>
        <div style='display:flex;gap:10px;'>
          <div style='text-align:center;background:{T["bg"]};border-radius:8px;padding:8px 12px;'>
            <div style='font-size:.6rem;color:{muted_color};text-transform:uppercase;'>Low</div>
            <div style='font-family:"{T["font"]}",monospace;font-size:.9rem;
                        font-weight:700;color:{T["low"]};'>{preview_prob[0]*100:.0f}%</div>
          </div>
          <div style='text-align:center;background:{T["bg"]};border-radius:8px;padding:8px 12px;'>
            <div style='font-size:.6rem;color:{muted_color};text-transform:uppercase;'>Medium</div>
            <div style='font-family:"{T["font"]}",monospace;font-size:.9rem;
                        font-weight:700;color:{T["medium"]};'>{preview_prob[1]*100:.0f}%</div>
          </div>
          <div style='text-align:center;background:{T["bg"]};border-radius:8px;padding:8px 12px;'>
            <div style='font-size:.6rem;color:{muted_color};text-transform:uppercase;'>High</div>
            <div style='font-family:"{T["font"]}",monospace;font-size:.9rem;
                        font-weight:700;color:{T["high"]};'>{preview_prob[2]*100:.0f}%</div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Confirm button
    if st.button("⚡ CONFIRM & LOG PREDICTION", type="primary"):
        logged_ok = False
        new_count = log_count
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            db     = client[MONGO_DB]
            db["predictions_log"].insert_one({
                "gdp": gdp, "urban": urban, "energy": energy,
                "electricity": elec, "renewable": renew,
                "predicted_label": preview_lbl,
                "confidence": round(preview_conf, 3),
                "timestamp": datetime.now().isoformat(),
            })
            new_count = db["predictions_log"].count_documents({})
            client.close()
            logged_ok = True
        except Exception:
            pass

        st.markdown(f"""
        <div class="card" style="margin-top:16px;border-color:{preview_clr};">
          <div style='display:flex;justify-content:space-between;align-items:center;'>
            <div>
              <div class="kl">PREDICTION CONFIRMED</div>
              <div style='font-family:"{T["font"]}",monospace;font-size:2.5rem;
                          font-weight:900;color:{preview_clr};margin-top:6px;'>
                {preview_lbl.upper()} READINESS
              </div>
            </div>
            <div style='text-align:right;'>
              <div class="kl">Confidence</div>
              <div style='font-family:"{T["font"]}",monospace;font-size:2rem;
                          font-weight:700;color:{T["accent2"]};'>{preview_conf*100:.0f}%</div>
            </div>
          </div>
          <div style='display:flex;gap:16px;margin-top:16px;'>
            <div style='flex:1;background:{T["bg3"]};border-radius:8px;padding:12px;text-align:center;'>
              <div class="kl">Low</div>
              <div style='color:{T["low"]};font-size:1.3rem;font-weight:700;
                          font-family:"{T["font"]}",monospace;'>{preview_prob[0]*100:.0f}%</div>
            </div>
            <div style='flex:1;background:{T["bg3"]};border-radius:8px;padding:12px;text-align:center;'>
              <div class="kl">Medium</div>
              <div style='color:{T["medium"]};font-size:1.3rem;font-weight:700;
                          font-family:"{T["font"]}",monospace;'>{preview_prob[1]*100:.0f}%</div>
            </div>
            <div style='flex:1;background:{T["bg3"]};border-radius:8px;padding:12px;text-align:center;'>
              <div class="kl">High</div>
              <div style='color:{T["high"]};font-size:1.3rem;font-weight:700;
                          font-family:"{T["font"]}",monospace;'>{preview_prob[2]*100:.0f}%</div>
            </div>
          </div>
          <div style='margin-top:14px;padding-top:14px;border-top:1px solid {T["border"]};
                      font-size:.75rem;color:{muted_color};'>
            {'✅ Logged to MongoDB — ' + str(new_count) + '/' + str(RETRAIN_TH) + ' predictions collected'
             if logged_ok else '⚠️ MongoDB unavailable — prediction not logged'}
          </div>
        </div>
        """, unsafe_allow_html=True)

        if logged_ok and new_count >= RETRAIN_TH:
            st.warning(f"🔄 Threshold reached! {new_count} predictions logged. Click 'Force Retrain Now' in sidebar!")

    # Radar for current input
    st.markdown(f'<div class="sh">📡 Your Custom Country Profile</div>', unsafe_allow_html=True)
    inp_norm = {
        "log_gdp_per_capita":        (log_gdp    - df["log_gdp_per_capita"].min())        / (df["log_gdp_per_capita"].max()        - df["log_gdp_per_capita"].min()        + 1e-9) * 100,
        "urban_population_pct":      (urban      - df["urban_population_pct"].min())      / (df["urban_population_pct"].max()      - df["urban_population_pct"].min()      + 1e-9) * 100,
        "log_energy_use_per_capita": (log_energy - df["log_energy_use_per_capita"].min()) / (df["log_energy_use_per_capita"].max() - df["log_energy_use_per_capita"].min() + 1e-9) * 100,
        "electricity_access_pct":    (elec       - df["electricity_access_pct"].min())    / (df["electricity_access_pct"].max()    - df["electricity_access_pct"].min()    + 1e-9) * 100,
        "renewable_share_pct":       (renew      - df["renewable_share_pct"].min())       / (df["renewable_share_pct"].max()       - df["renewable_share_pct"].min()       + 1e-9) * 100,
        "energy_pressure_index":     (pressure   - df["energy_pressure_index"].min())     / (df["energy_pressure_index"].max()     - df["energy_pressure_index"].min()     + 1e-9) * 100,
        "infrastructure_score":      (infra      - df["infrastructure_score"].min())      / (df["infrastructure_score"].max()      - df["infrastructure_score"].min()      + 1e-9) * 100,
    }
    cats_p = [c.replace("_"," ").replace("log ","").title() for c in FEATURE_COLS]
    vals_p = [float(inp_norm[c]) for c in FEATURE_COLS]

    fig_pr = go.Figure(go.Scatterpolar(
        r=vals_p+[vals_p[0]], theta=cats_p+[cats_p[0]],
        fill="toself",
        fillcolor=LABEL_FILL[preview_lbl],
        line=dict(color=preview_clr, width=2),
        name="Your Input",
    ))
    fig_pr.update_layout(
        polar=dict(
            bgcolor=T["bg2"],
            radialaxis=dict(visible=True, range=[0,100], gridcolor=T["border"]),
            angularaxis=dict(gridcolor=T["border"], tickfont_color=muted_color),
        ),
        paper_bgcolor=T["bg"],
        height=400, showlegend=False,
        title=dict(text="Custom Country Feature Radar", font_color=T["accent1"]),
    )
    st.plotly_chart(fig_pr, use_container_width=True)

    # Full table
    st.markdown(f'<div class="sh">📋 Compare with All Countries</div>', unsafe_allow_html=True)
    sc4=["country_name","readiness_score","predicted_label",
         "prediction_confidence","electricity_access_pct","renewable_share_pct"]
    sc4=[c for c in sc4 if c in fdf.columns]
    st.dataframe(
        fdf[sc4].sort_values("readiness_score",ascending=False).reset_index(drop=True),
        use_container_width=True, hide_index=True, height=380,
    )