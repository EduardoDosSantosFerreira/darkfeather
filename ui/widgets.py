"""
Widgets reutilizáveis para a interface DarkFeather WiFi Analysis
"""

import subprocess
import re
import time
from typing import Dict, Optional, List
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QApplication, QSizePolicy, QToolButton, QGridLayout,
    QScrollArea, QSpacerItem
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QPixmap
import qtawesome as qta

from core.scanner import WifiNetwork
from core.frequency import FrequencyInfo, RealFrequencyDetector
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


class SectionHeader(QWidget):
    """Cabeçalho de seção colapsável"""
    
    toggled = Signal(bool)
    
    def __init__(self, title: str, collapsed: bool = False, parent=None):
        super().__init__(parent)
        self.title = title
        self.collapsed = collapsed
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedHeight(32)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(8)
        
        self.icon_label = QLabel()
        self.update_icon()
        layout.addWidget(self.icon_label)
        
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 600;
            color: #1e293b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        self.count_label = QLabel()
        self.count_label.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(self.count_label)
    
    def update_icon(self):
        icon = 'fa5s.chevron-down' if not self.collapsed else 'fa5s.chevron-right'
        self.icon_label.setPixmap(qta.icon(icon, color='#64748b').pixmap(12, 12))
    
    def set_count(self, count: int):
        self.count_label.setText(f"{count} itens" if count > 0 else "")
    
    def mousePressEvent(self, event):
        self.collapsed = not self.collapsed
        self.update_icon()
        self.toggled.emit(not self.collapsed)
        super().mousePressEvent(event)


class KeyValueGrid(QWidget):
    """Grid otimizado para exibição de pares chave-valor"""
    
    def __init__(self, columns: int = 2, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.rows = []
        self.setup_ui()
    
    def setup_ui(self):
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(24)
        self.grid_layout.setVerticalSpacing(8)
    
    def add_row(self, key: str, value: str, row: int, col: int, 
                warning: bool = False, error: bool = False, success: bool = False):
        """Adiciona uma linha na posição especificada"""
        
        key_label = QLabel(key)
        key_label.setStyleSheet("""
            color: #64748b;
            font-size: 11px;
            font-weight: 500;
        """)
        key_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.grid_layout.addWidget(key_label, row, col * 2, Qt.AlignRight)
        
        if error or "erro" in value.lower() or "falhou" in value.lower():
            style = "color: #ef4444; font-size: 11px; font-weight: 500; font-style: italic;"
        elif warning or "não" in value.lower() or "apenas quando" in value.lower():
            style = "color: #f59e0b; font-size: 11px; font-weight: 500; font-style: italic;"
        elif success or "disponível" in value.lower() and "perfil" in value.lower():
            style = "color: #10b981; font-size: 11px; font-weight: 500;"
        else:
            style = "color: #0f172a; font-size: 11px; font-weight: 500;"
        
        value_label = QLabel(value)
        value_label.setStyleSheet(style)
        value_label.setWordWrap(True)
        value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.grid_layout.addWidget(value_label, row, col * 2 + 1, Qt.AlignLeft)
        
        self.rows.append((key, value, row, col))
    
    def clear(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.rows.clear()


class CollapsibleSection(QWidget):
    """Seção colapsável com grid interno"""
    
    def __init__(self, title: str, columns: int = 2, parent=None):
        super().__init__(parent)
        self.title = title
        self.columns = columns
        self.collapsed = False
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        self.header = SectionHeader(self.title)
        self.header.toggled.connect(self.on_toggled)
        layout.addWidget(self.header)
        
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(16, 0, 0, 0)
        self.content_layout.setSpacing(8)
        
        self.grid = KeyValueGrid(self.columns)
        self.content_layout.addWidget(self.grid)
        self.content_layout.addStretch()
        
        layout.addWidget(self.content)
    
    def on_toggled(self, expanded: bool):
        self.collapsed = not expanded
        self.content.setVisible(expanded)
    
    def add_row(self, key: str, value: str, warning: bool = False, 
                error: bool = False, success: bool = False):
        row = len(self.grid.rows) // self.columns
        col = len(self.grid.rows) % self.columns
        self.grid.add_row(key, value, row, col, warning, error, success)
        self.header.set_count(len(self.grid.rows))
    
    def clear(self):
        self.grid.clear()
        self.header.set_count(0)


class MetricWidget(QFrame):
    """Widget compacto para métricas importantes"""
    
    def __init__(self, label: str, value: str, color: str, parent=None):
        super().__init__(parent)
        self.label = label
        self.value = value
        self.color = color
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedHeight(48)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color}10;
                border: 1px solid {self.color}30;
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        
        value_label = QLabel(self.value)
        value_label.setStyleSheet(f"color: {self.color}; font-size: 16px; font-weight: 600;")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        label_label = QLabel(self.label)
        label_label.setStyleSheet("color: #64748b; font-size: 10px;")
        label_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_label)


class NetworkDetailsWidget(QFrame):
    """
    Widget de detalhes da rede - Layout otimizado para alta densidade
    """
    
    def __init__(self):
        super().__init__()
        self.network = None
        self.password_visible = False
        self.real_password = None
        self.freq_detector = RealFrequencyDetector()
        self.real_data = {}
        self.sections = {}
        self.setup_ui()
        self.setup_shadow()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 6px;
                background: #f1f5f9;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 3px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Título
        title_label = QLabel("Detalhes da Rede")
        title_font = QFont()
        title_font.setPointSize(15)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0f172a;")
        main_layout.addWidget(title_label)
        
        # Área de scroll para conteúdo denso
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 4, 0)
        self.scroll_layout.setSpacing(16)
        
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
        
        self.show_placeholder()
    
    def show_placeholder(self):
        """Mostra placeholder quando nenhuma rede selecionada"""
        self.clear_content()
        
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        
        icon = QLabel()
        icon.setPixmap(qta.icon('fa5s.network-wired', color='#cbd5e1').pixmap(48, 48))
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)
        
        text = QLabel("Selecione uma rede para\nvisualizar dados técnicos")
        text.setStyleSheet("color: #94a3b8; font-size: 13px;")
        text.setAlignment(Qt.AlignCenter)
        layout.addWidget(text)
        
        self.scroll_layout.addWidget(placeholder)
        self.scroll_layout.addStretch()
    
    def set_network(self, network: WifiNetwork):
        """Carrega dados reais da rede selecionada"""
        self.network = network
        self.clear_content()
        
        # Coletar dados reais
        self.real_data = {
            **self.get_basic_info(),
            **self.get_interface_info(),
            **self.get_connection_info(),
            **self.get_ip_info(),
            **self.get_security_info(),
            **self.get_frequency_info()
        }
        
        # Cabeçalho com métricas principais
        self.add_header_section()
        
        # Seções organizadas
        self.add_identification_section()
        self.add_radio_section()
        self.add_ip_section()
        self.add_security_section()
        self.add_stats_section()
        self.add_password_section()
        
        self.scroll_layout.addStretch()
    
    def add_header_section(self):
        """Adiciona cabeçalho com métricas principais"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(8)
        
        # Nome da rede
        name_label = QLabel(self.real_data.get("ssid", "Rede"))
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setWeight(QFont.Weight.DemiBold)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #0f172a;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label, 1)
        
        # Badge de qualidade
        quality = self.real_data.get("signal_quality", "Desconhecido")
        quality_color = {
            "Excelente": "#10b981",
            "Bom": "#3b82f6",
            "Regular": "#f59e0b",
            "Fraco": "#ef4444",
            "Desconhecido": "#94a3b8"
        }.get(quality, "#94a3b8")
        
        quality_badge = QLabel(f"  {quality}  ")
        quality_badge.setStyleSheet(f"""
            background-color: {quality_color}20;
            color: {quality_color};
            border-radius: 12px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 600;
        """)
        layout.addWidget(quality_badge)
        
        self.scroll_layout.addWidget(header)
    
    def add_identification_section(self):
        """Seção de identificação"""
        section = CollapsibleSection("IDENTIFICAÇÃO", columns=2)
        section.add_row("SSID", self.real_data.get("ssid", "N/A"))
        section.add_row("BSSID", self.real_data.get("bssid", "Não disponível"))
        section.add_row("Interface", self.real_data.get("interface_name", "Não disponível"))
        section.add_row("MAC", self.real_data.get("interface_mac", "Não disponível"))
        section.add_row("GUID", self.real_data.get("interface_guid", "Não disponível"), warning=True)
        section.add_row("Oculto", self.real_data.get("hidden", "Não disponível"))
        self.scroll_layout.addWidget(section)
        self.sections["identification"] = section
    
    def add_radio_section(self):
        """Seção de rádio e sinal"""
        section = CollapsibleSection("RÁDIO E SINAL", columns=2)
        section.add_row("Canal", self.real_data.get("channel", "Não disponível"))
        section.add_row("Banda", self.real_data.get("band", "Não disponível"))
        
        freq = self.real_data.get("frequency_mhz", "Não disponível")
        if freq != "Não disponível":
            freq = f"{freq} MHz"
        section.add_row("Frequência", freq)
        
        section.add_row("RSSI", self.real_data.get("rssi_dbm", "Não disponível"))
        section.add_row("Sinal", self.real_data.get("signal_percent", "Não disponível"))
        section.add_row("Velocidade", self.real_data.get("link_speed", "Não disponível"))
        section.add_row("PHY", self.real_data.get("phy_type", "Não disponível"))
        
        if self.real_data.get("frequencies") and self.real_data.get("frequencies") != "Não disponível":
            section.add_row("Bandas", self.real_data.get("frequencies"))
        
        self.scroll_layout.addWidget(section)
        self.sections["radio"] = section
    
    def add_ip_section(self):
        """Seção de configuração IP"""
        section = CollapsibleSection("CONFIGURAÇÃO IP", columns=2)
        section.add_row("IPv4", self.real_data.get("ipv4", "Não disponível"))
        section.add_row("IPv6", self.real_data.get("ipv6", "Não disponível"))
        section.add_row("Máscara", self.real_data.get("subnet_mask", "Não disponível"))
        section.add_row("Gateway", self.real_data.get("gateway", "Não disponível"))
        section.add_row("DNS", self.real_data.get("dns_servers", "Não disponível"))
        section.add_row("DHCP", self.real_data.get("dhcp_enabled", "Não disponível"))
        self.scroll_layout.addWidget(section)
        self.sections["ip"] = section
    
    def add_security_section(self):
        """Seção de segurança"""
        section = CollapsibleSection("SEGURANÇA", columns=2)
        section.add_row("Autenticação", self.real_data.get("auth", "N/A"))
        section.add_row("AKM", self.real_data.get("akm", "Não disponível"))
        section.add_row("Criptografia", self.real_data.get("encryption", "N/A"))
        section.add_row("PMF", self.real_data.get("pmf", "Não disponível"))
        section.add_row("WPS", self.real_data.get("wps", "Não disponível"))
        self.scroll_layout.addWidget(section)
        self.sections["security"] = section
    
    def add_stats_section(self):
        """Seção de estatísticas"""
        section = CollapsibleSection("STATUS", columns=2)
        section.add_row("Estado", self.real_data.get("interface_status", "Não disponível"))
        if self.real_data.get("last_connection"):
            section.add_row("Última conexão", self.real_data.get("last_connection"))
        section.add_row("Tipo PHY", self.real_data.get("phy_type", "Não disponível"))
        self.scroll_layout.addWidget(section)
        self.sections["stats"] = section
    
    def add_password_section(self):
        """Seção de senha"""
        section = CollapsibleSection("CREDENCIAIS", columns=1)
        
        # Linha da senha
        password_widget = QWidget()
        password_layout = QHBoxLayout(password_widget)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(8)
        
        password_label = QLabel("Chave:")
        password_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 500;")
        password_label.setFixedWidth(60)
        password_layout.addWidget(password_label)
        
        self.password_value = QLabel("********")
        self.password_value.setStyleSheet("color: #0f172a; font-size: 11px; font-weight: 500;")
        self.password_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        password_layout.addWidget(self.password_value, 1)
        
        # Botões
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
        password_layout.addWidget(self.toggle_password_btn)
        
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
        password_layout.addWidget(self.copy_password_btn)
        
        # Habilitar/desabilitar
        has_password = bool(self.real_data.get("password"))
        self.toggle_password_btn.setEnabled(has_password)
        self.copy_password_btn.setEnabled(has_password)
        self.real_password = self.real_data.get("password")
        
        # Adicionar ao grid da seção
        section.grid.grid_layout.addWidget(password_widget, 0, 1, 1, 2)
        
        # HEX se disponível
        if self.real_data.get("password_hex"):
            hex_widget = QWidget()
            hex_layout = QHBoxLayout(hex_widget)
            hex_layout.setContentsMargins(0, 0, 0, 0)
            
            hex_label = QLabel("HEX:")
            hex_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 500;")
            hex_label.setFixedWidth(60)
            hex_layout.addWidget(hex_label)
            
            hex_val = self.real_data.get("password_hex", "")
            if len(hex_val) > 40:
                hex_val = hex_val[:40] + "..."
            
            hex_value = QLabel(hex_val)
            hex_value.setStyleSheet("color: #2563eb; font-size: 11px; font-family: monospace;")
            hex_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            hex_value.setWordWrap(True)
            hex_layout.addWidget(hex_value, 1)
            
            section.grid.grid_layout.addWidget(hex_widget, 1, 1, 1, 2)
        
        self.scroll_layout.addWidget(section)
        self.sections["password"] = section
    
    def get_basic_info(self) -> Dict:
        return {
            "ssid": self.network.ssid if self.network else "N/A",
            "auth": self.network.auth if self.network else "N/A",
            "encryption": self.network.encryption if self.network else "N/A",
            "signal_quality": self.network.signal_quality if self.network else "N/A",
            "password": self.network.password if self.network and self.network.password else None,
            "password_hex": self.network.password_hex if self.network and self.network.password_hex else None,
            "last_connection": self.network.last_connection if self.network and self.network.last_connection else None
        }
    
    def get_interface_info(self) -> Dict:
        data = {
            "interface_name": "Não disponível",
            "interface_mac": "Não disponível",
            "interface_status": "Não disponível",
            "interface_guid": "Não disponível"
        }
        
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode != 0:
                data["interface_name"] = f"Erro: netsh falhou (código {result.returncode})"
                return data
            
            output = result.stdout
            
            if "não há" in output.lower() or "there is no" in output.lower():
                data["interface_name"] = "Nenhuma interface WiFi encontrada"
                data["interface_status"] = "Desativada"
                return data
            
            name_match = re.search(r'Nome\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
            if name_match:
                data["interface_name"] = name_match.group(1).strip()
            
            mac_match = re.search(r'Endereço físico\s*:\s*([0-9A-Fa-f:-]+)', output, re.MULTILINE | re.IGNORECASE)
            if mac_match:
                data["interface_mac"] = mac_match.group(1).strip().upper()
            
            state_match = re.search(r'Estado\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
            if state_match:
                data["interface_status"] = state_match.group(1).strip()
            
            guid_match = re.search(r'GUID do perfil\s*:\s*({[0-9A-F-]+})', output, re.MULTILINE | re.IGNORECASE)
            if guid_match:
                data["interface_guid"] = guid_match.group(1).strip()
            
        except PermissionError:
            data["interface_name"] = "Permissão negada"
        except Exception as e:
            data["interface_name"] = f"Erro: {str(e)[:30]}"
        
        return data
    
    def get_connection_info(self) -> Dict:
        data = {
            "bssid": "Não disponível",
            "channel": "Não disponível",
            "frequency_mhz": "Não disponível",
            "band": "Não disponível",
            "rssi_dbm": "Não disponível",
            "signal_percent": "Não disponível",
            "link_speed": "Não disponível",
            "phy_type": "Não disponível"
        }
        
        if not self.network:
            return data
        
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode != 0:
                return data
            
            output = result.stdout
            
            current_ssid_match = re.search(r'SSID\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
            current_ssid = current_ssid_match.group(1).strip() if current_ssid_match else ""
            
            if current_ssid.lower() != self.network.ssid.lower():
                data["bssid"] = "Não conectada"
                data["channel"] = "Apenas quando conectado"
                return data
            
            bssid_match = re.search(r'BSSID\s*:\s*([0-9A-Fa-f:-]+)', output, re.MULTILINE | re.IGNORECASE)
            if bssid_match:
                data["bssid"] = bssid_match.group(1).strip().upper()
            
            channel_match = re.search(r'Canal\s*:\s*(\d+)', output, re.MULTILINE | re.IGNORECASE)
            if channel_match:
                channel = int(channel_match.group(1))
                data["channel"] = str(channel)
                
                if 1 <= channel <= 14:
                    data["band"] = "2.4 GHz"
                    data["frequency_mhz"] = str(2412 + (channel - 1) * 5) if channel <= 11 else "2484"
                elif 36 <= channel <= 165:
                    data["band"] = "5 GHz"
                    freq_map = {36:5180,40:5200,44:5220,48:5240,52:5260,56:5280,60:5300,64:5320,
                               100:5500,104:5520,108:5540,112:5560,116:5580,120:5600,124:5620,128:5640,
                               132:5660,136:5680,140:5700,144:5720,149:5745,153:5765,157:5785,161:5805,165:5825}
                    data["frequency_mhz"] = str(freq_map.get(channel, "?"))
                else:
                    data["band"] = "6 GHz"
            
            rssi_match = re.search(r'RSSI\s*:\s*(-?\d+)', output, re.MULTILINE | re.IGNORECASE)
            if rssi_match:
                rssi = int(rssi_match.group(1))
                data["rssi_dbm"] = f"{rssi} dBm"
                percent = max(0, min(100, int((rssi + 90) * 100 / 60)))
                data["signal_percent"] = f"{percent}%"
            
            speed_match = re.search(r'Velocidade de (?:transmissão|recebimento)[^:]*:\s*(\d+[.,]?\d*)\s*\(?[Mm]bps\)?', 
                                   output, re.MULTILINE | re.IGNORECASE)
            if speed_match:
                data["link_speed"] = speed_match.group(1).replace(',', '.') + " Mbps"
            
            phy_match = re.search(r'Tipo de rádio\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
            if phy_match:
                data["phy_type"] = phy_match.group(1).strip()
            
        except Exception as e:
            data["bssid"] = f"Erro: {str(e)[:30]}"
        
        return data
    
    def get_ip_info(self) -> Dict:
        data = {
            "ipv4": "Não disponível",
            "ipv6": "Não disponível",
            "subnet_mask": "Não disponível",
            "gateway": "Não disponível",
            "dns_servers": "Não disponível",
            "dhcp_enabled": "Não disponível"
        }
        
        try:
            result = subprocess.run(
                ["ipconfig", "/all"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode != 0:
                return data
            
            output = result.stdout
            
            sections = re.split(r'\r?\n\r?\n', output)
            for section in sections:
                if "wi-fi" in section.lower() or "wireless" in section.lower() or "wlan" in section.lower():
                    
                    dhcp_match = re.search(r'DHCP (?:ativado|habilitado)[ .]*:?\s*(.+)', section, re.IGNORECASE)
                    if dhcp_match:
                        data["dhcp_enabled"] = "Sim" if "sim" in dhcp_match.group(1).lower() else "Não"
                    
                    ip_match = re.search(r'Endereço IPv4[ .]*:?\s*([0-9.]+)', section, re.IGNORECASE)
                    if ip_match:
                        data["ipv4"] = ip_match.group(1)
                    
                    ip6_match = re.search(r'Endereço IPv6[ .]*:?\s*([0-9a-f:]+)', section, re.IGNORECASE)
                    if ip6_match:
                        data["ipv6"] = ip6_match.group(1)
                    
                    mask_match = re.search(r'Máscara de sub-rede[ .]*:?\s*([0-9.]+)', section, re.IGNORECASE)
                    if mask_match:
                        data["subnet_mask"] = mask_match.group(1)
                    
                    gw_match = re.search(r'Gateway padrão[ .]*:?\s*([0-9.]+)', section, re.IGNORECASE)
                    if gw_match:
                        data["gateway"] = gw_match.group(1)
                    
                    dns_list = []
                    dns_matches = re.findall(r'Servidores? DNS[ .]*:?\s*([0-9.]+)', section, re.IGNORECASE)
                    for dns in dns_matches[:3]:
                        dns_list.append(dns)
                    
                    if dns_list:
                        data["dns_servers"] = ", ".join(dns_list)
                    
                    break
        
        except Exception as e:
            data["ipv4"] = f"Erro: {str(e)[:30]}"
        
        return data
    
    def get_security_info(self) -> Dict:
        data = {
            "akm": "Não disponível",
            "pmf": "Não disponível",
            "wps": "Não disponível",
            "hidden": "Não disponível"
        }
        
        if not self.network:
            return data
        
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "profile", f"name={self.network.ssid}", "key=clear"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode != 0:
                data["akm"] = "Erro ao acessar perfil"
                return data
            
            output = result.stdout
            
            akm_match = re.search(r'Gerenciamento de chaves\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
            if akm_match:
                data["akm"] = akm_match.group(1).strip()
            
            pmf_match = re.search(r'PMF\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
            if pmf_match:
                pmf_value = pmf_match.group(1).strip()
                if "obrigatório" in pmf_value.lower():
                    data["pmf"] = "Obrigatório"
                elif "capaz" in pmf_value.lower() or "suportado" in pmf_value.lower():
                    data["pmf"] = "Suportado"
                elif "não" in pmf_value.lower():
                    data["pmf"] = "Não suportado"
                else:
                    data["pmf"] = pmf_value
            
            wps_match = re.search(r'WPS\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
            if wps_match:
                data["wps"] = wps_match.group(1).strip()
            
            hidden_match = re.search(r'SSID\s+oculto\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
            if hidden_match:
                hidden_val = hidden_match.group(1).strip().lower()
                data["hidden"] = "Sim" if "sim" in hidden_val or "true" in hidden_val else "Não"
            
        except Exception as e:
            data["akm"] = f"Erro: {str(e)[:30]}"
        
        return data
    
    def get_frequency_info(self) -> Dict:
        data = {
            "frequencies": "Não disponível",
            "channels": "Não disponível"
        }
        
        if not self.network:
            return data
        
        freqs = self.freq_detector.get_network_frequencies(self.network.ssid)
        
        if freqs:
            bands = list(set([f.band for f in freqs if f.band]))
            channels = [str(f.channel) for f in freqs if f.channel]
            
            data["frequencies"] = ", ".join(bands) if bands else "Desconhecido"
            data["channels"] = ", ".join(channels) if channels else "Desconhecido"
        
        return data
    
    def clear_content(self):
        """Limpa todo conteúdo"""
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.sections.clear()
    
    def setup_shadow(self):
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 1)
        self.setGraphicsEffect(shadow)
    
    def update_password_display(self):
        if self.password_visible and self.real_password:
            self.password_value.setText(self.real_password)
            self.toggle_password_btn.setIcon(qta.icon('fa5s.eye-slash', color='#2563eb'))
            self.toggle_password_btn.setToolTip("Ocultar senha")
        else:
            self.password_value.setText("********")
            self.toggle_password_btn.setIcon(qta.icon('fa5s.eye', color='#64748b'))
            self.toggle_password_btn.setToolTip("Mostrar senha")
    
    def toggle_password_visibility(self):
        if self.real_password:
            self.password_visible = not self.password_visible
            self.update_password_display()
    
    def copy_password(self):
        if self.real_password:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.real_password)
            self.copy_password_btn.setIcon(qta.icon('fa5s.check', color='#10b981'))
            QTimer.singleShot(800, self.restore_copy_icon)
    
    def restore_copy_icon(self):
        self.copy_password_btn.setIcon(qta.icon('fa5s.copy', color='#64748b'))