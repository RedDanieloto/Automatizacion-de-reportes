import sys
import os

API_HOST = "https://api-mantenimiento.gstmxcloud.com"
BASE_URL = f"{API_HOST}/api/estadisticas"

def obtener_ruta_base():
    if getattr(sys, 'frozen', False):
        ruta_exe = os.path.dirname(sys.executable)
        if ".app/Contents/MacOS" in ruta_exe:
            dir_app_parent = os.path.abspath(os.path.join(ruta_exe, "../../../"))
            raiz_proyecto = os.path.abspath(os.path.join(dir_app_parent, "../"))
            if os.path.exists(os.path.join(raiz_proyecto, "DASHBOARD_COSTURA_DT.xlsm")):
                return raiz_proyecto
            return dir_app_parent
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))

RUTA_BASE = obtener_ruta_base()

RUTA_DATOS = os.path.join(RUTA_BASE, "data/datos.xlsx")
RUTA_DASHBOARD = os.path.join(RUTA_BASE, "DASHBOARD_COSTURA_DT.xlsm")
RUTA_OUTPUT = os.path.join(RUTA_BASE, "output/")


class ProcesoCanceladoException(Exception):
    """Excepción lanzada cuando el usuario cancela la ejecución del proceso."""
    pass


def verificar_cancelacion(cancel_event=None):
    if cancel_event is not None and cancel_event.is_set():
        raise ProcesoCanceladoException("El proceso fue cancelado por el usuario.")
