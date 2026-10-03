import xlwings as xw
from config import RUTA_DASHBOARD, RUTA_OUTPUT, verificar_cancelacion
from pdf2image import convert_from_path
import os


def actualizar_excel(df_mes, df_dia, kpis, inicio, fin, tipo, ruta_salida=None, ruta_plantilla=None, area="SEWING", cancel_event=None, on_app_created=None):
    verificar_cancelacion(cancel_event)

    if ruta_salida is None:
        ruta_salida = RUTA_OUTPUT
        
    os.makedirs(ruta_salida, exist_ok=True)

    if ruta_plantilla is None:
        ruta_plantilla = RUTA_DASHBOARD

    # Crear una instancia aislada e invisible de Excel para evitar colisiones con archivos abiertos por el usuario
    app = xw.App(visible=False)
    app.display_alerts = False

    if on_app_created:
        on_app_created(app)

    try:
        verificar_cancelacion(cancel_event)
        wb = app.books.open(ruta_plantilla)

        ws_bd_dia = wb.sheets["PRUEBA NUEVO FORMATO"]   # 🔵 DIA
        ws_bd_mes = wb.sheets["BD_MES"]                 # 🟢 MES
        ws_dash = wb.sheets["DashBoardUPD"]

        # =========================
        # 🔵 BD DIA (para TODO)
        # =========================
        ultima_col_dia = len(df_dia.columns)
        if ultima_col_dia > 0 and len(df_dia) > 0:
            ws_bd_dia.range((2, 1), (10000, ultima_col_dia)).clear_contents()
            ws_bd_dia.range("A2").value = df_dia.values.tolist()

        # =========================
        # 🟢 BD MES (solo historial)
        # =========================
        ultima_col_mes = len(df_mes.columns)
        if ultima_col_mes > 0 and len(df_mes) > 0:
            ws_bd_mes.range((2, 1), (10000, ultima_col_mes)).clear_contents()
            ws_bd_mes.range("A2").value = df_mes.values.tolist()

        # =========================
        # 🔥 RECALCULAR
        # =========================
        verificar_cancelacion(cancel_event)
        app.calculate()

        # =========================
        # 🔥 REFRESH PIVOTS
        # =========================
        verificar_cancelacion(cancel_event)
        for sheet in wb.sheets:
            try:
                for pt in sheet.api.PivotTables():
                    pt.RefreshTable()
            except Exception:
                try:
                    for pt in sheet.api.pivot_tables():
                        pt.refresh_table()
                except Exception:
                    pass

        # =========================
        # KPIs (API)
        # =========================
        ws_dash.range("A1").value = f"MTTR\n{kpis['mttr']['data']['mttr']['horas']:.2f} h"
        ws_dash.range("A2").value = f"MTBF\n{kpis['mtbf']['data']['mtbf']['horas']:.2f} h"
        ws_dash.range("A3").value = f"DOWNTIME\n{kpis['downtime']['data']['tiempo_total']['horas']:.2f} h"
        ws_dash.range("A4").value = "REPORTES ABIERTOS\n0"

        # =========================
        # FECHA Y ÁREA
        # =========================
        if tipo == "mensual":
            meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            nombre_mes = meses[inicio.month]
            texto_fecha = f"{nombre_mes.upper()} {inicio.year}"
        elif inicio.date() != fin.date():
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
        verificar_cancelacion(cancel_event)
        wb.save()
        app.calculate()

        # =========================
        # EXPORTAR PDF
        # =========================
        verificar_cancelacion(cancel_event)
        nombre = os.path.join(ruta_salida, f"reporte_{tipo}_{inicio.date()}_{fin.date()}.pdf")
        
        # Verificar si el archivo PDF está siendo utilizado por otra aplicación
        if os.path.exists(nombre):
            try:
                os.remove(nombre)
            except PermissionError:
                raise PermissionError(f"El archivo PDF destino '{os.path.basename(nombre)}' está abierto en otra aplicación (visor de PDF o navegador).\nPor favor ciérralo antes de volver a generar el reporte.")

        ws_dash.to_pdf(nombre)

        # =========================
        # 🔥 PDF → PNG CON RECORTE
        # =========================
        verificar_cancelacion(cancel_event)
        try:
            from PIL import Image, ImageChops
            try:
                import fitz  # PyMuPDF (no requiere Poppler en Windows)
                doc = fitz.open(nombre)
                page = doc[0]
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                doc.close()
            except Exception:
                imagenes = convert_from_path(nombre)
                img = imagenes[0]
            
            fondo_blanco = Image.new(img.mode, img.size, (255, 255, 255))
            diferencia = ImageChops.difference(img, fondo_blanco)
            caja = diferencia.getbbox()
            
            if caja:
                margen = 20
                izq = max(0, caja[0] - margen)
                sup = max(0, caja[1] - margen)
                der = min(img.size[0], caja[2] + margen)
                inf = min(img.size[1], caja[3] + margen)
                img = img.crop((izq, sup, der, inf))
                
            ruta_png = nombre.replace(".pdf", ".png")
            img.save(ruta_png, "PNG")
            print(f"✅ Imagen PNG generada exitosamente: {ruta_png}")
        except Exception as e:
            print("⚠️ Error convirtiendo a imagen:", e)

        wb.close()
        return nombre
    finally:
        try:
            app.quit()
        except Exception:
            pass
