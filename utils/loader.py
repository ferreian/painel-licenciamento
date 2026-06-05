"""
utils/loader.py — Carregamento da base de licenciamento (H2H pré-agregado).

A base já vem com o H2H calculado: cada linha é um confronto
Head (Stine) × Check (concorrente) num nível de agregação
(Safra × Macro × Micro), com YG, WR%, YG%, P-Valor e N° prontos.
Não há cruzamento parcela a parcela — só leitura, tipagem e limpeza.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# Nome do arquivo da base. Trocar aqui quando vier uma nova versão.
ARQUIVO_BASE = "H2H_Licencia_STINE_3jun26_V1.xlsx"
ABA = "Export"

# Mapa para nomes internos curtos e estáveis (facilita filtros/joins).
RENOMEAR = {
    "Safra":                 "safra",
    "Macro":                 "macro",
    "Micro":                 "micro",
    "Head":                  "head_cod",
    "Cultivar Name":         "material",
    "Check":                 "check",
    "N°":                    "n_comp",
    "Cultivar Head (sc/ha)": "sc_head",
    "Check (sc/ha)":         "sc_check",
    "YG (sc/ha)":            "yg_sc",
    "WR%":                   "wr",
    "YG%":                   "yg_pct",
    "RM":                    "rm",
    "P-Valor":               "p_valor",
    "Ambiente":              "ambiente",
    "Plantio":               "plantio",
    "Fonte":                 "fonte",
    "Country":               "country",
}

COLS_NUM = ["n_comp", "sc_head", "sc_check", "yg_sc", "wr", "yg_pct", "rm", "p_valor"]


@st.cache_data(show_spinner=False)
def carregar_base() -> dict:
    """
    Retorna {"ok": bool, "df": DataFrame|None, "erro": str|None}.
    df já vem tipado e com colunas renomeadas para nomes internos.
    """
    path = DATA_DIR / ARQUIVO_BASE
    if not path.exists():
        return {"ok": False, "df": None,
                "erro": f"Arquivo não encontrado: {path}"}
    try:
        df = pd.read_excel(path, sheet_name=ABA)
        df = df.rename(columns=RENOMEAR)

        for c in COLS_NUM:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        # Colunas de texto: garantir string limpa
        for c in ["safra", "macro", "micro", "head_cod", "material", "check"]:
            if c in df.columns:
                df[c] = df[c].astype(str).str.strip()

        return {"ok": True, "df": df, "erro": None}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "df": None, "erro": str(e)}


# Faixas de RM (relative maturity) — usadas para agrupar Checks como no PPTX.
FAIXAS_GM_ORDEM = ["< 6.0", "6.0–6.2", "6.3–6.5", "6.6–6.9", "7.0–7.5", "≥ 7.6"]


def faixa_rm(rm: float) -> str:
    if pd.isna(rm):
        return "Sem RM"
    if rm < 6.0:
        return "< 6.0"
    if rm < 6.3:
        return "6.0–6.2"
    if rm < 6.6:
        return "6.3–6.5"
    if rm < 7.0:
        return "6.6–6.9"
    if rm < 7.6:
        return "7.0–7.5"
    return "≥ 7.6"


# Rótulo amigável para os níveis de agregação nos seletores.
def rotulo(v) -> str:
    s = str(v)
    if s == "ALL":
        return "Todas"
    if s == "Aggregation_analysis":
        return "Agregação"
    return s
