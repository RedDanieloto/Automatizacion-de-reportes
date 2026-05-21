from datetime import datetime, timedelta
from procesar import procesar_datos
from excel import actualizar_excel
from api import obtener_kpis, descargar_excel_datos

def main():
    print("""
¿Qué reporte quieres generar?

1. Diario (ayer)
2. Semanal (semana pasada)
3. Mensual (desde el día 1 hasta hoy)
4. Actualizar data (Descargar archivo Excel)
""")

    opcion = input("Selecciona una opción (1/2/3/4): ")

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

    elif opcion == "4":
        print("\nActualizando datos...")
        descargar_excel_datos()
        return

    else:
        print("Opción inválida")
        return

    print("\nIniciando proceso...")
    print("Descargando últimos datos...")
    descargar_excel_datos()  # Descarga automática por defecto (area_id=1)

    print("Generando reporte...")

    df_mes, df_dia = procesar_datos(inicio, fin)

    kpis = obtener_kpis(inicio, fin)  # Obtiene los KPIs de todo el rango seleccionado

    archivo = actualizar_excel(df_mes, df_dia, kpis, inicio, fin, tipo)

    print(f"Reporte listo: {archivo}")


if __name__ == "__main__":
    main()