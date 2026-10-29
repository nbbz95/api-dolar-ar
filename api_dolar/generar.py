"""Descarga las fuentes y escribe la API estática en un directorio (por defecto site/)."""

import argparse
import json
import shutil
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from api_dolar.transformar import calcular_brecha, normalizar_actual, normalizar_historico, resumen

FUENTE_ACTUAL = "https://dolarapi.com/v1/dolares"
FUENTE_HISTORICO = "https://api.argentinadatos.com/v1/cotizaciones/dolares/{casa}"


def descargar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "api-dolar-ar (github.com/nbbz95/api-dolar-ar)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def escribir(ruta, datos):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")


def generar(destino, descargar=descargar):
    v1 = destino / "v1"
    actual = normalizar_actual(descargar(FUENTE_ACTUAL))
    escribir(v1 / "dolares.json", actual)
    escribir(v1 / "brecha.json", calcular_brecha(actual))

    casas = []
    for c in actual:
        try:
            historico = normalizar_historico(descargar(FUENTE_HISTORICO.format(casa=c["casa"])))
        except Exception as e:  # una casa sin histórico no debe tirar abajo toda la API
            print(f"Sin histórico para {c['casa']}: {e}", file=sys.stderr)
            continue
        escribir(v1 / "historico" / f"{c['casa']}.json", historico)
        escribir(v1 / "resumen" / f"{c['casa']}.json", resumen(historico))
        casas.append(c["casa"])

    escribir(
        v1 / "index.json",
        {
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "casas": casas,
            "endpoints": ["/v1/dolares.json", "/v1/brecha.json", "/v1/historico/{casa}.json", "/v1/resumen/{casa}.json"],
        },
    )
    return casas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destino", default="site", type=Path)
    args = parser.parse_args()
    shutil.copytree(Path(__file__).parent.parent / "web", args.destino, dirs_exist_ok=True)
    casas = generar(args.destino)
    print(f"API generada en {args.destino} con {len(casas)} casas: {', '.join(casas)}")


if __name__ == "__main__":
    main()
