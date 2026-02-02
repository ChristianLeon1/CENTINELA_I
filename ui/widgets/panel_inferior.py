#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2025 CREADOR: Christian Yael Ramírez León

# ui/widgets/panel_inferior.py

from PySide6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QGridLayout,
    QLabel, QProgressBar, QGroupBox, QTextEdit, QPushButton
)
from PySide6.QtCore import Slot, Qt, QSize, QRectF, QTime
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient

# Importamos la paleta para los colores de la gráfica
from ui.theme import PALETTE

# --- --- --- --- --- --- --- --- --- --- ---
# --- 1. WIDGET: Gráfica de Pastel (Sin cambios) ---
# --- --- --- --- --- --- --- --- --- --- ---

class PieChartWidget(QWidget):
    # ... (Esta clase no cambia en absoluto) ...
    def __init__(self, parent=None):
        super().__init__(parent)
        self.received = 0
        self.lost = 0
        self.setMinimumHeight(80) 
    @Slot(int, int)
    def update_stats(self, received: int, lost: int):
        self.received = received
        self.lost = lost
        self.update() 
    def sizeHint(self) -> QSize:
        return QSize(80, 80)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        margin = 10 
        rect_size = min(self.width(), self.height()) - margin
        rect = QRectF(margin / 2, margin / 2, rect_size, rect_size) 
        total = self.received + self.lost
        grados_en_un_circulo = 360 * 16 
        if total == 0:
            gradient = QRadialGradient(rect.center(), rect.width() / 2)
            gradient.setColorAt(0, QColor(PALETTE['TEXT']['DISABLED']).lighter(120))
            gradient.setColorAt(1, QColor(PALETTE['TEXT']['DISABLED']).darker(120))
            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(rect)
            return
        angle_lost = (self.lost / total) * grados_en_un_circulo
        gradient_lost = QRadialGradient(rect.center(), rect.width() / 2)
        gradient_lost.setColorAt(0, QColor(PALETTE['STATUS']['DANGER']).lighter(150))
        gradient_lost.setColorAt(1, QColor(PALETTE['STATUS']['DANGER']).darker(150))
        painter.setBrush(gradient_lost)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPie(rect, 90 * 16, int(angle_lost))
        angle_received = (self.received / total) * grados_en_un_circulo
        gradient_received = QRadialGradient(rect.center(), rect.width() / 2)
        gradient_received.setColorAt(0, QColor(PALETTE['STATUS']['SUCCESS']).lighter(150))
        gradient_received.setColorAt(1, QColor(PALETTE['STATUS']['SUCCESS']).darker(150))
        painter.setBrush(gradient_received)
        painter.setPen(Qt.PenStyle.NoPen)
        start_angle = (90 * 16) + int(angle_lost)
        painter.drawPie(rect, start_angle, int(angle_received))

# --- --- --- --- --- --- --- --- --- --- ---
# --- 2. TU PANEL INFERIOR (Modificado) ---
# --- --- --- --- --- --- --- --- --- --- ---

class PanelInferior(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedHeight(170) 

        main_layout = QHBoxLayout(self)
        
        # --- 1. Panel Izquierdo (Sin cambios) ---
        panel_izquierdo = QFrame()
        panel_izquierdo.setFrameShape(QFrame.Shape.StyledPanel)
        layout_izquierdo = QVBoxLayout(panel_izquierdo)
        baterias_layout = QGridLayout()
        self.bateria_cohete_bar = QProgressBar()
        self.bateria_cohete_bar.setFixedHeight(18)
        self.bateria_cohete_bar.setTextVisible(True)
        self.bateria_cohete_bar.setValue(0)
        self.bateria_camara_bar = QProgressBar()
        self.bateria_camara_bar.setFixedHeight(18)
        self.bateria_camara_bar.setTextVisible(True)
        self.bateria_camara_bar.setValue(0)
        baterias_layout.addWidget(QLabel("Bateria de cohete:"), 0, 0)
        baterias_layout.addWidget(self.bateria_cohete_bar, 0, 1)
        baterias_layout.addWidget(QLabel("Bateria de camara:"), 1, 0)
        baterias_layout.addWidget(self.bateria_camara_bar, 1, 1)
        baterias_layout.setColumnStretch(1, 1) 
        layout_izquierdo.addLayout(baterias_layout)
        grupo_emergencia = QGroupBox("Mensajes")
        layout_emergencia = QVBoxLayout(grupo_emergencia)
        self.log_emergencia = QTextEdit()
        self.log_emergencia.setReadOnly(True)
        self.log_emergencia.setPlaceholderText("Esperando mensajes...")
        layout_emergencia.addWidget(self.log_emergencia)
        layout_izquierdo.addWidget(grupo_emergencia)

        # --- 2. Panel Central (Resumen de Paquetes) ---
        panel_central = QFrame()
        panel_central.setFrameShape(QFrame.Shape.StyledPanel)
        layout_central = QVBoxLayout(panel_central)
        
        grupo_paquetes = QGroupBox("Resumen de Paquetes")
        
        # Layout principal del grupo (Horizontal)
        layout_paquetes = QHBoxLayout(grupo_paquetes)
        
        # Columna Izquierda: Gráfica
        self.pie_chart_paquetes = PieChartWidget()
        
        # --- ¡CAMBIO AQUÍ! ---
        
        # Contenedor para centrar verticalmente el grid de texto
        layout_texto_wrapper = QVBoxLayout()
        
        # Grid para alinear el texto
        layout_texto_paquetes = QGridLayout()
        
        # Etiquetas estáticas (Columna 0)
        label_rec_static = QLabel("Recibidos:")
        label_per_static = QLabel("Perdidos:")
        label_rec_static.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        label_per_static.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Etiquetas de datos (Columna 1)
        self.label_paquetes_recibidos = QLabel("0")
        self.label_paquetes_perdidos = QLabel("0")
        self.label_paquetes_recibidos.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.label_paquetes_perdidos.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Añadir al Grid
        layout_texto_paquetes.addWidget(label_rec_static, 0, 0)
        layout_texto_paquetes.addWidget(self.label_paquetes_recibidos, 0, 1)
        layout_texto_paquetes.addWidget(label_per_static, 1, 0)
        layout_texto_paquetes.addWidget(self.label_paquetes_perdidos, 1, 1)
        
        # Añadir stretches al wrapper para centrar el grid
        layout_texto_wrapper.addStretch(1)
        layout_texto_wrapper.addLayout(layout_texto_paquetes)
        layout_texto_wrapper.addStretch(1)
        
        # Ensamblar el layout de paquetes
        layout_paquetes.addWidget(self.pie_chart_paquetes, 1) # Factor 1
        layout_paquetes.addLayout(layout_texto_wrapper, 1) # Factor 1
        
        layout_central.addWidget(grupo_paquetes)

        # --- 3. Panel Derecho (Sin cambios) ---
        panel_derecho = QFrame()
        panel_derecho.setFrameShape(QFrame.Shape.StyledPanel)
        layout_derecho = QVBoxLayout(panel_derecho)
        grupo_botones = QGroupBox("Comandos")
        layout_botones = QGridLayout(grupo_botones)
        self.btn_cmd_1 = QPushButton("ABORTAR")
        self.btn_cmd_2 = QPushButton("SECUENCIA")
        self.btn_cmd_3 = QPushButton("Payload 1")
        self.btn_cmd_4 = QPushButton("Payload 2")
        self.btn_cmd_5 = QPushButton("Comando 5")
        self.btn_cmd_6 = QPushButton("Comando 6")
        self.btn_cmd_1.setStyleSheet("background-color: #F44336; color: white; font-weight: bold;")
        layout_botones.addWidget(self.btn_cmd_1, 0, 0)
        layout_botones.addWidget(self.btn_cmd_2, 0, 1)
        layout_botones.addWidget(self.btn_cmd_3, 0, 2)
        layout_botones.addWidget(self.btn_cmd_4, 1, 0)
        layout_botones.addWidget(self.btn_cmd_5, 1, 1)
        layout_botones.addWidget(self.btn_cmd_6, 1, 2)
        layout_derecho.addWidget(grupo_botones)

        # --- 4. Ensamblar Layout Principal (35/20/45) ---
        main_layout.addWidget(panel_izquierdo, 35)
        main_layout.addWidget(panel_central, 20)
        main_layout.addWidget(panel_derecho, 45)

    # --- Slots ---
    
    @Slot(int)
    def update_bateria_cohete(self, porcentaje: int):
        self.bateria_cohete_bar.setValue(porcentaje)
    
    @Slot(int)
    def update_bateria_camara(self, porcentaje: int):
        self.bateria_camara_bar.setValue(porcentaje)
    
    @Slot(str)
    def add_mensaje_emergencia(self, mensaje: str):
        self.log_emergencia.append(f"[ERROR] {mensaje}") 

    def add_log_message(self, message: str, status_type: str):
        """
        Añade un mensaje al log de mensajes, con formato y color.
        """
        timestamp = QTime.currentTime().toString("hh:mm:ss")
        
        # Asignar color basado en el tipo de estado
        if status_type == "danger":
            color = PALETTE['STATUS']['DANGER']
        elif status_type == "success":
            color = PALETTE['STATUS']['SUCCESS']
        elif status_type == "info":
            color = PALETTE['TEXT']['SECONDARY']
        else:
            color = PALETTE['TEXT']['PRIMARY']
        
        # Usamos HTML simple para el color
        log_entry = f"""
            <span style="color: {PALETTE['TEXT']['SECONDARY']};">[{timestamp}] </span>
            <span style="color: {color};">{message}</span>
        """
        self.log_emergencia.append(log_entry)
        
    @Slot(int, int)
    def update_packet_summary(self, received: int, lost: int):
        """
        Slot público para actualizar el resumen de paquetes.
        """
        # --- ¡CAMBIO AQUÍ! ---
        self.label_paquetes_recibidos.setText(str(received))
        self.label_paquetes_perdidos.setText(str(lost))
        # ---------------------
        self.pie_chart_paquetes.update_stats(received, lost)
