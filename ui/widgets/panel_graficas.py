#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2025 CREADOR: Christian Yael Ramírez León

# ui/widgets/panel_graficas.py

import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QColor
from ui.theme import PALETTE

# Configuración global de pyqtgraph para que coincida con el tema
pg.setConfigOption('background', None) 
pg.setConfigOption('foreground', PALETTE['TEXT']['SECONDARY'])
pg.setConfigOption('antialias', True)

# --- 1. Clase Base para la Gráfica ---
class CustomGraph(pg.PlotWidget):
    def __init__(self, name="", units="",  pen=None, brush=None, parent=None):
        super().__init__(parent)
        
        # Configuración de Ejes y Rejilla
        self.showGrid(x=True, y=True, alpha=0.3)
        self.setLabel('left', name, units=units)
        self.setLabel('bottom', 'Tiempo', units='s')
        
        # Rango inicial del eje X (0 a 15 segundos)
        self.setXRange(0, 15)
        
        # Deshabilitar interacción del mouse para que no rompa la lógica automática
        # (Puedes cambiar a True si quieres permitir zoom manual)
        self.setMouseEnabled(x=False, y=True)
        self.getPlotItem().setMenuEnabled(False)
        
        # Ajuste de margen izquierdo para que los números no se corten
        self.getPlotItem().getAxis('left').setWidth(60)

        # Crear la curva de datos
        self.data_line = self.plot(pen=pen, fillLevel=0, brush=brush)

    def update_data(self, x_data, y_data):
        """Actualiza la línea con nuevos datos."""
        self.data_line.setData(x_data, y_data)

# --- 2. Panel Principal de Gráficas ---
class PanelGraficas(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("isPanel", True)
        
        # --- Variables para la lógica de paginación (Scroll) ---
        self.current_max_x = 15.0  # El límite actual (ej. 15, 30, 45...)
        self.window_size = 15.0    # El tamaño de la ventana (15 segundos)
        # -----------------------------------------------------

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Margen interno para que no se pegue al borde del frame
        main_layout.setContentsMargins(10, 10, 10, 10)

        # --- COLUMNA IZQUIERDA: PRESIÓN ---
        col_pressure = QVBoxLayout()
        col_pressure.setSpacing(5)
        
        # Estilo (Cian)
        pen_p = pg.mkPen(PALETTE['ACCENT']['ACTIVE'], width=2)
        brush_p = (*QColor(PALETTE['ACCENT']['ACTIVE']).getRgb()[:3], 30) # 30 = transparencia
        
        self.graph_pressure = CustomGraph("Presión", "KPa", pen=pen_p, brush=brush_p)
        self.label_pressure = QLabel("Presión: 0.00 KPa")
        self.label_pressure.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_pressure.setStyleSheet("font-size: 11pt; font-weight: bold;")
        
        col_pressure.addWidget(self.graph_pressure)
        col_pressure.addWidget(self.label_pressure)
        
        # --- COLUMNA DERECHA: TEMPERATURA ---
        col_temp = QVBoxLayout()
        col_temp.setSpacing(5)
        
        # Estilo (Amarillo/Ámbar)
        pen_t = pg.mkPen(PALETTE['STATUS']['WARNING'], width=2)
        brush_t = (*QColor(PALETTE['STATUS']['WARNING']).getRgb()[:3], 30)

        self.graph_temp = CustomGraph("Temperatura", "°C", pen=pen_t, brush=brush_t)
        self.label_temp = QLabel("Temperatura: 0.00 °C")
        self.label_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_temp.setStyleSheet("font-size: 11pt; font-weight: bold;")
        
        col_temp.addWidget(self.graph_temp)
        col_temp.addWidget(self.label_temp)

        # Añadir columnas al layout principal
        main_layout.addLayout(col_pressure, 1)
        main_layout.addLayout(col_temp, 1)

    # --- Lógica de Paginación del Eje X ---
    def check_and_scroll_xaxis(self, current_time):
        """
        Verifica si el tiempo actual ha superado el límite de la ventana.
        Si es así, desplaza el eje X al siguiente bloque de 15 segundos.
        """
        if current_time > self.current_max_x:
            # Aumentamos el límite en bloques de 15
            # (Usamos while por si hubo un salto grande de tiempo)
            while current_time > self.current_max_x:
                self.current_max_x += self.window_size
            
            min_x = self.current_max_x - self.window_size
            max_x = self.current_max_x
            
            # Aplicar el nuevo rango a AMBAS gráficas
            self.graph_pressure.setXRange(min_x, max_x)
            self.graph_temp.setXRange(min_x, max_x)

    # --- Slots de Actualización ---

    @Slot(list, list)
    def update_pressure_graph(self, x_data: list, y_data: list):
        if x_data:
             # 1. Verificar si hay que mover el eje X
             self.check_and_scroll_xaxis(x_data[-1])
             # 2. Actualizar datos
             self.graph_pressure.update_data(x_data, y_data)
    
    @Slot(str)
    def update_pressure_label(self, text):
        self.label_pressure.setText(text)

    @Slot(list, list)
    def update_temp_graph(self, x_data, y_data):
         if x_data:
             self.check_and_scroll_xaxis(x_data[-1])
             self.graph_temp.update_data(x_data, y_data)
    
    @Slot(str)
    def update_temp_label(self, text):
        self.label_temp.setText(text)
