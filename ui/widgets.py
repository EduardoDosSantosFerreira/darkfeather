"""
Widgets reutilizáveis para a interface DarkFeather WiFi Analysis
DESIGN ATUALIZADO - Clean, sem bordas, N/A, responsivo
"""

import subprocess
import re
from typing import Dict, Optional, List
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QApplication, QSizePolicy, QToolButton, QGridLayout,
    QScrollArea, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QPainter, QPen

import qtawesome as qta

from core.scanner import WifiNetwork
from core.frequency import FrequencyInfo
from utils.helpers import get_signal_color, format_signal_quality
from ui.theme import UIThemeManager


class LoadingSpinner(QWidget):
    """Widget de spinner para loading - DESIGN ORIGINAL"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = None
        self.setFixedSize(24, 24)
    
    def start_animation(self):
        """Inicia a animação do spinner"""
        if self.timer is None:
            self.timer = QTimer()
            self.timer.timeout.connect(self.rotate)
            self.timer.start(50)
        self.show()
    
    def stop_animation(self):
        """Para a animação do spinner"""
        if self.timer:
            self.timer.stop()
            self.timer = None
        self.hide()
    
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
    DESIGN CLEAN - SEM BORDAS GROSSAS
    """
    
    clicked = Signal(object)
    copy_requested = Signal(str)
    eye_clicked = Signal()
    
    def __init__(self, network: WifiNetwork, is_selected: bool = False):
        super().__init__()
        self.network = network
        self.is_selected = is_selected
        self.theme = UIThemeManager()
        self.setup_ui()
        self.setup_shadow()
        self.update_style()
    
    def setup_ui(self):
        """Configura a interface do card - CLEAN"""
        self.setFixedHeight(100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)
        
        # Linha superior
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        
        # Ícone WiFi - DINÂMICO
        self.wifi_icon = QLabel()
        quality_color = get_signal_color(self.network.signal_quality)
        icon_pixmap = qta.icon('fa5s.wifi', color=quality_color).pixmap(22, 22)
        self.wifi_icon.setPixmap(icon_pixmap)
        self.wifi_icon.setFixedSize(22, 22)
        top_row.addWidget(self.wifi_icon)
        
        # Nome da rede
        self.name_label = QLabel(self._elide_text(self.network.ssid, 28))
        name_font = QFont()
        name_font.setPointSize(13)
        name_font.setWeight(QFont.Weight.DemiBold)
        self.name_label.setFont(name_font)
        self.name_label.setStyleSheet("color: #0f172a;")
        self.name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_row.addWidget(self.name_label)
        
        # Botão de olho - ÍCONE LIVRE
        self.eye_button = QToolButton()
        self.eye_button.setIcon(qta.icon('fa5s.eye', color='#94a3b8'))
        self.eye_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.eye_button.setFixedSize(26, 26)
        self.eye_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 13px;
            }
            QToolButton:hover {
                background-color: #f1f5f9;
            }
        """)
        self.eye_button.clicked.connect(self.on_eye_clicked)
        self.eye_button.setToolTip("Mostrar senha")
        top_row.addWidget(self.eye_button)
        
        # Botão copiar - ÍCONE LIVRE
        self.copy_button = QToolButton()
        self.copy_button.setIcon(qta.icon('fa5s.copy', color='#94a3b8'))
        self.copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_button.setFixedSize(26, 26)
        self.copy_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 13px;
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
        if not has_password:
            self.eye_button.setIcon(qta.icon('fa5s.eye-slash', color='#cbd5e1'))
            self.copy_button.setIcon(qta.icon('fa5s.copy', color='#cbd5e1'))
        
        layout.addLayout(top_row)
        
        # Linha de badges - ÍCONES LIVRES
        badges_row = QHBoxLayout()
        badges_row.setSpacing(6)
        
        # Badge de autenticação
        auth_text = self._elide_text(self.network.auth, 12)
        self.auth_badge = QLabel(auth_text)
        self.auth_badge.setStyleSheet("""
            QLabel {
                background-color: #f1f5f9;
                color: #475569;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 500;
            }
        """)
        badges_row.addWidget(self.auth_badge)
        
        # Badge de qualidade
        quality_text, quality_color = format_signal_quality(self.network.signal_quality)
        self.quality_badge = QLabel(quality_text)
        self.quality_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {quality_color}15;
                color: {quality_color};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 600;
            }}
        """)
        badges_row.addWidget(self.quality_badge)
        
        # Badges de frequência - ÍCONES
        if self.network.frequencies:
            for freq_info in self.network.frequencies[:1]:  # Só mostra primeira frequência
                freq_badge = self.create_frequency_badge(freq_info)
                badges_row.addWidget(freq_badge)
        
        badges_row.addStretch()
        layout.addLayout(badges_row)
        
        # Tooltip
        self.setToolTip(self._generate_tooltip())
    
    def create_frequency_badge(self, freq_info: FrequencyInfo) -> QLabel:
        """Cria badge de frequência - ÍCONE + TEXTO"""
        colors = {
            "2.4 GHz": {"bg": "#dbeafe", "text": "#1e40af", "icon": "📶"},
            "5 GHz": {"bg": "#ede9fe", "text": "#5b21b6", "icon": "⚡"},
            "6 GHz": {"bg": "#fce7f3", "text": "#9d174d", "icon": "🚀"}
        }
        
        band = freq_info.band or "2.4 GHz"
        color = colors.get(band, colors["2.4 GHz"])
        
        badge = QLabel(f"{color['icon']} {band}")
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {color['bg']};
                color: {color['text']};
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 9px;
                font-weight: 600;
            }}
        """)
        return badge
    
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
        """Sombra suave"""
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(12)
        self.shadow.setColor(QColor(0, 0, 0, 10))
        self.shadow.setOffset(0, 1)
        self.setGraphicsEffect(self.shadow)
    
    def update_style(self):
        """Estilo CLEAN - SEM BORDAS GROSSAS"""
        if self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #f8fafc;
                    border: none;
                    border-radius: 12px;
                }
            """)
            self.shadow.setColor(QColor(37, 99, 235, 20))
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
            self.shadow.setColor(QColor(0, 0, 0, 10))
    
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
            QTimer.singleShot(800, self.restore_copy_icon)
    
    def restore_copy_icon(self):
        has_password = bool(self.network.password)
        if has_password:
            self.copy_button.setIcon(qta.icon('fa5s.copy', color='#94a3b8'))
        else:
            self.copy_button.setIcon(qta.icon('fa5s.copy', color='#cbd5e1'))


class NetworkDetailsWidget(QFrame):
    """
    Widget de detalhes da rede - COMPLETO, CLEAN, COM N/A
    """
    
    def __init__(self):
        super().__init__()
        self.network = None
        self.password_visible = False
        self.real_password = None
        self.setup_ui()
        self.setup_shadow()
    
    def setup_ui(self):
        """Configura a interface - FUNDO BRANCO, SEM BORDAS"""
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: none;
                border-radius: 16px;
            }
        """)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # Título
        title = QLabel("Detalhes da Rede")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        title.setStyleSheet("color: #0f172a;")
        main_layout.addWidget(title)
        
        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: #ffffff;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(20)
        
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
        
        self.show_placeholder()
    
    def setup_shadow(self):
        """Sombra suave"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 8))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def show_placeholder(self):
        """Mostra placeholder quando nenhuma rede selecionada"""
        self.clear_content()
        
        placeholder = QWidget()
        placeholder.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        
        icon = QLabel()
        icon.setPixmap(qta.icon('fa5s.network-wired', color='#cbd5e1').pixmap(48, 48))
        layout.addWidget(icon)
        
        text = QLabel("Selecione uma rede para ver detalhes")
        text.setStyleSheet("color: #94a3b8; font-size: 13px;")
        layout.addWidget(text)
        
        self.scroll_layout.addWidget(placeholder)
    
    def set_network(self, network: WifiNetwork):
        """Carrega dados da rede selecionada"""
        self.network = network
        self.clear_content()
        
        # Coletar informações
        try:
            from core.network_info import NetworkInfoCollector
            from core.frequency import RealFrequencyDetector
            
            self.ip_info = NetworkInfoCollector.get_interface_detailed()
            self.wlan_stats = NetworkInfoCollector.get_wlan_statistics()
            self.freq_detector = RealFrequencyDetector()
            self.frequencies = self.freq_detector.get_network_frequencies(network.ssid)
        except ImportError:
            self.ip_info = {}
            self.wlan_stats = {}
            self.frequencies = []
        
        # Cabeçalho
        self.add_header_section()
        
        # Cards de métricas
        self.add_metrics_row()
        
        # Seções de informações
        self.add_identification_section()
        self.add_radio_section()
        self.add_ip_section()
        self.add_security_section()
        self.add_credentials_section()
        
        self.scroll_layout.addStretch()
    
    def add_header_section(self):
        """Cabeçalho com nome"""
        header = QWidget()
        header.setStyleSheet("background-color: #ffffff;")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 8)
        
        # Nome
        name = QLabel(self.network.ssid)
        name_font = QFont()
        name_font.setPointSize(20)
        name_font.setWeight(QFont.Weight.Bold)
        name.setFont(name_font)
        name.setStyleSheet("color: #0f172a;")
        layout.addWidget(name, 1)
        
        # Badge de qualidade
        quality = self.network.signal_quality
        quality_colors = {
            "Excelente": "#10b981",
            "Bom": "#3b82f6",
            "Regular": "#f59e0b",
            "Fraco": "#ef4444",
            "Desconhecido": "#94a3b8"
        }
        color = quality_colors.get(quality, "#94a3b8")
        
        badge = QLabel(quality)
        badge.setStyleSheet(f"""
            background-color: {color}15;
            color: {color};
            border-radius: 16px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 600;
        """)
        layout.addWidget(badge)
        
        self.scroll_layout.addWidget(header)
    
    def add_metrics_row(self):
        """Adiciona cards de métricas (RSSI, Sinal, Canal, Banda)"""
        metrics_widget = QWidget()
        metrics_widget.setStyleSheet("background-color: #ffffff;")
        
        layout = QHBoxLayout(metrics_widget)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(10)
        
        # RSSI
        rssi = getattr(self.network, 'rssi_dbm', None)
        if rssi:
            rssi_value = rssi.replace(" dBm", "") if isinstance(rssi, str) else str(rssi)
            rssi_color = self.get_rssi_color(rssi_value)
            rssi_card = self.create_metric_card("RSSI", rssi_value, "dBm", rssi_color)
            layout.addWidget(rssi_card)
        
        # Sinal
        signal = getattr(self.network, 'signal_percent', None) or self.wlan_stats.get('signal', None)
        if signal:
            signal_value = signal.replace("%", "") if isinstance(signal, str) else str(signal)
            signal_color = self.get_signal_color(int(signal_value) if signal_value.isdigit() else 0)
            signal_card = self.create_metric_card("Sinal", signal_value, "%", signal_color)
            layout.addWidget(signal_card)
        
        # Canal
        channel = getattr(self.network, 'channel', None) or self.wlan_stats.get('channel', None)
        if channel:
            channel_card = self.create_metric_card("Canal", str(channel), "", "#8b5cf6")
            layout.addWidget(channel_card)
        
        # Banda
        if self.frequencies and len(self.frequencies) > 0:
            band = self.frequencies[0].band if hasattr(self.frequencies[0], 'band') else "2.4 GHz"
            band_value = band.replace(" GHz", "")
            band_color = "#3b82f6" if "2.4" in band else "#8b5cf6" if "5" in band else "#ec4899"
            band_card = self.create_metric_card("Banda", band_value, "GHz", band_color)
            layout.addWidget(band_card)
        
        layout.addStretch()
        self.scroll_layout.addWidget(metrics_widget)
    
    def create_metric_card(self, label: str, value: str, unit: str, color: str) -> QFrame:
        """Cria card de métrica - SEM BORDAS"""
        card = QFrame()
        card.setMinimumWidth(80)
        card.setMaximumWidth(100)
        card.setStyleSheet("background-color: #f8fafc; border-radius: 10px;")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 6)
        layout.setSpacing(2)
        
        # Valor
        value_layout = QHBoxLayout()
        value_layout.setSpacing(2)
        value_layout.setAlignment(Qt.AlignLeft)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 700;")
        value_layout.addWidget(value_label)
        
        if unit and value != "—":
            unit_label = QLabel(unit)
            unit_label.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: 500; margin-top: 4px;")
            value_layout.addWidget(unit_label)
        
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        # Label
        label_label = QLabel(label)
        label_label.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 600;")
        layout.addWidget(label_label)
        
        return card
    
    def get_rssi_color(self, rssi: str) -> str:
        """Retorna cor baseada no RSSI"""
        try:
            val = int(rssi)
            if val > -50:
                return "#10b981"
            elif val > -65:
                return "#3b82f6"
            elif val > -75:
                return "#f59e0b"
            else:
                return "#ef4444"
        except:
            return "#64748b"
    
    def get_signal_color(self, percent: int) -> str:
        """Retorna cor baseada na porcentagem do sinal"""
        if percent >= 80:
            return "#10b981"
        elif percent >= 60:
            return "#3b82f6"
        elif percent >= 40:
            return "#f59e0b"
        else:
            return "#ef4444"
    
    def add_identification_section(self):
        """Seção de identificação"""
        section = self.create_section("IDENTIFICAÇÃO")
        
        self.add_info_row(section, "SSID", self.network.ssid)
        self.add_info_row(section, "BSSID", self._na(getattr(self.network, 'bssid', None)))
        self.add_info_row(section, "Interface", self._na(getattr(self.network, 'interface_name', None) or self.ip_info.get('name')))
        self.add_info_row(section, "MAC", self._na(getattr(self.network, 'interface_mac', None) or self.ip_info.get('mac')))
        self.add_info_row(section, "Oculto", self._bool_na(getattr(self.network, 'hidden', None)))
        
        self.scroll_layout.addWidget(section)
    
    def add_radio_section(self):
        """Seção de rádio e sinal"""
        section = self.create_section("RÁDIO E SINAL")
        
        freq = getattr(self.network, 'frequency_mhz', None)
        self.add_info_row(section, "Frequência", self._na(f"{freq} MHz" if freq else None))
        
        speed = getattr(self.network, 'link_speed', None) or self.wlan_stats.get('link_speed')
        self.add_info_row(section, "Velocidade", self._na(speed))
        
        phy = getattr(self.network, 'phy_type', None) or self.wlan_stats.get('phy')
        self.add_info_row(section, "PHY", self._na(phy))
        
        width = getattr(self.network, 'channel_width', None)
        self.add_info_row(section, "Largura", self._na(f"{width} MHz" if width else None))
        
        self.scroll_layout.addWidget(section)
    
    def add_ip_section(self):
        """Seção de configuração IP"""
        section = self.create_section("CONFIGURAÇÃO IP")
        
        self.add_info_row(section, "IPv4", self._na(self.ip_info.get('ipv4')))
        self.add_info_row(section, "Gateway", self._na(self.ip_info.get('gateway')))
        self.add_info_row(section, "DNS", self._na(self.ip_info.get('dns')))
        self.add_info_row(section, "DHCP", self._na(self.ip_info.get('dhcp')))
        
        self.scroll_layout.addWidget(section)
    
    def add_security_section(self):
        """Seção de segurança"""
        section = self.create_section("SEGURANÇA")
        
        self.add_info_row(section, "Autenticação", self._na(self.network.auth))
        self.add_info_row(section, "Criptografia", self._na(self.network.encryption))
        self.add_info_row(section, "AKM", self._na(getattr(self.network, 'akm', None)))
        self.add_info_row(section, "PMF", self._na(getattr(self.network, 'pmf', None)))
        
        # Análise de risco
        try:
            from core.security import SecurityAnalyzer
            analysis = SecurityAnalyzer.analyze_network(self.network)
            
            risk_row = QWidget()
            risk_row.setStyleSheet("background-color: #ffffff;")
            risk_layout = QHBoxLayout(risk_row)
            risk_layout.setContentsMargins(0, 8, 0, 4)
            
            risk_label = QLabel("Nível de risco:")
            risk_label.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500;")
            risk_label.setFixedWidth(100)
            risk_layout.addWidget(risk_label)
            
            risk_color = {
                "Baixo": "#10b981",
                "Médio": "#f59e0b",
                "Alto": "#ef4444"
            }.get(analysis['risk_level'], "#94a3b8")
            
            risk_value = QLabel(f"{analysis['risk_level']} ({analysis['risk_score']}/100)")
            risk_value.setStyleSheet(f"color: {risk_color}; font-size: 12px; font-weight: 600;")
            risk_layout.addWidget(risk_value, 1)
            
            section.layout().addWidget(risk_row)
        except ImportError:
            pass
        
        self.scroll_layout.addWidget(section)
    
    def add_credentials_section(self):
        """Seção de credenciais - CLEAN"""
        if not self.network.password and not getattr(self.network, 'password_hex', None):
            return
        
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: none;
                border-radius: 12px;
                margin-top: 8px;
            }
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)
        
        # Título
        title = QLabel("🔐 CREDENCIAIS")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #0369a1;")
        layout.addWidget(title)
        
        # Senha
        if self.network.password:
            pass_row = QHBoxLayout()
            
            pass_label = QLabel("Senha:")
            pass_label.setStyleSheet("color: #0f172a; font-size: 13px; font-weight: 600;")
            pass_label.setFixedWidth(70)
            pass_row.addWidget(pass_label)
            
            self.password_value = QLabel("********")
            self.password_value.setStyleSheet("""
                color: #0f172a;
                font-size: 13px;
                font-weight: 500;
                font-family: monospace;
            """)
            self.password_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            pass_row.addWidget(self.password_value, 1)
            
            # Botões
            self.toggle_btn = QToolButton()
            self.toggle_btn.setIcon(qta.icon('fa5s.eye', color='#64748b'))
            self.toggle_btn.setCursor(Qt.PointingHandCursor)
            self.toggle_btn.setFixedSize(28, 28)
            self.toggle_btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 14px;
                }
                QToolButton:hover {
                    background-color: #e2e8f0;
                }
            """)
            self.toggle_btn.clicked.connect(self.toggle_password)
            pass_row.addWidget(self.toggle_btn)
            
            self.copy_btn = QToolButton()
            self.copy_btn.setIcon(qta.icon('fa5s.copy', color='#64748b'))
            self.copy_btn.setCursor(Qt.PointingHandCursor)
            self.copy_btn.setFixedSize(28, 28)
            self.copy_btn.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 14px;
                }
                QToolButton:hover {
                    background-color: #e2e8f0;
                }
            """)
            self.copy_btn.clicked.connect(self.copy_password)
            pass_row.addWidget(self.copy_btn)
            
            self.real_password = self.network.password
            layout.addLayout(pass_row)
        
        # HEX
        hex_val = getattr(self.network, 'password_hex', None)
        if hex_val:
            hex_row = QHBoxLayout()
            
            hex_label = QLabel("HEX:")
            hex_label.setStyleSheet("color: #0f172a; font-size: 13px; font-weight: 600;")
            hex_label.setFixedWidth(70)
            hex_row.addWidget(hex_label)
            
            if hex_val.startswith('[Hex'):
                hex_val = hex_val.replace('[Hex ', '').replace(']', '')
            
            hex_value = QLabel(hex_val[:40] + ("..." if len(hex_val) > 40 else ""))
            hex_value.setStyleSheet("""
                color: #0369a1;
                font-size: 12px;
                font-family: monospace;
                font-weight: 500;
            """)
            hex_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            hex_row.addWidget(hex_value, 1)
            
            layout.addLayout(hex_row)
        
        self.scroll_layout.addWidget(section)
    
    def create_section(self, title: str) -> QWidget:
        """Cria uma seção - SEM BORDAS"""
        section = QWidget()
        section.setStyleSheet("background-color: #ffffff;")
        
        layout = QVBoxLayout(section)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0f172a;")
        layout.addWidget(title_label)
        
        # Linha separadora sutil
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #e2e8f0; max-height: 1px;")
        layout.addWidget(line)
        
        return section
    
    def add_info_row(self, section: QWidget, label: str, value: str):
        """Adiciona linha de informação com formatação"""
        row = QHBoxLayout()
        row.setContentsMargins(0, 4, 0, 4)
        
        label_widget = QLabel(f"{label}:")
        label_widget.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500;")
        label_widget.setFixedWidth(90)
        row.addWidget(label_widget)
        
        value_widget = QLabel(value)
        value_widget.setStyleSheet("color: #0f172a; font-size: 12px; font-weight: 500;")
        value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
        value_widget.setWordWrap(True)
        row.addWidget(value_widget, 1)
        
        section.layout().addLayout(row)
    
    def _na(self, value) -> str:
        """Converte valor para N/A se N/A"""
        if value is None or value == "" or value == "N/A" or value == "None":
            return "N/A"
        return str(value)
    
    def _bool_na(self, value) -> str:
        """Converte valor booleano para Sim/Não ou N/A"""
        if value is None:
            return "N/A"
        return "Sim" if value else "Não"
    
    def toggle_password(self):
        """Alterna visibilidade da senha"""
        if self.real_password:
            self.password_visible = not self.password_visible
            if self.password_visible:
                self.password_value.setText(self.real_password)
                self.toggle_btn.setIcon(qta.icon('fa5s.eye-slash', color='#2563eb'))
            else:
                self.password_value.setText("********")
                self.toggle_btn.setIcon(qta.icon('fa5s.eye', color='#64748b'))
    
    def copy_password(self):
        """Copia senha para área de transferência"""
        if self.real_password:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.real_password)
            self.copy_btn.setIcon(qta.icon('fa5s.check', color='#10b981'))
            QTimer.singleShot(800, self.restore_copy_icon)
    
    def restore_copy_icon(self):
        """Restaura ícone de cópia"""
        self.copy_btn.setIcon(qta.icon('fa5s.copy', color='#64748b'))
    
    def toggle_password_visibility(self):
        """Alias para compatibilidade"""
        self.toggle_password()
    
    def clear_content(self):
        """Limpa todo o conteúdo do scroll"""
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()