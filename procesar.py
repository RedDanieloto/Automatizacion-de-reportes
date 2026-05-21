import pandas as pd
from config import RUTA_DATOS

def procesar_datos(inicio, fin):
    # 🔥 leer como texto
    df = pd.read_excel(RUTA_DATOS, dtype=str)

    # limpiar columnas
    df.columns = df.columns.str.strip()

    # fechas
    df["Inicio"] = pd.to_datetime(df["Inicio"], errors="coerce")
    df["Fin"] = pd.to_datetime(df["Fin"], errors="coerce")

    # numéricos
    cols_numericas = [
        "T. Reacción (min)",
        "T. Mantenimiento (min)",
        "T. Total (min)"
    ]

    for col in cols_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # =========================
    # 🔥 BD → TODO EL MES
    # =========================
    import datetime as dt
    inicio_mes = dt.datetime.combine(inicio.replace(day=1).date(), dt.time.min)
    fin_completo = dt.datetime.combine(fin.date(), dt.time.max)

    df_mes = df[
        (df["Inicio"] >= inicio_mes) &
        (df["Inicio"] <= fin_completo)
    ]

    # =========================
    # 🔥 BD → RANGO SELECCIONADO (DIA, SEMANA O MES)
    # =========================
    inicio_completo = dt.datetime.combine(inicio.date(), dt.time.min)

    df_dia = df[
        (df["Inicio"] >= inicio_completo) &
        (df["Inicio"] <= fin_completo)
    ]

    return df_mes, df_dia