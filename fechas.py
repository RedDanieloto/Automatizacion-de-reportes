from datetime import datetime, timedelta

def seleccionar_rango():
    print("\n¿Qué reporte quieres generar?\n")
    print("1. Diario (ayer)")
    print("2. Semanal (semana pasada)")
    print("3. Mensual (mes pasado)\n")

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
        inicio = (hoy.replace(day=1) - timedelta(days=1)).replace(day=1)
        fin = hoy.replace(day=1) - timedelta(days=1)
        tipo = "mensual"

    else:
        print("Opción inválida")
        return seleccionar_rango()

    return inicio, fin, tipo