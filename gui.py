import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import threading
import os
from datetime import datetime, timedelta

from procesar import procesar_datos
from excel import actualizar_excel
from api import obtener_kpis, descargar_excel_datos

def seleccionar_ruta():
    directorio = filedialog.askdirectory(title="Selecciona la carpeta de destino")
    if directorio:
        ruta_salida_var.set(directorio)

def seleccionar_plantilla():
    # Solo filtra archivos de Excel
    archivo = filedialog.askopenfilename(
        title="Selecciona el archivo de la plantilla",
        filetypes=[("Archivos de Excel habilitados para macros", "*.xlsm"), ("Todos los archivos de Excel", "*.xls*")]
    )
    if archivo:
        ruta_plantilla_var.set(archivo)

def procesar_reporte(opcion):
    hoy = datetime.now()
    ruta_salida = ruta_salida_var.get()
    ruta_plantilla = ruta_plantilla_var.get()
    area_seleccionada = area_var.get()
    
    # Sewing = 1, Cutting = 2
    area_id = 1 if area_seleccionada == "SEWING" else 2

    try:
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
            estado_var.set(f"Descargando datos de {area_seleccionada}...")
            descargar_excel_datos(area_id)
            estado_var.set("Datos actualizados correctamente.")
            messagebox.showinfo("Éxito", f"Los datos de {area_seleccionada} se han descargado e integrado.")
            return
        else:
            return

        # Descarga automática en segundo plano para garantizar precisión en tiempo real
        estado_var.set(f"Descargando últimos datos de {area_seleccionada}...")
        descargar_excel_datos(area_id)

        estado_var.set(f"Generando reporte {tipo}...")
        
        # Lógica de creación del reporte
        df_mes, df_dia = procesar_datos(inicio, fin)
        estado_var.set(f"Obteniendo KPIs para reporte {tipo}...")
        
        # Enviar también el query param del area
        kpis = obtener_kpis(inicio, fin, area_id)
        
        estado_var.set(f"Actualizando Excel y generando PDF...")
        
        archivo = actualizar_excel(df_mes, df_dia, kpis, inicio, fin, tipo, ruta_salida=ruta_salida, ruta_plantilla=ruta_plantilla, area=area_seleccionada)
        
        estado_var.set(f"Reporte {tipo} generado.")
        messagebox.showinfo("Éxito", f"Reporte listo y guardado en:\n{archivo}")
        
    except Exception as e:
        estado_var.set("Error en el proceso.")
        messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")
    finally:
        app.after(0, detener_loader)
        app.after(0, habilitar_botones)

def iniciar_hilo(opcion):
    if not ruta_salida_var.get():
        messagebox.showwarning("Advertencia", "Por favor selecciona una ruta de destino primero.")
        return
    deshabilitar_botones()
    progress_bar.start(10)  # Inicia la animación del loader
    hilo = threading.Thread(target=procesar_reporte, args=(opcion,))
    hilo.start()

def detener_loader():
    progress_bar.stop()

def deshabilitar_botones():
    btn_diario.config(state=tk.DISABLED)
    btn_semanal.config(state=tk.DISABLED)
    btn_mensual.config(state=tk.DISABLED)
    btn_actualizar.config(state=tk.DISABLED)
    btn_ruta.config(state=tk.DISABLED)
    btn_plantilla.config(state=tk.DISABLED)
    radio_sewing.config(state=tk.DISABLED)
    radio_cutting.config(state=tk.DISABLED)

def habilitar_botones():
    btn_diario.config(state=tk.NORMAL)
    btn_semanal.config(state=tk.NORMAL)
    btn_mensual.config(state=tk.NORMAL)
    btn_actualizar.config(state=tk.NORMAL)
    btn_ruta.config(state=tk.NORMAL)
    btn_plantilla.config(state=tk.NORMAL)
    radio_sewing.config(state=tk.NORMAL)
    radio_cutting.config(state=tk.NORMAL)

# --- CONFIGURACION VENTANA ---
app = tk.Tk()
app.title("Generador de Reportes")
app.geometry("450x550")
app.resizable(False, False)

# --- VARIABLES ---
from config import RUTA_DASHBOARD, RUTA_OUTPUT
ruta_salida_var = tk.StringVar()
ruta_salida_var.set(os.path.abspath(RUTA_OUTPUT))  # Por defecto apunta a output/

ruta_plantilla_var = tk.StringVar()
ruta_plantilla_var.set(os.path.abspath(RUTA_DASHBOARD)) # Plantilla por defecto

area_var = tk.StringVar()
area_var.set("SEWING")  # Área por defecto

# --- ESTILOS ---
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 11), padding=6)
style.configure("TLabel", font=("Helvetica", 12))

# --- INTERFAZ ---
titulo = ttk.Label(app, text="¿Qué proceso deseas realizar?", font=("Helvetica", 14, "bold"))
titulo.pack(pady=(15, 10))

# Fila de selección de Área
frame_area = tk.Frame(app)
frame_area.pack(fill="x", padx=30, pady=5)
lbl_area = tk.Label(frame_area, text="Área:", font=("Helvetica", 10, "bold"), width=10, anchor="w")
lbl_area.pack(side=tk.LEFT)
radio_sewing = ttk.Radiobutton(frame_area, text="Sewing", variable=area_var, value="SEWING")
radio_sewing.pack(side=tk.LEFT, padx=10)
radio_cutting = ttk.Radiobutton(frame_area, text="Cutting", variable=area_var, value="CUTTING")
radio_cutting.pack(side=tk.LEFT, padx=10)

# Fila de selección de plantilla
frame_plantilla = tk.Frame(app)
frame_plantilla.pack(fill="x", padx=30, pady=5)
lbl_plantilla = tk.Label(frame_plantilla, text="Plantilla:", font=("Helvetica", 10, "bold"), width=10, anchor="w")
lbl_plantilla.pack(side=tk.LEFT)
entr_plantilla = tk.Entry(frame_plantilla, textvariable=ruta_plantilla_var, state="readonly", fg="gray")
entr_plantilla.pack(side=tk.LEFT, fill="x", expand=True, ipady=3)
btn_plantilla = ttk.Button(frame_plantilla, text="Elegir Archivo", command=seleccionar_plantilla)
btn_plantilla.pack(side=tk.RIGHT, padx=5)

# Fila de selección de ruta
frame_ruta = tk.Frame(app)
frame_ruta.pack(fill="x", padx=30, pady=5)
lbl_ruta = tk.Label(frame_ruta, text="Guardar en:", font=("Helvetica", 10, "bold"), width=10, anchor="w")
lbl_ruta.pack(side=tk.LEFT)
entr_ruta = tk.Entry(frame_ruta, textvariable=ruta_salida_var, state="readonly", fg="gray")
entr_ruta.pack(side=tk.LEFT, fill="x", expand=True, ipady=3)
btn_ruta = ttk.Button(frame_ruta, text="Elegir Carpeta", command=seleccionar_ruta)
btn_ruta.pack(side=tk.RIGHT, padx=5)

# Botones de Acción
btn_diario = ttk.Button(app, text="1. Reporte Diario (Ayer)", command=lambda: iniciar_hilo("1"))
btn_diario.pack(fill="x", padx=50, pady=5)

btn_semanal = ttk.Button(app, text="2. Reporte Semanal", command=lambda: iniciar_hilo("2"))
btn_semanal.pack(fill="x", padx=50, pady=5)

btn_mensual = ttk.Button(app, text="3. Reporte Mensual", command=lambda: iniciar_hilo("3"))
btn_mensual.pack(fill="x", padx=50, pady=5)

btn_actualizar = ttk.Button(app, text="4. Descargar / Actualizar Data", command=lambda: iniciar_hilo("4"))
btn_actualizar.pack(fill="x", padx=50, pady=15)

# Barra de progreso (Loader)
progress_bar = ttk.Progressbar(app, mode='indeterminate', length=200)
progress_bar.pack(pady=5)

estado_var = tk.StringVar()
estado_var.set("Esperando acción...")
lbl_estado = ttk.Label(app, textvariable=estado_var, font=("Helvetica", 10, "italic"), foreground="gray")
lbl_estado.pack(side=tk.BOTTOM, pady=(0, 15))

app.mainloop()