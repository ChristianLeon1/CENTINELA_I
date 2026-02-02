#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2025 CREADOR: Christian Yael Ramírez León

import io

import folium
from PySide6.QtCore import Qt, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class PanelGPS(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- 1. Layout Principal Horizontal ---
        main_layout = QHBoxLayout(self)

        # --- 2. Columna Izquierda: El Mapa ---
        self.gps_frame = QFrame()
        # self.gps_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.gps_frame.setProperty("isPanel", True)

        frame_layout = QVBoxLayout(self.gps_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        self.gps_w = QWebEngineView()
        self.gps_w.setStyleSheet("background-color: #101829;")
        frame_layout.addWidget(self.gps_w)

        # --- 3. Columna Derecha: Panel de Datos ---
        self.info_panel = self._crear_panel_info()  # <-- Modificado

        # --- 4. Añadir ambas columnas al layout ---
        main_layout.addWidget(self.gps_frame, 3)  # 75% ancho
        main_layout.addWidget(self.info_panel, 1)  # 25% ancho

        # Cargar mapa inicial
        self._renderizar_mapa([19.4284, -99.1276], init=True)

    def _crear_panel_info(self) -> QFrame:
        """Crea el panel derecho con etiquetas alineadas y espaciado vertical."""
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)

        # Layout vertical principal para el panel derecho
        main_panel_layout = QVBoxLayout(panel)

        # --- 1. AÑADIR MARGEN SUPERIOR (FLEXIBLE) ---
        # Usamos un factor de estiramiento de 2 para un margen grande
        main_panel_layout.addStretch(2)

        # Añadimos un espacio fijo pequeño después del título
        main_panel_layout.addSpacing(20)

        # --- El QGridLayout para los datos ---
        data_layout = QGridLayout()
        data_layout.setContentsMargins(10, 10, 10, 10)
        data_layout.setColumnStretch(1, 1)
        data_layout.setVerticalSpacing(30)

        # --- Etiquetas Estáticas (Columna 0) ---
        label_lat_static = QLabel("Latitud:")
        label_lon_static = QLabel("Longitud:")
        label_start_static = QLabel("T. de inicio:")
        label_flight_static = QLabel("T. de vuelo:")

        label_lat_static.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        label_lon_static.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        label_start_static.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        label_flight_static.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        # --- Etiquetas de Datos (Columna 1) ---
        self.label_lat_data = QLabel("--")
        self.label_lon_data = QLabel("--")
        self.label_start_time_data = QLabel("--")
        self.label_flight_time_data = QLabel("--")

        # --- Añadir al Grid (con filas modificadas) ---
        # Fila 0: Latitud
        data_layout.addWidget(label_lat_static, 0, 0)
        data_layout.addWidget(self.label_lat_data, 0, 1)
        # Fila 1: Longitud
        data_layout.addWidget(label_lon_static, 1, 0)
        data_layout.addWidget(self.label_lon_data, 1, 1)

        # --- 2. SEPARADOR VERTICAL (FLEXIBLE) ---
        # Añadimos un stretch en la Fila 2 para separar los grupos
        data_layout.setRowStretch(2, 1)

        # Fila 3: T. de inicio
        data_layout.addWidget(label_start_static, 3, 0)
        data_layout.addWidget(self.label_start_time_data, 3, 1)
        # Fila 4: T. de vuelo
        data_layout.addWidget(label_flight_static, 4, 0)
        data_layout.addWidget(self.label_flight_time_data, 4, 1)

        # Añadir el grid al layout principal del panel
        main_panel_layout.addLayout(data_layout)

        # --- 3. AÑADIR MARGEN INFERIOR (FLEXIBLE) ---
        # Usamos un factor de 2 para que sea igual al superior
        main_panel_layout.addStretch(2)

        return panel

    def _renderizar_mapa(self, location: list, init=False):
        """Función interna para actualizar el mapa Folium."""
        m = folium.Map(
            location=location,
            zoom_start=18 if not init else 6,
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery",
        )
        if not init:
            folium.CircleMarker(
                location=location,
                radius=6,
                color="red",
                fill=True,
                border=True,
                opacity=1,
            ).add_to(m)
        data = io.BytesIO()
        m.save(data, close_file=False)
        self.gps_w.setHtml(data.getvalue().decode())

    @Slot(dict)
    def update_data(self, data: dict):
        """
        Este es el SLOT público. Actualiza el mapa
        y las etiquetas de datos separadas.
        """

        # Actualizar Mapa
        if "location" in data:
            self._renderizar_mapa(data["location"])

            # --- Actualizar las etiquetas de DATOS ---
            self.label_lat_data.setText(f"{data['location'][0]:.6f}")
            self.label_lon_data.setText(f"{data['location'][1]:.6f}")

        # Actualizar T. de inicio
        if "start_time" in data:
            self.label_start_time_data.setText(f"{data['start_time']}")

        # Actualizar T. de vuelo
        if "flight_time" in data:
            self.label_flight_time_data.setText(f"{data['flight_time']:.2f} s")
