#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AÑO: 2025 CREADOR: Christian Yael Ramírez León

# core/serial_worker.py

# core/serial_worker.py

import csv
import sys
import time
from datetime import datetime
from PySide6.QtCore import (
    QObject, Signal, Slot, QIODevice, QFileSystemWatcher, QThread
)
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo

class SerialWorker(QObject):
    """
    Módulo de lógica que maneja la conexión serial, monitoreo y parseo.
    CON TIEMPOS PERSONALIZADOS.
    """
    
    # --- Señales ---
    port_list_updated = Signal(list)
    status_update = Signal(str, str)
    
    cinematica_updated = Signal(dict)
    visor_3d_updated = Signal(float, float, float)
    gps_data_updated = Signal(dict)
    altimetro_data_updated = Signal(int)
    graficas_data_updated = Signal(dict)
    calidad_aire_updated = Signal(dict)
    baterias_data_updated = Signal(int, int)
    paquetes_data_updated = Signal(int, int)
    estados_data_updated = Signal(dict)

    CSV_HEADER = [
        'Contador_Paquetes_GS', 
        'Acc_x', 'Acc_y', 'Acc_z', 'Pitch', 'Roll', 'Yaw', 'Compass', 
        'Latitud', 'Longitud', 'Altitud_GPS', 'Hora_GPS', 
        'Bateria_Control', 'Bateria_Camara', 'Tiempo_encendido', 'Tiempo_Mision', 
        'No_Paquete_Enviado', 'Temperatura', 'Presion', 'Altitud_Barometro', 
        'TVOC', 'CO2', 'Humedad', 
        'Estado_Launc', 'Estado_Payload_1', 'Estado_Payload_2', 'Estado_Payload_3', 
        'Estado_Camara', 'Estado_SD', 'Etapa_mision', 'Codigo_Error', 
        'Ultimo_comando', 
        'Velocidad_Calculada_Z'
    ]

    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.known_port_list = []
        self.port_monitor = None
        self.serial_buffer = b"" 
        
        # Datos internos
        self.gs_packet_count = 0
        self.last_packet_id = 0
        self.lost_packets = 0
        self.vel_window = []
        self.velocidad_z = 0.0
        
        self.MAX_GRAPH_POINTS = 100
        self.graph_time = []
        self.graph_pressure = []
        self.graph_temp = []
        self.graph_co2 = []
        self.graph_tvoc = []
        self.graph_humidity = []
        
        self.csv_file = None
        self.csv_writer = None
        
        # --- VARIABLES DE TIEMPO (THROTTLING) ---
        self.last_update_30hz = 0 # 3D
        self.last_update_20hz = 0 # Cinemática, Paquetes
        self.last_update_05s = 0  # Gráficas
        self.last_update_5s = 0   # GPS, Textos lentos

    @Slot()
    def init_worker(self):
        self.serial_port = QSerialPort()
        self.serial_port.readyRead.connect(self.on_ready_read)
        self.serial_port.errorOccurred.connect(self.handle_serial_error)
        
        if sys.platform.startswith("linux"):
            print("Iniciando monitor de puertos (Modo Linux)")
            self.port_monitor = QFileSystemWatcher(self)
            self.port_monitor.directoryChanged.connect(self.check_available_ports)
            self.port_monitor.addPath("/dev")
        
        self.check_available_ports()

    @Slot()
    def check_available_ports(self):
        try:
            ports = QSerialPortInfo.availablePorts()
            port_names = [port.portName() for port in ports]
        except Exception as e:
            self.status_update.emit(f"Error listando puertos: {e}", "danger")
            port_names = []

        if port_names != self.known_port_list:
            self.known_port_list = port_names
            self.port_list_updated.emit(port_names)

    @Slot(str, int)
    def start_connection(self, port: str, baud: int):
        if self.serial_port.isOpen():
            return
        self.serial_port.setPortName(port)
        self.serial_port.setBaudRate(baud)
        
        if self.serial_port.open(QIODevice.OpenModeFlag.ReadWrite):
            self.serial_port.clear(QSerialPort.Direction.AllDirections)
            self.status_update.emit(f"Conectado a {port}", "success")
            self.reset_session_data()
            self.open_csv_file()
        else:
            self.status_update.emit(f"Error al abrir {port}: {self.serial_port.errorString()}", "danger")

    @Slot()
    def stop_connection(self):
        if self.serial_port and self.serial_port.isOpen():
            self.serial_port.close()
            self.status_update.emit("Desconectado.", "info")
        self.close_csv_file()

    @Slot(str)
    def send_command_sequence(self, command_str: str):
        if not self.serial_port or not self.serial_port.isOpen():
            self.status_update.emit("Error: No conectado.", "danger")
            return
        
        self.status_update.emit(f"Enviando: {command_str.strip()}", "info")
        cmd_bytes = command_str.encode('utf-8')
        try:
            self.serial_port.write(cmd_bytes)
        except Exception as e:
            self.status_update.emit(f"Error enviando: {e}", "danger")

    @Slot(QSerialPort.SerialPortError)
    def handle_serial_error(self, error):
        if error == QSerialPort.SerialPortError.ResourceError:
            self.status_update.emit("Desconexión inesperada.", "danger")
            self.stop_connection()

    @Slot()
    def stop_monitoring(self):
        if self.port_monitor and sys.platform.startswith("linux"):
            self.port_monitor.removePath("/dev")

    @Slot()
    def on_ready_read(self):
        self.serial_buffer += self.serial_port.readAll().data()
        while b'\n' in self.serial_buffer:
            packet_bytes, self.serial_buffer = self.serial_buffer.split(b'\n', 1)
            try:
                packet_string = packet_bytes.decode('utf-8').strip()
                if packet_string:
                    self.process_packet(packet_string)
                    print(f"[SERIAL]: {packet_string}")
            except UnicodeDecodeError:
                self.status_update.emit("Error decode UTF-8", "danger")

    def process_packet(self, packet_string: str):
        parts = packet_string.split(',')
        if len(parts) != 31:
            return

        try:
            self.gs_packet_count += 1
            now = time.time()
            
            # --- 1. Extracción ---
            data = {
                'ax': float(parts[0]), 'ay': float(parts[1]), 'az': float(parts[2]),
                'pitch': float(parts[3]), 'roll': float(parts[4]), 'yaw': float(parts[5]),
                'compass': float(parts[6]),
                'lat': float(parts[7]), 'lon': float(parts[8]), 'alt_gps': float(parts[9]),
                'hora_gps': parts[10],
                'bat_control': int(round(float(parts[11]))), 'bat_camara': int(round(float(parts[12]))),
                't_encendido': float(parts[13]), 't_mision': float(parts[14]),
                'no_paquete_enviado': int(round(float(parts[15]))),
                'temp': float(parts[16]), 'pres': float(parts[17]), 'alt_baro': float(parts[18]),
                'tvoc': float(parts[19]), 'co2': float(parts[20]), 'hum': float(parts[21]),
                'led_lanz': bool(int(round(float(parts[22])))), 'led_p1': bool(int(round(float(parts[23])))),
                'led_p2': bool(int(round(float(parts[24])))), 'led_p3': bool(int(round(float(parts[25])))),
                'led_cam': bool(int(round(float(parts[26])))), 'led_sd': bool(int(round(float(parts[27])))),
                'etapa_id': int(round(float(parts[28]))),
                'error': int(round(float(parts[29]))), 'comando': int(round(float(parts[30])))
            }

            # --- 2. Cálculos ---
            self.vel_window.append((data['t_mision'], data['alt_baro']))
            if len(self.vel_window) > 20: self.vel_window.pop(0)
            if len(self.vel_window) > 1:
                dt = self.vel_window[-1][0] - self.vel_window[0][0]
                dh = self.vel_window[-1][1] - self.vel_window[0][1]
                if dt > 0: self.velocidad_z = dh / dt

            # --- 3. Buffers y CSV ---
            self.graph_time.append(data['t_mision'])
            self.graph_pressure.append(data['pres'])
            self.graph_temp.append(data['temp'])
            self.graph_co2.append(data['co2'])
            self.graph_tvoc.append(data['tvoc'])
            self.graph_humidity.append(data['hum'])
            if len(self.graph_time) > self.MAX_GRAPH_POINTS:
                self.graph_time.pop(0); self.graph_pressure.pop(0); self.graph_temp.pop(0)
                self.graph_co2.pop(0); self.graph_tvoc.pop(0); self.graph_humidity.pop(0)

            if data['no_paquete_enviado'] > (self.last_packet_id + 1):
                self.lost_packets += (data['no_paquete_enviado'] - self.last_packet_id - 1)
            self.last_packet_id = data['no_paquete_enviado']

            if self.csv_writer:
                row = [self.gs_packet_count] + parts + [f"{self.velocidad_z:.3f}"]
                self.csv_writer.writerow(row)

            # --- 5. EMISIÓN CONTROLADA ---
            
            # A. Simulación 3D (30 Hz -> 0.033s)
            if (now - self.last_update_30hz) > 0.033:
                self.visor_3d_updated.emit(data['pitch'], data['roll'], data['yaw'])
                self.last_update_30hz = now

            # B. UI Rápida (20 Hz -> 0.05s)
            # Incluye: Brújula, Barras Acel/Vel, Gráfica de Pastel y Altimetro (para suavidad)
            if (now - self.last_update_20hz) > 0.05:
                self.cinematica_updated.emit({
                    'ax': data['ax'], 'ay': data['ay'], 'az': data['az'],
                    'vel': self.velocidad_z, 'yaw': data['compass']
                })
                self.paquetes_data_updated.emit(data['no_paquete_enviado'], self.lost_packets)
                self.altimetro_data_updated.emit(int(data['alt_baro']))
                self.last_update_20hz = now

            # C. Gráficas de Líneas (0.5s -> 2 Hz)
            if (now - self.last_update_05s) > 0.5:
                self.graficas_data_updated.emit({
                    'time': self.graph_time, 'temp': self.graph_temp, 'pres': self.graph_pressure
                })
                self.calidad_aire_updated.emit({
                    'time': self.graph_time, 'co2': self.graph_co2, 'tvoc': self.graph_tvoc, 'hum': self.graph_humidity
                })
                self.last_update_05s = now

            # D. UI Lenta / Textos / Mapa (5.0s -> 0.2 Hz)
            if (now - self.last_update_5s) > 5.0:
                # GPS (Mapa y Texto)
                self.gps_data_updated.emit({
                    'location': [data['lat'], data['lon']],
                    'start_time': data['hora_gps'],
                    'flight_time': data['t_mision']
                })
                # Baterías
                self.baterias_data_updated.emit(data['bat_control'], data['bat_camara'])
                
                # Estados y Etapa
                etapas = {0: "NO INICIADA", 1: "IGNICION", 2: "APOGEO", 3: "CAIDA LIBRE", 4: "ATERRIZAJE"}
                etapa_str = etapas.get(data['etapa_id'], "DESCONOCIDO")
                self.estados_data_updated.emit({
                    'etapa': etapa_str,
                    'lanzamiento': data['led_lanz'], 'carga1': data['led_p1'], 
                    'carga2': data['led_p2'], 'carga3': data['led_p3'], 
                    'camara': data['led_cam'], 'sd': data['led_sd']
                })
                
                self.last_update_5s = now

            # Eventos inmediatos (Sin retraso)
            if data['error'].strip() and data['error'] != "0":
                 self.status_update.emit(f"ERROR COD: {data['error']}", "danger")
            if data['comando'].strip():
                 self.status_update.emit(f"CMD CONFIRMADO: {data['comando']}", "info")

        except Exception as e:
            self.status_update.emit(f"Error procesando: {e}", "danger")

    def reset_session_data(self):
        self.last_packet_id = 0
        self.lost_packets = 0
        self.gs_packet_count = 0
        self.vel_window.clear()
        self.velocidad_z = 0.0
        self.graph_time.clear()
        self.graph_pressure.clear()
        self.graph_temp.clear()
        self.graph_co2.clear()
        self.graph_tvoc.clear()
        self.graph_humidity.clear()
        
        now = time.time()
        self.last_update_30hz = now
        self.last_update_20hz = now
        self.last_update_05s = now
        self.last_update_5s = now

    def open_csv_file(self):
        self.close_csv_file()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"log_vuelo_{timestamp}.csv"
        try:
            self.csv_file = open(filename, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(self.CSV_HEADER)
            self.status_update.emit(f"Grabando en: {filename}", "success")
        except Exception as e:
            self.status_update.emit(f"Error creando CSV: {e}", "danger")

    def close_csv_file(self):
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None
