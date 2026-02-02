#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2025 CREADOR: Christian Yael Ramírez León

# ui/widgets/panel_visor_3d.py

from pathlib import Path
from PySide6.QtCore import QUrl, Slot
from PySide6.QtGui import QVector3D, QColor, QQuaternion
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtWidgets import QWidget, QVBoxLayout

# Importamos la paleta para usar el color de fondo
from ui.theme import PALETTE 

# --- 1. La Ventana 3D (QWindow) ---
# Esta es tu clase original, renombrada para mayor claridad

class Visor3D(Qt3DExtras.Qt3DWindow):
    def __init__(self):
        super().__init__()
        
        # Usamos el color de fondo de la paleta
        self.defaultFrameGraph().setClearColor(QColor(PALETTE['BACKGROUND']['MAIN']))

        self.root_entity = Qt3DCore.QEntity()
        self.camara = self.camera()
        self.camara.setPosition(QVector3D(10, 100, 140))
        self.camara.setViewCenter(QVector3D(10,100,0))
        self.camara.setUpVector(QVector3D(0, 1, 0))
        self.camara.setFieldOfView(100)
        self.camera_transform = Qt3DCore.QTransform()
        self.camera_entity = Qt3DCore.QEntity(self.root_entity)

        self.setup_lights()
        self.load_3d_model()
        self.setRootEntity(self.root_entity)

        # Controlador de cámara orbital
        cam_controller = Qt3DExtras.QOrbitCameraController(self.root_entity)
        cam_controller.setLinearSpeed(50)
        cam_controller.setLookSpeed(180)
        cam_controller.setCamera(self.camara)
    
    def setup_lights(self):
        # Configuración de la luz
        self.spotlight_entity = Qt3DCore.QEntity(self.root_entity)
        
        self.spotlight = Qt3DRender.QSpotLight(self.spotlight_entity)
        self.spotlight.setColor(QColor(255, 255, 255))
        self.spotlight.setIntensity(1.5)
        self.spotlight.setCutOffAngle(150)
        self.spotlight.setConstantAttenuation(1.0)
        self.spotlight.setLinearAttenuation(0.0)
        self.spotlight.setQuadraticAttenuation(0.0)
        
        self.spotlight_transform = Qt3DCore.QTransform()
        self.spotlight_entity.addComponent(self.spotlight_transform)
        self.spotlight_entity.addComponent(self.spotlight)
        self.spotlight_transform.setTranslation(QVector3D(0,0,200))

    def load_3d_model(self):
        # Asumimos que la carpeta 'models' está en el directorio raíz
        # (un nivel arriba de 'ui', que está un nivel arriba de 'widgets')
        model_root = Path(__file__).parent.parent.parent 
        
        materials = self.load_mtl_materials(model_root / "models" / "cohete.mtl")
        
        model_entity = Qt3DCore.QEntity(self.root_entity)
        
        mesh = Qt3DRender.QMesh(model_entity)
        model_path = model_root / "models" / "cohete.obj"
        
        if not model_path.exists():
            print(f"Error: No se encontró el modelo 3D en {model_path}")
            return

        mesh.setSource(QUrl.fromLocalFile(str(model_path)))
        
        # Aplicamos un material por defecto
        # (Tu lógica de 'material96' está aquí)
        material = Qt3DExtras.QPhongMaterial(model_entity)
        material.setDiffuse(QColor(47, 68, 124))
        material.setSpecular(QColor(30, 30, 30))
        material.setShininess(100)
        
        self.model_transform = Qt3DCore.QTransform()
        self.model_transform.setScale(0.1)

        model_entity.addComponent(mesh)
        model_entity.addComponent(material)
        model_entity.addComponent(self.model_transform)

    def load_mtl_materials(self, mtl_file: Path):
        # Lector de materiales simplificado
        materials = {}
        current_mtl = None
        
        if not mtl_file.exists():
            print(f"Advertencia: No se encontró el archivo MTL en {mtl_file}")
            return materials

        try:
            with open(mtl_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split()
                    if parts[0] == 'newmtl':
                        current_mtl = parts[1]
                        materials[current_mtl] = {}
                    # (Aquí iría el resto de tu lógica de parseo de 'Ka', 'Kd', 'Ks')
        except Exception as e:
            print(f"Error cargando MTL: {e}")
        return materials

    def set_rotation(self, pitch, yaw, roll):
        """Aplica la rotación al modelo 3D."""
        euler_rotation = QVector3D(roll, pitch, yaw)
        self.model_transform.setRotation(QQuaternion.fromEulerAngles(euler_rotation))

# --- 2. El "Envoltorio" (Wrapper) ---
# Este es el QWidget que sí puedes añadir a tu layout

class PanelVisor3D(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. Crear la ventana 3D
        self.visor_3d_window = Visor3D()
        
        # 2. Crear el contenedor QWidget que la "envuelve"
        widget_3d = QWidget.createWindowContainer(self.visor_3d_window, self)
        
        # 3. Poner el contenedor en un layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget_3d)

    @Slot(float, float, float)
    def update_rotation(self, pitch: float, yaw: float, roll: float):
        """
        Slot público para que la lógica externa
        pueda actualizar la rotación del modelo.
        """
        self.visor_3d_window.set_rotation(pitch, yaw, roll)
