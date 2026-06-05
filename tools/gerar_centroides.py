"""
tools/gerar_centroides.py
Gera data/geo/municipios_centroides.csv a partir de data/geo/municipios_br.json.
Rode depois de (re)gerar o GeoJSON:
    python tools/gerar_centroides.py
"""
import csv
import json
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ORIGEM = BASE_DIR / "data" / "geo" / "municipios_br.json"
DESTINO = BASE_DIR / "data" / "geo" / "municipios_centroides.csv"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().strip()
    return " ".join(s.split())


def coords_iter(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        for ring in c:
            yield from ring
    elif t == "MultiPolygon":
        for poly in c:
            for ring in poly:
                yield from ring


def main():
    if not ORIGEM.exists():
        raise SystemExit(f"GeoJSON não encontrado: {ORIGEM}")
    with open(ORIGEM, encoding="utf-8") as f:
        gj = json.load(f)

    rows = []
    for ft in gj["features"]:
        p = ft["properties"]
        name = p.get("name_muni") or p.get("nome")
        uf = p.get("abbrev_state")
        xs, ys = [], []
        for x, y in coords_iter(ft["geometry"]):
            xs.append(x); ys.append(y)
        if not xs:
            continue
        rows.append((norm(name), uf, round(sum(ys) / len(ys), 4),
                     round(sum(xs) / len(xs), 4), name))

    with open(DESTINO, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["nome_norm", "uf", "lat", "lon", "nome"])
        w.writerows(rows)
    print(f"Salvo: {DESTINO} ({len(rows)} municípios)")


if __name__ == "__main__":
    main()
