def calcular_kpis(df):
    if df.empty:
        return {
            "mttr": 0,
            "mtbf": 0,
            "downtime": 0,
            "abiertos": 0
        }

    total_reparacion = df["T. Mantenimiento (min)"].sum()
    total_fallas = len(df)

    mttr = (total_reparacion / total_fallas) / 60 if total_fallas else 0

    total_tiempo = df["T. Total (min)"].sum() / 60

    mtbf = total_tiempo / total_fallas if total_fallas else 0

    abiertos = 0  # ajusta si tienes lógica

    return {
        "mttr": mttr,
        "mtbf": mtbf,
        "downtime": total_tiempo,
        "abiertos": abiertos
    }