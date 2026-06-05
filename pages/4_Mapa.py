"""
pages/4_Mapa.py — Mapa coroplético por região (Macro/Micro)
Pinta cada município pela CLASSE de performance do material Stine na região (REC)
a que ele pertence, usando a base de-para município → macro/micro.

ARQUIVOS NECESSÁRIOS
--------------------
- data/geo/municipios_br.json                      (malha municipal — já no projeto)
- data/base_municipios_regioes_soja_milho.xlsx     (de-para município → macro/microSoja)

Como o REC casa com o H2H: o 'microSoja' (ex.: 'REC 201') corresponde ao prefixo de
3 dígitos do 'Micro' do H2H ('201Baixo' → 201). Alto/Baixo caem no mesmo REC.
"""

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
import plotly.graph_objects as go

from utils.theme import aplicar_tema, page_header, secao_titulo
from utils.loader import carregar_base, rotulo, faixa_rm, FAIXAS_GM_ORDEM
from utils.h2h_ui import (classificar_h2h, COR_FUNDO, como_ler, chart_pergunta,
                          chart_resposta, legenda_classes_chips, LEGENDA_CLASSES_MD)

st.set_page_config(page_title="Mapa · Licenciamento",
                   page_icon="🗺️", layout="wide", initial_sidebar_state="expanded")
aplicar_tema()
st.markdown("<style>.jaum-header img { height: 110px !important; }</style>", unsafe_allow_html=True)

BASE_DIR = Path(__file__).parent.parent
CLASSE_Z = {"Restrito": 0, "Competitivo": 1, "Superior": 2, "Alta Performance": 3}
MACRO_ROMANO = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}


REMOTE_GEOJSON_URLS = [
    "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-100-mun.json",
    "https://raw.githubusercontent.com/luizpedropisteli/brazil-geojson/main/brazil_geo.json",
]


def _normaliza_features(gj):
    if not gj or not gj.get("features"):
        return None
    for ft in gj["features"]:
        pr = ft.get("properties", {})
        cod = (pr.get("ibge7") or pr.get("code_muni") or pr.get("geocodigo") or
               pr.get("id") or pr.get("CD_MUN") or pr.get("GEOCODIGO") or pr.get("ibge"))
        try:
            pr["ibge7"] = str(int(float(cod))).zfill(7)
        except (TypeError, ValueError):
            pr["ibge7"] = ""
        ft["properties"] = pr
    return gj


@st.cache_data(show_spinner="Carregando malha municipal...")
def carregar_geo():
    # 1) arquivo local, se válido
    p = BASE_DIR / "data" / "geo" / "municipios_br.json"
    if p.exists() and p.stat().st_size > 1000:
        try:
            with open(p, encoding="utf-8") as f:
                g = _normaliza_features(json.load(f))
            if g and len(g["features"]) > 500:
                return g
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
            pass
    # 2) fallback: baixa a malha online (precisa de internet)
    for url in REMOTE_GEOJSON_URLS:
        try:
            r = requests.get(url, timeout=40)
            if r.status_code == 200:
                g = _normaliza_features(r.json())
                if g and len(g["features"]) > 500:
                    return g
        except Exception:
            continue
    return None


@st.cache_data(show_spinner=False)
def carregar_depara():
    candidatos = [
        BASE_DIR / "data" / "geo" / "base_municipios_regioes_soja_milho.xlsx",
        BASE_DIR / "data" / "base_municipios_regioes_soja_milho.xlsx",
        BASE_DIR / "config" / "base_municipios_regioes_soja_milho.xlsx",
    ]
    p = next((c for c in candidatos if c.exists()), None)
    if p is None:
        return None
    d = pd.read_excel(p, usecols=["cidade", "siglaEstado", "ibge", "latitude",
                                  "longitude", "macroSoja", "microSoja"])
    d["ibge7"] = d["ibge"].apply(lambda v: str(int(float(v))).zfill(7) if pd.notna(v) else "")
    d["rec"] = d["microSoja"].astype(str).str.extract(r"(\d{3})")
    d["macro_digit"] = d["macroSoja"].map(
        {"MACRO I": "1", "MACRO II": "2", "MACRO III": "3", "MACRO IV": "4", "MACRO V": "5"})
    return d


@st.cache_data(show_spinner=False)
def carregar_estados():
    urls = [
        "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        "https://raw.githubusercontent.com/giuliano-macedo/geodata-br-states/main/geojson/br_states.json",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                gj = r.json()
                if gj.get("features"):
                    for i, ft in enumerate(gj["features"]):
                        ft["properties"]["est_id"] = str(i)
                    return gj
        except Exception:
            continue
    return None


base = carregar_base()
if not base["ok"]:
    st.error(f"❌ Não foi possível carregar a base: {base['erro']}")
    st.stop()
df = base["df"]
geo = carregar_geo()
dep = carregar_depara()
estados = carregar_estados()

page_header("Mapa por Região",
            "Performance dos materiais Stine pintada sobre o mapa do Brasil.",
            imagem="Business_mission-amico.png")

if geo is None:
    st.error("❌ Não consegui carregar a malha municipal. O arquivo local "
             "**data/geo/municipios_br.json** está vazio/inválido e o download online "
             "também falhou (sem internet?). Substitua o arquivo local por um GeoJSON "
             "de municípios válido e recarregue.")
    st.stop()
if dep is None:
    st.error("❌ Base de-para não encontrada. Coloque o arquivo "
             "**base_municipios_regioes_soja_milho.xlsx** em **data/** ou **data/geo/** "
             "do projeto.")
    st.stop()

# ── Filtros (hierarquia) ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6B7280;text-transform:uppercase;'
        'letter-spacing:0.05em;padding:0.5rem 0.5rem 0;">Filtros</p>', unsafe_allow_html=True)

    st.markdown('<p style="font-size:12px;font-weight:700;color:#1E8449;margin:8px 0 6px;">'
                '1 · Recorte</p>', unsafe_allow_html=True)
    safras = sorted(df["safra"].unique().tolist())
    safra_sel = st.selectbox("Safra", safras, format_func=rotulo,
                             index=safras.index("2025") if "2025" in safras else 0)

    st.divider()
    st.markdown('<p style="font-size:12px;font-weight:700;color:#1E8449;margin:0 0 6px;">'
                '2 · Concorrentes</p>', unsafe_allow_html=True)
    bandas_gm = [f for f in FAIXAS_GM_ORDEM if f in set(df["rm"].dropna().apply(faixa_rm))]
    faixa_gm_sel = st.selectbox("Faixa de GM", ["Todas"] + bandas_gm)
    n_min = st.number_input("Nº mínimo de comparações", min_value=1, value=3, step=1)

# ── Controles principais ─────────────────────────────────────────────────────
c1, c2, c3 = st.columns([2, 2, 2])
with c1:
    material_sel = st.selectbox("Material (Stine)", sorted(df["material"].unique()))
with c2:
    nivel = st.selectbox("Nível", ["Micro", "Macro"])
with c3:
    metrica = st.selectbox("Métrica no rótulo", ["% de Vitórias (média)", "Ganho médio (%)"])
is_wr = metrica.startswith("%")
key = "rec" if nivel == "Micro" else "macro_digit"

# ── Performance do material por região ───────────────────────────────────────
real = df[(df["material"] == material_sel) & (df["safra"] == safra_sel) &
          (df["macro"].isin(["1", "2", "3", "4", "5"])) &
          (~df["micro"].astype(str).str.contains("_")) & (df["micro"] != "ALL")].copy()
real = real[real["n_comp"] >= n_min]
if faixa_gm_sel != "Todas":
    real = real[real["rm"].apply(faixa_rm) == faixa_gm_sel]
real["rec"] = real["micro"].astype(str).str.extract(r"(\d{3})")
real["macro_digit"] = real["macro"].astype(str)
real = real.dropna(subset=["rec"])

if real.empty:
    st.warning("⚠️ Sem dados de microrregião para esse material/safra/filtros.")
    st.stop()

real["_wr_w"] = real["wr"] * real["n_comp"]
real["_yg_w"] = real["yg_pct"] * real["n_comp"]
perf = real.groupby(key, as_index=False).agg(
    wr_w=("_wr_w", "sum"), yg_w=("_yg_w", "sum"),
    n_sum=("n_comp", "sum"), n_ck=("check", "nunique"))
perf["wr"] = perf["wr_w"] / perf["n_sum"]
perf["yg"] = perf["yg_w"] / perf["n_sum"]
perf["classe"] = perf["wr"].apply(lambda w: classificar_h2h(w)[0])
perf["z"] = perf["classe"].map(CLASSE_Z)

# ── Junta com municípios ─────────────────────────────────────────────────────
muni = dep.merge(perf, on=key, how="left")
muni["zmap"] = muni["z"].fillna(-1)

# ── Leitura ──────────────────────────────────────────────────────────────────
secao_titulo("LEITURA", "Como interpretar este mapa")
st.markdown(
    f'<p style="font-size:16px;color:#374151;line-height:1.7;margin:0 0 10px;">'
    f'Cada município é pintado pela <b>classe de desempenho</b> do <b>{material_sel}</b> '
    f'na região ({"microrregião / REC" if nivel == "Micro" else "macrorregião"}) a que '
    f'pertence. Regiões sem dado para este material ficam em cinza. As cores seguem a '
    f'régua de % de vitórias:</p>', unsafe_allow_html=True)
legenda_classes_chips()

# ── Mapa (pergunta → resposta → gráfico) ─────────────────────────────────────
secao_titulo("MAPA", f"{material_sel} · por {nivel} · Safra {rotulo(safra_sel)}")
como_ler(
    "**Coroplético**: cada município recebe a cor da classe de desempenho da sua "
    "região. Use **'Nível'** para alternar entre macro e microrregião e **'Métrica no "
    "rótulo'** para escolher o número exibido em cada região.\n\n" + LEGENDA_CLASSES_MD +
    "\nRegiões em **cinza** não têm dado deste material no recorte. Passe o mouse para "
    "ver os números.")

melhor = perf.loc[perf["wr"].idxmax()]
reg_lbl = (f"REC {melhor['rec']}" if nivel == "Micro"
           else f"MACRO {MACRO_ROMANO.get(melhor['macro_digit'], melhor['macro_digit'])}")
n_vence = int((perf["wr"] > 55).sum())
chart_pergunta("Onde o material é mais forte no mapa?")
chart_resposta(
    f"Entre as <b>{len(perf)}</b> regiões com dado, o melhor desempenho é em "
    f"<b>{reg_lbl}</b> ({melhor['wr']:.0f}% de vitórias, ganho {melhor['yg']:+.1f}%). "
    f"O material vence (acima de 55%) em <b>{n_vence}</b> delas.")

# Hover por município
def _hover(r):
    if pd.isna(r["wr"]):
        return f"{r['cidade']} ({r['siglaEstado']})<br>Sem dado deste material"
    reg = (f"REC {r['rec']}" if nivel == "Micro"
           else f"MACRO {MACRO_ROMANO.get(r['macro_digit'], r['macro_digit'])}")
    return (f"{r['cidade']} ({r['siglaEstado']}) · {reg}<br>"
            f"% de Vitórias: {r['wr']:.0f}%<br>Ganho: {r['yg']:+.1f}%")
muni["hover"] = muni.apply(_hover, axis=1)

com = muni[muni["wr"].notna()]
sem = muni[muni["wr"].isna()]

fig = go.Figure()

# Municípios SEM dado: fundo clarinho + borda visível (contorno do município)
if not sem.empty:
    fig.add_trace(go.Choropleth(
        geojson=geo, locations=sem["ibge7"], z=[0] * len(sem),
        featureidkey="properties.ibge7",
        colorscale=[[0, "#F4F4F4"], [1, "#F4F4F4"]], zmin=0, zmax=1, showscale=False,
        marker_line_color="#999999", marker_line_width=0.3,
        text=sem["hover"], hoverinfo="text"))

# Municípios COM dado: cor da classe
escala4 = [
    [0.00, "#FF0000"], [0.25, "#FF0000"],   # 0 Restrito
    [0.25, "#FFFF00"], [0.50, "#FFFF00"],   # 1 Competitivo
    [0.50, "#87CEFF"], [0.75, "#87CEFF"],   # 2 Superior
    [0.75, "#90EE90"], [1.00, "#90EE90"],   # 3 Alta Performance
]
fig.add_trace(go.Choropleth(
    geojson=geo, locations=com["ibge7"], z=com["z"],
    featureidkey="properties.ibge7",
    colorscale=escala4, zmin=-0.5, zmax=3.5, showscale=False,
    marker_line_color="#999999", marker_line_width=0.3,
    text=com["hover"], hoverinfo="text"))

# Contorno dos ESTADOS: linha preta grossa por cima dos municípios
if estados:
    est_ids = [f["properties"]["est_id"] for f in estados["features"]]
    fig.add_trace(go.Choropleth(
        geojson=estados, locations=est_ids, z=[0] * len(est_ids),
        featureidkey="properties.est_id",
        colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
        zmin=0, zmax=1, showscale=False,
        marker_line_color="#4A4A4A", marker_line_width=1.3,
        hoverinfo="skip"))

# Sigla da UF no centroide de cada estado
uf_cent = dep.dropna(subset=["latitude", "longitude"]).groupby("siglaEstado").agg(
    lat=("latitude", "mean"), lon=("longitude", "mean")).reset_index()
for _, u in uf_cent.iterrows():
    fig.add_trace(go.Scattergeo(
        lat=[u["lat"]], lon=[u["lon"]], mode="text",
        text=[f"<b>{u['siglaEstado']}</b>"],
        textfont=dict(size=12, color="#555555", family="Helvetica Neue, sans-serif"),
        hoverinfo="skip", showlegend=False))

# Rótulos por região (no centroide médio das cidades da região com dado)
reg_lab = (muni.dropna(subset=["wr"]).groupby(key)
           .agg(lat=("latitude", "mean"), lon=("longitude", "mean"),
                wr=("wr", "first"), yg=("yg", "first")).reset_index())
for _, r in reg_lab.iterrows():
    abbr = (f"REC {r[key]}" if nivel == "Micro"
            else f"M{r[key]}")
    val = f"{r['wr']:.0f}%" if is_wr else f"{r['yg']:+.1f}%"
    fig.add_trace(go.Scattergeo(
        lat=[r["lat"]], lon=[r["lon"]], mode="text",
        text=[f"<b>{abbr}</b><br>{val}"],
        textfont=dict(size=13, color="#1A1A1A", family="Helvetica Neue, sans-serif"),
        hoverinfo="skip", showlegend=False))

fig.update_geos(fitbounds="locations", visible=False, bgcolor="#FFFFFF",
                showcountries=False, showsubunits=True, subunitcolor="#D8D8D8")
fig.update_layout(height=880, margin=dict(t=0, b=0, l=0, r=0),
                  paper_bgcolor="#FFFFFF")
st.plotly_chart(fig, use_container_width=True)

st.caption(f"{len(perf)} regiões com dado · nível {nivel}.")
sem_muni = sorted(set(perf[key].dropna()) - set(dep[key].dropna()))
if sem_muni:
    rotulos = [(f"REC {x}" if nivel == "Micro" else f"MACRO {MACRO_ROMANO.get(x, x)}")
               for x in sem_muni]
    st.info("Regiões com dado mas sem município na base de-para (não pintadas): "
            + ", ".join(rotulos))
