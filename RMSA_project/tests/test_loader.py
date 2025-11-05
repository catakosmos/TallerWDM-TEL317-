import os
import sys

# Asegurar que la raíz del proyecto esté en sys.path para poder importar `src` durante los tests
base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if base not in sys.path:
    sys.path.insert(0, base)

from src.loader import load_routes_from_dir


def test_load_eurocore_exists_and_shapes():
    ruta = os.path.join(base, 'Rutas', 'Eurocore')
    routes_df, enlaces, rutas_usuarios = load_routes_from_dir(ruta)
    assert len(routes_df) > 0
    assert enlaces.shape[0] > 0
    assert rutas_usuarios.shape[0] == len(routes_df)
