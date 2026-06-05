"""
pages/2_Visao_por_Material.py
Visão comparativa dos 3 materiais Stine lado a lado, no mesmo recorte:
distribuição por classe (donut por material), barras de classes e tabela consolidada.
"""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.theme import aplicar_tema, page_header, secao_titulo
from utils.loader import carregar_base, faixa_rm, rotulo, FAIXAS_GM_ORDEM
from utils.h2h_ui import (classificar_h2h, donut_classes, tabela_resumo_html, to_excel,
                          COR_FUNDO, como_ler, chart_pergunta, chart_resposta,
                          legenda_classes_chips, LEGENDA_CLASSES_MD)

st.set_page_config(page_title="Visão por Material · Licenciamento",
                   page_icon="📊", layout="wide", initial_sidebar_state="expanded")
aplicar_tema()
st.markdown("<style>.jaum-header img { height: 110px !important; }</style>", unsafe_allow_html=True)

base = carregar_base()
if not base["ok"]:
    st.error(f"❌ Não foi possível carregar a base: {base['erro']}")
    st.stop()
df = base["df"]

page_header("Visão por Material",
            "Os três materiais Stine lado a lado, no mesmo recorte.",
            imagem="Design_stats-rafiki.png")

# ── Filtros (hierarquia: Recorte encadeado + Concorrentes) ───────────────────
with st.sidebar:
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6B7280;text-transform:uppercase;'
        'letter-spacing:0.05em;padding:0.5rem 0.5rem 0;">Filtros</p>', unsafe_allow_html=True)

    st.markdown('<p style="font-size:12px;font-weight:700;color:#1E8449;margin:8px 0 0;">'
                '1 · Recorte</p>'
                '<p style="font-size:11px;color:#6B7280;margin:0 0 6px;">'
                'Encadeado: a safra define os macros; o macro define os micros.</p>',
                unsafe_allow_html=True)
    safras = sorted(df["safra"].unique().tolist())
    safra_sel = st.selectbox("Safra", safras, format_func=rotulo,
                             index=safras.index("2025") if "2025" in safras else 0)
    df_s = df[df["safra"] == safra_sel]
    macros = sorted(df_s["macro"].unique().tolist())
    macro_sel = st.selectbox(
        "Macro", macros, format_func=rotulo,
        index=macros.index("ALL") if "ALL" in macros else 0)
    st.caption("Macro 1–5 = regiões geográficas. 'Agregação' combina microrregiões "
               "(vizinhas, ex. 202+206, ou com o ano anterior 'PY').")
    df_sm = df_s[df_s["macro"] == macro_sel]
    micros = sorted(df_sm["micro"].unique().tolist())
    micro_sel = st.selectbox("Micro", micros, format_func=rotulo,
                             index=micros.index("ALL") if "ALL" in micros else 0)

    st.divider()
    st.markdown('<p style="font-size:12px;font-weight:700;color:#1E8449;margin:0 0 6px;">'
                '2 · Concorrentes</p>', unsafe_allow_html=True)
    bandas_gm = [f for f in FAIXAS_GM_ORDEM
                 if f in set(df["rm"].dropna().apply(faixa_rm))]
    faixa_gm_sel = st.selectbox("Faixa de GM", ["Todas"] + bandas_gm)
    n_min = st.number_input("Nº mínimo de comparações", min_value=1, value=3, step=1)
    p_sig = st.checkbox("Só diferenças significativas (p < 0,05)", value=False)

# ── Filtragem ────────────────────────────────────────────────────────────────
sub = df[(df["safra"] == safra_sel) & (df["macro"] == macro_sel) &
         (df["micro"] == micro_sel)].copy()
sub = sub[sub["n_comp"] >= n_min]
if faixa_gm_sel != "Todas":
    sub = sub[sub["rm"].apply(faixa_rm) == faixa_gm_sel]
if p_sig:
    sub = sub[sub["p_valor"] < 0.05]

if sub.empty:
    st.warning("⚠️ Nenhum confronto para os filtros selecionados.")
    st.stop()

sub["Classe"] = sub["wr"].apply(lambda w: classificar_h2h(w)[0])

st.markdown(f'<p style="font-size:14px;color:#6B7280;margin:0.2rem 0 0.8rem;">'
            f'Safra {rotulo(safra_sel)} · Macro {rotulo(macro_sel)} · Micro {rotulo(micro_sel)}</p>',
            unsafe_allow_html=True)

materiais = sorted(sub["material"].unique().tolist())
COR_MAT = {materiais[i]: c for i, c in enumerate(["#27AE60", "#1E8449", "#145A32"])}

# ── Estatísticas por material ────────────────────────────────────────────────
stats = {}
for mat in materiais:
    g = sub[sub["material"] == mat]
    contagem = g["Classe"].value_counts().to_dict()
    stats[mat] = {
        "g": g, "contagem": contagem,
        "wr": g["wr"].mean(), "yg": g["yg_pct"].mean(),
        "venc": int((g["wr"] > 55).sum()),
        "supplus": contagem.get("Alta Performance", 0) + contagem.get("Superior", 0),
        "n": len(g),
        "gm": g["rm"].mean() if g["rm"].notna().any() else None,
    }

# Ranking por % em Superior+Alta
def pct_sup(m):
    return stats[m]["supplus"] / stats[m]["n"] * 100 if stats[m]["n"] else 0
ordenados = sorted(materiais, key=pct_sup, reverse=True)
lider = ordenados[0]

# ── Leitura ──────────────────────────────────────────────────────────────────
secao_titulo("LEITURA", "Como interpretar esta página")
st.markdown(
    '<p style="font-size:16px;color:#374151;line-height:1.7;margin:0 0 10px;">'
    'Cada material Stine é avaliado contra o mesmo conjunto de concorrentes, no recorte '
    'selecionado. Os <b>donuts</b> mostram, para cada material, quantos concorrentes '
    'caem em cada faixa de % de vitórias; as <b>barras</b> e a <b>tabela</b> comparam '
    'os três lado a lado. As classes seguem a faixa de % de vitórias:</p>',
    unsafe_allow_html=True)
legenda_classes_chips()

# ── Distribuição por material (pergunta → resposta → donuts) ─────────────────
tit, btn = st.columns([3, 1])
with tit:
    secao_titulo("DISTRIBUIÇÃO", "Por material")
    como_ler(
        "**Cada donut** é um material Stine. As fatias são a quantidade de "
        "concorrentes em cada faixa de % de vitórias.\n\n"
        + LEGENDA_CLASSES_MD +
        "\nO número no centro é o total de concorrentes avaliados naquele material.")

chart_pergunta("Qual material é superior contra a maior parte dos concorrentes?")
resp = " · ".join(f"<b>{m}</b> {pct_sup(m):.0f}%" for m in ordenados)
chart_resposta(
    f"Considerando Superior + Alta Performance: {resp}. "
    f"O <b>{lider}</b> é o mais consistente neste recorte "
    f"(<b>{stats[lider]['supplus']} de {stats[lider]['n']}</b> concorrentes).")

cols = st.columns(len(materiais), gap="large")
for col, mat in zip(cols, materiais):
    s = stats[mat]
    gm_txt = f"GM {s['gm']:.1f}" if s["gm"] is not None else ""
    with col:
        st.markdown(
            f'<div style="border:1px solid #E5E7EB;border-radius:12px;padding:14px 16px;'
            f'background:#FFFFFF;box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
            f'<p style="font-size:1.85rem;font-weight:700;color:{COR_MAT[mat]};margin:0;">{mat}</p>'
            f'<p style="font-size:16px;color:#1A1A1A;margin:3px 0 12px;">{gm_txt} · '
            f'{s["n"]} concorrentes</p>'
            f'<div style="display:flex;gap:14px;">'
            f'<div><p style="font-size:14px;color:#1A1A1A;margin:0;">Vitórias (média)</p>'
            f'<p style="font-size:1.6rem;font-weight:700;color:#1A1A1A;margin:0;">{s["wr"]:.0f}%</p></div>'
            f'<div><p style="font-size:14px;color:#1A1A1A;margin:0;">Ganho médio</p>'
            f'<p style="font-size:1.6rem;font-weight:700;color:#1A1A1A;margin:0;">{s["yg"]:+.1f}%</p></div>'
            f'<div><p style="font-size:14px;color:#1A1A1A;margin:0;">Vencidos (&gt;55%)</p>'
            f'<p style="font-size:1.6rem;font-weight:700;color:#27AE60;margin:0;">{s["venc"]}</p></div>'
            f'</div></div>', unsafe_allow_html=True)
        st.plotly_chart(donut_classes(s["contagem"]), use_container_width=True,
                        key=f"donut_{mat}")

# ── Barras empilhadas (pergunta → resposta → gráfico) ────────────────────────
classes_ord = ["Alta Performance", "Superior", "Competitivo", "Restrito"]
contagem_classe = {c: {m: int(((sub["material"] == m) & (sub["Classe"] == c)).sum())
                       for m in materiais} for c in classes_ord}
lider_alta = max(materiais, key=lambda m: contagem_classe["Alta Performance"][m])

tit2, btn2 = st.columns([3, 1])
with tit2:
    secao_titulo("COMPARATIVO", "Classes por material")
    como_ler(
        "**Barra 100% empilhada**: cada material vira uma barra do mesmo tamanho, "
        "dividida pela **proporção** de concorrentes em cada faixa de % de vitórias. "
        "Assim dá para comparar os materiais mesmo tendo totais diferentes — quanto "
        "mais verde e azul, melhor. O número dentro de cada faixa é a fatia de "
        "concorrentes ali (a barra inteira soma 100%).\n\n" + LEGENDA_CLASSES_MD)

chart_pergunta("Quem tem mais concorrentes em Alta Performance?")
chart_resposta(
    f"O <b>{lider_alta}</b> tem o maior número de concorrentes em <b>Alta Performance</b> "
    f"(<b>{contagem_classe['Alta Performance'][lider_alta]}</b>), ou seja, vence em mais de "
    f"75% dos locais contra esses concorrentes.")

fig = go.Figure()
totais = {m: stats[m]["n"] for m in materiais}
ordem_y = ordenados  # melhor no topo
for classe in classes_ord:                       # verde → azul → amarelo → vermelho
    counts = [contagem_classe[classe][m] for m in ordem_y]
    pcts = [(c / totais[m] * 100) if totais[m] else 0 for c, m in zip(counts, ordem_y)]
    fig.add_bar(
        name=classe, y=ordem_y, x=counts, orientation="h",
        marker_color=COR_FUNDO[classe],
        text=[f"{p:.0f}%" if p > 0 else "" for p in pcts],
        textposition="inside", insidetextanchor="middle",
        textfont=dict(color="#1A1A1A", size=12),
        customdata=counts,
        hovertemplate="%{y} · " + classe + ": %{customdata} concorrentes<extra></extra>",
    )
fig.update_layout(
    barmode="stack", barnorm="percent", height=300,
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
    margin=dict(t=10, b=10, l=10, r=10),
    uniformtext=dict(minsize=9, mode="show"),   # força o rótulo a sempre aparecer
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center",
                traceorder="normal", font=dict(size=13, color="#1A1A1A")),
    font=dict(family="Helvetica Neue, sans-serif", color="#000000", size=14),
)
fig.update_xaxes(range=[0, 100], showticklabels=False, showgrid=False,
                 zeroline=False, title_text="")
fig.update_yaxes(autorange="reversed", tickfont=dict(size=15, color="#000000"))
st.plotly_chart(fig, use_container_width=True)

# ── Tabela consolidada ──────────────────────────────────────────────────────
secao_titulo("RESUMO", "Tabela consolidada")
tab = pd.DataFrame([{
    "Material": mat,
    "GM médio": round(stats[mat]["gm"], 1) if stats[mat]["gm"] is not None else None,
    "Concorrentes": stats[mat]["n"],
    "% de Vitórias (média)": round(stats[mat]["wr"], 1),
    "Ganho médio (%)": round(stats[mat]["yg"], 1),
    "Alta Performance": stats[mat]["contagem"].get("Alta Performance", 0),
    "Superior": stats[mat]["contagem"].get("Superior", 0),
    "Competitivo": stats[mat]["contagem"].get("Competitivo", 0),
    "Restrito": stats[mat]["contagem"].get("Restrito", 0),
} for mat in ordenados])
tabela_resumo_html(tab)
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
st.download_button("⬇️ Exportar Excel", data=to_excel(tab),
                   file_name=f"visao_materiais_{safra_sel}_M{macro_sel}_{micro_sel}.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
