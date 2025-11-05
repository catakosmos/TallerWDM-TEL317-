import numpy as np

def allocate_sliding_fit(capacity, route_row, demand):
    """Sliding-Fit simple:
    - Busca todas las posiciones donde la demanda cabe (como FF),
      y elige la que esté más cerca del centro del espectro (minimizar distancia al centro).
    - Idea: reducir fragmentación moviendo asignaciones hacia el centro.
    """
    route_indices = [int(e) for e in route_row if int(e) != -1]
    if len(route_indices) == 0:
        return -1, False
    n_slots = capacity.shape[1]
    if demand > n_slots:
        return -1, False

    center = (n_slots - demand) / 2.0
    best_start = -1
    best_score = None
    for start in range(0, n_slots - demand + 1):
        end = start + demand
        ok = True
        for e in route_indices:
            if np.any(capacity[e, start:end] != 0):
                ok = False
                break
        if ok:
            score = abs(start - center)
            if best_score is None or score < best_score:
                best_score = score
                best_start = start
    if best_start == -1:
        return -1, False
    for e in route_indices:
        capacity[e, best_start:best_start + demand] = 1
    return best_start, True
