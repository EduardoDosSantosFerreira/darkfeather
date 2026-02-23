"""
Janela do servidor de rede - VERSÃO ULTRA SIMPLES
Arquivo: network_ui/server_window.py
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QLineEdit, QListWidget,
    QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
import qtawesome as qta
import socket
import threading
import time


class ServerWindow(QDialog):
    """Janela do servidor - VERSÃO SIMPLÍSSIMA"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.server_socket = None
        self.clients = []  # Lista de (socket, endereço, nome)
        self.running = False
        self.setWindowFlags(Qt.Window)
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("DarkFeather - Servidor de Chat")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # ========== CONTROLE ==========
        ctrl_group = QGroupBox("Controle")
        ctrl_layout = QHBoxLayout(ctrl_group)
        
        self.btn_start = QPushButton(" Iniciar Servidor")
        self.btn_start.setIcon(qta.icon('fa5s.play', color='white'))
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #047857; }
        """)
        self.btn_start.clicked.connect(self.start_server)
        ctrl_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton(" Parar Servidor")
        self.btn_stop.setIcon(qta.icon('fa5s.stop', color='white'))
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #b91c1c; }
        """)
        self.btn_stop.clicked.connect(self.stop_server)
        self.btn_stop.setEnabled(False)
        ctrl_layout.addWidget(self.btn_stop)
        
        self.status_label = QLabel("⏸ Servidor parado")
        self.status_label.setStyleSheet("color: #64748b; margin-left: 10px;")
        ctrl_layout.addWidget(self.status_label)
        
        ctrl_layout.addStretch()
        layout.addWidget(ctrl_group)
        
        # ========== CLIENTES ==========
        clients_group = QGroupBox("Clientes Conectados")
        clients_layout = QVBoxLayout(clients_group)
        
        self.clients_list = QListWidget()
        clients_layout.addWidget(self.clients_list)
        layout.addWidget(clients_group)
        
        # ========== LOG ==========
        log_group = QGroupBox("Log do Servidor")
        log_layout = QVBoxLayout(log_group)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("font-family: monospace; font-size: 11px;")
        log_layout.addWidget(self.log_area)
        layout.addWidget(log_group)
        
        # Timer para atualizar UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clients_list)
        self.timer.start(1000)
        
        self.log("Servidor pronto para iniciar")
    
    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', 8888))
            self.server_socket.listen(5)
            self.server_socket.setblocking(False)
            
            self.running = True
            
            # Atualizar UI
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.status_label.setText("✅ Servidor rodando na porta 8888")
            self.status_label.setStyleSheet("color: #059669; margin-left: 10px;")
            
            self.log("🚀 Servidor iniciado em 0.0.0.0:8888")
            
            # Thread de aceitação
            thread = threading.Thread(target=self.accept_loop, daemon=True)
            thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao iniciar servidor: {str(e)}")
    
    def accept_loop(self):
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_socket.setblocking(False)
                
                # Adicionar cliente
                client_info = {
                    'socket': client_socket,
                    'address': address,
                    'name': f"Cliente_{len(self.clients)+1}",
                    'buffer': ''
                }
                self.clients.append(client_info)
                
                self.log(f"✅ Cliente conectado de {address[0]}:{address[1]}")
                
                # Thread para este cliente
                thread = threading.Thread(target=self.client_loop, args=(client_info,), daemon=True)
                thread.start()
                
            except BlockingIOError:
                time.sleep(0.1)
            except:
                break
    
    def client_loop(self, client):
        buffer = ''
        
        while self.running and client in self.clients:
            try:
                data = client['socket'].recv(1024).decode('utf-8', errors='ignore')
                if not data:
                    break
                
                buffer += data
                
                # Processar linhas completas
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self.process_message(client, line.strip())
                        
            except BlockingIOError:
                time.sleep(0.1)
            except:
                break
        
        self.remove_client(client)
    
    def process_message(self, client, message):
        """Processa mensagem de um cliente"""
        # Formato esperado: "NOME: mensagem"
        if ':' in message:
            nome, msg = message.split(':', 1)
            client['name'] = nome.strip()
            msg = msg.strip()
        else:
            msg = message
        
        # Log
        self.log(f"[{client['name']}] {msg}")
        
        # Broadcast para todos os clientes
        self.broadcast(f"{client['name']}: {msg}\n", exclude=client)
    
    def broadcast(self, message, exclude=None):
        """Envia mensagem para todos os clientes"""
        for client in self.clients[:]:  # Cópia da lista
            if client == exclude:
                continue
            try:
                client['socket'].send(message.encode('utf-8'))
            except:
                self.remove_client(client)
    
    def remove_client(self, client):
        if client in self.clients:
            self.clients.remove(client)
            try:
                client['socket'].close()
            except:
                pass
            self.log(f"❌ Cliente {client['name']} desconectado")
    
    def stop_server(self):
        self.running = False
        
        # Fechar todos os clientes
        for client in self.clients[:]:
            try:
                client['socket'].close()
            except:
                pass
        self.clients.clear()
        
        # Fechar socket do servidor
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        # Atualizar UI
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.status_label.setText("⏸ Servidor parado")
        self.status_label.setStyleSheet("color: #64748b; margin-left: 10px;")
        self.clients_list.clear()
        self.log("🛑 Servidor parado")
    
    def update_clients_list(self):
        """Atualiza lista de clientes na UI"""
        self.clients_list.clear()
        for client in self.clients:
            self.clients_list.addItem(f"{client['name']} - {client['address'][0]}:{client['address'][1]}")
    
    def log(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")
    
    def closeEvent(self, event):
        self.stop_server()
        event.accept()