import numpy as np

def find_first_fit_and_allocate(capacity, route_row, demand):
    """Busca el primer bloque contiguo de `demand` ranuras libre en todos los enlaces de la ruta.
    - capacity: np.array shape (n_enlaces, n_slots) con 0=libre,1=ocupado
    - route_row: iterable de indices de enlaces (puede contener -1 al final)
    - demand: int, número de ranuras contiguas requeridas

    Retorna: (start_index, True) si se asignó y start_index es la posición; (-1, False) si fallo.
    Modifica `capacity` in-place cuando asigna.
    """
    route_indices = [int(e) for e in route_row if int(e) != -1]
    if len(route_indices) == 0:
        return -1, False
    n_slots = capacity.shape[1]
    if demand > n_slots:
        return -1, False
    for start in range(0, n_slots - demand + 1):
        ok = True
        end = start + demand
        for e in route_indices:
            if np.any(capacity[e, start:end] != 0):
                ok = False
                break
        if ok:
            for e in route_indices:
                capacity[e, start:end] = 1
            return start, True
    return -1, False
