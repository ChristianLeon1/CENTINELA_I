#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2025 CREADOR: Christian Yael Ramírez León

# ui/widgets/panel_calidad_aire.py

import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QColor

# Importamos la paleta y numpy para los datos
from ui.theme import PALETTE
import numpy as np

# (Configuramos el tema de pyqtgraph)
pg.setConfigOption('background', None) 
pg.setConfigOption('foreground', PALETTE['TEXT']['SECONDARY'])

class PanelCalidadAire(QFrame):
    """
    Panel que muestra las gráficas de Calidad del Aire (CO2/TVOC)
    y Humedad.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 1. El QFrame exterior (PanelCalidadAire) obtiene el estilo
        self.setProperty("isPanel", True)
        
        # Layout principal (sin márgenes) para el QFrame
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 2. Widget contenedor interno (transparente)
        container_widget = QWidget()
        
        # 3. Layout del contenedor (CON los márgenes)
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(10, 10, 100, 10) # ¡EL MARGEN INTERNO!
        container_layout.setSpacing(10)

        # 4. Añadir el contenedor al layout principal
        main_layout.addWidget(container_widget)

        # --- A partir de aquí, añadimos todo al "container_layout" ---

        titulo = QLabel("Calidad del Aire")
        titulo.setProperty("isTitulo", True)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(titulo)

        # Gráfica Superior (CO2 y TVOC)
        self.plot_gases = pg.PlotWidget()
        self.plot_gases.showGrid(x=True, y=True)
        self.plot_gases.setLabel('left', 'Gases', units='ppm')
        self.plot_gases.setLabel('bottom', 'Tiempo', units='s')
        self.plot_gases.getPlotItem().setMenuEnabled(False)
        self.plot_gases.setXRange(0, 15) 
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

        # Gráfica Inferior (Humedad)
        self.plot_humedad = pg.PlotWidget()
        self.plot_humedad.showGrid(x=True, y=True)
        self.plot_humedad.setLabel('left', 'Humedad', units='%')
        self.plot_humedad.setLabel('bottom', 'Tiempo', units='s')
        self.plot_humedad.getPlotItem().setMenuEnabled(False)
        self.plot_humedad.setXRange(0, 15)
        self.plot_humedad.getPlotItem().setAspectLocked(False)
        pen_hum = pg.mkPen(PALETTE['STATUS']['INFO'], width=2)
        brush_hum = (*QColor(PALETTE['STATUS']['INFO']).getRgb()[:3], 50)
        self.line_humedad = self.plot_humedad.plot(
            pen=pen_hum,
            fillLevel=0, 
            brush=brush_hum
        )
        container_layout.addWidget(self.plot_humedad, 1)

    # --- SLOTS (Sin cambios) ---

    @Slot(list, list, list)
    def update_gases_graph(self, x_data: list, co2_data: list, tvoc_data: list):
        self.line_co2.setData(x_data, co2_data)
        self.line_tvoc.setData(x_data, tvoc_data)
    
    @Slot(list, list)
    def update_humidity_graph(self, x_data: list, humidity_data: list):
        self.line_humedad.setData(x_data, humidity_data)
