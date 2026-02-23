"""
Janela do cliente de rede - VERSÃO ULTRA SIMPLES
Arquivo: network_ui/client_window.py
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QLineEdit, QGroupBox,
    QMessageBox
)
from PySide6.QtCore import Qt, QTimer
import qtawesome as qta
import socket
import threading
import time


class ClientWindow(QDialog):
    """Janela do cliente - VERSÃO SIMPLÍSSIMA"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.socket = None
        self.connected = False
        self.running = False
        self.setWindowFlags(Qt.Window)
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("DarkFeather - Cliente de Chat")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # ========== CONEXÃO ==========
        conn_group = QGroupBox("Conexão")
        conn_layout = QHBoxLayout(conn_group)
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Servidor")
        self.host_input.setText("127.0.0.1")
        self.host_input.setFixedWidth(100)
        conn_layout.addWidget(self.host_input)
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Porta")
        self.port_input.setText("8888")
        self.port_input.setFixedWidth(60)
        conn_layout.addWidget(self.port_input)
        
        self.btn_connect = QPushButton(" Conectar")
        self.btn_connect.setIcon(qta.icon('fa5s.plug', color='white'))
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #047857; }
        """)
        self.btn_connect.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.btn_connect)
        
        self.status_label = QLabel("⏸ Desconectado")
        self.status_label.setStyleSheet("color: #64748b;")
        conn_layout.addWidget(self.status_label)
        
        conn_layout.addStretch()
        layout.addWidget(conn_group)
        
        # ========== CHAT ==========
        chat_group = QGroupBox("Chat")
        chat_layout = QVBoxLayout(chat_group)
        
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
            }
        """)
        chat_layout.addWidget(self.chat_area)
        
        # Input
        input_layout = QHBoxLayout()
        
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Digite sua mensagem...")
        self.msg_input.returnPressed.connect(self.send_message)
        self.msg_input.setEnabled(False)
        input_layout.addWidget(self.msg_input)
        
        self.btn_send = QPushButton(" Enviar")
        self.btn_send.setIcon(qta.icon('fa5s.paper-plane', color='white'))
        self.btn_send.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton:disabled { background-color: #94a3b8; }
        """)
        self.btn_send.clicked.connect(self.send_message)
        self.btn_send.setEnabled(False)
        input_layout.addWidget(self.btn_send)
        
        chat_layout.addLayout(input_layout)
        layout.addWidget(chat_group)
        
        self.add_message("Bem-vindo ao DarkFeather Chat", "SISTEMA")
    
    def toggle_connection(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        host = self.host_input.text().strip()
        try:
            port = int(self.port_input.text().strip())
        except:
            QMessageBox.warning(self, "Erro", "Porta inválida")
            return
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(3)
            self.socket.connect((host, port))
            self.socket.setblocking(False)
            
            self.connected = True
            self.running = True
            
            # Atualizar UI
            self.btn_connect.setText(" Desconectar")
            self.btn_connect.setIcon(qta.icon('fa5s.power-off', color='white'))
            self.btn_connect.setStyleSheet("""
                QPushButton {
                    background-color: #dc2626;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #b91c1c; }
            """)
            self.msg_input.setEnabled(True)
            self.btn_send.setEnabled(True)
            self.host_input.setEnabled(False)
            self.port_input.setEnabled(False)
            self.status_label.setText("✅ Conectado")
            self.status_label.setStyleSheet("color: #059669;")
            
            self.add_message(f"Conectado ao servidor {host}:{port}", "SISTEMA")
            
            # Iniciar thread de recebimento
            thread = threading.Thread(target=self.receive_loop, daemon=True)
            thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível conectar: {str(e)}")
            self.socket = None
    
    def receive_loop(self):
        """Loop de recebimento - versão super simples"""
        buffer = ""
        
        while self.running and self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8', errors='ignore')
                if not data:
                    break
                
                buffer += data
                
                # Processa linhas completas
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        # Formato esperado: "NOME: mensagem"
                        if ':' in line:
                            nome, msg = line.split(':', 1)
                            self.add_message(msg.strip(), nome.strip())
                        else:
                            self.add_message(line.strip(), "Servidor")
                            
            except BlockingIOError:
                time.sleep(0.1)
            except:
                break
        
        self.disconnect()
    
    def send_message(self):
        msg = self.msg_input.text().strip()
        if not msg or not self.connected:
            return
        
        try:
            # Formato: "NOME: mensagem\n"
            self.socket.send(f"Você: {msg}\n".encode('utf-8'))
            self.add_message(msg, "Você")
            self.msg_input.clear()
        except:
            self.disconnect()
            QMessageBox.warning(self, "Erro", "Falha ao enviar mensagem")
    
    def add_message(self, text, sender):
        from datetime import datetime
        hora = datetime.now().strftime("%H:%M")
        
        if sender == "SISTEMA":
            self.chat_area.append(f'<div style="color: #64748b; text-align: center; margin: 5px;">⚙️ {text}</div>')
        elif sender == "Você":
            self.chat_area.append(f'<div style="text-align: right; margin: 5px;">'
                                 f'<span style="background-color: #2563eb; color: white; padding: 6px 10px; border-radius: 10px; display: inline-block;">'
                                 f'<b>Você</b> {hora}<br>{text}</span></div>')
        else:
            self.chat_area.append(f'<div style="text-align: left; margin: 5px;">'
                                 f'<span style="background-color: #f1f5f9; color: #0f172a; padding: 6px 10px; border-radius: 10px; display: inline-block;">'
                                 f'<b>{sender}</b> {hora}<br>{text}</span></div>')
        
        # Rolar para o final
        scroll = self.chat_area.verticalScrollBar()
        scroll.setValue(scroll.maximum())
    
    def disconnect(self):
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # Atualizar UI
        self.btn_connect.setText(" Conectar")
        self.btn_connect.setIcon(qta.icon('fa5s.plug', color='white'))
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #047857; }
        """)
        self.msg_input.setEnabled(False)
        self.btn_send.setEnabled(False)
        self.host_input.setEnabled(True)
        self.port_input.setEnabled(True)
        self.status_label.setText("⏸ Desconectado")
        self.status_label.setStyleSheet("color: #64748b;")
        
        self.add_message("Desconectado do servidor", "SISTEMA")
    
    def closeEvent(self, event):
        self.disconnect()
        event.accept()