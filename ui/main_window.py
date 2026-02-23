"""
MainWindow principal da aplicação DarkFeather WiFi Analysis
Design moderno e refinado - PROPORÇÕES AJUSTADAS
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QApplication,
    QMessageBox, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Slot
from PySide6.QtGui import QFont, QColor, QPalette
import qtawesome as qta

from ui.widgets import WifiCardWidget, LoadingSpinner
from ui.modern_details_widget import ModernDetailsWidget as NetworkDetailsWidget
from ui.theme import UIThemeManager
from core.scanner import WifiScanner, WifiNetwork
from core.report import ReportGenerator
from audit.logger import AuditLogger
from core.security import SecurityAnalyzer


class MainWindow(QMainWindow):
    """
    Janela principal da aplicação - Design Moderno
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
        """Configura a interface do usuário com design moderno"""
        self.setWindowTitle("DarkFeather WiFi Analysis")
        self.setMinimumSize(1300, 800)
        
        # Aplicar tema
        self.setPalette(self.theme.get_palette())
        self.setStyleSheet(self.get_global_style())
        
        # Widget central
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)
        
        self.setup_header()
        self.setup_metrics_bar()
        self.setup_content_area()
        self.setup_status_bar()
    
    def get_global_style(self) -> str:
        """Estilos globais modernos"""
        return """
            QMainWindow {
                background-color: #f8fafc;
            }
            QWidget#centralWidget {
                background-color: #f8fafc;
            }
            QFrame {
                background-color: #ffffff;
                border-radius: 16px;
            }
            QLabel {
                color: #0f172a;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 6px;
                background: #e2e8f0;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #94a3b8;
                border-radius: 3px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: #64748b;
            }
        """
    
    def setup_header(self):
        """Configura o cabeçalho moderno"""
        header_widget = QWidget()
        header_widget.setObjectName("headerWidget")
        header_widget.setFixedHeight(70)
        header_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)
        
        # Logo e título
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(12)
        
        # Ícone com fundo
        icon_frame = QFrame()
        icon_frame.setFixedSize(44, 44)
        icon_frame.setStyleSheet("""
            QFrame {
                background-color: #2563eb;
                border-radius: 12px;
                border: none;
            }
        """)
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.wifi', color='#ffffff').pixmap(24, 24))
        icon_layout.addWidget(icon_label)
        logo_layout.addWidget(icon_frame)
        
        # Título e versão
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        
        title_label = QLabel("DarkFeather")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0f172a;")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("WiFi Security Analysis")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_font.setWeight(QFont.Weight.Normal)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #64748b;")
        title_layout.addWidget(subtitle_label)
        
        logo_layout.addWidget(title_container)
        header_layout.addWidget(logo_container)
        
        header_layout.addStretch()
        
        # Ações
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)
        
        # Botão Segurança
        self.btn_security = self.create_modern_button(
            " Segurança", 
            'fa5s.shield-alt', 
            "#8b5cf6",
            "#7c3aed"
        )
        self.btn_security.clicked.connect(self.open_security_window)
        actions_layout.addWidget(self.btn_security)
        
        # Botão atualizar
        self.btn_refresh = self.create_modern_button(
            " Atualizar", 
            'fa5s.sync-alt', 
            "#2563eb",
            "#1d4ed8"
        )
        actions_layout.addWidget(self.btn_refresh)
        
        # Botão relatório
        self.btn_report = self.create_modern_button(
            " Relatório", 
            'fa5s.file-alt', 
            "#059669",
            "#047857"
        )
        self.btn_report.clicked.connect(self.generate_report)
        actions_layout.addWidget(self.btn_report)
        
        # Loading spinner
        self.spinner = LoadingSpinner()
        self.spinner.setVisible(False)
        self.spinner.setFixedSize(24, 24)
        actions_layout.addWidget(self.spinner)
        
        header_layout.addWidget(actions_container)
        self.main_layout.addWidget(header_widget)
    
    def create_modern_button(self, text: str, icon: str, color: str, hover_color: str) -> QPushButton:
        """Cria botão moderno com efeitos"""
        btn = QPushButton(text)
        btn.setIcon(qta.icon(icon, color='#ffffff'))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(120, 40)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:disabled {{
                background-color: #cbd5e1;
            }}
        """)
        
        # Sombra suave
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 2)
        btn.setGraphicsEffect(shadow)
        
        return btn
    
    def setup_metrics_bar(self):
        """Configura barra de métricas compacta"""
        metrics_widget = QWidget()
        metrics_widget.setFixedHeight(80)
        
        metrics_layout = QHBoxLayout(metrics_widget)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(12)
        
        # Card de saúde
        self.health_card = self.create_metric_card(
            "Saúde", 
            "0%", 
            "#059669"
        )
        metrics_layout.addWidget(self.health_card)
        
        # Card de redes
        self.networks_card = self.create_metric_card(
            "Redes", 
            "0", 
            "#2563eb"
        )
        metrics_layout.addWidget(self.networks_card)
        
        # Card de risco alto
        self.high_risk_card = self.create_metric_card(
            "Risco Alto", 
            "0", 
            "#dc2626"
        )
        metrics_layout.addWidget(self.high_risk_card)
        
        # Card de risco médio
        self.medium_risk_card = self.create_metric_card(
            "Risco Médio", 
            "0", 
            "#d97706"
        )
        metrics_layout.addWidget(self.medium_risk_card)
        
        metrics_layout.addStretch()
        self.main_layout.addWidget(metrics_widget)
    
    def create_metric_card(self, title: str, value: str, color: str) -> QFrame:
        """Cria card de métrica compacto"""
        card = QFrame()
        card.setFixedSize(140, 70)
        card.setStyleSheet("background-color: #f8fafc; border-radius: 12px;")
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        
        # Valor
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 700;")
        layout.addWidget(value_label)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #475569; font-size: 11px; font-weight: 600;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label, 1)
        
        # Armazenar referência para o label de valor
        card.value_label = value_label
        
        return card
    
    def setup_content_area(self):
        """Configura a área de conteúdo principal com novas proporções"""
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)
        
        # Painel esquerdo - Lista de redes (35%)
        self.setup_networks_panel(content_layout)
        
        # Painel direito - Detalhes da rede (65%)
        self.setup_details_panel(content_layout)
        
        self.main_layout.addWidget(content_widget, stretch=1)
    
    def setup_networks_panel(self, parent_layout):
        """Configura o painel esquerdo com lista de redes - MAIS ESTREITO"""
        panel = QFrame()
        panel.setObjectName("networksPanel")
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        panel.setMinimumWidth(320)
        panel.setMaximumWidth(380)  # Limitado para não expandir demais
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 16, 16, 16)
        panel_layout.setSpacing(12)
        
        # Cabeçalho do painel
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Redes Wi-Fi Salvas")
        title_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #0f172a;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Badge com contador
        self.network_counter = QLabel("0")
        self.network_counter.setStyleSheet("""
            background-color: #e2e8f0;
            color: #334155;
            border-radius: 16px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: 600;
        """)
        header_layout.addWidget(self.network_counter)
        
        panel_layout.addWidget(header_widget)
        
        # Área de scroll para os cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        
        self.networks_layout = QVBoxLayout(scroll_content)
        self.networks_layout.setContentsMargins(0, 0, 4, 0)
        self.networks_layout.setSpacing(8)
        self.networks_layout.addStretch()
        
        self.scroll_area.setWidget(scroll_content)
        panel_layout.addWidget(self.scroll_area)
        
        parent_layout.addWidget(panel, stretch=35)  # 35% do espaço
    
    def setup_details_panel(self, parent_layout):
        """Configura o painel direito com detalhes - MAIS LARGO"""
        self.details_widget = NetworkDetailsWidget()
        self.details_widget.setVisible(False)
        self.details_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.details_widget.setMinimumWidth(500)  # Aumentado
        
        parent_layout.addWidget(self.details_widget, stretch=65)  # 65% do espaço
    
    def setup_status_bar(self):
        """Configura a barra de status moderna"""
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: white;
                color: #64748b;
                border-top: 1px solid #e2e8f0;
                padding: 6px 16px;
                font-size: 12px;
            }
        """)
        
        self.status_label = QLabel("Pronto")
        self.status_label.setStyleSheet("color: #64748b;")
        self.status_bar.addWidget(self.status_label, 1)
        
        # Indicador de saúde
        self.health_indicator = QLabel()
        self.status_bar.addPermanentWidget(self.health_indicator)
    
    def setup_animations(self):
        """Configura animações da interface"""
        self.header_animation = QPropertyAnimation(self.btn_refresh, b"geometry")
        self.header_animation.setDuration(200)
        self.header_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def setup_connections(self):
        """Configura conexões de sinais e slots"""
        self.btn_refresh.clicked.connect(self.start_scan)
        
        # Conectar sinais do scanner
        self.scanner.scan_finished.connect(self.on_scan_finished)
        self.scanner.scan_error.connect(self.on_scan_error)
        self.scanner.scan_progress.connect(self.on_scan_progress)
    
    @Slot()
    def start_scan(self):
        """Inicia scan REAL de redes Wi-Fi"""
        self.set_scanning_state(True)
        self.status_label.setText("Iniciando scan...")
        self.scanner.scan_networks()
    
    @Slot(list)
    def on_scan_finished(self, networks):
        """Callback quando scan termina"""
        self.networks = networks
        self.audit.log_scan_finished(len(networks))
        
        # Analisar segurança
        self.security_analysis = {}
        for net in networks:
            self.security_analysis[net.ssid] = SecurityAnalyzer.analyze_network(net)
        
        # Análise do ambiente
        self.environment_summary = SecurityAnalyzer.analyze_environment(networks)
        
        # Atualizar interface
        self.update_metrics()
        self.update_networks_display()
        self.network_counter.setText(str(len(networks)))
        
        if networks:
            health = self.environment_summary.get('health_status', 'N/A')
            score = self.environment_summary.get('health_score', 0)
            self.status_label.setText(f"Encontradas {len(networks)} redes")
            self.update_health_indicator(score, health)
        else:
            self.status_label.setText("Nenhuma rede encontrada")
            self.update_health_indicator(0, "Sem redes")
        
        self.set_scanning_state(False)
    
    def update_metrics(self):
        """Atualiza cards de métricas"""
        if self.environment_summary:
            # Atualizar card de saúde
            score = self.environment_summary.get('health_score', 0)
            self.health_card.value_label.setText(f"{score}%")
            
            # Atualizar card de redes
            total = self.environment_summary.get('total_networks', 0)
            self.networks_card.value_label.setText(str(total))
            
            # Atualizar card de risco alto
            high = self.environment_summary.get('high_risk', 0)
            self.high_risk_card.value_label.setText(str(high))
            
            # Atualizar card de risco médio
            medium = self.environment_summary.get('medium_risk', 0)
            self.medium_risk_card.value_label.setText(str(medium))
    
    def update_health_indicator(self, score: int, status: str):
        """Atualiza indicador de saúde na status bar"""
        if score >= 80:
            color = "#059669"
            icon = "●"
        elif score >= 50:
            color = "#d97706"
            icon = "●"
        else:
            color = "#dc2626"
            icon = "●"
        
        self.health_indicator.setText(f"{icon} Saúde {score}% - {status}")
        self.health_indicator.setStyleSheet(f"color: {color}; font-weight: 600; margin-right: 10px;")
    
    @Slot(str)
    def on_scan_error(self, error_msg):
        self.status_label.setText(f"Erro: {error_msg}")
        self.show_error_state(error_msg)
        self.set_scanning_state(False)
    
    @Slot(str)
    def on_scan_progress(self, progress_msg):
        self.status_label.setText(progress_msg)
    
    def update_networks_display(self):
        """Atualiza a exibição com dados REAIS"""
        self.clear_network_cards()
        
        if not self.networks:
            self.show_empty_state()
            self.details_widget.setVisible(False)
            return
        
        for i, network in enumerate(self.networks):
            analysis = self.security_analysis.get(network.ssid, {})
            
            card = WifiCardWidget(network, is_selected=(i == 0))
            card.clicked.connect(self.on_network_selected)
            card.copy_requested.connect(self.on_copy_password)
            card.eye_clicked.connect(self.on_eye_clicked_from_card)
            
            self.networks_layout.insertWidget(self.networks_layout.count() - 1, card)
            self.network_cards.append(card)
        
        if self.networks:
            self.on_network_selected(self.networks[0])
    
    def clear_network_cards(self):
        """Remove todos os cards de rede"""
        for card in self.network_cards:
            card.deleteLater()
        self.network_cards.clear()
        
        while self.networks_layout.count() > 1:
            item = self.networks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    @Slot(object)
    def on_network_selected(self, network):
        """Callback quando uma rede é selecionada"""
        self.selected_network = network
        
        for card in self.network_cards:
            card.set_selected(card.network.ssid == network.ssid)
        
        self.details_widget.set_network(network)
        self.details_widget.setVisible(True)
    
    @Slot(str)
    def on_copy_password(self, password):
        if password and self.selected_network:
            clipboard = QApplication.clipboard()
            clipboard.setText(password)
            self.audit.log_password_copied(self.selected_network.ssid)
            self.status_label.setText("✓ Senha copiada")
            QTimer.singleShot(2000, lambda: self.status_label.setText("Pronto"))
        else:
            self.status_label.setText("❌ Senha não disponível")
    
    def on_eye_clicked_from_card(self):
        if hasattr(self, 'details_widget') and self.details_widget.isVisible():
            self.details_widget.toggle_password_visibility()
    
    def open_security_window(self):
        if not self.networks:
            QMessageBox.warning(self, "Aviso", "Nenhuma rede para analisar.")
            return
        
        from ui.security.security_window import SecurityWindow
        self.security_window = SecurityWindow(self.networks, self)
        self.security_window.show()
    
    def generate_report(self):
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
            
            import subprocess
            subprocess.Popen(f'explorer /select,"{report_path}"')
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gerar relatório:\n{str(e)}")
    
    def set_scanning_state(self, scanning: bool):
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
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(12)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.wifi', color='#cbd5e1').pixmap(64, 64))
        icon_label.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(icon_label)
        
        text_label = QLabel("Nenhuma rede Wi-Fi encontrada")
        text_label.setStyleSheet("font-size: 15px; color: #64748b; font-weight: 500;")
        text_label.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(text_label)
        
        hint_label = QLabel("Clique em 'Atualizar' para escanear")
        hint_label.setStyleSheet("font-size: 12px; color: #94a3b8;")
        hint_label.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(hint_label)
        
        self.networks_layout.insertWidget(0, empty_widget)
    
    def show_error_state(self, error_message):
        self.clear_network_cards()
        
        error_widget = QWidget()
        error_layout = QVBoxLayout(error_widget)
        error_layout.setAlignment(Qt.AlignCenter)
        error_layout.setSpacing(12)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.exclamation-triangle', color='#dc2626').pixmap(48, 48))
        icon_label.setAlignment(Qt.AlignCenter)
        error_layout.addWidget(icon_label)
        
        text_label = QLabel("Erro ao escanear redes")
        text_label.setStyleSheet("font-size: 15px; color: #dc2626; font-weight: 600;")
        text_label.setAlignment(Qt.AlignCenter)
        error_layout.addWidget(text_label)
        
        error_detail = QLabel(error_message[:100] + ("..." if len(error_message) > 100 else ""))
        error_detail.setStyleSheet("font-size: 12px; color: #64748b;")
        error_detail.setWordWrap(True)
        error_detail.setAlignment(Qt.AlignCenter)
        error_layout.addWidget(error_detail)
        
        hint_label = QLabel("Execute como Administrador")
        hint_label.setStyleSheet("font-size: 12px; color: #94a3b8;")
        hint_label.setAlignment(Qt.AlignCenter)
        error_layout.addWidget(hint_label)
        
        self.networks_layout.insertWidget(0, error_widget)
        self.details_widget.setVisible(False)