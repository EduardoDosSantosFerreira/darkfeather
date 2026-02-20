"""
MainWindow principal da aplicação DarkFeather WiFi Analysis
COM SCANNER REAL - SEM DADOS MOCKADOS
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QApplication,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Slot
from PySide6.QtGui import QFont
import qtawesome as qta

from ui.widgets import WifiCardWidget, NetworkDetailsWidget, LoadingSpinner
from ui.theme import UIThemeManager
from core.scanner import WifiScanner, WifiNetwork
from utils.helpers import network_to_dict


class MainWindow(QMainWindow):
    """
    Janela principal da aplicação
    Usa SCANNER REAL - SEM DADOS MOCKADOS
    """
    
    def __init__(self):
        super().__init__()
        self.scanner = WifiScanner()
        self.theme = UIThemeManager()
        self.networks = []
        self.selected_network = None
        self.network_cards = []
        self.setup_ui()
        self.setup_animations()
        self.setup_connections()
        
        # Escanear automaticamente após inicialização
        QTimer.singleShot(100, self.start_scan)
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        self.setWindowTitle("DarkFeather WiFi Analysis")
        self.setMinimumSize(900, 700)
        
        # Aplicar tema
        self.setPalette(self.theme.get_palette())
        self.setStyleSheet(self.theme.get_main_window_style())
        
        # Widget central
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)
        
        self.setup_header()
        self.setup_networks_section()
        self.setup_details_section()
        self.setup_status_bar()
    
    def setup_header(self):
        """Configura o cabeçalho da aplicação"""
        header_widget = QWidget()
        header_widget.setObjectName("headerWidget")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 16)
        
        # Título e ícone
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(12)
        
        # Ícone WiFi
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.wifi', color='#2563eb').pixmap(32, 32))
        title_layout.addWidget(icon_label)
        
        # Título
        title_label = QLabel("DarkFeather WiFi Analysis")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setWeight(QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0f172a;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        
        # Container de ações
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(12)
        
        # Botão atualizar com loading spinner
        self.btn_refresh = QPushButton(" Atualizar")
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='#ffffff'))
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setFixedSize(120, 40)
        self.btn_refresh.setStyleSheet(self.theme.get_button_style("primary"))
        
        # Loading spinner
        self.spinner = LoadingSpinner()
        self.spinner.setVisible(False)
        self.spinner.setFixedSize(24, 24)
        
        actions_layout.addWidget(self.spinner)
        actions_layout.addWidget(self.btn_refresh)
        
        header_layout.addWidget(actions_container)
        self.main_layout.addWidget(header_widget)
    
    def setup_networks_section(self):
        """Configura a seção de listagem de redes"""
        section_label = QLabel("Redes Wi-Fi Salvas")
        section_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #334155;
            padding: 8px 0;
        """)
        self.main_layout.addWidget(section_label)
        
        # Área de scroll para cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("networksScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #f1f5f9;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        
        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_content.setStyleSheet("background-color: transparent;")
        
        self.networks_layout = QVBoxLayout(scroll_content)
        self.networks_layout.setContentsMargins(0, 0, 4, 0)
        self.networks_layout.setSpacing(12)
        
        self.scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(self.scroll_area, stretch=1)
    
    def setup_details_section(self):
        """Configura a seção de detalhes da rede"""
        self.details_widget = NetworkDetailsWidget()
        self.details_widget.setVisible(False)
        self.main_layout.addWidget(self.details_widget)
    
    def setup_status_bar(self):
        """Configura a barra de status"""
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #ffffff;
                color: #64748b;
                border-top: 1px solid #e2e8f0;
                padding: 4px 12px;
            }
        """)
        
        self.status_label = QLabel("Pronto")
        self.status_bar.addWidget(self.status_label)
    
    def setup_animations(self):
        """Configura animações da interface"""
        self.header_animation = QPropertyAnimation(self.btn_refresh, b"geometry")
        self.header_animation.setDuration(200)
        self.header_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def setup_connections(self):
        """Configura conexões de sinais e slots"""
        self.btn_refresh.clicked.connect(self.start_scan)
        
        # Conectar sinais do scanner REAL
        self.scanner.scan_finished.connect(self.on_scan_finished)
        self.scanner.scan_error.connect(self.on_scan_error)
        self.scanner.scan_progress.connect(self.on_scan_progress)
    
    @Slot()
    def start_scan(self):
        """Inicia scan REAL de redes Wi-Fi"""
        self.set_scanning_state(True)
        self.status_label.setText("Iniciando scan...")
        
        # Iniciar scan em thread separada
        self.scanner.scan_networks()
    
    @Slot(list)
    def on_scan_finished(self, networks):
        """Callback quando scan REAL termina"""
        self.networks = networks
        
        # Atualizar interface
        self.update_networks_display()
        
        # Mostrar resultado
        if networks:
            self.status_label.setText(f"Encontradas {len(networks)} redes Wi-Fi reais")
        else:
            self.status_label.setText("Nenhuma rede Wi-Fi encontrada no sistema")
        
        self.set_scanning_state(False)
    
    @Slot(str)
    def on_scan_error(self, error_msg):
        """Callback quando ocorre erro no scan"""
        self.status_label.setText(f"Erro: {error_msg}")
        self.show_error_state(error_msg)
        self.set_scanning_state(False)
    
    @Slot(str)
    def on_scan_progress(self, progress_msg):
        """Callback para progresso do scan"""
        self.status_label.setText(progress_msg)
    
    def update_networks_display(self):
        """Atualiza a exibição com dados REAIS"""
        # Limpar cards existentes
        self.clear_network_cards()
        
        if not self.networks:
            self.show_empty_state()
            self.details_widget.setVisible(False)
            return
        
        # Criar cards para cada rede REAL
        for i, network in enumerate(self.networks):
            card = WifiCardWidget(network, is_selected=(i == 0))
            card.clicked.connect(self.on_network_selected)
            card.copy_requested.connect(self.on_copy_password)
            card.eye_clicked.connect(self.on_eye_clicked_from_card)
            
            self.networks_layout.addWidget(card)
            self.network_cards.append(card)
        
        # Selecionar primeira rede por padrão
        if self.networks:
            self.on_network_selected(self.networks[0])
        
        self.networks_layout.addStretch()
    
    def clear_network_cards(self):
        """Remove todos os cards de rede"""
        for card in self.network_cards:
            card.deleteLater()
        self.network_cards.clear()
        
        # Limpar layout
        while self.networks_layout.count():
            item = self.networks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    @Slot(object)
    def on_network_selected(self, network):
        """Callback quando uma rede REAL é selecionada"""
        self.selected_network = network
        
        # Atualizar seleção dos cards
        for card in self.network_cards:
            card.set_selected(card.network.ssid == network.ssid)
        
        # Atualizar detalhes
        self.details_widget.set_network(network)
        self.details_widget.setVisible(True)
    
    @Slot(str)
    def on_copy_password(self, password):
        """Callback quando a senha REAL é copiada"""
        if password:
            clipboard = QApplication.clipboard()
            clipboard.setText(password)
            
            # Feedback visual
            self.status_label.setText("✓ Senha REAL copiada para área de transferência")
            QTimer.singleShot(2000, lambda: self.status_label.setText("Pronto"))
        else:
            self.status_label.setText("❌ Esta rede não possui senha disponível")
    
    def on_eye_clicked_from_card(self):
        """Callback quando olho é clicado"""
        if hasattr(self, 'details_widget') and self.details_widget.isVisible():
            self.details_widget.toggle_password_visibility()
    
    def set_scanning_state(self, scanning: bool):
        """Define o estado de escaneamento"""
        if scanning:
            self.btn_refresh.setEnabled(False)
            self.btn_refresh.setText(" Escaneando...")
            self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='#94a3b8'))
            self.spinner.setVisible(True)
            self.spinner.start_animation()
        else:
            self.btn_refresh.setEnabled(True)
            self.btn_refresh.setText(" Atualizar")
            self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='#ffffff'))
            self.spinner.setVisible(False)
            self.spinner.stop_animation()
    
    def show_empty_state(self):
        """Mostra estado vazio (nenhuma rede REAL encontrada)"""
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.wifi', color='#94a3b8').pixmap(64, 64))
        
        text_label = QLabel("Nenhuma rede Wi-Fi encontrada")
        text_label.setStyleSheet("""
            font-size: 16px;
            color: #64748b;
            margin-top: 16px;
        """)
        
        hint_label = QLabel("Clique em 'Atualizar' para escanear novamente")
        hint_label.setStyleSheet("font-size: 12px; color: #94a3b8;")
        
        empty_layout.addWidget(icon_label)
        empty_layout.addWidget(text_label)
        empty_layout.addWidget(hint_label)
        
        self.networks_layout.addWidget(empty_widget)
    
    def show_error_state(self, error_message: str):
        """Mostra estado de erro sem usar dados mockados"""
        # Apenas log e feedback visual, SEM criar redes falsas
        print(f"Erro no scan REAL: {error_message}")
        
        # Mostrar mensagem de erro elegante
        self.clear_network_cards()
        
        error_widget = QWidget()
        error_layout = QVBoxLayout(error_widget)
        error_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.exclamation-triangle', color='#ef4444').pixmap(48, 48))
        
        text_label = QLabel("Erro ao escanear redes")
        text_label.setStyleSheet("""
            font-size: 16px;
            color: #ef4444;
            margin-top: 16px;
        """)
        
        error_detail = QLabel(error_message[:100] + "...")
        error_detail.setStyleSheet("font-size: 12px; color: #64748b;")
        error_detail.setWordWrap(True)
        
        hint_label = QLabel("Tente executar como Administrador")
        hint_label.setStyleSheet("font-size: 12px; color: #94a3b8; margin-top: 8px;")
        
        error_layout.addWidget(icon_label)
        error_layout.addWidget(text_label)
        error_layout.addWidget(error_detail)
        error_layout.addWidget(hint_label)
        
        self.networks_layout.addWidget(error_widget)
        self.details_widget.setVisible(False)