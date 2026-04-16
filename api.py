import requests
from config import BASE_URL

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