"""
MainWindow principal da aplicação DarkFeather WiFi Analysis
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QApplication,
    QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Slot
from PySide6.QtGui import QFont
import qtawesome as qta

from ui.widgets import WifiCardWidget, NetworkDetailsWidget, LoadingSpinner
from ui.theme import UIThemeManager
from core.scanner import WifiScanner, WifiNetwork
from core.report import ReportGenerator
from audit.logger import AuditLogger
from core.security import SecurityAnalyzer


class MainWindow(QMainWindow):
    """
    Janela principal da aplicação
    """
    
    def __init__(self):
        super().__init__()
        self.scanner = WifiScanner()
        self.theme = UIThemeManager()
        self.audit = AuditLogger()
        self.networks = []
        self.selected_network = None
        self.network_cards = []
        self.security_analysis = {}
        self.environment_summary = {}
        self.setup_ui()
        self.setup_animations()
        self.setup_connections()
        
        # Registrar inicialização
        self.audit.log_app_started()
        
        # Configurar para iniciar maximizado
        self.showMaximized()
        
        # Escanear automaticamente após inicialização
        QTimer.singleShot(100, self.start_scan)
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        self.setWindowTitle("DarkFeather WiFi Analysis")
        self.setMinimumSize(1000, 700)
        
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
        self.setup_content_area()
        self.setup_status_bar()
    
    def setup_header(self):
        """Configura o cabeçalho da aplicação"""
        header_widget = QWidget()
        header_widget.setObjectName("headerWidget")
        header_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 16)
        header_layout.setSpacing(12)
        
        # Título e ícone
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        # Ícone WiFi
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.wifi', color='#2563eb').pixmap(28, 28))
        title_layout.addWidget(icon_label)
        
        # Título
        title_label = QLabel("DarkFeather WiFi Analysis")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0f172a;")
        title_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        title_layout.addWidget(title_label)
        
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        
        # Container de ações
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)
        
        # Botão Segurança
        self.btn_security = QPushButton(" Segurança")
        self.btn_security.setIcon(qta.icon('fa5s.shield-alt', color='#ffffff'))
        self.btn_security.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_security.setFixedSize(110, 36)
        self.btn_security.setStyleSheet(self.theme.get_button_style("primary"))
        self.btn_security.clicked.connect(self.open_security_window)
        
        # Botão atualizar
        self.btn_refresh = QPushButton(" Atualizar")
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='#ffffff'))
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setFixedSize(110, 36)
        self.btn_refresh.setStyleSheet(self.theme.get_button_style("primary"))
        
        # Botão relatório
        self.btn_report = QPushButton(" Relatório")
        self.btn_report.setIcon(qta.icon('fa5s.file-alt', color='#ffffff'))
        self.btn_report.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_report.setFixedSize(110, 36)
        self.btn_report.setStyleSheet(self.theme.get_button_style("primary"))
        self.btn_report.clicked.connect(self.generate_report)
        
        # Loading spinner
        self.spinner = LoadingSpinner()
        self.spinner.setVisible(False)
        self.spinner.setFixedSize(20, 20)
        
        actions_layout.addWidget(self.spinner)
        actions_layout.addWidget(self.btn_security)
        actions_layout.addWidget(self.btn_refresh)
        actions_layout.addWidget(self.btn_report)
        
        header_layout.addWidget(actions_container)
        self.main_layout.addWidget(header_widget)
    
    def setup_content_area(self):
        """Configura a área de conteúdo principal"""
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)
        
        # Painel esquerdo - Lista de redes
        self.setup_networks_panel(content_layout)
        
        # Painel direito - Detalhes da rede
        self.setup_details_panel(content_layout)
        
        self.main_layout.addWidget(content_widget, stretch=1)
    
    def setup_networks_panel(self, parent_layout):
        """Configura o painel esquerdo com lista de redes"""
        panel = QWidget()
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        panel.setMinimumWidth(400)
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(12)
        
        # Título do painel
        title_widget = QWidget()
        title_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Redes Wi-Fi Salvas")
        title_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 600;
            color: #334155;
        """)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        title_layout.addWidget(title_label)
        
        # Contador de redes
        self.network_counter = QLabel("0")
        self.network_counter.setStyleSheet("""
            color: #64748b;
            font-size: 13px;
            background-color: #f1f5f9;
            border-radius: 12px;
            padding: 2px 10px;
        """)
        title_layout.addWidget(self.network_counter)
        
        panel_layout.addWidget(title_widget)
        
        # Área de scroll para os cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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
                min-height: 30px;
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
        self.networks_layout.setSpacing(10)
        self.networks_layout.addStretch()
        
        self.scroll_area.setWidget(scroll_content)
        panel_layout.addWidget(self.scroll_area)
        
        parent_layout.addWidget(panel, stretch=3)
    
    def setup_details_panel(self, parent_layout):
        """Configura o painel direito com detalhes"""
        self.details_widget = NetworkDetailsWidget()
        self.details_widget.setVisible(False)
        self.details_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.details_widget.setMinimumWidth(350)
        
        parent_layout.addWidget(self.details_widget, stretch=2)
    
    def setup_status_bar(self):
        """Configura a barra de status"""
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #ffffff;
                color: #64748b;
                border-top: 1px solid #e2e8f0;
                padding: 6px 16px;
                font-size: 12px;
            }
        """)
        
        self.status_label = QLabel("Pronto")
        self.status_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.status_bar.addWidget(self.status_label, 1)
    
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
        
        # Registrar no log de auditoria
        self.audit.log_scan_finished(len(networks))
        
        # Analisar segurança
        self.security_analysis = {}
        for net in networks:
            self.security_analysis[net.ssid] = SecurityAnalyzer.analyze_network(net)
        
        # Análise do ambiente
        self.environment_summary = SecurityAnalyzer.analyze_environment(networks)
        
        # Atualizar interface
        self.update_networks_display()
        
        # Atualizar contador
        self.network_counter.setText(str(len(networks)))
        
        # Mostrar resultado
        if networks:
            health = self.environment_summary.get('health_status', 'N/A')
            score = self.environment_summary.get('health_score', 0)
            self.status_label.setText(
                f"Encontradas {len(networks)} redes | "
                f"Saúde: {health} ({score}%)"
            )
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
            # Obter análise de segurança
            analysis = self.security_analysis.get(network.ssid, {})
            
            card = WifiCardWidget(network, is_selected=(i == 0))
            card.clicked.connect(self.on_network_selected)
            card.copy_requested.connect(self.on_copy_password)
            card.eye_clicked.connect(self.on_eye_clicked_from_card)
            
            self.networks_layout.insertWidget(self.networks_layout.count() - 1, card)
            self.network_cards.append(card)
        
        # Selecionar primeira rede por padrão
        if self.networks:
            self.on_network_selected(self.networks[0])
    
    def clear_network_cards(self):
        """Remove todos os cards de rede"""
        for card in self.network_cards:
            card.deleteLater()
        self.network_cards.clear()
        
        # Limpar layout mantendo o stretch
        while self.networks_layout.count() > 1:
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
        if password and self.selected_network:
            clipboard = QApplication.clipboard()
            clipboard.setText(password)
            
            # Registrar na auditoria
            self.audit.log_password_copied(self.selected_network.ssid)
            
            # Feedback visual
            self.status_label.setText("✓ Senha copiada para área de transferência")
            QTimer.singleShot(2000, lambda: self.status_label.setText("Pronto"))
        else:
            self.status_label.setText("❌ Esta rede não possui senha disponível")
    
    def on_eye_clicked_from_card(self):
        """Callback quando olho é clicado"""
        if hasattr(self, 'details_widget') and self.details_widget.isVisible():
            self.details_widget.toggle_password_visibility()
    
    def open_security_window(self):
        """Abre a tela independente de segurança"""
        if not self.networks:
            QMessageBox.warning(self, "Aviso", "Nenhuma rede para analisar.")
            return
        
        # Importar diretamente do arquivo
        from ui.security.security_window import SecurityWindow
        self.security_window = SecurityWindow(self.networks, self)
        self.security_window.show()
    
    def generate_report(self):
        """Gera relatório de auditoria"""
        if not self.networks:
            QMessageBox.warning(self, "Aviso", "Nenhuma rede para gerar relatório.")
            return
        
        try:
            reporter = ReportGenerator(self.networks, self.audit)
            report_path = reporter.save_report("txt")
            
            QMessageBox.information(
                self,
                "Relatório Gerado",
                f"Relatório salvo em:\n{report_path}"
            )
            
            # Abrir pasta
            import subprocess
            subprocess.Popen(f'explorer /select,"{report_path}"')
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gerar relatório:\n{str(e)}")
    
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
        """Mostra estado vazio"""
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.wifi', color='#94a3b8').pixmap(64, 64))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        text_label = QLabel("Nenhuma rede Wi-Fi encontrada")
        text_label.setStyleSheet("font-size: 15px; color: #64748b; margin-top: 16px;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        hint_label = QLabel("Clique em 'Atualizar' para escanear novamente")
        hint_label.setStyleSheet("font-size: 12px; color: #94a3b8;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_layout.addWidget(icon_label)
        empty_layout.addWidget(text_label)
        empty_layout.addWidget(hint_label)
        
        self.networks_layout.insertWidget(0, empty_widget)
    
    def show_error_state(self, error_message: str):
        """Mostra estado de erro"""
        self.clear_network_cards()
        
        error_widget = QWidget()
        error_layout = QVBoxLayout(error_widget)
        error_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.exclamation-triangle', color='#ef4444').pixmap(48, 48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        text_label = QLabel("Erro ao escanear redes")
        text_label.setStyleSheet("font-size: 15px; color: #ef4444; margin-top: 16px;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        error_detail = QLabel(error_message[:100] + "...")
        error_detail.setStyleSheet("font-size: 12px; color: #64748b;")
        error_detail.setWordWrap(True)
        error_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        hint_label = QLabel("Tente executar como Administrador")
        hint_label.setStyleSheet("font-size: 12px; color: #94a3b8; margin-top: 8px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        error_layout.addWidget(icon_label)
        error_layout.addWidget(text_label)
        error_layout.addWidget(error_detail)
        error_layout.addWidget(hint_label)
        
        self.networks_layout.insertWidget(0, error_widget)
        self.details_widget.setVisible(False)