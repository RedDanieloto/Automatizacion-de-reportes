import xlwings as xw
from config import RUTA_DASHBOARD, RUTA_OUTPUT
from pdf2image import convert_from_path


def actualizar_excel(df_mes, df_dia, kpis, inicio, fin, tipo, ruta_salida=None, ruta_plantilla=None, area="SEWING"):
    if ruta_salida is None:
        ruta_salida = RUTA_OUTPUT
    elif not ruta_salida.endswith('/'):
        ruta_salida += '/'
        
    if ruta_plantilla is None:
        ruta_plantilla = RUTA_DASHBOARD

    wb = xw.Book(ruta_plantilla)

    ws_bd_dia = wb.sheets["PRUEBA NUEVO FORMATO"]   # 🔵 DIA
    ws_bd_mes = wb.sheets["BD_MES"]                 # 🟢 MES
    ws_dash = wb.sheets["DashBoardUPD"]

    # =========================
    # 🔵 BD DIA (para TODO)
    # =========================
    ultima_col_dia = len(df_dia.columns)

    ws_bd_dia.range((2, 1), (10000, ultima_col_dia)).clear_contents()
    ws_bd_dia.range("A2").value = df_dia.values.tolist()

    # =========================
    # 🟢 BD MES (solo historial)
    # =========================
    ultima_col_mes = len(df_mes.columns)

    ws_bd_mes.range((2, 1), (10000, ultima_col_mes)).clear_contents()
    ws_bd_mes.range("A2").value = df_mes.values.tolist()

    # =========================
    # 🔥 RECALCULAR
    # =========================
    wb.app.calculate()

    # =========================
    # 🔥 REFRESH PIVOTS (MAC safe)
    # =========================
    for sheet in wb.sheets:
        try:
            for pt in sheet.api.pivot_tables():
                pt.refresh_table()
        except:
            pass

    # =========================
    # KPIs (API)
    # =========================
    ws_dash.range("A1").value = f"MTTR\n{kpis['mttr']['data']['mttr']['horas']:.2f} h"
    ws_dash.range("A2").value = f"MTBF\n{kpis['mtbf']['data']['mtbf']['horas']:.2f} h"
    ws_dash.range("A3").value = f"DOWNTIME\n{kpis['downtime']['data']['tiempo_total']['horas']:.2f} h"
    ws_dash.range("A4").value = f"REPORTES ABIERTOS\n{kpis['abiertos']['data']['reportes_abiertos']['abiertos']}"

    # =========================
    # FECHA Y ÁREA
    # =========================
    if tipo == "mensual":
        meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        nombre_mes = meses[inicio.month]
        texto_fecha = f"{nombre_mes.upper()} {inicio.year}"
    elif tipo == "semanal":
        texto_fecha = f"{inicio.date()} AL {fin.date()}"
    else:
        texto_fecha = str(inicio.date())

    ws_dash.range("C1").value = f"DASHBOARD DOWNTIME {area.upper()} {texto_fecha}"

    # =========================
    # CONFIG PDF
    # =========================
    ws_dash.page_setup.orientation = 'landscape'
    ws_dash.page_setup.zoom = False
    ws_dash.page_setup.fit_to_pages_wide = 1
    ws_dash.page_setup.fit_to_pages_tall = 1

    # =========================
    # 🔥 GUARDAR + RECALCULAR
    # =========================
    wb.save()
    wb.app.calculate()

    # =========================
    # EXPORTAR PDF
    # =========================
    nombre = f"{ruta_salida}reporte_{tipo}_{inicio.date()}_{fin.date()}.pdf"
    ws_dash.to_pdf(nombre)

    # =========================
    # 🔥 PDF → PNG CON RECORTE
    # =========================
    try:
        from PIL import Image, ImageChops
        imagenes = convert_from_path(nombre)
        img = imagenes[0]
        
        # Crear un fondo blanco y buscar la diferencia para detectar dónde empieza el contenido
        fondo_blanco = Image.new(img.mode, img.size, (255, 255, 255))
        diferencia = ImageChops.difference(img, fondo_blanco)
        caja = diferencia.getbbox() # Obtiene los límites [izq, arriba, der, abajo] de lo que NO es blanco
        
        if caja:
            # Damos un pequeño respiro (margen) de 20 pixeles para que no quede al ras
            margen = 20
            izq = max(0, caja[0] - margen)
            sup = max(0, caja[1] - margen)
            der = min(img.size[0], caja[2] + margen)
            inf = min(img.size[1], caja[3] + margen)
            
            img = img.crop((izq, sup, der, inf))
            
        img.save(nombre.replace(".pdf", ".png"), "PNG")
    except Exception as e:
        print("⚠️ Error convirtiendo a imagen:", e)

    wb.close()

    return nombre