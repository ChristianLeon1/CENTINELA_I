#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2025 CREADOR: Christian Yael Ramírez León

# ui/widgets/panel_cinematica.py

from PySide6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QGridLayout,
    QLabel, QProgressBar, QDial
)
from PySide6.QtCore import Slot, Qt

from .compass_widget import Compass 

class PanelCinematica(QFrame):
    """
    Panel de cinemática para el visor 3D.
    Muestra Aceleración, Velocidad y una Brújula.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("isPanel", True)
        
        self.setFixedHeight(180) 

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)

        # --- 1. Panel Izquierdo (Datos y Barras) ---
        panel_datos = QWidget()
        layout_datos = QGridLayout(panel_datos)
        layout_datos.setSpacing(5)
        
        # --- ¡CAMBIO AQUÍ! Configuración de proporciones ---
        # Columna 0 (Etiquetas): 10%
        # Columna 1 (Datos):     15%
        # Columna 2 (Barras):    75%
        layout_datos.setColumnStretch(0, 10)
        layout_datos.setColumnStretch(1, 15)
        layout_datos.setColumnStretch(2, 75)
        # -------------------------------------------------

        # --- Aceleración X ---
        self.label_accel_x = QLabel("0.0 m/s²")
        self.accel_x_bar = QProgressBar()
        self.accel_x_bar.setRange(0, 20)
        self.accel_x_bar.setTextVisible(False)

        # --- Aceleración Y ---
        self.label_accel_y = QLabel("0.0 m/s²")
        self.accel_y_bar = QProgressBar()
        self.accel_y_bar.setRange(0, 20)
        self.accel_y_bar.setTextVisible(False)
        
        # --- Aceleración Z ---
        self.label_accel_z = QLabel("0.0 m/s²")
        self.accel_z_bar = QProgressBar()
        self.accel_z_bar.setRange(0, 20)
        self.accel_z_bar.setTextVisible(False)
        
        # --- Velocidad ---
        self.label_vel = QLabel("0.0 m/s")
        self.vel_bar = QProgressBar()
        self.vel_bar.setRange(0, 150)
        self.vel_bar.setTextVisible(False)

        # --- Ensamblado del Grid ---
        # Fila 0
        layout_datos.addWidget(QLabel("Accel X:"), 0, 0)
        layout_datos.addWidget(self.label_accel_x, 0, 1) # Columna del 15%
        layout_datos.addWidget(self.accel_x_bar, 0, 2)   # Columna del 75%
        
        # Fila 1
        layout_datos.addWidget(QLabel("Accel Y:"), 1, 0)
        layout_datos.addWidget(self.label_accel_y, 1, 1)
        layout_datos.addWidget(self.accel_y_bar, 1, 2)
        
        # Fila 2
        layout_datos.addWidget(QLabel("Accel Z:"), 2, 0)
        layout_datos.addWidget(self.label_accel_z, 2, 1)
        layout_datos.addWidget(self.accel_z_bar, 2, 2)
        
        # Fila 3 - Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        # El separador abarca las 3 columnas
        layout_datos.addWidget(separator, 3, 0, 1, 3) 
        
        # Fila 4
        layout_datos.addWidget(QLabel("Velocidad:"), 4, 0)
        layout_datos.addWidget(self.label_vel, 4, 1)
        layout_datos.addWidget(self.vel_bar, 4, 2)

        # --- 2. Panel Derecho (Brújula) ---
        panel_brujula = QWidget()
        layout_brujula = QVBoxLayout(panel_brujula)
        
        self.compass = Compass()
        
        layout_brujula.addWidget(self.compass)
        
        # --- 3. Ensamblado Principal ---
        main_layout.addWidget(panel_datos, 3)
        main_layout.addWidget(panel_brujula, 1)

    @Slot(dict)
    def update_cinematica(self, data: dict):
        """
        Slot público para recibir datos de cinemática y actualizar la UI.
        """
        
        if 'ax' in data:
            val_ax = data['ax']
            self.label_accel_x.setText(f"{val_ax:.1f} m/s²")
            self.accel_x_bar.setValue(int(abs(val_ax))) 
            
        if 'ay' in data:
            val_ay = data['ay']
            self.label_accel_y.setText(f"{val_ay:.1f} m/s²")
            self.accel_y_bar.setValue(int(abs(val_ay)))
            
        if 'az' in data:
            val_az = data['az']
            self.label_accel_z.setText(f"{val_az:.1f} m/s²")
            self.accel_z_bar.setValue(int(abs(val_az)))
            
        if 'vel' in data:
            val_vel = data['vel']
            self.label_vel.setText(f"{val_vel:.1f} m/s")
            self.vel_bar.setValue(int(val_vel))
            
        if 'yaw' in data:
            val_yaw = int(data['yaw'])
            val_yaw = val_yaw % 360
            self.compass.updateValue(val_yaw)
