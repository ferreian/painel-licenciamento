"""
pages/3_Detalhe_por_Concorrente.py
Um material Stine contra um concorrente específico, região a região.
Tabela detalhada + barras de % de vitórias por região, coloridas pela classe.
"""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.theme import aplicar_tema, page_header, secao_titulo
from utils.loader import carregar_base, rotulo
from utils.h2h_ui import (classificar_h2h, ag_table_h2h, to_excel, COR_FUNDO,
                          como_ler, chart_pergunta, chart_resposta,
                          legenda_classes_chips, LEGENDA_CLASSES_MD)

st.set_page_config(page_title="Detalhe por Concorrente · Licenciamento",
                   page_icon="🔍", layout="wide", initial_sidebar_state="expanded")
aplicar_tema()
st.markdown("<style>.jaum-header img { height: 110px !important; }</style>", unsafe_allow_html=True)

base = carregar_base()
if not base["ok"]:
    st.error(f"❌ Não foi possível carregar a base: {base['erro']}")
    st.stop()
df = base["df"]

page_header("Detalhe por Concorrente",
            "Material Stine × um concorrente, região a região.",
            imagem="Researchers-pana.png")

# ── Seleção do par ───────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    material_sel = st.selectbox("Material (Stine)", sorted(df["material"].unique()))
checks_disp = sorted(df[df["material"] == material_sel]["check"].unique())
with c2:
    check_sel = st.selectbox("Concorrente", checks_disp)

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
    excluir_agg = st.checkbox("Mostrar só microrregiões", value=True)
    st.caption("Oculta os níveis agregados (Macro/Micro 'Todas' e 'Agregação'), "
               "deixando só as microrregiões individuais.")

    st.divider()
    st.markdown('<p style="font-size:12px;font-weight:700;color:#1E8449;margin:0 0 6px;">'
                '2 · Confiabilidade</p>', unsafe_allow_html=True)
    n_min = st.number_input("Nº mínimo de comparações", min_value=1, value=3, step=1)

par = df[(df["material"] == material_sel) & (df["check"] == check_sel)
         & (df["safra"] == safra_sel)].copy()
par = par[par["n_comp"] >= n_min]
if excluir_agg:
    par = par[(par["macro"] != "ALL") & (par["macro"] != "Aggregation_analysis") &
              (par["micro"] != "ALL")]

if par.empty:
    st.warning("⚠️ Nenhum confronto para esse par com os filtros atuais.")
    st.stop()

par["Classe"] = par["wr"].apply(lambda w: classificar_h2h(w)[0])
par["regiao"] = "M" + par["macro"].astype(str) + " · " + par["micro"].astype(str)

# ── Cabeçalho do par ─────────────────────────────────────────────────────────
gm_h = par["rm"].mean()
gm_txt = f"GM {gm_h:.1f}" if pd.notna(gm_h) else ""
wr_pond = (par["wr"] * par["n_comp"]).sum() / par["n_comp"].sum()
yg_pond = (par["yg_pct"] * par["n_comp"]).sum() / par["n_comp"].sum()
classe_geral = classificar_h2h(wr_pond)[0]

st.markdown(
    f'<div style="margin:0.5rem 0 0.6rem;">'
    f'<h2 style="font-size:1.7rem;font-weight:700;color:#1A1A1A;margin:0;line-height:1.2;">'
    f'<span style="color:#27AE60;">{material_sel}</span>'
    f'<span style="color:#6B7280;font-weight:500;"> vs </span>'
    f'<span style="color:#374151;">{check_sel}</span></h2>'
    f'<p style="font-size:14px;color:#6B7280;margin:4px 0 0;">'
    f'Safra {rotulo(safra_sel)} · {len(par)} recortes regionais · {gm_txt}</p></div>',
    unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("% de Vitórias (ponderado)", f"{wr_pond:.0f}%")
m2.metric("Ganho (ponderado)", f"{yg_pond:+.1f}%")
m3.metric("Classe geral", classe_geral)
m4.metric("Total de comparações", int(par["n_comp"].sum()))

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Leitura ──────────────────────────────────────────────────────────────────
secao_titulo("LEITURA", "Como interpretar esta página")
st.markdown(
    f'<p style="font-size:16px;color:#374151;line-height:1.7;margin:0 0 10px;">'
    f'Aqui o material <b>{material_sel}</b> é comparado <b>só com {check_sel}</b>, '
    f'em cada microrregião onde os dois foram avaliados. As métricas no topo são a '
    f'média ponderada pelo nº de comparações. A cor segue a faixa de % de vitórias:</p>',
    unsafe_allow_html=True)
legenda_classes_chips()

# ── Barras de % de vitórias por região (pergunta → resposta → gráfico) ───────
n_reg = len(par)
n_vence = int((par["wr"] > 55).sum())
melhor = par.loc[par["wr"].idxmax()]
pior = par.loc[par["wr"].idxmin()]

tit, btn = st.columns([3, 1])
with tit:
    secao_titulo("POR REGIÃO", "% de vitórias por microrregião")
    como_ler(
        "**Cada barra** é uma microrregião. O valor é o **% de vitórias** do material "
        "sobre este concorrente ali (entre parênteses, o nº de comparações).\n\n"
        "A linha tracejada marca **50%**. Cores:\n\n" + LEGENDA_CLASSES_MD)

chart_pergunta("Em quais regiões o material vence este concorrente?")
chart_resposta(
    f"Vence em <b>{n_vence} de {n_reg}</b> microrregiões (> 55% de vitórias). "
    f"Melhor desempenho em <b>{melhor['regiao']}</b> (<b>{melhor['wr']:.0f}%</b>)" +
    (f"; menor em <b>{pior['regiao']}</b> ({pior['wr']:.0f}%)." if n_reg > 1 else "."))

pdf = par.sort_values("wr", ascending=True)
cores = [COR_FUNDO[classificar_h2h(w)[0]] for w in pdf["wr"]]
fig = go.Figure(go.Bar(
    x=pdf["wr"], y=pdf["regiao"], orientation="h",
    marker=dict(color=cores, line=dict(color="#888", width=0.5)),
    text=[f"{w:.0f}% ({int(n)})" for w, n in zip(pdf["wr"], pdf["n_comp"])],
    textposition="outside", textfont=dict(size=13, color="#000000"),
    hovertemplate="%{y}<br>% de vitórias: %{x:.0f}%<extra></extra>",
))
fig.add_vline(x=50, line_width=1, line_dash="dash", line_color="#9CA3AF")
fig.update_layout(
    height=max(320, 30 * len(pdf)), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
    margin=dict(t=10, b=10, l=10, r=70),
    xaxis_title="% de vitórias  ·  (nº de comparações)", xaxis_range=[0, 112],
    font=dict(family="Helvetica Neue, sans-serif", color="#000000", size=14),
)
fig.update_xaxes(gridcolor="#EEE", title_font=dict(size=15, color="#000000"),
                 tickfont=dict(size=13, color="#000000"))
fig.update_yaxes(tickfont=dict(size=13, color="#000000"))
st.plotly_chart(fig, use_container_width=True)

# ── Tabela detalhada ────────────────────────────────────────────────────────
secao_titulo("DETALHE", "Confronto região a região")
tab = pd.DataFrame({
    "Safra":             par["safra"].apply(rotulo),
    "Macro":             par["macro"].apply(rotulo),
    "Micro":             par["micro"].apply(rotulo),
    "sc/ha Material":    par["sc_head"].round(1),
    "sc/ha Concorrente": par["sc_check"].round(1),
    "Ganho (sc/ha)":     par["yg_sc"].round(1),
    "Ganho (%)":         par["yg_pct"].round(1),
    "% de Vitórias":     par["wr"].round(1),
    "Nº Comp.":          par["n_comp"].astype(int),
    "P-Valor":           par["p_valor"].round(3),
    "Classe":            par["Classe"],
}).sort_values(["Macro", "Micro"]).reset_index(drop=True)

ag_table_h2h(tab, height=min(620, int(36 + 33 * len(tab) + 20)), key="ag_par")
st.download_button("⬇️ Exportar Excel", data=to_excel(tab),
                   file_name=f"detalhe_{material_sel}_vs_{check_sel}.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
