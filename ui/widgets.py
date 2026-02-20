"""
Widgets reutilizáveis para a interface DarkFeather WiFi Analysis
"""

from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QApplication, QSizePolicy, QToolButton
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPainter, QPen
import qtawesome as qta

from core.scanner import WifiNetwork  # Importar do local correto
from utils.helpers import get_signal_color, format_signal_quality  # Apenas os que existem


class LoadingSpinner(QWidget):
    """Widget de spinner para loading"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = None
        self.setFixedSize(24, 24)
    
    def start_animation(self):
        """Inicia a animação do spinner"""
        from PySide6.QtCore import QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)
    
    def stop_animation(self):
        """Para a animação do spinner"""
        if self.timer:
            self.timer.stop()
            self.timer = None
    
    def rotate(self):
        """Atualiza o ângulo do spinner"""
        self.angle = (self.angle + 10) % 360
        self.update()
    
    def paintEvent(self, event):
        """Desenha o spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(QColor("#2563eb"), 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)
        
        for i in range(8):
            opacity = 0.2 + (i / 8) * 0.8
            painter.setOpacity(opacity)
            painter.drawLine(0, 0, 8, 0)
            painter.rotate(45)


class WifiCardWidget(QFrame):
    """
    Card individual para exibição de uma rede WiFi
    """
    
    clicked = Signal(object)  # Emite a rede quando clicado
    copy_requested = Signal(str)  # Emite a senha quando cópia solicitada
    eye_clicked = Signal()  # Sinal para quando o olho é clicado
    
    def __init__(self, network: WifiNetwork, is_selected: bool = False):
        super().__init__()
        self.network = network
        self.is_selected = is_selected
        self.animation = None
        self.setup_ui()
        self.setup_animations()
        self.setup_shadow()
        self.update_style()
        
    def setup_ui(self):
        """Configura a interface do card"""
        self.setFixedHeight(90)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Layout principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)
        
        # Ícone WiFi com qualidade
        self.wifi_icon = QLabel()
        quality_color = get_signal_color(self.network.signal_quality)
        self.wifi_icon.setPixmap(
            qta.icon('fa5s.wifi', color=quality_color).pixmap(32, 32)
        )
        layout.addWidget(self.wifi_icon)
        
        # Informações da rede
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        
        # Nome da rede
        self.name_label = QLabel(self.network.ssid)
        name_font = QFont()
        name_font.setPointSize(13)
        name_font.setWeight(QFont.Weight.DemiBold)
        self.name_label.setFont(name_font)
        self.name_label.setStyleSheet("color: #0f172a;")
        info_layout.addWidget(self.name_label)
        
        # Badges de segurança e qualidade
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(8)
        
        # Badge de autenticação
        self.auth_badge = QLabel(f"  {self.network.auth}  ")
        self.auth_badge.setStyleSheet("""
            QLabel {
                background-color: #e2e8f0;
                color: #334155;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 11px;
                font-weight: 600;
            }
        """)
        badges_layout.addWidget(self.auth_badge)
        
        # Badge de qualidade
        quality_text, quality_color = format_signal_quality(self.network.signal_quality)
        self.quality_badge = QLabel(f"  {quality_text}  ")
        self.quality_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {quality_color}20;
                color: {quality_color};
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)
        badges_layout.addWidget(self.quality_badge)
        badges_layout.addStretch()
        
        info_layout.addLayout(badges_layout)
        layout.addLayout(info_layout, stretch=1)
        
        # Botão de olho
        self.eye_button = QToolButton()
        self.eye_button.setIcon(qta.icon('fa5s.eye', color='#64748b'))
        self.eye_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.eye_button.setFixedSize(32, 32)
        self.eye_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 16px;
            }
            QToolButton:hover {
                background-color: #f1f5f9;
            }
            QToolButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        self.eye_button.clicked.connect(self.on_eye_clicked)
        self.eye_button.setToolTip("Mostrar senha no painel de detalhes")
        
        # Botão copiar
        self.copy_button = QToolButton()
        self.copy_button.setIcon(qta.icon('fa5s.copy', color='#64748b'))
        self.copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_button.setFixedSize(32, 32)
        self.copy_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 16px;
            }
            QToolButton:hover {
                background-color: #f1f5f9;
            }
            QToolButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        self.copy_button.clicked.connect(self.on_copy_clicked)
        self.copy_button.setToolTip("Copiar senha")
        
        # Desabilitar botões se não houver senha
        has_password = bool(self.network.password)
        self.eye_button.setEnabled(has_password)
        self.copy_button.setEnabled(has_password)
        
        layout.addWidget(self.eye_button)
        layout.addWidget(self.copy_button)
    
    def setup_animations(self):
        """Configura animações do card"""
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def setup_shadow(self):
        """Configura sombra do card"""
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 30))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
    
    def update_style(self):
        """Atualiza o estilo baseado no estado"""
        if self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #e8f0fe;
                    border: none;
                    border-radius: 16px;
                }
            """)
            self.shadow.setColor(QColor(37, 99, 235, 40))
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: none;
                    border-radius: 16px;
                }
                QFrame:hover {
                    background-color: #f8fafc;
                }
            """)
            self.shadow.setColor(QColor(0, 0, 0, 30))
    
    def set_selected(self, selected: bool):
        """Define se o card está selecionado"""
        self.is_selected = selected
        self.update_style()
    
    def enterEvent(self, event):
        """Evento de mouse enter"""
        super().enterEvent(event)
        if not self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #f8fafc;
                    border: none;
                    border-radius: 16px;
                }
            """)
    
    def leaveEvent(self, event):
        """Evento de mouse leave"""
        super().leaveEvent(event)
        self.update_style()
    
    def mousePressEvent(self, event):
        """Evento de clique do mouse"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.network)
        super().mousePressEvent(event)
    
    def on_eye_clicked(self):
        """Quando o olho é clicado"""
        self.eye_clicked.emit()
    
    def on_copy_clicked(self):
        """Quando o botão copiar é clicado"""
        if self.network.password:
            self.copy_requested.emit(self.network.password)
            
            # Feedback visual
            self.copy_button.setIcon(qta.icon('fa5s.check', color='#10b981'))
            self.copy_button.setToolTip("✓ Copiado!")
            
            # Restaurar após 800ms
            QTimer.singleShot(800, self.restore_copy_button)
    
    def restore_copy_button(self):
        """Restaura o botão de cópia ao estado normal"""
        self.copy_button.setIcon(qta.icon('fa5s.copy', color='#64748b'))
        self.copy_button.setToolTip("Copiar senha")


class NetworkDetailsWidget(QFrame):
    """
    Widget de detalhes da rede selecionada
    """
    
    def __init__(self):
        super().__init__()
        self.network = None
        self.password_visible = False
        self.real_password = None
        self.setup_ui()
        self.setup_shadow()
        
    def setup_ui(self):
        """Configura a interface do widget"""
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # Título
        title_layout = QHBoxLayout()
        title_label = QLabel("Detalhes da Rede")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0f172a;")
        title_layout.addWidget(title_label)
        
        # Badge de segurança
        self.security_badge = QLabel()
        self.security_badge.setStyleSheet("""
            QLabel {
                background-color: #e2e8f0;
                color: #334155;
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            }
        """)
        title_layout.addWidget(self.security_badge, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(title_layout)
        
        # Grid de detalhes
        grid_layout = QVBoxLayout()
        grid_layout.setSpacing(12)
        
        self.detail_rows = {}
        fields = [
            ("SSID", "ssid"),
            ("Autenticação", "auth"),
            ("Criptografia", "encryption"),
            ("Última conexão", "last_connection")
        ]
        
        for label_text, field in fields:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            
            # Label
            label = QLabel(label_text)
            label.setStyleSheet("color: #64748b; font-size: 12px;")
            label.setFixedWidth(120)
            row.addWidget(label)
            
            # Valor
            value_label = QLabel("-")
            value_label.setStyleSheet("color: #0f172a; font-size: 12px; font-weight: 500;")
            value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            row.addWidget(value_label)
            row.addStretch()
            
            self.detail_rows[field] = value_label
            grid_layout.addLayout(row)
        
        # Linha da senha
        password_row = QHBoxLayout()
        
        password_label = QLabel("Chave de segurança")
        password_label.setStyleSheet("color: #64748b; font-size: 12px;")
        password_label.setFixedWidth(120)
        password_row.addWidget(password_label)
        
        self.password_value = QLabel("********")
        self.password_value.setStyleSheet("color: #0f172a; font-size: 12px; font-weight: 500;")
        self.password_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        password_row.addWidget(self.password_value)
        
        # Botão revelar senha
        self.toggle_password_btn = QToolButton()
        self.toggle_password_btn.setIcon(qta.icon('fa5s.eye', color='#64748b'))
        self.toggle_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_password_btn.setFixedSize(28, 28)
        self.toggle_password_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 14px;
            }
            QToolButton:hover {
                background-color: #f1f5f9;
            }
            QToolButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        self.toggle_password_btn.setToolTip("Mostrar senha")
        password_row.addWidget(self.toggle_password_btn)
        
        # Botão copiar
        self.copy_password_btn = QToolButton()
        self.copy_password_btn.setIcon(qta.icon('fa5s.copy', color='#64748b'))
        self.copy_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_password_btn.setFixedSize(28, 28)
        self.copy_password_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 14px;
            }
            QToolButton:hover {
                background-color: #f1f5f9;
            }
            QToolButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        self.copy_password_btn.clicked.connect(self.copy_password)
        self.copy_password_btn.setToolTip("Copiar senha")
        password_row.addWidget(self.copy_password_btn)
        
        password_row.addStretch()
        grid_layout.addLayout(password_row)
        
        # Linha HEX
        hex_row = QHBoxLayout()
        hex_label = QLabel("Chave (HEX)")
        hex_label.setStyleSheet("color: #64748b; font-size: 11px;")
        hex_label.setFixedWidth(120)
        hex_row.addWidget(hex_label)
        
        self.hex_value = QLabel("")
        self.hex_value.setStyleSheet("color: #2563eb; font-size: 11px; font-family: monospace;")
        hex_row.addWidget(self.hex_value)
        hex_row.addStretch()
        
        self.hex_container = hex_row
        grid_layout.addLayout(hex_row)
        
        layout.addLayout(grid_layout)
    
    def setup_shadow(self):
        """Configura sombra do widget"""
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 20))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
    
    def set_network(self, network: WifiNetwork):
        """Define a rede a ser exibida"""
        self.network = network
        
        # Atualizar valores
        self.detail_rows["ssid"].setText(network.ssid)
        self.detail_rows["auth"].setText(network.auth)
        self.detail_rows["encryption"].setText(network.encryption)
        self.detail_rows["last_connection"].setText(
            network.last_connection if network.last_connection else "Não disponível"
        )
        
        # Atualizar badge de segurança
        self.security_badge.setText(f"  {network.auth}  ")
        
        # Armazenar senha real
        self.real_password = network.password
        
        # Resetar estado de visibilidade
        self.password_visible = False
        self.update_password_display()
        
        # Habilitar/desabilitar botões
        has_password = bool(self.real_password)
        self.toggle_password_btn.setEnabled(has_password)
        self.copy_password_btn.setEnabled(has_password)
        
        # Atualizar HEX
        if network.password_hex:
            self.hex_value.setText(network.password_hex)
            self.hex_value.setVisible(True)
        else:
            self.hex_value.setVisible(False)
    
    def update_password_display(self):
        """Atualiza a exibição da senha"""
        if self.password_visible and self.real_password:
            self.password_value.setText(self.real_password)
            self.toggle_password_btn.setIcon(qta.icon('fa5s.eye-slash', color='#2563eb'))
            self.toggle_password_btn.setToolTip("Ocultar senha")
        else:
            self.password_value.setText("********")
            self.toggle_password_btn.setIcon(qta.icon('fa5s.eye', color='#64748b'))
            self.toggle_password_btn.setToolTip("Mostrar senha")
    
    def toggle_password_visibility(self):
        """Alterna visibilidade da senha"""
        if self.real_password:
            self.password_visible = not self.password_visible
            self.update_password_display()
    
    def copy_password(self):
        """Copia a senha para o clipboard"""
        if self.real_password:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.real_password)
            
            # Feedback visual
            self.copy_password_btn.setIcon(qta.icon('fa5s.check', color='#10b981'))
            self.copy_password_btn.setToolTip("✓ Copiado!")
            
            # Restaurar após 800ms
            QTimer.singleShot(800, self.restore_copy_icon)
    
    def restore_copy_icon(self):
        """Restaura o ícone de cópia"""
        self.copy_password_btn.setIcon(qta.icon('fa5s.copy', color='#64748b'))
        self.copy_password_btn.setToolTip("Copiar senha")