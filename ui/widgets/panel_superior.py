#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2025 CREADOR: Christian Yael Ramírez León

# ui/widgets/panel_superior.py

from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap, QResizeEvent
from PySide6.QtCore import Qt, QTimer, QDateTime

class PanelSuperior(QFrame):
    """
    El panel superior que muestra el logo, título dinámico (con dos QLabels) y hora.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        self.setFixedHeight(70) 

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 10, 30, 5)

        self.title_threshold = 900 

        # --- 1. Izquierda: Logo ---
        self.logo = QLabel()
        pixmap = QPixmap("logo.png") 
        
        if pixmap.isNull():
            self.logo.setText("LOGO")
            self.logo.setStyleSheet("font-weight: bold;")
        else:
            self.logo.setPixmap(pixmap.scaledToHeight(70, Qt.TransformationMode.SmoothTransformation))
        
        # --- 2. Centro: Título Dinámico ---
        self.title_container = QWidget()
        self.title_layout = QHBoxLayout(self.title_container)
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_layout.setSpacing(5)
        
        # --- ¡CAMBIO AQUÍ! ---
        # 1. Establecer la alineación del QHBoxLayout principal
        #    Esto centra verticalmente AMBOS (Centinela y el grupo de subtítulos)
        self.title_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.label_centinela = QLabel("CENTINELA")
        self.label_centinela.setStyleSheet("font-size: 22pt; font-weight: bold;")
        # (Ya no se necesita alineación aquí, el layout la maneja)

        # QVBoxLayout para las dos líneas pequeñas
        self.label_subtitles_layout = QVBoxLayout()
        self.label_subtitles_layout.setContentsMargins(0, 0, 0, 0)
        self.label_subtitles_layout.setSpacing(0)

        self.label_centro_inicial = QLabel("CENTRO INICIAL")
        self.label_centro_inicial.setStyleSheet("font-size: 10pt;")
        self.label_centro_inicial.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.label_ejecucion = QLabel("EJECUCION LANZAMIENTO")
        self.label_ejecucion.setStyleSheet("font-size: 10pt;")
        self.label_ejecucion.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.label_subtitles_layout.addStretch(1) # Espacio flexible ARRIBA
        self.label_subtitles_layout.addWidget(self.label_centro_inicial)
        self.label_subtitles_layout.addWidget(self.label_ejecucion)
        self.label_subtitles_layout.addStretch(1) # Espacio flexible ABAJO

        # Añadimos los elementos al layout horizontal del título
        self.title_layout.addWidget(self.label_centinela)
        self.title_layout.addLayout(self.label_subtitles_layout)
        
        # --- 3. Derecha: Hora ---
        self.time_label = QLabel("--:--:--")
        self.time_label.setStyleSheet("font-size: 14pt; font-family: 'Consolas', 'Monospace';")
        
        # --- 4. Ensamblado del Layout Principal (Horizontal) ---
        main_layout.addWidget(self.logo)
        main_layout.addStretch(1)
        main_layout.addWidget(self.title_container)
        main_layout.addStretch(1)
        main_layout.addWidget(self.time_label)

        # --- 5. Temporizador para el reloj ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        self._update_time()
        
        self._update_title_visibility_based_on_size()

    def _update_time(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss ap")
        self.time_label.setText(current_time)

    def _update_title_visibility_based_on_size(self):
        """
        Comprueba el ancho actual del panel y ajusta la visibilidad.
        """
        current_width = self.width()
        
        if current_width < self.title_threshold:
            # Espacio PEQUEÑO: Ocultar los subtítulos
            self.label_centro_inicial.hide()
            self.label_ejecucion.hide()
            self.label_centinela.setText("CENTINELA") # Quitar los dos puntos
            self.title_layout.setSpacing(0)
            self.label_centinela.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            # Espacio GRANDE: Mostrar todo
            self.label_centro_inicial.show()
            self.label_ejecucion.show()
            self.label_centinela.setText("CENTINELA   ") # Poner los dos puntos
            self.title_layout.setSpacing(5)
            # Alinear con el layout de subtítulos
            self.label_centinela.setAlignment(Qt.AlignmentFlag.AlignVCenter)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self._update_title_visibility_based_on_size()
