# API Dólar AR

API pública y gratuita con las cotizaciones del dólar en Argentina (oficial, blue, MEP, CCL, mayorista, cripto y tarjeta). No tiene servidor: una GitHub Action la regenera todos los días y GitHub Pages la sirve como JSON estático.

**Demo y documentación:** https://nbbz95.github.io/api-dolar-ar/

## Endpoints

| Endpoint | Devuelve |
|---|---|
| `GET /v1/dolares.json` | Cotización actual de cada casa |
| `GET /v1/brecha.json` | Brecha porcentual de cada casa contra el oficial |
| `GET /v1/historico/{casa}.json` | Serie diaria completa (compra y venta) |
| `GET /v1/resumen/{casa}.json` | Último valor y variación a 7, 30 y 365 días |
| `GET /v1/index.json` | Casas disponibles y fecha de generación |

Ejemplo:

```bash
curl https://nbbz95.github.io/api-dolar-ar/v1/resumen/blue.json
```

```json
{ "fecha": "2026-10-28", "venta": 1575, "variacion_pct": { "7d": -1.25, "30d": 2.1, "365d": 12.3 } }
```

(valores ilustrativos)

## Arquitectura

```
cron diario (GitHub Actions)
  → api_dolar/generar.py descarga DolarApi y ArgentinaDatos
  → api_dolar/transformar.py normaliza, deduplica y calcula brecha y variaciones
  → escribe JSON en site/v1/
  → deploy a GitHub Pages
```

- La lógica de transformación es pura (sin red) y está cubierta con tests en `tests/`, que usan fixtures reales.
- Si falla el histórico de una casa, se publica el resto igual.
- Solo usa la librería estándar de Python.

## Correr localmente

```bash
python -m pytest -q                       # tests
python -m api_dolar.generar --destino site
python -m http.server -d site 8000        # http://localhost:8000
```

## Fuentes

[DolarApi](https://dolarapi.com) para la cotización actual y [ArgentinaDatos](https://argentinadatos.com) para el histórico.
