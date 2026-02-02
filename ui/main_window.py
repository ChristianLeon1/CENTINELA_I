#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2025 CREADOR: Christian Yael Ramírez León

# ui/main_window.py

from PySide6.QtWidgets import (
    QMainWindow, QToolBar, QWidget, 
    QHBoxLayout, QVBoxLayout,
    QLabel, QComboBox, QLineEdit
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Slot, QSize, Qt, Signal, QTimer

# Importar tus módulos de UI
from ui.theme import PALETTE
from ui.widgets.panel_superior import PanelSuperior
from ui.widgets.panel_gps import PanelGPS
from ui.widgets.panel_estados import PanelEstados
from ui.widgets.panel_inferior import PanelInferior
from ui.widgets.panel_visor_3d import PanelVisor3D
from ui.widgets.panel_cinematica import PanelCinematica
from ui.widgets.panel_altimetro import PanelAltimetro
from ui.widgets.panel_graficas import PanelGraficas
from ui.widgets.panel_calidad_aire import PanelCalidadAire

class GroundStation(QMainWindow):

    # Señales para el Controlador
    conexion_solicitada = Signal(str, int)
    desconexion_solicitada = Signal()
    actualizar_puertos_solicitado = Signal()
    comando_solicitado = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Estación Terrena")
        self.setGeometry(100, 100, 1800, 950) 
        
        # Buffer de datos para la actualización por Timers
        self.data_store = {
            'cinematica': None,
            'visor_3d': None,
            'gps': None,
            'altimetro': None,
            'graficas': None,
            'calidad_aire': None,
            'baterias': None,
            'paquetes': None,
            'estados': None
        }

        self.setup_toolbar()
        self.setup_central_widget()
        self.setup_ui_timers()

    def setup_ui_timers(self):
        # 30 Hz -> Visor 3D
        self.timer_30hz = QTimer(self)
        self.timer_30hz.timeout.connect(self.update_ui_30hz)
        self.timer_30hz.start(33)

        # 20 Hz -> Cinemática, Altimetro, Paquetes
        self.timer_20hz = QTimer(self)
        self.timer_20hz.timeout.connect(self.update_ui_20hz)
        self.timer_20hz.start(50)

        # 0.5s -> Gráficas
        self.timer_05s = QTimer(self)
        self.timer_05s.timeout.connect(self.update_ui_05s)
        self.timer_05s.start(500)

        # 5s -> GPS, Textos lentos
        self.timer_5s = QTimer(self)
        self.timer_5s.timeout.connect(self.update_ui_5s)
        self.timer_5s.start(5000)

    # --- SLOTS DE DATOS (Solo guardan) ---
    @Slot(dict)
    def on_cinematica_updated(self, data: dict): self.data_store['cinematica'] = data
    @Slot(float, float, float)
    def on_visor_3d_updated(self, p, y, r): self.data_store['visor_3d'] = (p, y, r)
    @Slot(dict)
    def on_gps_data_updated(self, data: dict): self.data_store['gps'] = data
    @Slot(int)
    def on_altimetro_data_updated(self, alt): self.data_store['altimetro'] = alt
    @Slot(dict)
    def on_graficas_data_updated(self, data: dict): self.data_store['graficas'] = data
    @Slot(dict)
    def on_calidad_aire_updated(self, data: dict): self.data_store['calidad_aire'] = data
    @Slot(int, int)
    def on_baterias_data_updated(self, bc, bcam): self.data_store['baterias'] = (bc, bcam)
    @Slot(int, int)
    def on_paquetes_data_updated(self, r, l): self.data_store['paquetes'] = (r, l)
    @Slot(dict)
    def on_estados_data_updated(self, data: dict): self.data_store['estados'] = data

    # --- ACTUALIZACIÓN UI ---
    def update_ui_30hz(self):
        if self.data_store['visor_3d']:
            self.panel_visor_3d.update_rotation(*self.data_store['visor_3d'])

    def update_ui_20hz(self):
        if self.data_store['cinematica']: self.panel_cinematica.update_cinematica(self.data_store['cinematica'])
        if self.data_store['altimetro'] is not None: self.panel_altimetro.update_altitud(self.data_store['altimetro'])
        if self.data_store['paquetes']: self.panel_inferior.update_packet_summary(*self.data_store['paquetes'])

    def update_ui_05s(self):
        dg = self.data_store['graficas']
        if dg and 'time' in dg:
            self.panel_graficas.update_pressure_graph(dg['time'], dg['pres'])
            self.panel_graficas.update_temp_graph(dg['time'], dg['temp'])
            if dg['pres']: self.panel_graficas.update_pressure_label(f"Presión: {dg['pres'][-1]:.2f} KPa")
            if dg['temp']: self.panel_graficas.update_temp_label(f"Temperatura: {dg['temp'][-1]:.2f} °C")
        
        da = self.data_store['calidad_aire']
        if da and 'time' in da:
            self.panel_calidad_aire.update_gases_graph(da['time'], da['co2'], da['tvoc'])
            self.panel_calidad_aire.update_humidity_graph(da['time'], da['hum'])

    def update_ui_5s(self):
        if self.data_store['gps']: self.panel_gps.update_data(self.data_store['gps'])
        if self.data_store['baterias']: self.panel_inferior.update_bateria_cohete(self.data_store['baterias'][0]); self.panel_inferior.update_bateria_camara(self.data_store['baterias'][1])
        if self.data_store['estados']: self.panel_estados.update_data(self.data_store['estados'])

    # --- CONFIGURACIÓN UI ---
    def setup_central_widget(self):
        central_container = QWidget()
        main_layout = QVBoxLayout(central_container)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.panel_superior = PanelSuperior()
        main_layout.addWidget(self.panel_superior)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        
        # Columna Izquierda
        col_izq = QWidget()
        lay_izq = QVBoxLayout(col_izq)
        lay_izq.setContentsMargins(0, 0, 0, 0); lay_izq.setSpacing(10)
        self.panel_gps = PanelGPS()
        self.panel_graficas = PanelGraficas()
        lay_izq.addWidget(self.panel_gps, 2)
        lay_izq.addWidget(self.panel_graficas, 1)
        
        # Columna Central
        col_cen = QWidget()
        lay_cen = QVBoxLayout(col_cen)
        lay_cen.setContentsMargins(0, 0, 0, 0); lay_cen.setSpacing(10)
        lay_cen_top = QHBoxLayout(); lay_cen_top.setSpacing(10)
        self.panel_visor_3d = PanelVisor3D()
        self.panel_altimetro = PanelAltimetro()
        lay_cen_top.addWidget(self.panel_visor_3d, 1)
        lay_cen_top.addWidget(self.panel_altimetro)
        self.panel_cinematica = PanelCinematica() 
        lay_cen.addLayout(lay_cen_top, 1)
        lay_cen.addWidget(self.panel_cinematica)
        
        # Columna Derecha
        col_der = QWidget()
        lay_der = QVBoxLayout(col_der)
        lay_der.setContentsMargins(0, 0, 10, 0); lay_der.setSpacing(10)
        self.panel_estados = PanelEstados()
        self.panel_calidad_aire = PanelCalidadAire()
        lay_der.addWidget(self.panel_estados, 1)
        lay_der.addWidget(self.panel_calidad_aire, 1)
        
        content_layout.addWidget(col_izq, 2)
        content_layout.addWidget(col_cen, 2)
        content_layout.addWidget(col_der, 1)
        main_layout.addLayout(content_layout, 1)

        self.panel_inferior = PanelInferior()
        main_layout.addWidget(self.panel_inferior) 
        self.setCentralWidget(central_container)

    def setup_toolbar(self):
        self.toolbar = QToolBar("Herramientas")
        self.toolbar.setIconSize(QSize(16,16))
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.toolbar)
        self.toolbar.setFloatable(False); self.toolbar.setMovable(False)
        
        label_baud = QLabel("Baudrate: ")
        self.baud_opts = QComboBox()
        self.baud_opts.addItems(['9600', '19200', '31250', '38400', '57600', '74880', '115200', '230400', '250000', '460800', '500000', '921600', '1000000', '2000000'])
        self.baud_opts.setCurrentText("115200")
        self.serial_opts = QComboBox() 
        label_serial = QLabel("Puertos Disponibles: ") 
        label_canal = QLabel("Canal: ") 
        self.canal = QLineEdit(); self.canal.setFixedWidth(60) 
        
        self.boton_actualizar = QAction("Actualizar Puertos")
        self.boton_conec_ser = QAction("Conectar")
        self.boton_descon = QAction("Desconectar")
        self.boton_act_servo = QAction("Cerrar Servo")
        self.boton_des_servo = QAction("Abrir Servo")
        self.boton_calib_altura = QAction("Calibrar Altura")
        self.boton_tiempo_vuelo = QAction("Comenzar Tiempo de Vuelo")
        self.boton_act_canal = QAction("Actualizar Canal")
        
        self.boton_conec_ser.setEnabled(False)
        self.boton_descon.setEnabled(False)
        self.boton_calib_altura.setEnabled(False)
        self.boton_tiempo_vuelo.setEnabled(False)
        self.boton_act_canal.setEnabled(False)

        self.boton_actualizar.triggered.connect(self.actualizar_puertos_solicitado)
        self.boton_conec_ser.triggered.connect(self.on_conectar_click)
        self.boton_descon.triggered.connect(self.on_desconectar_click)
        self.boton_calib_altura.triggered.connect(self.on_calib_altura_click)
        self.boton_tiempo_vuelo.triggered.connect(self.on_tiempo_vuelo_click)
        self.boton_act_canal.triggered.connect(self.on_actualizar_canal_click)

        self.toolbar.addAction(self.boton_actualizar)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(label_serial)
        self.toolbar.addWidget(self.serial_opts)
        self.toolbar.addWidget(label_baud)
        self.toolbar.addWidget(self.baud_opts)
        self.toolbar.addAction(self.boton_conec_ser)
        self.toolbar.addAction(self.boton_descon)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(label_canal)
        self.toolbar.addWidget(self.canal)
        self.toolbar.addAction(self.boton_act_canal)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.boton_act_servo)
        self.toolbar.addAction(self.boton_des_servo)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.boton_calib_altura)
        self.toolbar.addAction(self.boton_tiempo_vuelo)
    
    # --- SLOTS DE BOTONES ---
    @Slot()
    def on_calib_altura_click(self): self.comando_solicitado.emit("66\n")
    @Slot()
    def on_tiempo_vuelo_click(self): self.comando_solicitado.emit("30\n"); self.boton_tiempo_vuelo.setEnabled(False)
    @Slot()
    def on_actualizar_canal_click(self):
        if not self.canal.text().isdigit() or not (0 <= int(self.canal.text()) <= 126):
            self.panel_inferior.add_log_message("Canal inválido.", "danger"); return
        self.comando_solicitado.emit(f"{self.canal.text()}\n")
        self.panel_inferior.add_log_message(f"Canal {self.canal.text()}...", "info")

    @Slot(list)
    def update_port_list(self, ports: list):
        cur = self.serial_opts.currentText()
        self.serial_opts.clear()
        self.serial_opts.addItems(ports)
        if cur in ports: self.serial_opts.setCurrentText(cur)
        if not self.boton_descon.isEnabled(): self.boton_conec_ser.setEnabled(len(ports) > 0)

    @Slot()
    def on_conectar_click(self):
        if not self.serial_opts.currentText(): return
        self.conexion_solicitada.emit(self.serial_opts.currentText(), int(self.baud_opts.currentText()))
        self.boton_conec_ser.setEnabled(False)
        self.boton_actualizar.setEnabled(False)
        self.serial_opts.setEnabled(False)
        self.baud_opts.setEnabled(False)
        self.boton_descon.setEnabled(True)

    @Slot()
    def on_desconectar_click(self):
        self.desconexion_solicitada.emit()
        self.boton_conec_ser.setEnabled(self.serial_opts.count() > 0)
        self.boton_actualizar.setEnabled(True)
        self.serial_opts.setEnabled(True)
        self.baud_opts.setEnabled(True)
        self.boton_descon.setEnabled(False)
        self.boton_calib_altura.setEnabled(False)
        self.boton_tiempo_vuelo.setEnabled(False)
        self.boton_act_canal.setEnabled(False)

    # --- ¡AQUÍ ESTÁ LA CORRECCIÓN! ---
    @Slot(str, str)
    def on_connection_status(self, message: str, status_type: str):
        """Recibe el estado. SOLO desconecta si es manual o físico."""
        self.panel_inferior.add_log_message(message, status_type)
        
        if status_type == "success":
            self.boton_calib_altura.setEnabled(True)
            self.boton_tiempo_vuelo.setEnabled(True)
            self.boton_act_canal.setEnabled(True)
            
        # Lógica estricta: Solo desconectar UI si el mensaje es de desconexión
        elif message == "Desconectado." or "Puerto desconectado" in message:
            self.on_desconectar_click()
            
        # Otros errores "danger" (parseo, etc.) NO entran aquí y no desconectan.

    def closeEvent(self, event):
        self.desconexion_solicitada.emit() 
        event.accept()
