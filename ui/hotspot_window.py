"""
Janela dedicada do Mobile Hotspot
Arquivo: ui/hotspot_window.py
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import qtawesome as qta

from ui.hotspot_widget import HotspotWidget


class HotspotWindow(QDialog):
    """
    Janela dedicada para controle do Mobile Hotspot
    """
    
    closed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface da janela"""
        self.setWindowTitle("DarkFeather - Mobile Hotspot")
        self.setMinimumSize(500, 600)
        self.setModal(False)
        
        # Estilo da janela
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
        """)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        title = QLabel("Controle do Mobile Hotspot")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Medium)
        title.setFont(title_font)
        title.setStyleSheet("color: #0f172a;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botão de ajuda
        btn_help = QPushButton()
        btn_help.setIcon(qta.icon('fa5s.question-circle', color='#64748b'))
        btn_help.setFixedSize(32, 32)
        btn_help.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
        """)
        btn_help.clicked.connect(self.show_help)
        header_layout.addWidget(btn_help)
        
        layout.addLayout(header_layout)
        
        # Descrição
        desc_label = QLabel(
            "Compartilhe a conexão de internet do seu computador "
            "com outros dispositivos via Wi-Fi."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #475569; font-size: 13px; padding: 4px 0;")
        layout.addWidget(desc_label)
        
        # Widget principal do hotspot
        self.hotspot_widget = HotspotWidget()
        layout.addWidget(self.hotspot_widget)
        
        # Barra inferior
        footer_layout = QHBoxLayout()
        
        # Status
        self.status_label = QLabel("Pronto")
        self.status_label.setStyleSheet("color: #64748b; font-size: 11px;")
        footer_layout.addWidget(self.status_label)
        
        footer_layout.addStretch()
        
        # Botão fechar
        btn_close = QPushButton(" Fechar")
        btn_close.setIcon(qta.icon('fa5s.times', color='#334155'))
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                color: #334155;
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        btn_close.clicked.connect(self.close)
        footer_layout.addWidget(btn_close)
        
        layout.addLayout(footer_layout)
        
        # Conectar sinais
        self.hotspot_widget.status_changed.connect(self.on_status_changed)
    
    def on_status_changed(self, status: str):
        """Atualiza o status na barra inferior"""
        self.status_label.setText(f"Status: {status}")
    
    def show_help(self):
        """Mostra ajuda sobre o hotspot"""
        from PySide6.QtWidgets import QMessageBox
        
        help_text = (
            "<b>Mobile Hotspot no Windows</b><br><br>"
            "Este recurso permite compartilhar sua conexão de internet "
            "com outros dispositivos via Wi-Fi.<br><br>"
            "<b>Requisitos:</b><br>"
            "• Windows 10 ou 11<br>"
            "• Adaptador Wi-Fi compatível<br>"
            "• Driver atualizado<br><br>"
            "<b>Se o controle direto não funcionar:</b><br>"
            "1. Clique em 'Abrir Configurações do Windows'<br>"
            "2. Configure manualmente nas Configurações<br>"
            "3. Verifique se o serviço 'ICS' está ativo"
        )
        
        QMessageBox.information(self, "Ajuda - Mobile Hotspot", help_text)
    
    def closeEvent(self, event):
        """Evento de fechamento da janela"""
        self.closed.emit()
        event.accept()