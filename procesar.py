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
    inicio_mes = inicio.replace(day=1)

    df_mes = df[
        (df["Inicio"] >= inicio_mes) &
        (df["Inicio"] <= fin)
    ]

    # =========================
    # 🔥 KPIs → SOLO EL DÍA
    # =========================
    df_dia = df[
        (df["Inicio"].dt.date == inicio.date())
    ]

    return df_mes, df_dia