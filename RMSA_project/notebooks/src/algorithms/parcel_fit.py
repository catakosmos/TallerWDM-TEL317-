import numpy as np

def allocate_parcel_fit(capacity, route_row, demand, parcel_size=2):
    """Parcel-Fit simple:
    - Intenta asignar bloques contiguos de tamaño `parcel_size` hasta cubrir `demand`.
    - Si la demanda no es múltiplo de parcel_size, la última parcela puede ser más pequeña.
    - Parcels pueden ubicarse en distintas posiciones (no necesariamente contiguas entre sí).
    Nota: este es un simplificado Parcel-Fit para experimento inicial.
    """
    route_indices = [int(e) for e in route_row if int(e) != -1]
    if len(route_indices) == 0:
        return [], False
    n_slots = capacity.shape[1]
    if demand > n_slots:
        return [], False
    # Crear lista de parcelas
    parcels = []
    remaining = demand
    while remaining > 0:
        size = min(parcel_size, remaining)
        parcels.append(size)
        remaining -= size

    allocations = []
    # Para cada parcela, buscar primer fit libre (como FF) y asignar
    for p in parcels:
        assigned = False
        for start in range(0, n_slots - p + 1):
            ok = True
            end = start + p
            for e in route_indices:
                if np.any(capacity[e, start:end] != 0):
                    ok = False
                    break
            if ok:
                # asignar parcela
                for e in route_indices:
                    capacity[e, start:end] = 1
                allocations.append((start, p))
                assigned = True
                break
        if not assigned:
            # revertir asignaciones previas
            for (s, l) in allocations:
                for e in route_indices:
                    capacity[e, s:s+l] = 0
            return [], False
    return allocations, True
