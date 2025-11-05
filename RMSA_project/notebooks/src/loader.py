import os
import json
import pandas as pd
import numpy as np
import networkx as nx
from networkx.exception import NetworkXNoPath

def load_routes_from_dir(directory):
    """Carga el primer archivo .json en `directory` que contenga rutas.
    Devuelve: (routes_df, enlaces_array, rutas_usuarios_array)
    """
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directorio no encontrado: {directory}")
    archivos = os.listdir(directory)
    json_file = None
    for a in archivos:
        if a.endswith('.json'):
            json_file = os.path.join(directory, a)
            break
    if json_file is None:
        raise FileNotFoundError(f"No se encontró archivo .json en {directory}")
    routes_data = pd.read_json(json_file)
    routes_df = pd.json_normalize(routes_data['routes'])
    # Mantener sólo el primer path por entrada (como en la T2 original)
    routes_df['paths'] = routes_df['paths'].apply(lambda paths: [paths[0]] if len(paths) > 0 else [])
    enlaces = obtener_enlaces_directos(routes_df)
    rutas_usuarios = crear_rutas_usuarios(routes_df, enlaces)
    return routes_df, enlaces, rutas_usuarios

def obtener_enlaces_directos(routes_df):
    """Extrae enlaces directos (pares de nodos consecutivos) como lista única.
    Retorna un numpy.array de shape (n_enlaces, 2) con tuplas (src,dst).
    """
    enlaces = []
    for path_list in routes_df['paths']:
        for path in path_list:
            for i in range(len(path) - 1):
                enlace = (path[i], path[i+1])
                if enlace not in enlaces:
                    enlaces.append(enlace)
    return np.array(enlaces)

def crear_rutas_usuarios(routes_df, enlaces):
    """Convierte rutas de nodos a rutas de índices de enlaces (llenando con -1).
    Resultado: numpy array int16 (n_rutas x max_len)
    """
    enlaces_tuplas = [tuple(e) for e in enlaces]
    rutas_usuarios = []
    for path_list in routes_df['paths']:
        path = path_list[0]
        indices = []
        for i in range(len(path) - 1):
            enlace = (path[i], path[i+1])
            idx = enlaces_tuplas.index(enlace)
            indices.append(idx)
        rutas_usuarios.append(indices)
    if len(rutas_usuarios) == 0:
        return np.empty((0, 0), dtype=np.int16)
    max_len = max(len(r) for r in rutas_usuarios)
    rutas_usuarios_arr = np.full((len(rutas_usuarios), max_len), -1, dtype=np.int16)
    for i, ruta in enumerate(rutas_usuarios):
        rutas_usuarios_arr[i, :len(ruta)] = ruta
    return rutas_usuarios_arr

def load_distance_file(file_path):
    """Carga archivo de distancias tipo tabular (csv/tsv) y retorna DataFrame.
    Acepta archivos con cabecera o tablas separadas por tabulador.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)
    try:
        df = pd.read_csv(file_path, sep='\t')
    except Exception:
        df = pd.read_csv(file_path, sep='\s+')
    return df

if __name__ == '__main__':
    # Pequeña prueba manual si se ejecuta directamente
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    ruta = os.path.join(base, 'Rutas', 'Eurocore')
    print('Intentando cargar rutas desde', ruta)
    routes_df, enlaces, rutas_usuarios = load_routes_from_dir(ruta)
    print('Rutas cargadas:', len(routes_df))
    print('Enlaces encontrados:', len(enlaces))

def load_topology_file(file_path):
    """Carga un archivo de topología en formatos comunes (graphml, gml, json, edgelist).
    Retorna un networkx.Graph.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)
    lower = file_path.lower()
    if lower.endswith('.graphml'):
        G = nx.read_graphml(file_path)
    elif lower.endswith('.gml'):
        G = nx.read_gml(file_path)
    elif lower.endswith('.json'):
        # intentar como node-link JSON
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            G = nx.node_link_graph(data)
        except Exception:
            # intentar como lista de aristas
            G = nx.read_edgelist(file_path)
    else:
        # por defecto intentar como edgelist
        G = nx.read_edgelist(file_path)
    return G

def graph_from_enlaces(enlaces):
    """Construye un networkx.Graph a partir de un array de enlaces [(u,v), ...].
    Asume que los nodos en los enlaces son enteros.
    """
    G = nx.Graph()
    for u, v in enlaces:
        G.add_edge(int(u), int(v))
    return G

def build_k_shortest_routes_from_graph(G, k=3, weight=None):
    """Genera hasta k rutas por cada par (u,v) usando shortest_simple_paths.
    Retorna una lista de dicts: { 'src': u, 'dst': v, 'paths': [ [nodos...], ... ] }
    Nota: puede ser costoso para grafos grandes; utiliza k pequeño.
    """
    nodes = list(G.nodes())
    routes = []
    for i, src in enumerate(nodes):
        for dst in nodes:
            if src == dst:
                continue
            paths = []
            try:
                generator = nx.shortest_simple_paths(G, src, dst, weight=weight)
                for idx, p in enumerate(generator):
                    if idx >= k:
                        break
                    paths.append([int(n) for n in p])
            except NetworkXNoPath:
                paths = []
            routes.append({'src': int(src), 'dst': int(dst), 'paths': paths})
    return routes

def routes_df_from_graph(G, k=3, weight=None):
    """Construye un DataFrame con columnas ['src','dst','paths'] a partir del grafo G.
    """
    routes = build_k_shortest_routes_from_graph(G, k=k, weight=weight)
    df = pd.DataFrame(routes)
    return df

def load_topology_bench_dir(directory, k=3):
    """Busca archivos de topología en `directory` y construye routes_df, enlaces, rutas_usuarios.
    Soporta archivos graphml, gml, json o edgelist. Si no encuentra archivos, lanza FileNotFoundError.
    """
    if not os.path.isdir(directory):
        raise FileNotFoundError(directory)
    files = os.listdir(directory)
    topo_file = None
    for f in files:
        if f.lower().endswith(('.graphml', '.gml', '.json', '.edgelist', '.txt')):
            topo_file = os.path.join(directory, f)
            break
    if topo_file is None:
        raise FileNotFoundError(f"No topology file found in {directory}")
    G = load_topology_file(topo_file)
    routes_df = routes_df_from_graph(G, k=k)
    # Obtener enlaces únicos a partir del grafo
    enlaces = np.array([ (int(u), int(v)) for u, v in G.edges() ])
    rutas_usuarios = crear_rutas_usuarios(routes_df, enlaces) if len(routes_df)>0 else np.empty((0,0), dtype=np.int16)
    return routes_df, enlaces, rutas_usuarios
