# Painel de Licenciamento Stine

Painel Streamlit multipágina para análise Head-to-Head dos materiais Stine em
licenciamento (out-licensing 25/26), a partir de uma base de H2H pré-agregada.

## Estrutura de pastas

```
painel_licenciamento/
├── app.py                          # Home (página inicial)
├── requirements.txt                # Dependências Python
├── README.md
│
├── .streamlit/
│   └── config.toml                 # Tema (cores, fonte)
│
├── assets/                         # Logo + ilustrações usadas nos headers
│   ├── logo.png
│   ├── App_development-amico.png
│   ├── Data_analysis-pana.png
│   └── ... (demais ilustrações)
│
├── data/
│   ├── H2H_Licencia_STINE_3jun26_V1.xlsx   # Base de dados (aba "Export")
│   └── geo/
│       ├── municipios_br.json              # GeoJSON dos municípios (mapa)
│       └── municipios_centroides.csv       # Centroides pré-calculados (mapa)
│
├── pages/                          # Páginas do painel (ordem pelo prefixo numérico)
│   ├── 1_Comparacao_Competidores.py
│   ├── 2_Visao_por_Material.py
│   ├── 3_Detalhe_por_Concorrente.py
│   └── 4_Mapa.py
│
├── tools/                          # Scripts utilitários (não fazem parte do app)
│   ├── montar_geojson_municipios.py        # (re)gera data/geo/municipios_br.json (geobr)
│   └── gerar_centroides.py                 # (re)gera o CSV de centroides a partir do GeoJSON
│
└── utils/                          # Código compartilhado entre páginas
    ├── __init__.py
    ├── theme.py                    # CSS/tema e helpers de header
    ├── loader.py                   # Leitura/tipagem da base
    └── h2h_ui.py                   # Classificação, tabela AgGrid, donut, export Excel
```

Regra do Streamlit: tudo dentro de `pages/` vira item de menu automaticamente, na
ordem do prefixo numérico. `app.py` é a home. `utils/` e `tools/` não viram páginas.

## Ambiente virtual no Positron

### Opção A — pela interface (recomendado)
1. Abra a pasta `painel_licenciamento` no Positron (File → Open Folder).
2. Command Palette (Ctrl/Cmd+Shift+P) → **Python: Create Environment**.
3. Escolha **Venv** e o interpretador Python (3.10+).
4. Quando perguntar, marque `requirements.txt` para instalar as dependências.
   Isso cria a pasta `.venv/` e instala tudo.
5. Confirme no seletor de interpretador (canto/superior do Console) que o `.venv`
   está selecionado.

### Opção B — pelo terminal integrado
```bash
# na raiz do projeto
python -m venv .venv

# ativar:
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows (PowerShell)

pip install -r requirements.txt
```

### Alternativa com Conda (se preferir)
```bash
conda create -n licenciamento python=3.11 -y
conda activate licenciamento
pip install -r requirements.txt
```

## Rodar o painel

Com o ambiente ativo, no terminal integrado do Positron:
```bash
streamlit run app.py
```
O Streamlit abre no navegador (normalmente http://localhost:8501). Não use o
botão "Run" do editor — Streamlit precisa ser iniciado pela linha de comando.

## Regenerar dados de geografia (opcional)

O GeoJSON e os centroides já vêm prontos. Só rode isto se quiser atualizá-los:
```bash
python tools/montar_geojson_municipios.py   # gera data/geo/municipios_br.json (precisa de geobr/geopandas)
python tools/gerar_centroides.py            # gera data/geo/municipios_centroides.csv
```

## Sobre a base e o que ela suporta

A base é H2H **pré-agregado**: cada linha é um confronto material × concorrente,
num nível de agregação (Safra × Macro × Micro), já com Yield Gain, Win Rate,
YG% e p-valor calculados. A granularidade mais fina é a **microrregião** — não há
dado por parcela/local individual nem produtividade bruta por local. Por isso as
análises do painel trabalham nesse nível, sem recalcular o H2H.
