"""Transformaciones puras: no hacen red, así se pueden testear con fixtures."""

from datetime import date


def normalizar_actual(cotizaciones):
    """Deja un esquema estable y ordenado por casa."""
    salida = []
    for c in cotizaciones:
        salida.append(
            {
                "casa": c["casa"],
                "nombre": c["nombre"],
                "compra": c.get("compra"),
                "venta": c.get("venta"),
                "actualizado": c["fechaActualizacion"],
            }
        )
    return sorted(salida, key=lambda c: c["casa"])


def calcular_brecha(actual):
    """Brecha porcentual de cada cotización contra el oficial (precio de venta)."""
    oficial = next((c for c in actual if c["casa"] == "oficial"), None)
    if not oficial or not oficial["venta"]:
        return []
    base = oficial["venta"]
    return [
        {"casa": c["casa"], "venta": c["venta"], "brecha_pct": round((c["venta"] / base - 1) * 100, 2)}
        for c in actual
        if c["casa"] != "oficial" and c["venta"]
    ]


def normalizar_historico(registros):
    """Ordena por fecha, descarta duplicados y valores vacíos."""
    vistos = {}
    for r in registros:
        if r.get("venta") is None:
            continue
        vistos[r["fecha"]] = {"fecha": r["fecha"], "compra": r.get("compra"), "venta": r["venta"]}
    return [vistos[f] for f in sorted(vistos)]


def resumen(historico, hoy=None):
    """Último valor y variación contra 7, 30 y 365 días antes (o el dato anterior más cercano)."""
    if not historico:
        return None
    hoy = date.fromisoformat(historico[-1]["fecha"]) if hoy is None else hoy
    ultimo = historico[-1]

    def valor_hace(dias):
        objetivo = date.fromordinal(hoy.toordinal() - dias).isoformat()
        anteriores = [r for r in historico if r["fecha"] <= objetivo]
        return anteriores[-1]["venta"] if anteriores else None

    variaciones = {}
    for etiqueta, dias in (("7d", 7), ("30d", 30), ("365d", 365)):
        previo = valor_hace(dias)
        variaciones[etiqueta] = round((ultimo["venta"] / previo - 1) * 100, 2) if previo else None
    return {"fecha": ultimo["fecha"], "venta": ultimo["venta"], "variacion_pct": variaciones}
