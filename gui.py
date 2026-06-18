import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import threading
import os
import json
import time
from datetime import datetime, timedelta

from procesar import procesar_datos
from excel import actualizar_excel
from api import obtener_kpis, descargar_excel_datos
from config import RUTA_BASE, RUTA_DASHBOARD, RUTA_OUTPUT

RUTA_CONFIG_JSON = os.path.join(RUTA_BASE, "config_rutas.json")

def cargar_configuracion_rutas():
    # Valores por defecto iniciales
    def_sewing_plantilla = os.path.abspath(RUTA_DASHBOARD)
    def_sewing_salida = os.path.abspath(RUTA_OUTPUT)
    
    # Intentar buscar una plantilla de corte en la misma ruta
    corte_plantilla_sugerida = RUTA_DASHBOARD.replace("COSTURA", "CORTE")
    if not os.path.exists(corte_plantilla_sugerida):
        # Si no existe, usar la misma de costura
        corte_plantilla_sugerida = def_sewing_plantilla
        
    def_cutting_plantilla = os.path.abspath(corte_plantilla_sugerida)
    def_cutting_salida = os.path.abspath(RUTA_OUTPUT)
    
    config_defecto = {
        "SEWING": {
            "plantilla": def_sewing_plantilla,
            "salida": def_sewing_salida
        },
        "CUTTING": {
            "plantilla": def_cutting_plantilla,
            "salida": def_cutting_salida
        },
        "last_auto_run": "",
        "last_auto_status": "Nunca ejecutado"
    }
    
    if os.path.exists(RUTA_CONFIG_JSON):
        try:
            with open(RUTA_CONFIG_JSON, "r", encoding="utf-8") as f:
                config_guardada = json.load(f)
                # Combinar con los valores por defecto en caso de que falte alguna clave
                for area in ["SEWING", "CUTTING"]:
                    if area not in config_guardada:
                        config_guardada[area] = config_defecto[area]
                    else:
                        for k in ["plantilla", "salida"]:
                            if k not in config_guardada[area]:
                                config_guardada[area][k] = config_defecto[area][k]
                if "last_auto_run" not in config_guardada:
                    config_guardada["last_auto_run"] = config_defecto["last_auto_run"]
                if "last_auto_status" not in config_guardada:
                    config_guardada["last_auto_status"] = config_defecto["last_auto_status"]
                return config_guardada
        except Exception as e:
            print("Error al cargar config_rutas.json, usando valores por defecto:", e)
            
    return config_defecto

def guardar_configuracion_rutas(config):
    try:
        with open(RUTA_CONFIG_JSON, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Error al guardar config_rutas.json:", e)

# Cargar configuración global al iniciar
config_rutas = cargar_configuracion_rutas()

def seleccionar_ruta():
    directorio = filedialog.askdirectory(title="Selecciona la carpeta de destino")
    if directorio:
        ruta_salida_var.set(directorio)
        area_seleccionada = area_var.get()
        config_rutas[area_seleccionada]["salida"] = directorio
        guardar_configuracion_rutas(config_rutas)

def seleccionar_plantilla():
    # Solo filtra archivos de Excel
    archivo = filedialog.askopenfilename(
        title="Selecciona el archivo de la plantilla",
        filetypes=[("Archivos de Excel habilitados para macros", "*.xlsm"), ("Todos los archivos de Excel", "*.xls*")]
    )
    if archivo:
        ruta_plantilla_var.set(archivo)
        area_seleccionada = area_var.get()
        config_rutas[area_seleccionada]["plantilla"] = archivo
        guardar_configuracion_rutas(config_rutas)

def cambiar_area():
    area_seleccionada = area_var.get()
    ruta_plantilla_var.set(config_rutas[area_seleccionada]["plantilla"])
    ruta_salida_var.set(config_rutas[area_seleccionada]["salida"])

def ultimo_dia_del_mes(year, month):
    if month == 12:
        return datetime(year, 12, 31)
    return datetime(year, month + 1, 1) - timedelta(days=1)

def crear_selector_fecha(parent, pref_fecha=None):
    if pref_fecha is None:
        pref_fecha = datetime.now()
    
    frame = tk.Frame(parent)
    
    año_actual = datetime.now().year
    años = [str(a) for a in range(2020, año_actual + 2)]
    
    cb_año = ttk.Combobox(frame, values=años, width=6, state="readonly")
    cb_año.set(str(pref_fecha.year))
    cb_año.pack(side=tk.LEFT, padx=2)
    
    lbl_sep1 = tk.Label(frame, text="-")
    lbl_sep1.pack(side=tk.LEFT)
    
    meses = [f"{m:02d}" for m in range(1, 13)]
    cb_mes = ttk.Combobox(frame, values=meses, width=4, state="readonly")
    cb_mes.set(f"{pref_fecha.month:02d}")
    cb_mes.pack(side=tk.LEFT, padx=2)
    
    lbl_sep2 = tk.Label(frame, text="-")
    lbl_sep2.pack(side=tk.LEFT)
    
    días = [f"{d:02d}" for d in range(1, 32)]
    cb_dia = ttk.Combobox(frame, values=días, width=4, state="readonly")
    cb_dia.set(f"{pref_fecha.day:02d}")
    cb_dia.pack(side=tk.LEFT, padx=2)
    
    def obtener_fecha():
        y = int(cb_año.get())
        m = int(cb_mes.get())
        d = int(cb_dia.get())
        return datetime(y, m, d)
        
    return frame, obtener_fecha, cb_año, cb_mes, cb_dia

def crear_selector_mes(parent, pref_fecha=None):
    if pref_fecha is None:
        pref_fecha = datetime.now()
    
    frame = tk.Frame(parent)
    
    año_actual = datetime.now().year
    años = [str(a) for a in range(2020, año_actual + 2)]
    
    cb_año = ttk.Combobox(frame, values=años, width=6, state="readonly")
    cb_año.set(str(pref_fecha.year))
    cb_año.pack(side=tk.LEFT, padx=2)
    
    lbl_sep = tk.Label(frame, text="-")
    lbl_sep.pack(side=tk.LEFT)
    
    meses = [f"{m:02d}" for m in range(1, 13)]
    cb_mes = ttk.Combobox(frame, values=meses, width=4, state="readonly")
    cb_mes.set(f"{pref_fecha.month:02d}")
    cb_mes.pack(side=tk.LEFT, padx=2)
    
    def obtener_anio_mes():
        y = int(cb_año.get())
        m = int(cb_mes.get())
        return y, m
        
    return frame, obtener_anio_mes, cb_año, cb_mes

def ejecutar_reporte_nucleo(inicio, fin, tipo, area_seleccionada, ruta_salida, ruta_plantilla, callback_estado=None):
    # Sewing = 1, Cutting = 2
    area_id = 1 if area_seleccionada == "SEWING" else 2

    if callback_estado:
        callback_estado(f"Descargando últimos datos de {area_seleccionada}...")
    descargar_excel_datos(area_id, inicio=inicio, fin=fin)

    if callback_estado:
        callback_estado(f"Generando reporte {tipo} ({area_seleccionada})...")
    
    df_mes, df_dia = procesar_datos(inicio, fin)
    
    if callback_estado:
        callback_estado(f"Obteniendo KPIs de {area_seleccionada}...")
    kpis = obtener_kpis(inicio, fin, area_id)
    
    if callback_estado:
        callback_estado(f"Actualizando Excel ({area_seleccionada})...")
    
    if ruta_salida and not ruta_salida.endswith('/'):
        ruta_salida += '/'
        
    archivo = actualizar_excel(
        df_mes, df_dia, kpis, inicio, fin, tipo,
        ruta_salida=ruta_salida, ruta_plantilla=ruta_plantilla, area=area_seleccionada
    )
    return archivo

def procesar_reporte(inicio, fin, tipo):
    ruta_salida = ruta_salida_var.get()
    ruta_plantilla = ruta_plantilla_var.get()
    area_seleccionada = area_var.get()

    try:
        def callback_estado(msg):
            estado_var.set(msg)
            
        archivo = ejecutar_reporte_nucleo(
            inicio, fin, tipo, area_seleccionada, ruta_salida, ruta_plantilla, callback_estado
        )
        estado_var.set(f"Reporte {tipo} generado.")
        messagebox.showinfo("Éxito", f"Reporte listo y guardado en:\n{archivo}")
        
    except Exception as e:
        estado_var.set("Error en el proceso.")
        messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")
    finally:
        app.after(0, detener_loader)
        app.after(0, habilitar_botones)

def es_primer_dia_habil_del_mes(fecha):
    if fecha.weekday() >= 5:
        return False
    for d in range(1, fecha.day):
        dia_previo = fecha.replace(day=d)
        if dia_previo.weekday() < 5:
            return False
    return True

def obtener_tipo_reporte_automatizado(fecha):
    if fecha.weekday() >= 5:
        return None, None, None
        
    if es_primer_dia_habil_del_mes(fecha):
        if fecha.month == 1:
            anio_prev = fecha.year - 1
            mes_prev = 12
        else:
            anio_prev = fecha.year
            mes_prev = fecha.month - 1
        inicio = datetime(anio_prev, mes_prev, 1)
        fin = ultimo_dia_del_mes(anio_prev, mes_prev)
        return inicio, fin, "mensual"
        
    if fecha.weekday() == 0:
        inicio = fecha - timedelta(days=7)
        fin = fecha - timedelta(days=1)
        return inicio, fin, "semanal"
        
    inicio = fecha - timedelta(days=1)
    fin = inicio
    return inicio, fin, "diario"

def calcular_proxima_ejecucion(desde=None):
    if desde is None:
        desde = datetime.now()
    hoy_750 = desde.replace(hour=7, minute=50, second=0, microsecond=0)
    if desde < hoy_750 and desde.weekday() < 5:
        if config_rutas.get("last_auto_run") != desde.strftime("%Y-%m-%d"):
            return hoy_750
            
    dia = desde + timedelta(days=1)
    while dia.weekday() >= 5:
        dia += timedelta(days=1)
    return dia.replace(hour=7, minute=50, second=0, microsecond=0)

def ejecutar_automatizacion_programada(ahora):
    inicio, fin, tipo = obtener_tipo_reporte_automatizado(ahora)
    if not tipo:
        return

    app.after(0, deshabilitar_botones)
    app.after(0, lambda: progress_bar.start(10))
    app.after(0, lambda: estado_var.set(f"Automatización: Generando reporte {tipo}..."))
    app.after(0, lambda: lbl_auto_estado_val.config(text="Ejecutando...", fg="orange"))

    sewing_ok = False
    cutting_ok = False

    try:
        # SEWING
        try:
            ejecutar_reporte_nucleo(
                inicio, fin, tipo, "SEWING",
                config_rutas["SEWING"]["salida"],
                config_rutas["SEWING"]["plantilla"],
                lambda msg: app.after(0, lambda: estado_var.set(msg))
            )
            sewing_ok = True
        except Exception as e:
            print("Error automatización SEWING:", e)

        # CUTTING
        try:
            ejecutar_reporte_nucleo(
                inicio, fin, tipo, "CUTTING",
                config_rutas["CUTTING"]["salida"],
                config_rutas["CUTTING"]["plantilla"],
                lambda msg: app.after(0, lambda: estado_var.set(msg))
            )
            cutting_ok = True
        except Exception as e:
            print("Error automatización CUTTING:", e)

        status_str = "Éxito"
        if not sewing_ok and not cutting_ok:
            status_str = "Error Completo"
        elif not sewing_ok:
            status_str = "Error SEWING"
        elif not cutting_ok:
            status_str = "Error CUTTING"

        config_rutas["last_auto_run"] = ahora.strftime("%Y-%m-%d")
        config_rutas["last_auto_status"] = f"{status_str} ({tipo}) a las {ahora.strftime('%H:%M:%S')}"
        guardar_configuracion_rutas(config_rutas)

    except Exception as ex:
        print("Error en ejecución de automatización:", ex)
    finally:
        app.after(0, detener_loader)
        app.after(0, habilitar_botones)
        
        def actualizar_labels():
            lbl_auto_ultimo_val.config(text=f"{config_rutas['last_auto_run']} ({config_rutas['last_auto_status']})")
            lbl_auto_estado_val.config(text="Activa", fg="green")
            prox = calcular_proxima_ejecucion()
            lbl_auto_proxima_val.config(text=prox.strftime("%Y-%m-%d a las 07:50 AM"))
            estado_var.set(f"Automatización finalizada: {config_rutas['last_auto_status']}")
            
        app.after(0, actualizar_labels)

def run_scheduler():
    global config_rutas
    while True:
        try:
            ahora = datetime.now()
            if ahora.weekday() < 5:
                hora_ejecucion = ahora.replace(hour=7, minute=50, second=0, microsecond=0)
                if ahora >= hora_ejecucion:
                    hoy_str = ahora.strftime("%Y-%m-%d")
                    if config_rutas.get("last_auto_run") != hoy_str:
                        ejecutar_automatizacion_programada(ahora)
        except Exception as ex:
            print("Error en scheduler loop:", ex)
        time.sleep(30)

def iniciar_hilo_generar():
    if not ruta_salida_var.get():
        messagebox.showwarning("Advertencia", "Por favor selecciona una ruta de destino primero.")
        return
        
    seleccion = cb_periodo.get()
    hoy = datetime.now()
    
    inicio = None
    fin = None
    tipo = "personalizado"
    
    if seleccion == "Diario (Ayer)":
        inicio = hoy - timedelta(days=1)
        fin = inicio
        tipo = "diario"
    elif seleccion == "Semanal":
        inicio = hoy - timedelta(days=7)
        fin = hoy - timedelta(days=1)
        tipo = "semanal"
    elif seleccion == "Mensual":
        inicio = hoy.replace(day=1)
        fin = hoy
        tipo = "mensual"
    elif seleccion == "Día Específico":
        try:
            inicio = obtener_fecha_dia()
            fin = inicio
            tipo = "diario"
        except ValueError:
            messagebox.showerror("Error", "La fecha seleccionada no es válida. Por favor, verifica el día y mes.")
            return
    elif seleccion == "Mes Completo":
        try:
            y, m = obtener_anio_mes()
            inicio = datetime(y, m, 1)
            fin = ultimo_dia_del_mes(y, m)
            tipo = "mensual"
        except ValueError:
            messagebox.showerror("Error", "El mes seleccionado no es válido.")
            return
    elif seleccion == "Rango de Fechas":
        try:
            inicio = obtener_fecha_rango_desde()
            fin = obtener_fecha_rango_hasta()
            if inicio > fin:
                messagebox.showerror("Error", "La fecha 'Desde' no puede ser posterior a la fecha 'Hasta'.")
                return
            tipo = "personalizado"
        except ValueError:
            messagebox.showerror("Error", "Una de las fechas seleccionadas no es válida. Por favor, verifica.")
            return

    deshabilitar_botones()
    progress_bar.start(10)  # Inicia la animación del loader
    hilo = threading.Thread(target=procesar_reporte, args=(inicio, fin, tipo))
    hilo.start()

def iniciar_hilo_actualizar():
    if not ruta_salida_var.get():
        messagebox.showwarning("Advertencia", "Por favor selecciona una ruta de destino primero.")
        return
    deshabilitar_botones()
    progress_bar.start(10)
    hilo = threading.Thread(target=actualizar_data_solo)
    hilo.start()

def actualizar_data_solo():
    area_seleccionada = area_var.get()
    area_id = 1 if area_seleccionada == "SEWING" else 2
    try:
        estado_var.set(f"Descargando datos de {area_seleccionada}...")
        descargar_excel_datos(area_id)
        estado_var.set("Datos actualizados correctamente.")
        messagebox.showinfo("Éxito", f"Los datos de {area_seleccionada} se han descargado e integrado.")
    except Exception as e:
        estado_var.set("Error al actualizar datos.")
        messagebox.showerror("Error", f"Ocurrió un error al descargar datos:\n{str(e)}")
    finally:
        app.after(0, detener_loader)
        app.after(0, habilitar_botones)

def detener_loader():
    progress_bar.stop()

def deshabilitar_botones():
    btn_generar.config(state=tk.DISABLED)
    btn_actualizar.config(state=tk.DISABLED)
    btn_ruta.config(state=tk.DISABLED)
    btn_plantilla.config(state=tk.DISABLED)
    radio_sewing.config(state=tk.DISABLED)
    radio_cutting.config(state=tk.DISABLED)
    cb_periodo.config(state=tk.DISABLED)
    for cb in lista_comboboxes_fechas:
        cb.config(state=tk.DISABLED)

def habilitar_botones():
    btn_generar.config(state=tk.NORMAL)
    btn_actualizar.config(state=tk.NORMAL)
    btn_ruta.config(state=tk.NORMAL)
    btn_plantilla.config(state=tk.NORMAL)
    radio_sewing.config(state=tk.NORMAL)
    radio_cutting.config(state=tk.NORMAL)
    cb_periodo.config(state="readonly")
    for cb in lista_comboboxes_fechas:
        cb.config(state="readonly")

# --- CONFIGURACION VENTANA ---
app = tk.Tk()
app.title("Generador de Reportes")
app.geometry("480x740")
app.resizable(False, False)

# --- VARIABLES ---
ruta_salida_var = tk.StringVar()
ruta_salida_var.set(config_rutas["SEWING"]["salida"])  # Por defecto apunta a salida de SEWING

ruta_plantilla_var = tk.StringVar()
ruta_plantilla_var.set(config_rutas["SEWING"]["plantilla"]) # Plantilla por defecto SEWING

area_var = tk.StringVar()
area_var.set("SEWING")  # Área por defecto

lista_comboboxes_fechas = []

# --- ESTILOS ---
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 11), padding=6)
style.configure("TLabel", font=("Helvetica", 12))

# --- INTERFAZ ---
titulo = ttk.Label(app, text="Generador de Reportes", font=("Helvetica", 14, "bold"))
titulo.pack(pady=(15, 10))

# Fila de selección de Área
frame_area = tk.Frame(app)
frame_area.pack(fill="x", padx=30, pady=5)
lbl_area = tk.Label(frame_area, text="Área:", font=("Helvetica", 10, "bold"), width=12, anchor="w")
lbl_area.pack(side=tk.LEFT)
radio_sewing = ttk.Radiobutton(frame_area, text="Sewing", variable=area_var, value="SEWING", command=cambiar_area)
radio_sewing.pack(side=tk.LEFT, padx=10)
radio_cutting = ttk.Radiobutton(frame_area, text="Cutting", variable=area_var, value="CUTTING", command=cambiar_area)
radio_cutting.pack(side=tk.LEFT, padx=10)

# Fila de selección de plantilla
frame_plantilla = tk.Frame(app)
frame_plantilla.pack(fill="x", padx=30, pady=5)
lbl_plantilla = tk.Label(frame_plantilla, text="Plantilla:", font=("Helvetica", 10, "bold"), width=12, anchor="w")
lbl_plantilla.pack(side=tk.LEFT)
entr_plantilla = tk.Entry(frame_plantilla, textvariable=ruta_plantilla_var, state="readonly", fg="gray")
entr_plantilla.pack(side=tk.LEFT, fill="x", expand=True, ipady=3)
btn_plantilla = ttk.Button(frame_plantilla, text="Elegir Archivo", command=seleccionar_plantilla)
btn_plantilla.pack(side=tk.RIGHT, padx=5)

# Fila de selección de ruta
frame_ruta = tk.Frame(app)
frame_ruta.pack(fill="x", padx=30, pady=5)
lbl_ruta = tk.Label(frame_ruta, text="Guardar en:", font=("Helvetica", 10, "bold"), width=12, anchor="w")
lbl_ruta.pack(side=tk.LEFT)
entr_ruta = tk.Entry(frame_ruta, textvariable=ruta_salida_var, state="readonly", fg="gray")
entr_ruta.pack(side=tk.LEFT, fill="x", expand=True, ipady=3)
btn_ruta = ttk.Button(frame_ruta, text="Elegir Carpeta", command=seleccionar_ruta)
btn_ruta.pack(side=tk.RIGHT, padx=5)

# Separador
separator = ttk.Separator(app, orient='horizontal')
separator.pack(fill='x', padx=30, pady=10)

# Fila de selección de Periodo
frame_periodo = tk.Frame(app)
frame_periodo.pack(fill="x", padx=30, pady=5)
lbl_periodo = tk.Label(frame_periodo, text="Periodo:", font=("Helvetica", 10, "bold"), width=12, anchor="w")
lbl_periodo.pack(side=tk.LEFT)
cb_periodo = ttk.Combobox(frame_periodo, values=[
    "Diario (Ayer)",
    "Semanal",
    "Mensual",
    "Día Específico",
    "Mes Completo",
    "Rango de Fechas"
], state="readonly")
cb_periodo.set("Diario (Ayer)")
cb_periodo.pack(side=tk.LEFT, fill="x", expand=True)

# Frame dinámico para detalles de fecha
frame_detalles_fecha = tk.LabelFrame(app, text="Parámetros de Fecha", font=("Helvetica", 9, "bold"))
frame_detalles_fecha.pack(fill="x", padx=30, pady=10, ipady=5)

# 1. Subframe Automático
frame_automatico_msg = tk.Frame(frame_detalles_fecha)
lbl_auto = tk.Label(frame_automatico_msg, text="El rango se determinará automáticamente.", font=("Helvetica", 9, "italic"), fg="gray")
lbl_auto.pack(pady=10)

# 2. Subframe Día Específico
frame_dia_especifico = tk.Frame(frame_detalles_fecha)
lbl_dia_especifico = tk.Label(frame_dia_especifico, text="Selecciona fecha:", font=("Helvetica", 9))
lbl_dia_especifico.pack(side=tk.LEFT, padx=5)
f_dia, obtener_fecha_dia, cb_a_d, cb_m_d, cb_d_d = crear_selector_fecha(frame_dia_especifico)
f_dia.pack(side=tk.LEFT)
lista_comboboxes_fechas.extend([cb_a_d, cb_m_d, cb_d_d])

# 3. Subframe Mes Completo
frame_mes_completo = tk.Frame(frame_detalles_fecha)
lbl_mes_completo = tk.Label(frame_mes_completo, text="Selecciona mes:", font=("Helvetica", 9))
lbl_mes_completo.pack(side=tk.LEFT, padx=5)
f_mes, obtener_anio_mes, cb_a_m, cb_m_m = crear_selector_mes(frame_mes_completo)
f_mes.pack(side=tk.LEFT)
lista_comboboxes_fechas.extend([cb_a_m, cb_m_m])

# 4. Subframe Rango de Fechas
frame_rango_fechas = tk.Frame(frame_detalles_fecha)

frame_rango_desde = tk.Frame(frame_rango_fechas)
frame_rango_desde.pack(fill="x", pady=2)
lbl_desde = tk.Label(frame_rango_desde, text="Desde:", font=("Helvetica", 9), width=8, anchor="e")
lbl_desde.pack(side=tk.LEFT, padx=5)
f_desde, obtener_fecha_rango_desde, cb_a_rd, cb_m_rd, cb_d_rd = crear_selector_fecha(frame_rango_desde, pref_fecha=datetime.now() - timedelta(days=7))
f_desde.pack(side=tk.LEFT)

frame_rango_hasta = tk.Frame(frame_rango_fechas)
frame_rango_hasta.pack(fill="x", pady=2)
lbl_hasta = tk.Label(frame_rango_hasta, text="Hasta:", font=("Helvetica", 9), width=8, anchor="e")
lbl_hasta.pack(side=tk.LEFT, padx=5)
f_hasta, obtener_fecha_rango_hasta, cb_a_rh, cb_m_rh, cb_d_rh = crear_selector_fecha(frame_rango_hasta)
f_hasta.pack(side=tk.LEFT)

lista_comboboxes_fechas.extend([cb_a_rd, cb_m_rd, cb_d_rd, cb_a_rh, cb_m_rh, cb_d_rh])

def actualizar_panel_fecha(event=None):
    frame_automatico_msg.pack_forget()
    frame_dia_especifico.pack_forget()
    frame_mes_completo.pack_forget()
    frame_rango_fechas.pack_forget()
    
    seleccion = cb_periodo.get()
    if seleccion in ["Diario (Ayer)", "Semanal", "Mensual"]:
        frame_automatico_msg.pack(fill="x", expand=True, pady=10)
    elif seleccion == "Día Específico":
        frame_dia_especifico.pack(fill="x", expand=True, pady=10)
    elif seleccion == "Mes Completo":
        frame_mes_completo.pack(fill="x", expand=True, pady=10)
    elif seleccion == "Rango de Fechas":
        frame_rango_fechas.pack(fill="x", expand=True, pady=10)

cb_periodo.bind("<<ComboboxSelected>>", actualizar_panel_fecha)

# Mostrar el frame inicial
actualizar_panel_fecha()

# --- PANEL DE AUTOMATIZACION ---
frame_auto_info = tk.LabelFrame(app, text="Automatización Programada (07:50 AM)", font=("Helvetica", 9, "bold"))
frame_auto_info.pack(fill="x", padx=30, pady=(0, 10), ipady=5)

frame_auto_estado = tk.Frame(frame_auto_info)
frame_auto_estado.pack(fill="x", padx=10, pady=2)
lbl_auto_estado_title = tk.Label(frame_auto_estado, text="Estado del Servicio:", font=("Helvetica", 9, "bold"), width=18, anchor="w")
lbl_auto_estado_title.pack(side=tk.LEFT)
lbl_auto_estado_val = tk.Label(frame_auto_estado, text="Activa", font=("Helvetica", 9), fg="green")
lbl_auto_estado_val.pack(side=tk.LEFT)

frame_auto_next = tk.Frame(frame_auto_info)
frame_auto_next.pack(fill="x", padx=10, pady=2)
lbl_auto_proxima_title = tk.Label(frame_auto_next, text="Próxima Ejecución:", font=("Helvetica", 9, "bold"), width=18, anchor="w")
lbl_auto_proxima_title.pack(side=tk.LEFT)
lbl_auto_proxima_val = tk.Label(frame_auto_next, text="", font=("Helvetica", 9))
lbl_auto_proxima_val.pack(side=tk.LEFT)

frame_auto_last = tk.Frame(frame_auto_info)
frame_auto_last.pack(fill="x", padx=10, pady=2)
lbl_auto_ultimo_title = tk.Label(frame_auto_last, text="Última Ejecución:", font=("Helvetica", 9, "bold"), width=18, anchor="w")
lbl_auto_ultimo_title.pack(side=tk.LEFT)
lbl_auto_ultimo_val = tk.Label(frame_auto_last, text="", font=("Helvetica", 9))
lbl_auto_ultimo_val.pack(side=tk.LEFT)

# Inicializar valores de automatización
lbl_auto_ultimo_val.config(text=f"{config_rutas.get('last_auto_run', 'Nunca')} ({config_rutas.get('last_auto_status', '')})")
prox_run = calcular_proxima_ejecucion()
lbl_auto_proxima_val.config(text=prox_run.strftime("%Y-%m-%d a las 07:50 AM"))

# Botones de Acción
btn_generar = ttk.Button(app, text="Generar Reporte", command=iniciar_hilo_generar)
btn_generar.pack(fill="x", padx=50, pady=5)

btn_actualizar = ttk.Button(app, text="Descargar / Actualizar Data (Últimos 2 Meses)", command=iniciar_hilo_actualizar)
btn_actualizar.pack(fill="x", padx=50, pady=10)

# Barra de progreso (Loader)
progress_bar = ttk.Progressbar(app, mode='indeterminate', length=200)
progress_bar.pack(pady=5)

estado_var = tk.StringVar()
estado_var.set("Esperando acción...")
lbl_estado = ttk.Label(app, textvariable=estado_var, font=("Helvetica", 10, "italic"), foreground="gray")
lbl_estado.pack(side=tk.BOTTOM, pady=(0, 15))

# Iniciar hilo del scheduler
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

app.mainloop()