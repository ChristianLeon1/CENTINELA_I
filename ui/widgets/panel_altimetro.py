#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2025 CREADOR: Christian Yael Ramírez León

# ui/widgets/panel_altimetro.py

from PySide6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, 
    QLabel, QProgressBar
)
from PySide6.QtCore import Slot, Qt
from ui.theme import PALETTE

class PanelAltimetro(QFrame):
    """
    Panel de altímetro vertical (estilo "cinta").
    Rango 1.2 km. Texto de valor fijo para evitar saltos.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- Configuración del Panel ---
        self.setProperty("isPanel", True) 
        self.setFixedWidth(140) 

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # --- 1. ZONA SUPERIOR: Barra y Marcas ---
        container_grafico = QWidget()
        layout_grafico = QHBoxLayout(container_grafico)
        layout_grafico.setContentsMargins(0, 0, 0, 0)

        # 1a. La Barra (Izquierda)
        self.alt_bar = QProgressBar()
        self.alt_bar.setOrientation(Qt.Orientation.Vertical)
        self.alt_bar.setRange(0, 1200) 
        self.alt_bar.setValue(0)
        self.alt_bar.setTextVisible(False) 
        
        self.alt_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {PALETTE['TEXT']['PRIMARY']};
                border-radius: 1px;
                background-color: transparent;
                width: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {PALETTE['STATUS']['DANGER']};
            }}
        """)
        
        layout_grafico.addWidget(self.alt_bar)

        # 1b. Las Marcas (Derecha)
        layout_marcas = QVBoxLayout()
        layout_marcas.setContentsMargins(5, 0, 0, 0)
        layout_marcas.setSpacing(0)

        def crear_marca(texto):
            lbl = QLabel(f"- {texto}")
            lbl.setStyleSheet(f"font-size: 8pt; color: {PALETTE['TEXT']['PRIMARY']};")
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            lbl.setFixedHeight(15) 
            return lbl

        # ESCALA (0 - 1200)
        layout_marcas.addWidget(crear_marca("1.2 km"))
        layout_marcas.addStretch(200)
        layout_marcas.addWidget(crear_marca("1 km"))
        layout_marcas.addStretch(500)
        layout_marcas.addWidget(crear_marca("500 m"))
        layout_marcas.addStretch(300)
        layout_marcas.addWidget(crear_marca("200 m"))
        layout_marcas.addStretch(200)
        layout_marcas.addWidget(crear_marca("0 m"))

        layout_grafico.addLayout(layout_marcas)
        
        main_layout.addWidget(container_grafico, 1)

        # --- 2. ZONA MEDIA: Título "ALTITUD" ---
        frame_titulo = QFrame()
        frame_titulo.setStyleSheet(f"""
            background-color: {PALETTE['ACCENT']['ACTIVE']}; 
            border-radius: 4px;
        """)
        frame_titulo.setFixedHeight(30)
        
        layout_titulo = QVBoxLayout(frame_titulo)
        layout_titulo.setContentsMargins(0, 0, 0, 0)
        
        label_titulo = QLabel("ALTURA")
        label_titulo.setStyleSheet("font-weight: bold; color: black;")
        label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout_titulo.addWidget(label_titulo)
        main_layout.addWidget(frame_titulo)

        # --- 3. ZONA INFERIOR: Valor Numérico (CORREGIDO) ---
        
        # Usamos un contenedor para centrar el label fijo
        container_valor = QWidget()
        layout_valor = QHBoxLayout(container_valor)
        layout_valor.setContentsMargins(0, 0, 0, 0)
        layout_valor.setAlignment(Qt.AlignmentFlag.AlignCenter) # Centra el label en el panel
        
        self.label_valor = QLabel("0 m")
        self.label_valor.setAlignment(Qt.AlignmentFlag.AlignCenter) # Centra el texto en el label
        self.label_valor.setFixedHeight(30)
        
        # --- ¡CAMBIO CLAVE! ---
        # Fijamos el ancho para que no cambie al cambiar los dígitos (ej. 10 vs 1000)
        # El panel mide 140, menos 20 de margen = 120 disponible. Usamos 115.
        self.label_valor.setFixedWidth(115) 
        
        # Usamos una fuente Monospace (ancho fijo por caracter) para evitar saltos internos
        self.label_valor.setStyleSheet(f"""
            background-color: {PALETTE['BACKGROUND']['MAIN']};
            border: 1px solid {PALETTE['BORDER']['DEFAULT']};
            border-radius: 4px;
            color: {PALETTE['TEXT']['PRIMARY']};
            font-size: 10pt;
            font-family: 'Consolas', 'Monospace', monospace; 
        """)
        
        layout_valor.addWidget(self.label_valor)
        main_layout.addWidget(container_valor)

    @Slot(int)
    def update_altitud(self, altitud: int):
        """
        Slot público para actualizar la altitud.
        """
        val_limitado = max(0, min(altitud, 1200))
        self.alt_bar.setValue(val_limitado)
        
        # Formateo de texto fijo
        self.label_valor.setText(f"Altura: {altitud} m")
