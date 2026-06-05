"""
app.py — Painel de Licenciamento Stine · Home
"""
from pathlib import Path
import streamlit as st
from utils.theme import aplicar_tema, page_header
from utils.loader import carregar_base

BASE_DIR = Path(__file__).parent

st.set_page_config(page_title="Painel Licenciamento Stine", page_icon="🌱",
                   layout="wide", initial_sidebar_state="expanded")
aplicar_tema()
st.markdown("<style>.jaum-header img { height: 60px !important; }</style>", unsafe_allow_html=True)
page_header("Painel de Licenciamento de Cultivares", "Stine Seed · Out-Licensing 25/26")

base = carregar_base()

col_esq, col_dir = st.columns([2, 3], gap="large")

with col_esq:
    st.markdown("""
<div style="margin-top:1rem;">
  <p style="font-size:15px;color:#1A1A1A;line-height:1.8;">
    Análise Head-to-Head dos materiais Stine em processo de
    <strong>licenciamento</strong> frente aos principais concorrentes do mercado,
    por safra, macro e microrregião.
  </p>
  <p style="font-size:14px;color:#374151;line-height:1.8;margin-top:0.8rem;">
    Comece pela <strong>Comparação com Concorrentes</strong> para ver cada
    material frente aos Checks, como no relatório de out-licensing.
  </p>
</div>
""", unsafe_allow_html=True)

    img_path = BASE_DIR / "assets" / "App_development-amico.png"
    if img_path.exists():
        st.image(str(img_path), use_container_width=True)

    if base["ok"]:
        df = base["df"]
        st.divider()
        a, b, c = st.columns(3)
        a.metric("Materiais Head", df["material"].nunique())
        b.metric("Concorrentes (Checks)", df["check"].nunique())
        c.metric("Confrontos", f"{len(df):,}".replace(",", "."))
    else:
        st.error(f"❌ Base não carregada: {base['erro']}")

PAGINAS = [
    {"icone": "⚔️", "titulo": "Comparação com Concorrentes",
     "subtitulo": "Head vs todos os Checks",
     "descricao": "Cada material Stine frente a todos os concorrentes, com Yield Gain, "
                  "Win Rate, classificação por cores, donut e gráfico de ganho.",
     "tags": ["H2H", "Win Rate", "Yield Gain", "Classe"]},
    {"icone": "📊", "titulo": "Visão por Material",
     "subtitulo": "Os 3 materiais lado a lado",
     "descricao": "Comparativo dos três materiais no mesmo recorte: métricas-resumo, "
                  "distribuição de classes em donut e tabela consolidada.",
     "tags": ["Resumo", "Classes", "Comparativo"]},
    {"icone": "🔍", "titulo": "Detalhe por Concorrente",
     "subtitulo": "Par Head × Check",
     "descricao": "Um material contra um concorrente específico, região a região, "
                  "com Win Rate ponderado e barras por recorte.",
     "tags": ["Par", "Região", "Safra"]},
    {"icone": "🗺️", "titulo": "Mapa por Microrregião",
     "subtitulo": "Performance no mapa do Brasil",
     "descricao": "Bolhas por microrregião coloridas pela performance do material. "
                  "De-para Micro→cidades editável (Macros 1 e 2 já mapeadas).",
     "tags": ["Mapa", "Micro", "Geografia"]},
]

with col_dir:
    st.markdown("""
<div style="margin:0.2rem 0 1rem;">
  <p style="font-size:12px;font-weight:600;color:#6B7280;text-transform:uppercase;
            letter-spacing:0.07em;margin:0 0 4px;">Páginas do Painel</p>
  <h2 style="font-size:1.4rem;font-weight:700;color:#1A1A1A;margin:0;">
    O que você quer analisar?</h2>
</div>
""", unsafe_allow_html=True)

    for pg in PAGINAS:
        tags = "".join(
            f'<span style="display:inline-block;background:#E9F7EF;color:#1E8449;'
            f'font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px;'
            f'margin:2px 2px 0 0;">{t}</span>' for t in pg["tags"])
        st.markdown(f"""
<div style="border:1px solid #E5E7EB;border-radius:12px;padding:14px;background:#FFFFFF;
            min-height:120px;box-shadow:0 1px 4px rgba(0,0,0,0.06);margin-bottom:10px;">
  <div style="font-size:22px;margin-bottom:6px;">{pg['icone']}</div>
  <p style="font-size:14px;font-weight:700;color:#1A1A1A;margin:0 0 2px;">{pg['titulo']}</p>
  <p style="font-size:11px;color:#6B7280;margin:0 0 8px;font-weight:500;">{pg['subtitulo']}</p>
  <p style="font-size:12px;color:#374151;line-height:1.5;margin:0 0 10px;">{pg['descricao']}</p>
  <div>{tags}</div>
</div>
""", unsafe_allow_html=True)

st.divider()
st.markdown(
    '<p style="font-size:13px;color:#374151;text-align:center;">Painel de Licenciamento · '
    'Stine Seed · Desenvolvido por <a href="https://www.linkedin.com/in/eng-agro-andre-ferreira/" '
    'target="_blank" style="color:#27AE60;text-decoration:none;">Andre Ferreira</a></p>',
    unsafe_allow_html=True)
