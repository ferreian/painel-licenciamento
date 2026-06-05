"""
utils/theme.py
CSS e helpers de tema compartilhados entre todas as páginas.
"""

import base64
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).parent.parent


def aplicar_tema():
    st.markdown("""
<style>
:root {
    color-scheme: light !important;
    --green-primary:  #27AE60;
    --green-dark:     #1E8449;
    --green-light:    #E9F7EF;
    --green-mid:      #A9DFBF;
    --text-primary:   #1A1A1A;
    --text-secondary: #6B7280;
    --bg-main:        #F8FAF9;
    --bg-white:       #FFFFFF;
    --border:         #E5E7EB;
    --shadow:         0 1px 4px rgba(0,0,0,0.07);
}

html, body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
}

/* ── Força tema claro mesmo com sistema/navegador em modo escuro ── */
.stApp,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main {
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
}
[data-testid="stHeader"],
[data-testid="stToolbar"] {
    background: var(--bg-main) !important;
}
/* Texto padrão em escuro nos blocos de markdown/labels */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stWidgetLabel"],
label, p, span, h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary);
}
/* Inputs/selects claros */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
.stTextInput input, .stNumberInput input {
    background-color: var(--bg-white) !important;
    color: var(--text-primary) !important;
}
/* Aplicar fonte globalmente sem sobrescrever componentes externos como AgGrid */
[class*="css"]:not([class*="ag-"]) {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
}

/* ── Sidebar limpa ── */
[data-testid="stSidebar"] {
    background-color: var(--bg-white) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ── Nav pages ── */
[data-testid="stSidebarNav"] {
    padding-top: 1.5rem !important;
}
[data-testid="stSidebarNav"] a {
    padding: 9px 16px !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: background 0.15s !important;
    color: var(--text-primary) !important;
    text-decoration: none !important;
    display: flex !important;
    align-items: center !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: var(--green-light) !important;
    color: var(--green-dark) !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: var(--green-light) !important;
    color: var(--green-dark) !important;
    font-weight: 600 !important;
}

/* ── Oculta label padrão "Navigation" do pages ── */
[data-testid="stSidebarNav"]::before { display: none !important; }

/* ── Topo da página — header com logo ── */
.jaum-header {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    padding: 0.5rem 0 1.2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.jaum-header img {
    height: 150px;
    width: auto;
}
.jaum-header-divider {
    width: 1px;
    height: 32px;
    background: var(--border);
}
.jaum-header-text h1 {
    font-size: 2.4rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}
.jaum-header-text p {
    font-size: 15px !important;
    color: var(--text-secondary) !important;
    margin: 2px 0 0 !important;
}

/* ── Conteúdo principal ── */
.main .block-container {
    padding: 1.5rem 2.5rem 2rem !important;
    max-width: 1400px !important;
}

/* ── Títulos ── */
h1 { font-size: 1.9rem !important; font-weight: 700 !important; }
h2 { font-size: 1.5rem !important; font-weight: 600 !important; }
h3 { font-size: 1.2rem !important; font-weight: 600 !important; }

/* ── Botão primário ── */
.stButton > button[kind="primary"] {
    background-color: var(--green-primary) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 0.5rem 1.2rem !important;
    transition: background 0.2s !important;
}
.stButton > button[kind="primary"]:hover { background-color: var(--green-dark) !important; }

/* ── Botão secundário ── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    border: 1px solid var(--border) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: var(--green-primary) !important;
    color: var(--green-primary) !important;
}

/* ── Botões de popover ("Como ler") e download — claros ── */
[data-testid="stPopover"] button,
[data-testid="stPopoverButton"],
.stDownloadButton > button {
    background-color: var(--bg-white) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
[data-testid="stPopover"] button:hover,
[data-testid="stPopoverButton"]:hover,
.stDownloadButton > button:hover {
    border-color: var(--green-primary) !important;
    color: var(--green-primary) !important;
}
/* Conteúdo do popover (modal "como ler") claro */
[data-testid="stPopoverBody"],
[data-baseweb="popover"] [data-testid="stPopoverBody"] {
    background-color: var(--bg-white) !important;
    color: var(--text-primary) !important;
}
[data-testid="stPopoverBody"] * { color: var(--text-primary) !important; }

/* ── Dropdowns (selectbox) claros + destaque verde no foco ── */
[data-baseweb="select"] > div {
    background-color: var(--bg-white) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
}
[data-baseweb="select"] > div:focus-within,
[data-baseweb="select"] > div[aria-expanded="true"] {
    border-color: var(--green-primary) !important;
    box-shadow: 0 0 0 1px var(--green-primary) !important;
}
[data-baseweb="select"] svg { color: var(--text-secondary) !important; fill: var(--text-secondary) !important; }
[data-baseweb="menu"], [role="listbox"] { background-color: var(--bg-white) !important; }
[role="option"] { background-color: var(--bg-white) !important; color: var(--text-primary) !important; }
[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background-color: var(--green-light) !important;
    color: var(--green-dark) !important;
}

/* ── Inputs de texto/número claros + foco verde ── */
[data-baseweb="input"] {
    background-color: var(--bg-white) !important;
    border-color: var(--border) !important;
}
[data-baseweb="input"]:focus-within {
    border-color: var(--green-primary) !important;
    box-shadow: 0 0 0 1px var(--green-primary) !important;
}
.stNumberInput input, .stTextInput input {
    background-color: var(--bg-white) !important;
    color: var(--text-primary) !important;
}
/* botões +/- do number_input */
.stNumberInput button,
[data-testid="stNumberInputStepUp"],
[data-testid="stNumberInputStepDown"] {
    background-color: var(--bg-white) !important;
    color: var(--text-primary) !important;
    border-color: var(--border) !important;
}
.stNumberInput button:hover,
[data-testid="stNumberInputStepUp"]:hover,
[data-testid="stNumberInputStepDown"]:hover {
    color: var(--green-primary) !important;
    background-color: var(--green-light) !important;
}

/* ── Checkbox claro + marcado em verde ── */
[data-baseweb="checkbox"] > span:first-child,
[data-testid="stCheckbox"] [data-baseweb="checkbox"] span:first-child {
    background-color: var(--bg-white) !important;
    border-color: var(--border) !important;
}
[data-baseweb="checkbox"] input:checked + span:first-child,
[data-baseweb="checkbox"] span[data-checked="true"],
[data-baseweb="checkbox"]:has(input:checked) span:first-child {
    background-color: var(--green-primary) !important;
    border-color: var(--green-primary) !important;
}
[data-baseweb="checkbox"]:has(input:checked) span:first-child svg,
[data-baseweb="checkbox"] input:checked + span:first-child svg {
    fill: #FFFFFF !important; color: #FFFFFF !important;
}

/* ── Slider em verde ── */
[data-baseweb="slider"] [role="slider"] { background-color: var(--green-primary) !important; }
[data-baseweb="slider"] [data-testid="stTickBarMin"],
[data-baseweb="slider"] [data-testid="stTickBarMax"] { color: var(--text-secondary) !important; }

/* ── Conteúdo de popover / menu suspenso claro (reforço) ── */
[data-baseweb="popover"] > div,
[data-baseweb="popover"] [data-testid="stPopoverBody"] {
    background-color: var(--bg-white) !important;
}
[data-baseweb="popover"] p,
[data-baseweb="popover"] li,
[data-baseweb="popover"] span,
[data-baseweb="popover"] strong { color: var(--text-primary) !important; }

/* ── Barra superior, menu (⋮) e indicador "Running" legíveis ── */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"] {
    background-color: var(--bg-main) !important;
}
[data-testid="stToolbar"] *,
[data-testid="stStatusWidget"] *,
[data-testid="stMainMenu"] *,
[data-testid="stMainMenuPopover"] * {
    color: var(--text-primary) !important;
}
[data-testid="stMainMenuPopover"],
[data-testid="stMainMenuList"],
[data-testid="stMainMenu"] ul {
    background-color: var(--bg-white) !important;
}
[data-testid="stMainMenuList"] li,
[data-testid="stMainMenu"] li,
[role="option"] { font-weight: 500 !important; }
[data-testid="stMainMenuList"] li:hover,
[data-testid="stMainMenu"] li:hover {
    background-color: var(--green-light) !important;
    color: var(--green-dark) !important;
}

/* ── Métricas ── */
[data-testid="stMetric"] {
    background: var(--bg-white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1rem 1.2rem !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; font-size: 14px !important; }
[data-testid="stMetricValue"] { color: var(--text-primary) !important; font-size: 1.8rem !important; font-weight: 700 !important; }

/* ── Alerts ── */
.stAlert { border-radius: 8px !important; font-size: 14px !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    background: var(--bg-white) !important;
}

hr { border-color: var(--border) !important; }

/* ── AgGrid — cabeçalho escuro e ícones brancos ── */
.ag-theme-alpine .ag-header,
.ag-theme-alpine .ag-header-row,
.ag-theme-alpine .ag-header-cell,
.ag-theme-alpine .ag-header-cell-resize {
    background-color: #4A4A4A !important;
    background: #4A4A4A !important;
}
.ag-theme-alpine .ag-header-cell-text,
.ag-theme-alpine .ag-header-cell-label,
.ag-theme-alpine .ag-header-group-cell-label {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 13px !important;
}
.ag-theme-alpine .ag-icon,
.ag-theme-alpine .ag-header-icon,
.ag-theme-alpine .ag-icon-menu,
.ag-theme-alpine .ag-icon-filter,
.ag-theme-alpine .ag-icon-columns,
.ag-theme-alpine .ag-header-cell-menu-button,
.ag-theme-alpine .ag-header-cell-menu-button span {
    color: #FFFFFF !important;
    opacity: 1 !important;
    fill: #FFFFFF !important;
}
[data-testid="stCaptionContainer"] { color: #374151 !important; font-size: 13px !important; }
.stSpinner > div { border-top-color: var(--green-primary) !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-main); }
::-webkit-scrollbar-thumb { background: var(--green-mid); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--green-primary); }
</style>
""", unsafe_allow_html=True)


def logo_base64():
    for ext in ["png", "svg", "jpg", "jpeg"]:
        path = BASE_DIR / "assets" / f"logo.{ext}"
        if path.exists():
            mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
            data = base64.b64encode(path.read_bytes()).decode()
            return f"data:{mime};base64,{data}"
    return None


def page_header(titulo: str, subtitulo: str = "", imagem: str = ""):
    """
    Renderiza o header padrão de cada página:
    [Logo ou imagem customizada] | [Título da página / subtítulo]
    """
    if imagem:
        path = BASE_DIR / "assets" / imagem
        if path.exists():
            ext = imagem.rsplit(".", 1)[-1].lower()
            mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
            data = base64.b64encode(path.read_bytes()).decode()
            src = f"data:{mime};base64,{data}"
        else:
            src = logo_base64()
    else:
        src = logo_base64()
    logo_html = (
        f'<img src="{src}" />'
        if src
        else '<span style="font-size:1.4rem;font-weight:700;color:#27AE60;">🌱</span>'
    )
    sub_html = f'<p>{subtitulo}</p>' if subtitulo else ""

    st.markdown(f"""
<div class="jaum-header">
    {logo_html}
    <div class="jaum-header-divider"></div>
    <div class="jaum-header-text">
        <h1>{titulo}</h1>
        {sub_html}
    </div>
</div>
""", unsafe_allow_html=True)


# Mantém compatibilidade com chamadas antigas
def sidebar_header():
    pass


def secao_titulo(label: str, titulo: str, descricao: str = ""):
    """Bloco editorial: label em caps + título grande + descrição."""
    desc_html = (
        f'<p style="font-size:16px;color:#6B7280;margin:6px 0 0;line-height:1.6;">{descricao}</p>'
        if descricao else ""
    )
    st.markdown(f"""
<div style="margin: 1.5rem 0 1rem;">
    <p style="font-size:13px;font-weight:600;color:#6B7280;text-transform:uppercase;
              letter-spacing:0.05em;margin:0 0 6px;">{label}</p>
    <h2 style="font-size:2.0rem;font-weight:700;color:#1A1A1A;margin:0;line-height:1.2;">{titulo}</h2>
    {desc_html}
</div>
""", unsafe_allow_html=True)
