#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2025 CREADOR: Christian Yael Ramírez León

# ui/widgets/panel_calidad_aire.py

# ui/widgets/panel_calidad_aire.py

import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QColor

# Importamos la paleta y numpy para los datos
from ui.theme import PALETTE

# (Configuramos el tema de pyqtgraph)
pg.setConfigOption('background', None) 
pg.setConfigOption('foreground', PALETTE['TEXT']['SECONDARY'])
pg.setConfigOption('antialias', True)

class PanelCalidadAire(QFrame):
    """
    Panel que muestra las gráficas de Calidad del Aire (CO2/TVOC)
    y Humedad con paginación automática del eje X.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 1. El QFrame exterior obtiene el estilo
        self.setProperty("isPanel", True)
        
        # --- VARIABLES PARA LA PAGINACIÓN (SCROLL) ---
        self.current_max_x = 15.0  # Límite actual
        self.window_size = 15.0    # Tamaño de ventana
        # --------------------------------------------
        
        # Layout principal (sin márgenes)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 2. Widget contenedor interno
        container_widget = QWidget()
        
        # 3. Layout del contenedor (CON los márgenes internos)
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(10)

        # 4. Añadir el contenedor al layout principal
        main_layout.addWidget(container_widget)

        titulo = QLabel("Calidad del Aire")
        titulo.setProperty("isTitulo", True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(titulo)

        # --- 1. Gráfica Superior (CO2 y TVOC) ---
        self.plot_gases = pg.PlotWidget()
        self.plot_gases.showGrid(x=True, y=True, alpha=0.3)
        self.plot_gases.setLabel('left', 'Gases', units='ppm')
        self.plot_gases.setLabel('bottom', 'Tiempo', units='s')
        self.plot_gases.getPlotItem().setMenuEnabled(False)
        
        # Configuración de Ejes
        self.plot_gases.setXRange(0, 15)
        self.plot_gases.setMouseEnabled(x=False, y=True) # Bloquear zoom X manual
        
        self.plot_gases.addLegend(offset=(10, 5))

        self.line_co2 = self.plot_gases.plot(
            pen=pg.mkPen(PALETTE['ACCENT']['ACTIVE'], width=2), 
            name="CO2"
        )
        self.line_tvoc = self.plot_gases.plot(
            pen=pg.mkPen(PALETTE['STATUS']['WARNING'], width=2),
            name="TVOC"
        )
        
        container_layout.addWidget(self.plot_gases, 1)

        # --- 2. Gráfica Inferior (Humedad) ---
        self.plot_humedad = pg.PlotWidget()
        self.plot_humedad.showGrid(x=True, y=True, alpha=0.3)
        self.plot_humedad.setLabel('left', 'Humedad', units='%')
        self.plot_humedad.setLabel('bottom', 'Tiempo', units='s')
        self.plot_humedad.getPlotItem().setMenuEnabled(False)
        
        # Configuración de Ejes
        self.plot_humedad.setXRange(0, 15)
        self.plot_humedad.setMouseEnabled(x=False, y=True) # Bloquear zoom X manual
        self.plot_humedad.getPlotItem().setAspectLocked(False)
        
        pen_hum = pg.mkPen(PALETTE['STATUS']['INFO'], width=2)
        brush_hum = (*QColor(PALETTE['STATUS']['INFO']).getRgb()[:3], 50)
        
        self.line_humedad = self.plot_humedad.plot(
            pen=pen_hum,
            fillLevel=0, 
            brush=brush_hum
        )
        
        container_layout.addWidget(self.plot_humedad, 1)

    # --- Lógica de Paginación del Eje X ---
    def check_and_scroll_xaxis(self, current_time):
        """
        Verifica si el tiempo actual ha superado el límite.
        Si es así, desplaza ambas gráficas al siguiente bloque de 15s.
        """
        if current_time > self.current_max_x:
            while current_time > self.current_max_x:
                self.current_max_x += self.window_size
            
            min_x = self.current_max_x - self.window_size
            max_x = self.current_max_x
            
            # Aplicar a AMBAS gráficas para mantener sincronía
            self.plot_gases.setXRange(min_x, max_x)
            self.plot_humedad.setXRange(min_x, max_x)

    # --- SLOTS DE ACTUALIZACIÓN ---

    @Slot(list, list, list)
    def update_gases_graph(self, x_data: list, co2_data: list, tvoc_data: list):
        """
        Actualiza la gráfica superior con nuevos datos de CO2 y TVOC.
        """
        if x_data:
            self.check_and_scroll_xaxis(x_data[-1])
            self.line_co2.setData(x_data, co2_data)
            self.line_tvoc.setData(x_data, tvoc_data)
    
    @Slot(list, list)
    def update_humidity_graph(self, x_data: list, humidity_data: list):
        """
        Actualiza la gráfica inferior con nuevos datos de Humedad.
        """
        if x_data:
            # (La comprobación ya se hace arriba, pero no daña repetirla si llegan desfasados)
            self.check_and_scroll_xaxis(x_data[-1])
            self.line_humedad.setData(x_data, humidity_data)
