# RMSA Project

Proyecto inicial para análisis comparativo topológico de algoritmos RMSA en redes ópticas elásticas (EON).

Estructura mínima:
- `src/` : código fuente (loader, algoritmos, utilidades)
- `notebooks/` : notebooks de experimentos
- `tests/` : pruebas unitarias
- `requirements.txt` : dependencias

Cómo probar (desde la raíz del proyecto `T2`):

1. Instalar dependencias:

```bash
pip install -r RMSA_project/requirements.txt
```

2. Ejecutar pruebas:

```bash
python -m pytest RMSA_project/tests -q
```

Este repositorio añade un loader que reutiliza las rutas existentes en `Rutas/*`.
