import json
from pathlib import Path

from api_dolar.generar import FUENTE_ACTUAL, generar
from api_dolar.transformar import calcular_brecha, normalizar_actual, normalizar_historico, resumen

FIXTURES = Path(__file__).parent / "fixtures"


def cargar(nombre):
    return json.loads((FIXTURES / nombre).read_text())


def test_normalizar_actual_ordena_y_renombra():
    actual = normalizar_actual(cargar("dolares.json"))
    assert [c["casa"] for c in actual] == ["blue", "contadoconliqui", "oficial"]
    assert set(actual[0]) == {"casa", "nombre", "compra", "venta", "actualizado"}


def test_brecha_contra_oficial():
    brecha = {b["casa"]: b["brecha_pct"] for b in calcular_brecha(normalizar_actual(cargar("dolares.json")))}
    assert brecha == {"blue": 0.32, "contadoconliqui": 6.76}


def test_brecha_sin_oficial_devuelve_vacio():
    assert calcular_brecha([{"casa": "blue", "venta": 10}]) == []


def test_historico_ordena_y_deduplica():
    datos = [
        {"fecha": "2026-01-02", "compra": 1, "venta": 2},
        {"fecha": "2026-01-01", "compra": 1, "venta": 1},
        {"fecha": "2026-01-02", "compra": 1, "venta": 3},
        {"fecha": "2026-01-03", "compra": 1, "venta": None},
    ]
    assert normalizar_historico(datos) == [
        {"fecha": "2026-01-01", "compra": 1, "venta": 1},
        {"fecha": "2026-01-02", "compra": 1, "venta": 3},
    ]


def test_resumen_calcula_variaciones():
    historico = normalizar_historico(cargar("historico_blue.json"))
    r = resumen(historico)
    assert r["fecha"] == historico[-1]["fecha"]
    assert r["variacion_pct"]["7d"] is not None
    assert r["variacion_pct"]["365d"] is None  # el fixture tiene solo 40 días


def test_generar_escribe_todos_los_endpoints(tmp_path):
    def falso(url):
        return cargar("dolares.json") if url == FUENTE_ACTUAL else cargar("historico_blue.json")

    casas = generar(tmp_path, descargar=falso)
    assert casas == ["blue", "contadoconliqui", "oficial"]
    for ruta in ["v1/dolares.json", "v1/brecha.json", "v1/index.json", "v1/historico/blue.json", "v1/resumen/oficial.json"]:
        assert (tmp_path / ruta).exists(), ruta
