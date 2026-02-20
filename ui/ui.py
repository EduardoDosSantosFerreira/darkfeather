from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFrame, QDialog, QMessageBox,
                               QScrollArea, QSizePolicy, QApplication)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal, QPoint
from PySide6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QPen, QBrush, QIcon
from system import get_all_wifi_profiles

class NetworkCard(QFrame):
    """Card individual para cada rede WiFi"""
    
    clicked = Signal(object)  # Sinal emitido quando o card é clicado
    
    def __init__(self, network_data, is_selected=False):
        super().__init__()
        self.network_data = network_data
        self.is_selected = is_selected
        self.setup_ui()
        self.update_style()
        
    def setup_ui(self):
        # Configurações do card
        self.setFixedHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Layout principal horizontal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(15)
        
        # ===== Ícone WiFi =====
        self.wifi_icon = QLabel()
        self.wifi_icon.setFixedSize(32, 32)
        self.wifi_icon.setPixmap(self.create_wifi_icon())
        layout.addWidget(self.wifi_icon)
        
        # ===== Informações da rede =====
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # Nome da rede
        self.name_label = QLabel(self.network_data.get("SSID", "Rede Desconhecida"))
        name_font = QFont("Segoe UI", 12)
        name_font.setWeight(QFont.Weight.DemiBold)
        self.name_label.setFont(name_font)
        self.name_label.setStyleSheet("color: #1e293b;")
        info_layout.addWidget(self.name_label)
        
        # Tipo de segurança e qualidade
        auth = self.network_data.get("Autenticação", "Desconhecido")
        quality = self.network_data.get("Qualidade", "Desconhecido")
        
        self.details_label = QLabel(f"{auth} — {quality}")
        details_font = QFont("Segoe UI", 10)
        self.details_label.setFont(details_font)
        self.details_label.setStyleSheet("color: #64748b;")
        info_layout.addWidget(self.details_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # ===== Ícone de olho =====
        self.eye_icon = QLabel()
        self.eye_icon.setFixedSize(24, 24)
        self.eye_icon.setPixmap(self.create_eye_icon())
        self.eye_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.eye_icon)
        
    def create_wifi_icon(self):
        """Cria um ícone WiFi estilizado"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Desenhar ícone WiFi simplificado
        pen = QPen(QColor("#94a3b8"), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        center = QPoint(16, 20)
        
        # Arcos do WiFi
        painter.drawArc(center.x() - 12, center.y() - 12, 24, 24, 30 * 16, 120 * 16)
        painter.drawArc(center.x() - 8, center.y() - 8, 16, 16, 30 * 16, 120 * 16)
        
        # Ponto central
        painter.setBrush(QBrush(QColor("#94a3b8")))
        painter.drawEllipse(QPoint(16, 22), 2, 2)
        
        painter.end()
        return pixmap
    
    def create_eye_icon(self):
        """Cria um ícone de olho"""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(QColor("#64748b"), 1.5)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Desenhar ícone de olho simplificado
        painter.drawEllipse(6, 6, 12, 8)
        painter.drawEllipse(9, 8, 6, 4)
        
        painter.end()
        return pixmap
    
    def update_style(self):
        """Atualiza o estilo baseado no estado selecionado"""
        if self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #e8f0fe;
                    border: 2px solid #2563eb;
                    border-radius: 12px;
                }
                QFrame:hover {
                    background-color: #dbeafe;
                }
            """)
            self.name_label.setStyleSheet("color: #1e293b; font-weight: 600;")
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                }
                QFrame:hover {
                    background-color: #f8fafc;
                    border-color: #cbd5e1;
                }
            """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.network_data)
        super().mousePressEvent(event)


class DetailsCard(QFrame):
    """Card de detalhes da rede selecionada"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # Título da seção
        title_label = QLabel("Detalhes da Rede")
        title_font = QFont("Segoe UI", 12)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1e293b;")
        layout.addWidget(title_label)
        
        # Grid de detalhes (2 colunas)
        grid_widget = QWidget()
        grid_layout = QVBoxLayout(grid_widget)
        grid_layout.setSpacing(12)
        
        # Lista de campos
        self.fields = {
            "SSID": "",
            "Autenticação": "",
            "Criptografia": "",
            "Última conexão": "",
            "Chave de segurança": ""
        }
        
        self.field_labels = {}
        
        for field_name in self.fields.keys():
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            
            # Label do campo
            label = QLabel(field_name)
            label_font = QFont("Segoe UI", 10)
            label.setFont(label_font)
            label.setStyleSheet("color: #64748b;")
            label.setFixedWidth(120)
            row.addWidget(label)
            
            # Valor do campo
            value_label = QLabel("-")
            value_font = QFont("Segoe UI", 10)
            value_label.setFont(value_font)
            value_label.setStyleSheet("color: #0f172a; font-weight: 500;")
            value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            row.addWidget(value_label)
            row.addStretch()
            
            self.field_labels[field_name] = value_label
            grid_layout.addLayout(row)
        
        layout.addWidget(grid_widget)
        
        # Linha de chave HEX em destaque
        hex_row = QHBoxLayout()
        hex_label = QLabel("Chave (HEX)")
        hex_label.setFont(QFont("Segoe UI", 9))
        hex_label.setStyleSheet("color: #64748b;")
        hex_row.addWidget(hex_label)
        
        self.hex_value = QLabel("")
        self.hex_value.setFont(QFont("Segoe UI", 9))
        self.hex_value.setStyleSheet("color: #2563eb; font-family: monospace;")
        hex_row.addWidget(self.hex_value)
        hex_row.addStretch()
        
        layout.addLayout(hex_row)
    
    def update_details(self, network_data):
        """Atualiza os detalhes com os dados da rede"""
        if not network_data:
            return
            
        self.field_labels["SSID"].setText(network_data.get("SSID", "-"))
        self.field_labels["Autenticação"].setText(network_data.get("Autenticação", "-"))
        self.field_labels["Criptografia"].setText(network_data.get("Criptografia", "-"))
        self.field_labels["Última conexão"].setText(network_data.get("Última Conexão", "-"))
        
        # Chave de segurança (ASCII)
        key_ascii = network_data.get("Chave (ASCII)", "********")
        self.field_labels["Chave de segurança"].setText(key_ascii)
        
        # Chave HEX
        key_hex = network_data.get("Chave (HEX)", "")
        if key_hex:
            self.hex_value.setText(key_hex)
            self.hex_value.setVisible(True)
        else:
            self.hex_value.setVisible(False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.profiles = []
        self.selected_network = None
        self.network_cards = []
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("DarkFeather - WiFi Analysis")
        self.setFixedSize(800, 700)
        
        # Widget central com fundo cinza claro
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #f3f4f6;")
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(24)
        
        # ========== HEADER ==========
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("DarkFeather - WiFi Analysis")
        title_font = QFont("Segoe UI", 20)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #334155; font-weight: 400;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botão Scan
        self.btn_scan = QPushButton("🔄 Atualizar")
        self.btn_scan.setFixedSize(120, 36)
        self.btn_scan.setFont(QFont("Segoe UI", 10))
        self.btn_scan.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f8fafc;
                border-color: #cbd5e1;
            }
            QPushButton:pressed {
                background-color: #f1f5f9;
            }
        """)
        self.btn_scan.clicked.connect(self.scan_networks)
        header_layout.addWidget(self.btn_scan)
        
        main_layout.addLayout(header_layout)
        
        # ========== LISTA DE CARDS ==========
        # Área de scroll para os cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        
        self.cards_layout = QVBoxLayout(scroll_content)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # ========== CARD DE DETALHES ==========
        self.details_card = DetailsCard()
        main_layout.addWidget(self.details_card)
        
        # ========== RODAPÉ ==========
        footer_label = QLabel("Clique em qualquer card para ver detalhes • Double-click no ícone de olho para copiar")
        footer_label.setFont(QFont("Segoe UI", 9))
        footer_label.setStyleSheet("color: #94a3b8; padding: 8px 0;")
        main_layout.addWidget(footer_label)
        
        # Aplicar tema claro
        self.apply_light_theme()
        
        # Escanear automaticamente ao iniciar
        QTimer.singleShot(100, self.scan_networks)
    
    def apply_light_theme(self):
        """Aplica o tema claro à aplicação"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(243, 244, 246))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(51, 65, 85))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(249, 250, 251))
        palette.setColor(QPalette.ColorRole.Text, QColor(15, 23, 42))
        palette.setColor(QPalette.ColorRole.Button, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(51, 65, 85))
        self.setPalette(palette)
    
    def scan_networks(self):
        """Escaneia todas as redes WiFi salvas"""
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("🔄 Escaneando...")
        
        # Limpar cards existentes
        self.clear_cards()
        
        # Buscar perfis
        self.profiles = get_all_wifi_profiles()
        
        # Se não encontrou perfis, criar dados de exemplo
        if not self.profiles:
            self.profiles = self.get_sample_data()
        
        # Criar cards para cada rede
        for i, profile in enumerate(self.profiles):
            card = NetworkCard(profile, is_selected=(i == 0))
            card.clicked.connect(self.on_network_selected)
            self.cards_layout.addWidget(card)
            self.network_cards.append(card)
        
        # Selecionar primeira rede por padrão
        if self.profiles:
            self.on_network_selected(self.profiles[0])
        
        self.cards_layout.addStretch()
        
        # Restaurar botão
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("🔄 Atualizar")
    
    def get_sample_data(self):
        """Retorna dados de exemplo para demonstração"""
        return [
            {
                "SSID": "HomeNetwork_5G",
                "Autenticação": "WPA2-Personal",
                "Qualidade": "Excelente",
                "Criptografia": "AES-GCMP",
                "Chave (ASCII)": "********",
                "Chave (HEX)": "[Hex 7465737465313233]",
                "Última Conexão": "2023-11-15 14:30"
            },
            {
                "SSID": "OfficeWiFi",
                "Autenticação": "WPA2-Enterprise",
                "Qualidade": "Bom",
                "Criptografia": "AES-CCMP",
                "Chave (ASCII)": "********",
                "Chave (HEX)": "",
                "Última Conexão": "2023-11-14 09:15"
            },
            {
                "SSID": "CafePublic",
                "Autenticação": "Open",
                "Qualidade": "Fraco",
                "Criptografia": "Nenhuma",
                "Chave (ASCII)": "",
                "Chave (HEX)": "",
                "Última Conexão": "2023-11-10 16:45"
            }
        ]
    
    def clear_cards(self):
        """Remove todos os cards da lista"""
        for card in self.network_cards:
            card.deleteLater()
        self.network_cards.clear()
        
        # Limpar layout
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def on_network_selected(self, network_data):
        """Quando uma rede é selecionada"""
        self.selected_network = network_data
        
        # Atualizar seleção dos cards
        for card in self.network_cards:
            card.is_selected = (card.network_data.get("SSID") == network_data.get("SSID"))
            card.update_style()
        
        # Atualizar card de detalhes
        self.details_card.update_details(network_data)