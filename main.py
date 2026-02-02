# main.py

import os
import sys

from PySide6.QtCore import QThread
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from core.serial_worker import SerialWorker
from ui.main_window import GroundStation

# Importamos los módulos de Interfaz (Vista) y Lógica (Modelo)
from ui.theme import PALETTE, get_stylesheet, set_dark_palette

os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["QT_XCB_GL_INTEGRATION"] = "xcb_glx"
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"


def main():
    # 1. Iniciar la Aplicación
    app = QApplication(sys.argv)

    # --- Configuración Visual (Tema y Fuente) ---
    app.setStyle("Fusion")

    # Cargar fuente Gotham-Book
    font_id = QFontDatabase.addApplicationFont("Gotham-Book.otf")
    if font_id == -1:
        print("Aviso: No se pudo cargar 'Gotham-Book.otf'. Usando fuente por defecto.")
        family_name = "sans-serif"
    else:
        family_name = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(family_name, 10))
        print(f"Fuente '{family_name}' cargada correctamente.")

    # Aplicar Colores y QSS
    set_dark_palette(app)
    app.setStyleSheet(get_stylesheet(family_name))

    # --- 2. Crear los Objetos Principales ---
    window = GroundStation()  # La Ventana (GUI)
    serial_thread = QThread()  # El Hilo Secundario
    serial_worker = SerialWorker()  # El Trabajador (Lógica)

    # Mover la lógica al hilo secundario
    serial_worker.moveToThread(serial_thread)

    # --- 3. Conectar Señales (Lógica -> GUI) ---
    # Estas conexiones permiten que el worker actualice la interfaz

    # Estado y Conexión
    serial_worker.port_list_updated.connect(window.update_port_list)
    serial_worker.status_update.connect(window.on_connection_status)

    # Datos de Telemetría
    serial_worker.cinematica_updated.connect(window.on_cinematica_updated)
    serial_worker.visor_3d_updated.connect(window.on_visor_3d_updated)
    serial_worker.gps_data_updated.connect(window.on_gps_data_updated)
    serial_worker.altimetro_data_updated.connect(window.on_altimetro_data_updated)
    serial_worker.graficas_data_updated.connect(window.on_graficas_data_updated)
    serial_worker.calidad_aire_updated.connect(window.on_calidad_aire_updated)
    serial_worker.baterias_data_updated.connect(window.on_baterias_data_updated)
    serial_worker.paquetes_data_updated.connect(window.on_paquetes_data_updated)
    serial_worker.estados_data_updated.connect(window.on_estados_data_updated)

    # --- 4. Conectar Señales (GUI -> Lógica) ---
    # Estas conexiones permiten que los botones controlen al worker

    window.actualizar_puertos_solicitado.connect(serial_worker.check_available_ports)
    window.conexion_solicitada.connect(serial_worker.start_connection)
    window.desconexion_solicitada.connect(serial_worker.stop_connection)
    window.comando_solicitado.connect(serial_worker.send_command_sequence)

    # --- 5. Gestión del Hilo ---

    # Iniciar el worker cuando el hilo arranque
    serial_thread.started.connect(serial_worker.init_worker)

    # Limpieza correcta al cerrar la app
    app.aboutToQuit.connect(serial_worker.stop_monitoring)
    app.aboutToQuit.connect(serial_thread.quit)
    serial_thread.finished.connect(serial_worker.deleteLater)
    serial_thread.finished.connect(serial_thread.deleteLater)

    # Arrancar el hilo
    serial_thread.start()

    # --- 6. Ejecutar ---
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()  # main.py
