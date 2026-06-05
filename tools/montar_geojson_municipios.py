"""
tools/montar_geojson_municipios.py
Gera data/geo/municipios_br.json usando geobr (opcional — o arquivo já vem pronto no projeto).
Rode da raiz do projeto:
    python tools/montar_geojson_municipios.py
Depois regenere os centroides:
    python tools/gerar_centroides.py
"""
import sys
import json
from pathlib import Path

# Salva direto na pasta de dados do projeto (não em assets/)
DESTINO = Path(__file__).parent.parent / "data" / "geo" / "municipios_br.json"
DESTINO.parent.mkdir(parents=True, exist_ok=True)

try:
    import geobr
    import geopandas as gpd  # noqa: F401
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "geobr", "geopandas"])
    import geobr
    import geopandas as gpd  # noqa: F401

print("Baixando municipios...")
mun = geobr.read_municipality(code_muni="all", year=2020)
print(f"Total: {len(mun)} municipios")

mun = mun.to_crs(epsg=4326)
print("Simplificando geometrias...")
mun["geometry"] = mun["geometry"].simplify(tolerance=0.01, preserve_topology=True)

tmp = DESTINO.with_suffix(".tmp")
print("Salvando...")
mun.to_file(str(tmp), driver="GeoJSON", encoding="utf-8")

print("Normalizando propriedades...")
with open(tmp, "r", encoding="utf-8") as f:
    gj = json.load(f)

for i, feat in enumerate(gj["features"]):
    p = feat.get("properties", {})
    feat["properties"]["mun_id"] = str(i)
    feat["properties"]["geocodigo"] = str(p.get("code_muni", ""))
    feat["properties"]["nome"] = str(p.get("name_muni", ""))

with open(DESTINO, "w", encoding="utf-8") as f:
    json.dump(gj, f, ensure_ascii=False)

tmp.unlink(missing_ok=True)

sz = DESTINO.stat().st_size / 1024 / 1024
print(f"\nSalvo em: {DESTINO}  ({sz:.1f} MB)")
print("Agora rode: python tools/gerar_centroides.py")
