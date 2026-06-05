"""
pages/1_Comparacao_Competidores.py
Comparação de um material Head (Stine) com todos os Checks (concorrentes).
Espelha o slide "Comparison with main competitors" da apresentação de licenciamento:
RM · Check · Yield Gain (%) · Win Rate (%), classificado por % de vitórias.
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.theme import aplicar_tema, page_header, secao_titulo
from utils.loader import carregar_base, faixa_rm, rotulo, FAIXAS_GM_ORDEM
from utils.h2h_ui import (classificar_h2h, ag_table_h2h, to_excel, donut_classes,
                          COR_FUNDO, como_ler, chart_pergunta, chart_resposta,
                          legenda_classes_chips, LEGENDA_CLASSES_MD)

st.set_page_config(page_title="Comparação · Licenciamento",
                   page_icon="⚔️", layout="wide", initial_sidebar_state="expanded")
aplicar_tema()
st.markdown("<style>.jaum-header img { height: 110px !important; }</style>",
            unsafe_allow_html=True)

# ── Dados ─────────────────────────────────────────────────────────────────────
base = carregar_base()
if not base["ok"]:
    st.error(f"❌ Não foi possível carregar a base: {base['erro']}")
    st.stop()
df = base["df"]

page_header("Comparação com Concorrentes",
            "Cada material Stine frente a todos os Checks, por safra e região.",
            imagem="Data_analysis-pana.png")

# ── Sidebar — filtros ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#6B7280;text-transform:uppercase;'
        'letter-spacing:0.05em;padding:0.5rem 0.5rem 0;">Filtros</p>', unsafe_allow_html=True)

    # ── Bloco 1: Recorte (encadeado: safra › macro › micro) ──────────────────
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

    # ── Bloco 2: Filtros de concorrentes ─────────────────────────────────────
    st.markdown('<p style="font-size:12px;font-weight:700;color:#1E8449;margin:0 0 6px;">'
                '2 · Concorrentes</p>', unsafe_allow_html=True)

    bandas_gm = [f for f in FAIXAS_GM_ORDEM
                 if f in set(df["rm"].dropna().apply(faixa_rm))]
    faixa_gm_sel = st.selectbox("Faixa de GM", ["Todas"] + bandas_gm)

    n_min = st.number_input("Nº mínimo de comparações", min_value=1, value=3, step=1)
    p_sig = st.checkbox("Só diferenças significativas (p < 0,05)", value=False)

# ── Seleção do Head ─────────────────────────────────────────────────────────────
materiais = sorted(df["material"].unique().tolist())
col_h, _ = st.columns([2, 3])
with col_h:
    material_sel = st.selectbox("Material (Stine)", materiais)

gm_mat = df[df["material"] == material_sel]["rm"].dropna()
gm_mat_txt = f"GM {gm_mat.mean():.1f}" if not gm_mat.empty else ""

# ── Filtragem ────────────────────────────────────────────────────────────────
sub = df[(df["safra"] == safra_sel) & (df["macro"] == macro_sel) &
         (df["micro"] == micro_sel) & (df["material"] == material_sel)].copy()
sub = sub[sub["n_comp"] >= n_min]
# Filtro por faixa de GM (só quando uma faixa específica é escolhida)
if faixa_gm_sel != "Todas":
    sub = sub[sub["rm"].apply(faixa_rm) == faixa_gm_sel]
if p_sig:
    sub = sub[sub["p_valor"] < 0.05]

if sub.empty:
    st.warning("⚠️ Nenhum confronto para os filtros selecionados.")
    st.stop()

# ── Monta tabela de exibição ────────────────────────────────────────────────
sub["faixa_gm"] = sub["rm"].apply(faixa_rm)
sub[["Classe", "_cor"]] = sub["wr"].apply(lambda w: pd.Series(classificar_h2h(w)))

tabela = pd.DataFrame({
    "Concorrente":       sub["check"],
    "GM":                sub["rm"].round(1),
    "Faixa GM":          sub["faixa_gm"],
    "sc/ha Material":    sub["sc_head"].round(1),
    "sc/ha Concorrente": sub["sc_check"].round(1),
    "Ganho (sc/ha)":     sub["yg_sc"].round(1),
    "Ganho (%)":         sub["yg_pct"].round(1),
    "% de Vitórias":     sub["wr"].round(1),
    "Nº Comp.":          sub["n_comp"].astype(int),
    "P-Valor":           sub["p_valor"].round(3),
    "Classe":            sub["Classe"],
}).sort_values("% de Vitórias", ascending=False).reset_index(drop=True)

# ── Título + contexto ───────────────────────────────────────────────────────
n_checks = len(tabela)
st.markdown(
    f'<div style="margin:0.5rem 0 0.2rem;">'
    f'<p style="font-size:13px;font-weight:600;color:#6B7280;text-transform:uppercase;'
    f'letter-spacing:0.05em;margin:0 0 4px;">Comparação com Concorrentes</p>'
    f'<h2 style="font-size:1.9rem;font-weight:700;color:#1A1A1A;margin:0;line-height:1.2;">'
    f'<span style="color:#27AE60;">{material_sel}</span>'
    f'<span style="font-size:1rem;font-weight:500;color:#6B7280;margin-left:10px;">'
    f'{gm_mat_txt} · {n_checks} concorrentes</span></h2>'
    f'<p style="font-size:14px;color:#6B7280;margin:4px 0 0;">'
    f'Safra {safra_sel} · Macro {macro_sel} · Micro {micro_sel}</p></div>',
    unsafe_allow_html=True)

# ── Métricas-resumo ────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Vitórias (média)", f"{sub['wr'].mean():.0f}%")
m2.metric("Ganho médio", f"{sub['yg_pct'].mean():+.1f}%")
m3.metric("Concorrentes vencidos (>55%)", int((sub["wr"] > 55).sum()))
m4.metric("Total de comparações", int(sub["n_comp"].sum()))

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Resumo por classe ───────────────────────────────────────────────────────
contagem = tabela["Classe"].value_counts().to_dict()
total_cls = len(tabela)
c1, c2, c3, c4 = st.columns(4)
for col_ui, label, cor_txt in zip(
    [c1, c2, c3, c4],
    ["Alta Performance", "Superior", "Competitivo", "Restrito"],
    ["#27AE60", "#1E40AF", "#F2C811", "#FF0000"],
):
    n_cls = int(contagem.get(label, 0))
    pct = f"{n_cls / total_cls * 100:.0f}%" if total_cls else "—"
    col_ui.markdown(
        f'<div style="border:1px solid #E5E7EB;border-radius:10px;padding:10px 14px;'
        f'background:#FFFFFF;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.07);">'
        f'<p style="margin:0;font-size:14px;font-weight:600;color:#374151;">{label}</p>'
        f'<p style="margin:4px 0 0;font-size:2.2rem;font-weight:700;color:{cor_txt};">'
        f'{n_cls} <span style="font-size:1.2rem;font-weight:500;">({pct})</span></p></div>',
        unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── Insights dinâmicos (calculados do recorte filtrado) ──────────────────────
n_tot = len(tabela)
n_alta = int(contagem.get("Alta Performance", 0))
n_sup = int(contagem.get("Superior", 0))
n_restr = int(contagem.get("Restrito", 0))
sup_plus = n_alta + n_sup
pct_sup = sup_plus / n_tot * 100 if n_tot else 0

melhor = tabela.loc[tabela["Ganho (%)"].idxmax()]
n_pos = int((tabela["Ganho (%)"] > 0).sum())
n_neg = int((tabela["Ganho (%)"] < 0).sum())

# ── Como interpretar esta seção (antes dos gráficos) ─────────────────────────
secao_titulo("LEITURA", "Como interpretar os gráficos abaixo")
st.markdown(
    '<p style="font-size:16px;color:#374151;line-height:1.7;margin:0 0 10px;">'
    'O <b>donut</b> resume <b>em quantos concorrentes</b> o material é superior, '
    'agrupando-os por faixa de % de vitórias. Já o <b>gráfico de ganho</b> mostra '
    '<b>quanto a mais (ou a menos)</b> o material produz, em %, contra cada concorrente. '
    'Em ambos, a cor segue a faixa de % de vitórias:</p>',
    unsafe_allow_html=True)
legenda_classes_chips()

# ── Donut + gráfico de Ganho de Produtividade ────────────────────────────────
col_donut, col_bar = st.columns([1, 2], gap="large")

with col_donut:
    tit, btn = st.columns([3, 2])
    with tit:
        secao_titulo("DISTRIBUIÇÃO", "Por classe")
        como_ler(
            "**Cada fatia** é a quantidade de concorrentes em cada faixa de % de vitórias.\n\n"
            + LEGENDA_CLASSES_MD +
            "\nO número no centro é o total de concorrentes avaliados.")
    chart_pergunta("Contra quantos concorrentes o material é superior?")
    chart_resposta(
        f"<b>{sup_plus} de {n_tot}</b> concorrentes ({pct_sup:.0f}%) caem em "
        f"<b>Superior</b> ou <b>Alta Performance</b> — o material vence na maioria dos "
        f"locais contra a maior parte dos concorrentes avaliados." +
        (f" Apenas <b>{n_restr}</b> o colocam em situação Restrita." if n_restr else
         " Nenhum concorrente o coloca em situação Restrita."))
    st.plotly_chart(donut_classes(contagem), use_container_width=True)

with col_bar:
    tit, btn = st.columns([3, 1])
    with tit:
        secao_titulo("GANHO DE PRODUTIVIDADE", "Ganho (%) por concorrente")
        como_ler(
            "**Cada item** é o ganho médio de produtividade do material sobre um "
            "concorrente, em %.\n\n"
            "- À **direita do zero** → o material **produz mais** que o concorrente.\n"
            "- À **esquerda** → produz menos.\n\n"
            "A **cor** segue a faixa de % de vitórias:\n\n"
            + LEGENDA_CLASSES_MD +
            "\n**Importante:** por padrão o gráfico mostra **apenas os 25 maiores "
            "ganhos**. Marque **'Mostrar todos os concorrentes'** para ver a lista "
            "completa, inclusive os de ganho negativo.\n\n"
            "Use **'Ver como lollipop'** para trocar a barra por bolinhas (lollipop).")
    chart_pergunta("Onde está o maior ganho?")

    ctrl1, ctrl2 = st.columns([1, 1])
    with ctrl1:
        ver_lollipop = st.checkbox("Ver como lollipop", value=False,
                                   key="ganho_lollipop")
        tipo_graf = "Lollipop" if ver_lollipop else "Barra"
    with ctrl2:
        mostrar_todos = st.checkbox("Mostrar todos os concorrentes", value=False,
                                    key="ganho_todos")

    ordenado = tabela.sort_values("Ganho (%)")
    plot_df = ordenado if mostrar_todos else ordenado.tail(25)
    n_mostrados = len(plot_df)

    nota_exib = ("" if mostrar_todos or n_tot <= 25 else
                 f" Exibindo os <b>{n_mostrados} maiores</b> de {n_tot} — marque a caixa "
                 f"acima para ver todos" + (f", inclusive o(s) {n_neg} negativo(s)." if n_neg else "."))
    chart_resposta(
        f"O maior ganho é contra <b>{melhor['Concorrente']}</b> "
        f"(<b>{melhor['Ganho (%)']:+.1f}%</b>). "
        f"<b>{n_pos} de {n_tot}</b> concorrentes têm ganho positivo" +
        (f"; só <b>{n_neg}</b> ficam abaixo de zero." if n_neg else
         " — o material não perde em produtividade média para nenhum deles.") +
        nota_exib)

    ys = plot_df["Concorrente"].tolist()
    xs = plot_df["Ganho (%)"].tolist()
    cores = [COR_FUNDO[classificar_h2h(w)[0]] for w in plot_df["% de Vitórias"]]

    fig = go.Figure()
    if tipo_graf == "Barra":
        fig.add_trace(go.Bar(
            x=xs, y=ys, orientation="h",
            marker=dict(color=cores, line=dict(color="#888", width=0.5)),
            text=[f"{v:+.1f}%" for v in xs],
            textposition="outside", textfont=dict(size=12, color="#000000"),
            hovertemplate="%{y}<br>Ganho: %{x:+.1f}%<extra></extra>", showlegend=False))
    else:
        for x, y, c in zip(xs, ys, cores):
            fig.add_trace(go.Scatter(
                x=[0, x], y=[y, y], mode="lines",
                line=dict(color=c, width=2.5),
                hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="markers+text",
            marker=dict(color=cores, size=13, line=dict(color="#666", width=0.8)),
            text=[f"{v:+.1f}%" for v in xs],
            textposition=["middle right" if v >= 0 else "middle left" for v in xs],
            textfont=dict(size=12, color="#000000"),
            hovertemplate="%{y}<br>Ganho: %{x:+.1f}%<extra></extra>", showlegend=False))

    fig.add_vline(x=0, line_width=1.2, line_color="#374151")
    xmin, xmax = min(0, min(xs)), max(xs)
    fig.update_layout(
        height=max(340, 24 * len(plot_df)),
        margin=dict(t=10, b=10, l=10, r=60),
        xaxis_title="Ganho de produtividade (%)  —  positivo = material ganha",
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        font=dict(family="Helvetica Neue, sans-serif", color="#000000", size=14),
    )
    fig.update_xaxes(gridcolor="#EEE", zeroline=False,
                     range=[xmin - 2, xmax + max(3, xmax * 0.15)],
                     title_font=dict(size=15, color="#000000"),
                     tickfont=dict(size=13, color="#000000"))
    fig.update_yaxes(categoryorder="array", categoryarray=ys, showgrid=False,
                     tickfont=dict(size=13, color="#000000"))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ── Tabela ──────────────────────────────────────────────────────────────────
secao_titulo("TABELA", "Confrontos detalhados",
             "Cada linha é o material Stine frente a um concorrente, no nível de "
             "agregação selecionado. Cores pela faixa de % de vitórias.")

with st.popover("ℹ️ Como interpretar"):
    st.markdown("""
- **Ganho (sc/ha · %)** → quanto o material produz a mais (ou a menos) que o concorrente.
- **% de Vitórias** → % de locais em que o material superou o concorrente — base da classificação.
- **Nº Comp.** → número de confrontos no nível de agregação.
- **P-Valor** → significância estatística da diferença (< 0,05 = diferença confiável).

**Cores (% de vitórias):** Alta Performance > 75% · Superior 56–75% · Competitivo 46–55% · Restrito ≤ 45%.
""")

ag_table_h2h(tabela, height=min(700, int(36 + 33 * len(tabela) + 20)), key="ag_comp")

st.download_button(
    "⬇️ Exportar Excel",
    data=to_excel(tabela),
    file_name=f"comparacao_{material_sel}_{safra_sel}_M{macro_sel}_{micro_sel}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
