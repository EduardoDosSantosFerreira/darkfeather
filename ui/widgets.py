"""
Widgets reutilizáveis para a interface DarkFeather WiFi Analysis
"""

from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QApplication, QSizePolicy, QToolButton
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QPixmap
import qtawesome as qta

from core.scanner import WifiNetwork
from core.frequency import FrequencyInfo
from utils.helpers import get_signal_color, format_signal_quality


class LoadingSpinner(QWidget):
    """Widget de spinner para loading"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = None
        self.setFixedSize(20, 20)
    
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
            painter.drawLine(0, 0, 6, 0)
            painter.rotate(45)


class FrequencyBadge(QLabel):
    """Badge para exibir frequência real da rede"""
    
    COLORS = {
        "2.4 GHz": {"bg": "#3b82f620", "text": "#3b82f6", "icon": "📡"},
        "5 GHz": {"bg": "#8b5cf620", "text": "#8b5cf6", "icon": "🚀"},
        "6 GHz": {"bg": "#ec489920", "text": "#ec4899", "icon": "⚡"}
    }
    
    def __init__(self, frequency_info: FrequencyInfo, parent=None):
        super().__init__(parent)
        self.frequency_info = frequency_info
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a aparência do badge"""
        band = self.frequency_info.band or "2.4 GHz"
        color = self.COLORS.get(band, self.COLORS["2.4 GHz"])
        
        # Texto do badge
        if self.frequency_info.channel:
            text = f"{color['icon']} {band} (Ch {self.frequency_info.channel})"
        else:
            text = f"{color['icon']} {band}"
        
        self.setText(text)
        
        # Estilo
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color['bg']};
                color: {color['text']};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 600;
                max-height: 18px;
            }}
        """)
        
        # Tooltip com informações detalhadas
        tooltip = []
        tooltip.append(f"<b>Frequência:</b> {self.frequency_info.band}")
        if self.frequency_info.channel:
            tooltip.append(f"<b>Canal:</b> {self.frequency_info.channel}")
        if self.frequency_info.frequency_mhz:
            tooltip.append(f"<b>Frequência:</b> {self.frequency_info.frequency_mhz} MHz")
        if self.frequency_info.bssid:
            tooltip.append(f"<b>BSSID:</b> {self.frequency_info.bssid}")
        if self.frequency_info.signal_percent:
            tooltip.append(f"<b>Sinal:</b> {self.frequency_info.signal_percent}%")
        
        self.setToolTip("<br>".join(tooltip))


class WifiCardWidget(QFrame):
    """
    Card individual para exibição de uma rede WiFi
    """
    
    clicked = Signal(object)
    copy_requested = Signal(str)
    eye_clicked = Signal()
    
    def __init__(self, network: WifiNetwork, is_selected: bool = False):
        super().__init__()
        self.network = network
        self.is_selected = is_selected
        self.setup_ui()
        self.setup_shadow()
        self.update_style()
    
    def setup_ui(self):
        """Configura a interface do card"""
        self.setFixedHeight(110)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Linha superior
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        
        # Ícone WiFi
        self.wifi_icon = QLabel()
        quality_color = get_signal_color(self.network.signal_quality)
        icon_pixmap = qta.icon('fa5s.wifi', color=quality_color).pixmap(24, 24)
        self.wifi_icon.setPixmap(icon_pixmap)
        self.wifi_icon.setFixedSize(24, 24)
        top_row.addWidget(self.wifi_icon)
        
        # Nome da rede
        self.name_label = QLabel(self._elide_text(self.network.ssid, 30))
        name_font = QFont()
        name_font.setPointSize(13)
        name_font.setWeight(QFont.Weight.DemiBold)
        self.name_label.setFont(name_font)
        self.name_label.setStyleSheet("color: #0f172a;")
        self.name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_row.addWidget(self.name_label)
        
        # Botão de olho
        self.eye_button = QToolButton()
        self.eye_button.setIcon(qta.icon('fa5s.eye', color='#64748b'))
        self.eye_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.eye_button.setFixedSize(28, 28)
        self.eye_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 14px;
            }
            QToolButton:hover {
                background-color: #f1f5f9;
            }
        """)
        self.eye_button.clicked.connect(self.on_eye_clicked)
        self.eye_button.setToolTip("Mostrar senha")
        top_row.addWidget(self.eye_button)
        
        # Botão copiar
        self.copy_button = QToolButton()
        self.copy_button.setIcon(qta.icon('fa5s.copy', color='#64748b'))
        self.copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_button.setFixedSize(28, 28)
        self.copy_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 14px;
            }
            QToolButton:hover {
                background-color: #f1f5f9;
            }
        """)
        self.copy_button.clicked.connect(self.on_copy_clicked)
        self.copy_button.setToolTip("Copiar senha")
        top_row.addWidget(self.copy_button)
        
        # Desabilitar botões se não houver senha
        has_password = bool(self.network.password)
        self.eye_button.setEnabled(has_password)
        self.copy_button.setEnabled(has_password)
        
        layout.addLayout(top_row)
        
        # Linha de badges
        badges_row = QHBoxLayout()
        badges_row.setSpacing(6)
        
        # Badge de autenticação
        auth_text = self._elide_text(self.network.auth, 15)
        self.auth_badge = QLabel(f"  {auth_text}  ")
        self.auth_badge.setStyleSheet("""
            QLabel {
                background-color: #e2e8f0;
                color: #334155;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 10px;
                font-weight: 600;
                max-height: 18px;
            }
        """)
        badges_row.addWidget(self.auth_badge)
        
        # Badge de qualidade
        quality_text, quality_color = format_signal_quality(self.network.signal_quality)
        self.quality_badge = QLabel(f"  {quality_text}  ")
        self.quality_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {quality_color}20;
                color: {quality_color};
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 10px;
                font-weight: 600;
                max-height: 18px;
            }}
        """)
        badges_row.addWidget(self.quality_badge)
        
        # Badges de frequência
        if self.network.frequencies:
            for freq_info in self.network.frequencies[:2]:  # Máximo 2 badges
                freq_badge = FrequencyBadge(freq_info)
                badges_row.addWidget(freq_badge)
        
        badges_row.addStretch()
        layout.addLayout(badges_row)
        
        # Tooltip
        self.setToolTip(self._generate_tooltip())
    
    def _elide_text(self, text: str, max_length: int) -> str:
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _generate_tooltip(self) -> str:
        lines = []
        lines.append(f"<b>{self.network.ssid}</b>")
        lines.append(f"Autenticação: {self.network.auth}")
        lines.append(f"Criptografia: {self.network.encryption}")
        lines.append(f"Sinal: {self.network.signal_quality}")
        
        if self.network.frequencies:
            lines.append("<b>Frequências:</b>")
            for freq in self.network.frequencies:
                band_info = f"  • {freq.band}"
                if freq.channel:
                    band_info += f" (Canal {freq.channel})"
                lines.append(band_info)
        
        return "<br>".join(lines)
    
    def setup_shadow(self):
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 20))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
    
    def update_style(self):
        if self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #e8f0fe;
                    border: none;
                    border-radius: 12px;
                }
            """)
            self.shadow.setColor(QColor(37, 99, 235, 30))
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: none;
                    border-radius: 12px;
                }
                QFrame:hover {
                    background-color: #f8fafc;
                }
            """)
            self.shadow.setColor(QColor(0, 0, 0, 20))
    
    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.update_style()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.network)
        super().mousePressEvent(event)
    
    def on_eye_clicked(self):
        self.eye_clicked.emit()
    
    def on_copy_clicked(self):
        if self.network.password:
            self.copy_requested.emit(self.network.password)
            self.copy_button.setIcon(qta.icon('fa5s.check', color='#10b981'))
            QTimer.singleShot(800, self.restore_copy_button)
    
    def restore_copy_button(self):
        self.copy_button.setIcon(qta.icon('fa5s.copy', color='#64748b'))


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
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # Título
        title_label = QLabel("Detalhes da Rede")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0f172a;")
        layout.addWidget(title_label)
        
        # Grid de detalhes
        self.details_layout = QVBoxLayout()
        self.details_layout.setSpacing(8)
        
        self.detail_rows = {}
        fields = [
            ("SSID", "ssid"),
            ("Autenticação", "auth"),
            ("Criptografia", "encryption"),
            ("Sinal", "signal_quality"),
            ("Última conexão", "last_connection")
        ]
        
        for label_text, field in fields:
            row = self._create_detail_row(label_text, field)
            self.details_layout.addLayout(row)
        
        # Linha de frequências
        self.frequency_layout = QHBoxLayout()
        self.frequency_layout.setContentsMargins(0, 0, 0, 0)
        self.frequency_layout.setSpacing(8)
        
        freq_label = QLabel("Frequência")
        freq_label.setStyleSheet("color: #64748b; font-size: 12px;")
        freq_label.setFixedWidth(90)
        self.frequency_layout.addWidget(freq_label)
        
        self.frequency_container = QWidget()
        self.frequency_container_layout = QHBoxLayout(self.frequency_container)
        self.frequency_container_layout.setContentsMargins(0, 0, 0, 0)
        self.frequency_container_layout.setSpacing(6)
        self.frequency_layout.addWidget(self.frequency_container, 1)
        
        self.details_layout.addLayout(self.frequency_layout)
        
        # Linha da senha
        password_row = self._create_password_row()
        self.details_layout.addLayout(password_row)
        
        # Linha HEX (inicialmente oculta)
        self.hex_row = self._create_hex_row()
        self.details_layout.addLayout(self.hex_row)
        
        layout.addLayout(self.details_layout)
        layout.addStretch()
    
    def _create_detail_row(self, label_text: str, field: str) -> QHBoxLayout:
        """Cria uma linha de detalhe"""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        
        # Label
        label = QLabel(label_text)
        label.setStyleSheet("color: #64748b; font-size: 12px;")
        label.setFixedWidth(90)
        row.addWidget(label)
        
        # Valor
        value_label = QLabel("-")
        value_label.setStyleSheet("color: #0f172a; font-size: 12px; font-weight: 500;")
        value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        value_label.setWordWrap(True)
        value_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        row.addWidget(value_label, 1)
        
        self.detail_rows[field] = value_label
        return row
    
    def _create_password_row(self) -> QHBoxLayout:
        """Cria linha da senha com botões"""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        
        # Label
        label = QLabel("Chave")
        label.setStyleSheet("color: #64748b; font-size: 12px;")
        label.setFixedWidth(90)
        row.addWidget(label)
        
        # Valor da senha
        self.password_value = QLabel("********")
        self.password_value.setStyleSheet("color: #0f172a; font-size: 12px; font-weight: 500;")
        self.password_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.password_value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        row.addWidget(self.password_value, 1)
        
        # Botão revelar
        self.toggle_password_btn = QToolButton()
        self.toggle_password_btn.setIcon(qta.icon('fa5s.eye', color='#64748b'))
        self.toggle_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_password_btn.setFixedSize(24, 24)
        self.toggle_password_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 12px;
            }
            QToolButton:hover {
                background-color: #f1f5f9;
            }
        """)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        self.toggle_password_btn.setToolTip("Mostrar senha")
        row.addWidget(self.toggle_password_btn)
        
        # Botão copiar
        self.copy_password_btn = QToolButton()
        self.copy_password_btn.setIcon(qta.icon('fa5s.copy', color='#64748b'))
        self.copy_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_password_btn.setFixedSize(24, 24)
        self.copy_password_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 12px;
            }
            QToolButton:hover {
                background-color: #f1f5f9;
            }
        """)
        self.copy_password_btn.clicked.connect(self.copy_password)
        self.copy_password_btn.setToolTip("Copiar senha")
        row.addWidget(self.copy_password_btn)
        
        return row
    
    def _create_hex_row(self) -> QHBoxLayout:
        """Cria linha para chave HEX"""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        
        # Label
        label = QLabel("Chave HEX")
        label.setStyleSheet("color: #64748b; font-size: 11px;")
        label.setFixedWidth(90)
        row.addWidget(label)
        
        # Valor HEX
        self.hex_value = QLabel("")
        self.hex_value.setStyleSheet("color: #2563eb; font-size: 11px; font-family: monospace;")
        self.hex_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.hex_value.setWordWrap(True)
        self.hex_value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        row.addWidget(self.hex_value, 1)
        
        return row
    
    def setup_shadow(self):
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 15))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
    
    def set_network(self, network: WifiNetwork):
        """Define a rede a ser exibida"""
        self.network = network
        
        # Atualizar valores
        self.detail_rows["ssid"].setText(network.ssid)
        self.detail_rows["auth"].setText(network.auth)
        self.detail_rows["encryption"].setText(network.encryption)
        self.detail_rows["signal_quality"].setText(network.signal_quality)
        self.detail_rows["last_connection"].setText(
            network.last_connection if network.last_connection else "Não disponível"
        )
        
        # Atualizar frequências
        self._update_frequencies()
        
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
            self.hex_row.itemAt(0).widget().setVisible(True)
            self.hex_row.itemAt(1).widget().setVisible(True)
        else:
            self.hex_value.setVisible(False)
            self.hex_row.itemAt(0).widget().setVisible(False)
            self.hex_row.itemAt(1).widget().setVisible(False)
    
    def _update_frequencies(self):
        """Atualiza a exibição das frequências"""
        # Limpar container
        while self.frequency_container_layout.count():
            item = self.frequency_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if self.network.frequencies:
            for freq_info in self.network.frequencies:
                badge = FrequencyBadge(freq_info)
                self.frequency_container_layout.addWidget(badge)
            
            self.frequency_container_layout.addStretch()
            self.frequency_container.setVisible(True)
        else:
            # Mostrar mensagem se não há frequência
            no_freq_label = QLabel("Não disponível")
            no_freq_label.setStyleSheet("color: #94a3b8; font-size: 12px; font-style: italic;")
            self.frequency_container_layout.addWidget(no_freq_label)
    
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