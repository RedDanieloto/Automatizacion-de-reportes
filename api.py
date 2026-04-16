import requests
from config import BASE_URL, RUTA_DATOS
from datetime import datetime, timedelta

def descargar_excel_datos():
    hoy = datetime.now()
    primer_dia = hoy.replace(day=1)
    
    # Calcular ultimo dia del mes
    if primer_dia.month == 12:
        siguiente_mes = primer_dia.replace(year=primer_dia.year + 1, month=1)
    else:
        siguiente_mes = primer_dia.replace(month=primer_dia.month + 1)
    ultimo_dia = siguiente_mes - timedelta(days=1)
    
    url = "https://tiemposapi.danito.tech/api/areas/1/reportes/exportarexcel"
    params = {
        "from": primer_dia.strftime("%Y-%m-%d"),
        "to": ultimo_dia.strftime("%Y-%m-%d")
    }
    
    print(f"Descargando datos actualizados del {params['from']} al {params['to']}...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        with open(RUTA_DATOS, "wb") as f:
            f.write(response.content)
        print("Datos guardados exitosamente en", RUTA_DATOS)
    else:
        print("Error al descargar los datos. Status:", response.status_code)

def obtener_kpis(inicio, fin):
    params = {
        "inicio": inicio.strftime("%Y-%m-%d"),
        "fin": fin.strftime("%Y-%m-%d")
    }

    mttr = requests.get(f"{BASE_URL}/mttr", params=params).json()
    mtbf = requests.get(f"{BASE_URL}/mtbf", params=params).json()
    downtime = requests.get(f"{BASE_URL}/tiempo-total", params=params).json()
    abiertos = requests.get(f"{BASE_URL}/reportes-abiertos", params=params).json()

    return {
        "mttr": mttr,
        "mtbf": mtbf,
        "downtime": downtime,
        "abiertos": abiertos
    }