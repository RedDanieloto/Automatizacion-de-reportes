import requests
import os
import pandas as pd
from config import BASE_URL, RUTA_DATOS
from datetime import datetime, timedelta


def _construir_respuesta_abiertos(abiertos, inicio, fin, fuente="local_historico"):
    return {
        "app": "local",
        "timestamp": datetime.now().isoformat(),
        "periodo": {
            "desde": inicio.strftime("%Y-%m-%d"),
            "hasta": fin.strftime("%Y-%m-%d")
        },
        "data": {
            "reportes_abiertos": {
                "total_activos": int(abiertos),
                "abiertos": int(abiertos),
                "en_mantenimiento": 0
            },
            "contexto": {
                "fuente": fuente
            }
        }
    }


def _calcular_abiertos_historicos(inicio, fin, area_id=1):
    if not os.path.exists(RUTA_DATOS):
        return None

    try:
        df = pd.read_excel(RUTA_DATOS, dtype=str)
        df.columns = df.columns.str.strip()

        if "Inicio" not in df.columns or "Fin" not in df.columns:
            return None

        df["Inicio"] = pd.to_datetime(df["Inicio"], errors="coerce")
        df["Fin"] = pd.to_datetime(df["Fin"], errors="coerce")
        df = df[df["Inicio"].notna()].copy()

        # Filtrado opcional por area si existe la columna y hay coincidencias.
        mapa_areas = {
            1: ["costura", "sewing"],
            2: ["corte", "cutting"]
        }
        if "Área" in df.columns and area_id in mapa_areas:
            patron = "|".join(mapa_areas[area_id])
            area_col = df["Área"].fillna("").astype(str).str.strip().str.lower()
            df_area = df[area_col.str.contains(patron, na=False)]
            if not df_area.empty:
                df = df_area

        corte = fin.replace(hour=23, minute=59, second=59, microsecond=999999)
        abiertos = df[(df["Inicio"] <= corte) & (df["Fin"].isna() | (df["Fin"] > corte))]

        return int(len(abiertos))
    except Exception as e:
        print(f"No se pudo calcular abiertos historicos: {e}")
        return None

def descargar_excel_datos(area_id=1):
    hoy = datetime.now()
    
    # Calcular el primer día del mes anterior
    if hoy.month == 1:
        primer_dia_prev = hoy.replace(year=hoy.year - 1, month=12, day=1)
    else:
        primer_dia_prev = hoy.replace(month=hoy.month - 1, day=1)
        
    # Calcular el último día del mes actual
    primer_dia_act = hoy.replace(day=1)
    if primer_dia_act.month == 12:
        siguiente_mes = primer_dia_act.replace(year=primer_dia_act.year + 1, month=1)
    else:
        siguiente_mes = primer_dia_act.replace(month=primer_dia_act.month + 1)
    ultimo_dia_act = siguiente_mes - timedelta(days=1)
    
    url = f"https://tiemposapi.danito.tech/api/areas/{area_id}/reportes/exportarexcel"
    params = {
        "from": primer_dia_prev.strftime("%Y-%m-%d"),
        "to": ultimo_dia_act.strftime("%Y-%m-%d")
    }
    
    print(f"Descargando datos actualizados del {params['from']} al {params['to']}...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # Crear la carpeta data si no existe
        os.makedirs(os.path.dirname(RUTA_DATOS), exist_ok=True)
        with open(RUTA_DATOS, "wb") as f:
            f.write(response.content)
        print("Datos guardados exitosamente en", RUTA_DATOS)
    else:
        print("Error al descargar los datos. Status:", response.status_code)

def obtener_kpis(inicio, fin, area_id=1):
    params = {
        "inicio": inicio.strftime("%Y-%m-%d"),
        "fin": fin.strftime("%Y-%m-%d"),
        "area_id": area_id
    }

    mttr = requests.get(f"{BASE_URL}/mttr", params=params).json()
    mtbf = requests.get(f"{BASE_URL}/mtbf", params=params).json()
    downtime = requests.get(f"{BASE_URL}/tiempo-total", params=params).json()
    abiertos = requests.get(f"{BASE_URL}/reportes-abiertos", params=params).json()

    # Para periodos cerrados (ayer/semana pasada), usa valor historico al cierre de 'fin'.
    if fin.date() < datetime.now().date():
        abiertos_historicos = _calcular_abiertos_historicos(inicio, fin, area_id)
        if abiertos_historicos is not None:
            abiertos = _construir_respuesta_abiertos(abiertos_historicos, inicio, fin)

    return {
        "mttr": mttr,
        "mtbf": mtbf,
        "downtime": downtime,
        "abiertos": abiertos
    }