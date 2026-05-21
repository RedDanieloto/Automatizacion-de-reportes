from datetime import datetime, timedelta
from api import _calcular_abiertos_historicos
import pandas as pd
from config import RUTA_DATOS

ayer = datetime.now() - timedelta(days=1)
print("Ayer:", ayer)
print("Resultado de _calcular_abiertos_historicos:", _calcular_abiertos_historicos(ayer, ayer))

try:
    df = pd.read_excel(RUTA_DATOS, dtype=str)
    print("Columnas:", list(df.columns))
except Exception as e:
    print("Error leyendo:", e)

