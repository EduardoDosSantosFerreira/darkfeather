"""
Widget de controle do Mobile Hotspot
Arquivo: ui/hotspot_widget.py
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QMessageBox,
    QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal, QThreadPool, QTimer
from PySide6.QtGui import QFont, QColor
import qtawesome as qta

from core.hotspot import MobileHotspotController
from core.hotspot_worker import (
    HotspotStatusWorker, HotspotOperationWorker,
    HotspotWorkerSignals
)


class HotspotWidget(QFrame):
    """
    Widget de controle do Mobile Hotspot
    """
    
    status_changed = Signal(str)  # novo status
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = MobileHotspotController()
        self.thread_pool = QThreadPool.globalInstance()
        self.status_worker = None
        self.current_status = "Desconhecido"
        
        self.setup_ui()
        self.start_status_monitoring()
        self.load_config()
    
    def setup_ui(self):
        """Configura a interface do widget"""
        self.setObjectName("hotspotWidget")
        self.setStyleSheet("""
            QFrame#hotspotWidget {
                background-color: #ffffff;
                border-radius: 16px;
            }
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: #f8fafc;
            }
            QLineEdit:focus {
                border-color: #2563eb;
                background-color: #ffffff;
            }
            QLineEdit:disabled {
                background-color: #f1f5f9;
                color: #94a3b8;
            }
            QPushButton {
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        
        # Sombra suave
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # ===== CABEÇALHO =====
        header_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.wifi', color='#2563eb').pixmap(32, 32))
        header_layout.addWidget(icon_label)
        
        title = QLabel("Mobile Hotspot")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        title.setStyleSheet("color: #0f172a;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Badge de status
        self.status_badge = QLabel("  Desconhecido  ")
        self.status_badge.setStyleSheet("""
            QLabel {
                background-color: #94a3b820;
                color: #64748b;
                border-radius: 20px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: 600;
            }
        """)
        header_layout.addWidget(self.status_badge)
        
        layout.addLayout(header_layout)
        
        # ===== INFORMAÇÃO DE DISPONIBILIDADE =====
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #64748b; font-size: 12px; padding: 8px 0;")
        layout.addWidget(self.info_label)
        
        if not self.controller.is_available():
            self.info_label.setText(
                "⚠️ Controle direto via API não disponível.\n"
                "Use o botão abaixo para abrir as configurações do Windows."
            )
        
        # ===== CONFIGURAÇÕES =====
        config_frame = QFrame()
        config_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 12px;
            }
        """)
        config_layout = QVBoxLayout(config_frame)
        config_layout.setContentsMargins(16, 16, 16, 16)
        config_layout.setSpacing(12)
        
        # Título da seção
        config_title = QLabel("Configuração da Rede")
        config_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #0f172a;")
        config_layout.addWidget(config_title)
        
        # SSID
        ssid_layout = QVBoxLayout()
        ssid_layout.setSpacing(4)
        
        ssid_label = QLabel("Nome da rede (SSID)")
        ssid_label.setStyleSheet("color: #475569; font-size: 12px; font-weight: 500;")
        ssid_layout.addWidget(ssid_label)
        
        self.ssid_input = QLineEdit()
        self.ssid_input.setPlaceholderText("Ex: DarkFeather-Hotspot")
        self.ssid_input.setMaxLength(32)
        ssid_layout.addWidget(self.ssid_input)
        
        config_layout.addLayout(ssid_layout)
        
        # Senha
        password_layout = QVBoxLayout()
        password_layout.setSpacing(4)
        
        password_label = QLabel("Senha (mínimo 8 caracteres)")
        password_label.setStyleSheet("color: #475569; font-size: 12px; font-weight: 500;")
        password_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMaxLength(63)
        password_layout.addWidget(self.password_input)
        
        config_layout.addLayout(password_layout)
        
        # Botões de configuração
        config_buttons = QHBoxLayout()
        
        self.btn_save_config = QPushButton(" Salvar Configuração")
        self.btn_save_config.setIcon(qta.icon('fa5s.save', color='#ffffff'))
        self.btn_save_config.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        self.btn_save_config.clicked.connect(self.save_config)
        config_buttons.addWidget(self.btn_save_config)
        
        self.btn_refresh_config = QPushButton()
        self.btn_refresh_config.setIcon(qta.icon('fa5s.sync-alt', color='#475569'))
        self.btn_refresh_config.setFixedSize(40, 36)
        self.btn_refresh_config.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.btn_refresh_config.clicked.connect(self.load_config)
        config_buttons.addWidget(self.btn_refresh_config)
        
        config_layout.addLayout(config_buttons)
        
        layout.addWidget(config_frame)
        
        # ===== CONTROLES =====
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 12px;
            }
        """)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(16, 16, 16, 16)
        controls_layout.setSpacing(12)
        
        # Botão Iniciar
        self.btn_start = QPushButton(" Iniciar Hotspot")
        self.btn_start.setIcon(qta.icon('fa5s.play', color='#ffffff'))
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: white;
                border: none;
                padding: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        self.btn_start.clicked.connect(self.start_hotspot)
        controls_layout.addWidget(self.btn_start)
        
        # Botão Parar
        self.btn_stop = QPushButton(" Parar Hotspot")
        self.btn_stop.setIcon(qta.icon('fa5s.stop', color='#ffffff'))
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                padding: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        self.btn_stop.clicked.connect(self.stop_hotspot)
        controls_layout.addWidget(self.btn_stop)
        
        layout.addWidget(controls_frame)
        
        # ===== BOTÃO DE FALLBACK =====
        fallback_layout = QHBoxLayout()
        
        self.btn_settings = QPushButton(" Abrir Configurações do Windows")
        self.btn_settings.setIcon(qta.icon('fa5s.cog', color='#475569'))
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                color: #334155;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.btn_settings.clicked.connect(self.open_settings)
        fallback_layout.addWidget(self.btn_settings)
        
        layout.addLayout(fallback_layout)
        
        # Atualizar estado dos botões
        self.update_buttons_state()
    
    def start_status_monitoring(self):
        """Inicia o monitoramento periódico do status"""
        self.status_worker = HotspotStatusWorker(self.controller)
        self.status_worker.signals.status_updated.connect(self.on_status_updated)
        self.status_worker.signals.error_occurred.connect(self.on_error)
        self.status_worker.signals.fallback_triggered.connect(self.on_fallback_needed)
        self.thread_pool.start(self.status_worker)
    
    def load_config(self):
        """Carrega a configuração atual do hotspot"""
        worker = HotspotOperationWorker(self.controller, "get_config")
        worker.signals.config_loaded.connect(self.on_config_loaded)
        worker.signals.error_occurred.connect(self.on_error)
        self.thread_pool.start(worker)
    
    def save_config(self):
        """Salva a configuração do hotspot"""
        ssid = self.ssid_input.text().strip()
        password = self.password_input.text()
        
        # Validações
        if not ssid:
            QMessageBox.warning(self, "Aviso", "O nome da rede não pode estar vazio.")
            return
        
        if len(password) < 8:
            QMessageBox.warning(self, "Aviso", "A senha deve ter pelo menos 8 caracteres.")
            return
        
        worker = HotspotOperationWorker(
            self.controller, 
            "configure",
            ssid=ssid,
            password=password
        )
        worker.signals.operation_completed.connect(self.on_operation_completed)
        worker.signals.error_occurred.connect(self.on_error)
        self.thread_pool.start(worker)
    
    def start_hotspot(self):
        """Inicia o hotspot"""
        worker = HotspotOperationWorker(self.controller, "start")
        worker.signals.operation_completed.connect(self.on_operation_completed)
        worker.signals.error_occurred.connect(self.on_error)
        worker.signals.fallback_triggered.connect(self.on_fallback_needed)
        self.thread_pool.start(worker)
        self.update_buttons_state(working=True)
    
    def stop_hotspot(self):
        """Para o hotspot"""
        worker = HotspotOperationWorker(self.controller, "stop")
        worker.signals.operation_completed.connect(self.on_operation_completed)
        worker.signals.error_occurred.connect(self.on_error)
        worker.signals.fallback_triggered.connect(self.on_fallback_needed)
        self.thread_pool.start(worker)
        self.update_buttons_state(working=True)
    
    def open_settings(self):
        """Abre as configurações do Windows"""
        worker = HotspotOperationWorker(self.controller, "open_settings")
        worker.signals.operation_completed.connect(self.on_operation_completed)
        self.thread_pool.start(worker)
    
    def on_status_updated(self, status_text: str):
        """Callback quando o status é atualizado"""
        self.current_status = status_text
        self.status_badge.setText(f"  {status_text}  ")
        
        # Atualizar cor do badge
        if "Ativado" in status_text or "Enabled" in status_text:
            color = "#059669"
            bg = "#05966920"
        elif "Iniciando" in status_text or "Starting" in status_text:
            color = "#f59e0b"
            bg = "#f59e0b20"
        elif "Desativado" in status_text or "Disabled" in status_text:
            color = "#64748b"
            bg = "#64748b20"
        elif "Erro" in status_text or "Error" in status_text:
            color = "#dc2626"
            bg = "#dc262620"
        else:
            color = "#64748b"
            bg = "#64748b20"
        
        self.status_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {color};
                border-radius: 20px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)
        
        self.status_changed.emit(status_text)
        self.update_buttons_state()
    
    def on_config_loaded(self, config: dict):
        """Callback quando a configuração é carregada"""
        self.ssid_input.setText(config.get("ssid", ""))
        self.password_input.setText(config.get("password", ""))
    
    def on_operation_completed(self, success: bool, message: str):
        """Callback quando uma operação é concluída"""
        if success:
            # Mostrar mensagem temporária
            self.status_badge.setText(f"  ✓ {message}  ")
            QTimer.singleShot(2000, self.restore_status)
        else:
            if message:
                QMessageBox.warning(self, "Aviso", message)
        
        self.update_buttons_state()
    
    def on_error(self, error_msg: str):
        """Callback quando ocorre um erro"""
        # Apenas log, sem mostrar para o usuário
        print(f"Hotspot error: {error_msg}")
        self.update_buttons_state()
    
    def on_fallback_needed(self):
        """Callback quando fallback é necessário"""
        # Atualizar info label
        self.info_label.setText(
            "⚠️ Falha no controle direto. Use o botão abaixo "
            "para abrir as configurações do Windows."
        )
        self.btn_settings.setVisible(True)
    
    def restore_status(self):
        """Restaura o badge de status após mensagem temporária"""
        self.status_badge.setText(f"  {self.current_status}  ")
    
    def update_buttons_state(self, working: bool = False):
        """Atualiza o estado dos botões baseado no status"""
        is_available = self.controller.is_available()
        
        # Botões de configuração
        self.ssid_input.setEnabled(is_available and not working)
        self.password_input.setEnabled(is_available and not working)
        self.btn_save_config.setEnabled(is_available and not working)
        self.btn_refresh_config.setEnabled(is_available and not working)
        
        # Botões de controle
        if "Ativado" in self.current_status or "Enabled" in self.current_status:
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(is_available and not working)
        elif "Desativado" in self.current_status or "Disabled" in self.current_status:
            self.btn_start.setEnabled(is_available and not working)
            self.btn_stop.setEnabled(False)
        else:
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(False)
        
        # Botão de configurações sempre disponível
        self.btn_settings.setEnabled(True)