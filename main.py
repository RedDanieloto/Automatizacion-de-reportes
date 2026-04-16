from datetime import datetime, timedelta
from procesar import procesar_datos
from excel import actualizar_excel
from api import obtener_kpis   # 🔥 ESTE ES EL BUENO

def main():
    print("""
¿Qué reporte quieres generar?

1. Diario (ayer)
2. Semanal
3. Mensual
""")

    opcion = input("Selecciona una opción (1/2/3): ")

    hoy = datetime.now()

    if opcion == "1":
        inicio = hoy - timedelta(days=1)
        fin = inicio
        tipo = "diario"

    elif opcion == "2":
        inicio = hoy - timedelta(days=7)
        fin = hoy - timedelta(days=1)
        tipo = "semanal"

    elif opcion == "3":
        inicio = hoy.replace(day=1)
        fin = hoy
        tipo = "mensual"

    else:
        print("Opción inválida")
        return

    print("Generando reporte...")

    df_mes, df_dia = procesar_datos(inicio, fin)

    kpis = obtener_kpis(inicio, inicio)  # SOLO día

    archivo = actualizar_excel(df_mes, df_dia, kpis, inicio, fin, tipo)

    print(f"Reporte listo: {archivo}")


if __name__ == "__main__":
    main()