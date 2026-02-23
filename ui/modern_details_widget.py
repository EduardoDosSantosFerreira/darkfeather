"""
Widget de detalhes da rede - Layout otimizado para maior largura
"""

import subprocess
import re
from typing import Dict, Optional, List
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QApplication,
    QSizePolicy,
    QToolButton,
    QScrollArea,
    QGraphicsDropShadowEffect,
    QGridLayout,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QPixmap
import qtawesome as qta

from core.scanner import WifiNetwork
from core.frequency import RealFrequencyDetector


class ModernDetailsWidget(QFrame):
    """
    Widget de detalhes da rede - Layout otimizado para maior largura
    """

    def __init__(self):
        super().__init__()
        self.network = None
        self.password_visible = False
        self.real_password = None
        self.freq_detector = RealFrequencyDetector()
        self.real_data = {}
        self.setup_ui()
        self.apply_style()

    def apply_style(self):
        """Aplica estilos limpos e com bom contraste"""
        self.setStyleSheet(
            """
            ModernDetailsWidget {
                background-color: #ffffff;
                border-radius: 16px;
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
            .section-title {
                font-size: 15px;
                font-weight: 700;
                color: #000000;
                margin-top: 8px;
                margin-bottom: 8px;
            }
            .info-label {
                color: #000000;
                font-size: 13px;
                font-weight: 500;
            }
            .info-value {
                color: #000000;
                font-size: 13px;
                font-weight: 600;
            }
            .metric-container {
                background-color: #f8fafc;
                border-radius: 10px;
                padding: 8px;
                min-width: 80px;
            }
            .metric-value {
                font-size: 24px;
                font-weight: 700;
            }
            .metric-unit {
                font-size: 12px;
                margin-left: 2px;
            }
            .metric-label {
                color: #000000;
                font-size: 12px;
                font-weight: 600;
                margin-top: 2px;
            }
        """
        )

        # Sombra muito suave
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 5))
        shadow.setOffset(0, 1)
        self.setGraphicsEffect(shadow)

    def setup_ui(self):
        """Configura a interface"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Título
        title = QLabel("Detalhes da Rede")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        title.setStyleSheet("color: #000000;")
        main_layout.addWidget(title)

        # Área de scroll
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
        """Mostra placeholder simples"""
        self.clear_content()

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        icon = QLabel()
        icon.setPixmap(qta.icon("fa5s.network-wired", color="#cbd5e1").pixmap(48, 48))
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        text = QLabel("Selecione uma rede para ver detalhes")
        text.setStyleSheet("color: #000000; font-size: 14px; font-weight: 500;")
        text.setAlignment(Qt.AlignCenter)
        layout.addWidget(text)

        self.scroll_layout.addWidget(container)
        self.scroll_layout.addStretch()

    def set_network(self, network: WifiNetwork):
        """Carrega dados da rede"""
        self.network = network
        self.clear_content()

        # Coletar dados
        self.real_data = self.collect_all_data()

        # Construir interface
        self.add_network_header()
        self.add_metrics_row()
        self.add_identification_section()
        self.add_radio_section()
        self.add_ip_section()
        self.add_security_section()
        self.add_credentials_section()

        self.scroll_layout.addStretch()

    def collect_all_data(self) -> Dict:
        """Coleta todos os dados"""
        return {
            **self.get_basic_info(),
            **self.get_interface_info(),
            **self.get_connection_info(),
            **self.get_ip_info(),
            **self.get_security_info(),
            **self.get_frequency_info(),
        }

    def add_network_header(self):
        """Adiciona cabeçalho com nome e qualidade"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 8)

        # Nome da rede
        name_label = QLabel(self.real_data.get("ssid", "Rede"))
        name_font = QFont()
        name_font.setPointSize(20)
        name_font.setWeight(QFont.Weight.Bold)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #000000;")
        layout.addWidget(name_label)

        layout.addStretch()

        # Badge de qualidade
        quality = self.real_data.get("signal_quality", "Desconhecido")
        quality_colors = {
            "Excelente": "#059669",
            "Bom": "#2563eb",
            "Regular": "#d97706",
            "Fraco": "#dc2626",
            "Desconhecido": "#64748b",
        }
        color = quality_colors.get(quality, "#64748b")

        quality_badge = QLabel(f"  {quality}  ")
        quality_badge.setStyleSheet(
            f"""
            background-color: {color}15;
            color: {color};
            border-radius: 16px;
            padding: 6px 14px;
            font-size: 13px;
            font-weight: 700;
        """
        )
        layout.addWidget(quality_badge)

        self.scroll_layout.addWidget(header)

    def add_metrics_row(self):
        """Adiciona linha de métricas com cards visíveis"""
        metrics_widget = QWidget()
        
        layout = QHBoxLayout(metrics_widget)
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setSpacing(12)

        # RSSI
        rssi = self.real_data.get("rssi_dbm", "N/A")
        rssi_value = rssi.replace(" dBm", "") if rssi != "N/A" else "—"
        rssi_color = self.get_rssi_color(rssi_value)
        rssi_card = self.create_metric_card("RSSI", rssi_value, "dBm", rssi_color)
        layout.addWidget(rssi_card)

        # Sinal
        signal = self.real_data.get("signal_percent", "N/A")
        signal_value = signal.replace("%", "") if signal != "N/A" else "—"
        signal_color = self.get_signal_color(
            int(signal_value) if signal_value.isdigit() else 0
        )
        signal_card = self.create_metric_card("Sinal", signal_value, "%", signal_color)
        layout.addWidget(signal_card)

        # Canal
        channel = self.real_data.get("channel", "N/A")
        channel_value = str(channel) if channel != "N/A" else "—"
        channel_card = self.create_metric_card("Canal", channel_value, "", "#2563eb")
        layout.addWidget(channel_card)

        # Banda
        band = self.real_data.get("band", "N/A")
        band_value = band.replace(" GHz", "") if band != "N/A" else "—"
        band_color = (
            "#2563eb" if "2.4" in band else "#7c3aed" if "5" in band else "#db2777"
        )
        band_card = self.create_metric_card("Banda", band_value, "GHz", band_color)
        layout.addWidget(band_card)

        layout.addStretch()
        self.scroll_layout.addWidget(metrics_widget)

    def create_metric_card(self, label: str, value: str, unit: str, color: str) -> QFrame:
        """Cria um card de métrica com fundo e texto bem visíveis"""
        card = QFrame()
        card.setMinimumWidth(90)
        card.setMaximumWidth(110)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        # Linha do valor
        value_layout = QHBoxLayout()
        value_layout.setSpacing(2)
        value_layout.setAlignment(Qt.AlignLeft)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 700;")
        value_layout.addWidget(value_label)

        if unit and value != "—":
            unit_label = QLabel(unit)
            unit_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 500; margin-top: 4px;")
            value_layout.addWidget(unit_label)

        value_layout.addStretch()
        layout.addLayout(value_layout)

        # Label da métrica
        label_label = QLabel(label)
        label_label.setStyleSheet("color: #000000; font-size: 12px; font-weight: 600;")
        layout.addWidget(label_label)

        return card

    def add_identification_section(self):
        """Adiciona seção de identificação"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(8)

        # Título
        title = QLabel("Identificação")
        title.setProperty("class", "section-title")
        layout.addWidget(title)

        # Grid 2 colunas
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(8)

        items = [
            (0, 0, "SSID:", self.real_data.get("ssid", "N/A")),
            (0, 1, "BSSID:", self.format_bssid(self.real_data.get("bssid", "N/A"))),
            (1, 0, "Interface:", self.real_data.get("interface_name", "N/A")),
            (1, 1, "MAC:", self.format_mac(self.real_data.get("interface_mac", "N/A"))),
        ]

        for row, col, key, value in items:
            key_label = QLabel(key)
            key_label.setProperty("class", "info-label")
            grid.addWidget(key_label, row, col * 2, Qt.AlignRight)

            display_value = (
                value if value != "N/A" and value != "Não disponível" else "—"
            )
            value_label = QLabel(display_value)
            value_label.setProperty("class", "info-value")
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            if value != "N/A" and len(value) > 25:
                value_label.setToolTip(value)
            grid.addWidget(value_label, row, col * 2 + 1, Qt.AlignLeft)

        layout.addLayout(grid)
        self.scroll_layout.addWidget(section)

    def add_radio_section(self):
        """Adiciona seção de rádio"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(8)

        # Título
        title = QLabel("Rádio e Sinal")
        title.setProperty("class", "section-title")
        layout.addWidget(title)

        # Grid 2 colunas
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(8)

        freq = self.real_data.get("frequency_mhz", "N/A")
        freq_display = (
            f"{freq} MHz" if freq != "N/A" and freq != "Não disponível" else "—"
        )

        items = [
            (0, 0, "Frequência:", freq_display),
            (
                0,
                1,
                "PHY:",
                (
                    self.real_data.get("phy_type", "N/A")
                    if self.real_data.get("phy_type") != "Não disponível"
                    else "—"
                ),
            ),
            (
                1,
                0,
                "Velocidade:",
                (
                    self.real_data.get("link_speed", "N/A")
                    if self.real_data.get("link_speed") != "Não disponível"
                    else "—"
                ),
            ),
            (
                1,
                1,
                "Largura:",
                self.format_channel_width(self.real_data.get("channel_width", "N/A")),
            ),
        ]

        for row, col, key, value in items:
            key_label = QLabel(key)
            key_label.setProperty("class", "info-label")
            grid.addWidget(key_label, row, col * 2, Qt.AlignRight)

            display_value = (
                value if value != "N/A" and value != "Não disponível" else "—"
            )
            value_label = QLabel(display_value)
            value_label.setProperty("class", "info-value")
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            grid.addWidget(value_label, row, col * 2 + 1, Qt.AlignLeft)

        layout.addLayout(grid)
        self.scroll_layout.addWidget(section)

    def add_ip_section(self):
        """Adiciona seção IP"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(8)

        # Título
        title = QLabel("Configuração IP")
        title.setProperty("class", "section-title")
        layout.addWidget(title)

        # Grid 2 colunas
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(8)

        # Determinar status do DHCP
        dhcp_status = self.real_data.get("dhcp_enabled", "N/A")
        dhcp_display = (
            "Sim" if dhcp_status == "Sim" else "Não" if dhcp_status == "Não" else "—"
        )

        items = [
            (0, 0, "IPv4:", self.real_data.get("ipv4", "N/A")),
            (0, 1, "Gateway:", self.real_data.get("gateway", "N/A")),
            (1, 0, "DNS:", self.real_data.get("dns_servers", "N/A")),
            (1, 1, "DHCP:", dhcp_display),
        ]

        for row, col, key, value in items:
            key_label = QLabel(key)
            key_label.setProperty("class", "info-label")
            grid.addWidget(key_label, row, col * 2, Qt.AlignRight)

            display_value = (
                value if value != "N/A" and value != "Não disponível" else "—"
            )
            if len(display_value) > 20:
                display_value = display_value[:18] + "…"

            value_label = QLabel(display_value)
            value_label.setProperty("class", "info-value")
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            if value != "N/A" and len(value) > 20:
                value_label.setToolTip(value)
            grid.addWidget(value_label, row, col * 2 + 1, Qt.AlignLeft)

        layout.addLayout(grid)
        self.scroll_layout.addWidget(section)

    def add_security_section(self):
        """Adiciona seção de segurança"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(8)

        # Título
        title = QLabel("Segurança")
        title.setProperty("class", "section-title")
        layout.addWidget(title)

        # Grid 2 colunas
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(8)

        items = [
            (0, 0, "Autenticação:", self.real_data.get("auth", "N/A")),
            (0, 1, "Criptografia:", self.real_data.get("encryption", "N/A")),
        ]

        row = 1
        if self.real_data.get("akm") and self.real_data.get("akm") != "Não disponível":
            items.append((row, 0, "AKM:", self.real_data.get("akm")))
            row += 1

        if self.real_data.get("pmf") and self.real_data.get("pmf") != "Não disponível":
            items.append((row, 0, "PMF:", self.real_data.get("pmf")))

        for row, col, key, value in items:
            key_label = QLabel(key)
            key_label.setProperty("class", "info-label")
            grid.addWidget(key_label, row, col * 2, Qt.AlignRight)

            display_value = (
                value if value != "N/A" and value != "Não disponível" else "—"
            )
            value_label = QLabel(display_value)
            value_label.setProperty("class", "info-value")
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            grid.addWidget(value_label, row, col * 2 + 1, Qt.AlignLeft)

        layout.addLayout(grid)
        self.scroll_layout.addWidget(section)

    def add_credentials_section(self):
        """Adiciona seção de credenciais"""
        if not self.real_data.get("password") and not self.real_data.get(
            "password_hex"
        ):
            return

        section = QFrame()
        section.setStyleSheet(
            """
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 8px;
            }
        """
        )

        layout = QVBoxLayout(section)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Título
        title = QLabel("Credenciais")
        title_font = QFont()
        title_font.setPointSize(15)
        title_font.setWeight(QFont.Weight.Medium)
        title.setFont(title_font)
        title.setStyleSheet("color: #000000;")
        layout.addWidget(title)

        # Linha da senha
        password_row = QHBoxLayout()
        password_row.setSpacing(12)

        # Label "Senha"
        pass_label = QLabel("Senha:")
        pass_label.setStyleSheet("color: #000000; font-size: 13px; font-weight: 600;")
        pass_label.setFixedWidth(60)
        password_row.addWidget(pass_label)

        # Valor da senha
        self.password_value = QLabel("********")
        self.password_value.setStyleSheet(
            """
            color: #000000;
            font-size: 13px;
            font-weight: 500;
            font-family: monospace;
        """
        )
        self.password_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        password_row.addWidget(self.password_value, 1)

        # Botões
        self.toggle_btn = QToolButton()
        self.toggle_btn.setIcon(qta.icon("fa5s.eye", color="#64748b"))
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.setStyleSheet(
            """
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 16px;
            }
            QToolButton:hover {
                background-color: #e2e8f0;
            }
        """
        )
        self.toggle_btn.clicked.connect(self.toggle_password)
        password_row.addWidget(self.toggle_btn)

        self.copy_btn = QToolButton()
        self.copy_btn.setIcon(qta.icon("fa5s.copy", color="#64748b"))
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.setFixedSize(32, 32)
        self.copy_btn.setStyleSheet(
            """
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 16px;
            }
            QToolButton:hover {
                background-color: #e2e8f0;
            }
        """
        )
        self.copy_btn.clicked.connect(self.copy_password)
        password_row.addWidget(self.copy_btn)

        # Habilitar/desabilitar
        has_password = bool(self.real_data.get("password"))
        self.toggle_btn.setEnabled(has_password)
        self.copy_btn.setEnabled(has_password)
        self.real_password = self.real_data.get("password")

        layout.addLayout(password_row)

        # HEX
        if self.real_data.get("password_hex"):
            hex_row = QHBoxLayout()
            hex_row.setSpacing(12)

            hex_label = QLabel("HEX:")
            hex_label.setStyleSheet(
                "color: #000000; font-size: 13px; font-weight: 600;"
            )
            hex_label.setFixedWidth(60)
            hex_row.addWidget(hex_label)

            hex_val = self.real_data.get("password_hex", "")
            if len(hex_val) > 45:
                hex_val = hex_val[:42] + "…"

            hex_value = QLabel(hex_val)
            hex_value.setStyleSheet(
                """
                color: #2563eb;
                font-size: 12px;
                font-family: monospace;
                font-weight: 500;
            """
            )
            hex_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            hex_row.addWidget(hex_value, 1)

            layout.addLayout(hex_row)

        self.scroll_layout.addWidget(section)

    # Métodos utilitários
    def get_rssi_color(self, rssi: str) -> str:
        try:
            val = int(rssi)
            if val > -50:
                return "#059669"
            elif val > -65:
                return "#2563eb"
            elif val > -75:
                return "#d97706"
            else:
                return "#dc2626"
        except:
            return "#64748b"

    def get_signal_color(self, percent: int) -> str:
        if percent >= 80:
            return "#059669"
        elif percent >= 60:
            return "#2563eb"
        elif percent >= 40:
            return "#d97706"
        else:
            return "#dc2626"

    def format_bssid(self, bssid: str) -> str:
        if bssid and len(bssid) >= 17:
            return bssid
        return "—"

    def format_mac(self, mac: str) -> str:
        if mac and len(mac) >= 17:
            return mac
        return "—"

    def format_channel_width(self, width) -> str:
        if width and width != "N/A" and width != "Não disponível":
            return f"{width} MHz"
        return "—"

    def clear_content(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def toggle_password(self):
        """Alterna visibilidade da senha"""
        if self.real_password:
            self.password_visible = not self.password_visible
            if self.password_visible:
                self.password_value.setText(self.real_password)
                self.toggle_btn.setIcon(qta.icon("fa5s.eye-slash", color="#2563eb"))
            else:
                self.password_value.setText("********")
                self.toggle_btn.setIcon(qta.icon("fa5s.eye", color="#64748b"))

    def toggle_password_visibility(self):
        """Método alias para compatibilidade"""
        self.toggle_password()

    def copy_password(self):
        if self.real_password:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.real_password)
            self.copy_btn.setIcon(qta.icon("fa5s.check", color="#059669"))
            QTimer.singleShot(800, self.restore_copy_icon)

    def restore_copy_icon(self):
        self.copy_btn.setIcon(qta.icon("fa5s.copy", color="#64748b"))

    # Métodos de coleta de dados
    def get_basic_info(self) -> Dict:
        return {
            "ssid": self.network.ssid if self.network else "N/A",
            "auth": self.network.auth if self.network else "N/A",
            "encryption": self.network.encryption if self.network else "N/A",
            "signal_quality": self.network.signal_quality if self.network else "N/A",
            "password": (
                self.network.password
                if self.network and self.network.password
                else None
            ),
            "password_hex": (
                self.network.password_hex
                if self.network and self.network.password_hex
                else None
            ),
            "last_connection": (
                self.network.last_connection
                if self.network and self.network.last_connection
                else None
            ),
        }

    def get_interface_info(self) -> Dict:
        data = {
            "interface_name": "Não disponível",
            "interface_mac": "Não disponível",
            "interface_status": "Não disponível",
            "interface_guid": "Não disponível",
        }
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if result.returncode == 0:
                output = result.stdout
                if "não há" not in output.lower():
                    name_match = re.search(
                        r"Nome\s*:\s*(.+)$", output, re.MULTILINE | re.IGNORECASE
                    )
                    if name_match:
                        data["interface_name"] = name_match.group(1).strip()
                    mac_match = re.search(
                        r"Endereço físico\s*:\s*([0-9A-Fa-f:-]+)",
                        output,
                        re.MULTILINE | re.IGNORECASE,
                    )
                    if mac_match:
                        data["interface_mac"] = mac_match.group(1).strip().upper()
                    state_match = re.search(
                        r"Estado\s*:\s*(.+)$", output, re.MULTILINE | re.IGNORECASE
                    )
                    if state_match:
                        data["interface_status"] = state_match.group(1).strip()
                    guid_match = re.search(
                        r"GUID do perfil\s*:\s*({[0-9A-F-]+})",
                        output,
                        re.MULTILINE | re.IGNORECASE,
                    )
                    if guid_match:
                        data["interface_guid"] = guid_match.group(1).strip()
        except:
            pass
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
            "phy_type": "Não disponível",
            "channel_width": "Não disponível",
        }
        if not self.network:
            return data
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
            if result.returncode == 0:
                output = result.stdout
                current_ssid_match = re.search(
                    r"SSID\s*:\s*(.+)$", output, re.MULTILINE | re.IGNORECASE
                )
                current_ssid = (
                    current_ssid_match.group(1).strip() if current_ssid_match else ""
                )
                if current_ssid.lower() == self.network.ssid.lower():
                    bssid_match = re.search(
                        r"BSSID\s*:\s*([0-9A-Fa-f:-]+)",
                        output,
                        re.MULTILINE | re.IGNORECASE,
                    )
                    if bssid_match:
                        data["bssid"] = bssid_match.group(1).strip().upper()
                    channel_match = re.search(
                        r"Canal\s*:\s*(\d+)", output, re.MULTILINE | re.IGNORECASE
                    )
                    if channel_match:
                        channel = int(channel_match.group(1))
                        data["channel"] = str(channel)
                        if 1 <= channel <= 14:
                            data["band"] = "2.4 GHz"
                            data["frequency_mhz"] = (
                                str(2412 + (channel - 1) * 5)
                                if channel <= 11
                                else "2484"
                            )
                        elif 36 <= channel <= 165:
                            data["band"] = "5 GHz"
                            freq_map = {
                                36: 5180,
                                40: 5200,
                                44: 5220,
                                48: 5240,
                                52: 5260,
                                56: 5280,
                                60: 5300,
                                64: 5320,
                                100: 5500,
                                104: 5520,
                                108: 5540,
                                112: 5560,
                                116: 5580,
                                120: 5600,
                                124: 5620,
                                128: 5640,
                                132: 5660,
                                136: 5680,
                                140: 5700,
                                144: 5720,
                                149: 5745,
                                153: 5765,
                                157: 5785,
                                161: 5805,
                                165: 5825,
                            }
                            data["frequency_mhz"] = str(freq_map.get(channel, "?"))
                        else:
                            data["band"] = "6 GHz"
                    rssi_match = re.search(
                        r"RSSI\s*:\s*(-?\d+)", output, re.MULTILINE | re.IGNORECASE
                    )
                    if rssi_match:
                        rssi = int(rssi_match.group(1))
                        data["rssi_dbm"] = f"{rssi} dBm"
                        percent = max(0, min(100, int((rssi + 90) * 100 / 60)))
                        data["signal_percent"] = f"{percent}%"
                    speed_match = re.search(
                        r"Velocidade de (?:transmissão|recebimento)[^:]*:\s*(\d+[.,]?\d*)\s*\(?[Mm]bps\)?",
                        output,
                        re.MULTILINE | re.IGNORECASE,
                    )
                    if speed_match:
                        data["link_speed"] = (
                            speed_match.group(1).replace(",", ".") + " Mbps"
                        )
                    phy_match = re.search(
                        r"Tipo de rádio\s*:\s*(.+)$",
                        output,
                        re.MULTILINE | re.IGNORECASE,
                    )
                    if phy_match:
                        data["phy_type"] = phy_match.group(1).strip()
        except:
            pass
        return data

    def get_ip_info(self) -> Dict:
        data = {
            "ipv4": "Não disponível",
            "ipv6": "Não disponível",
            "subnet_mask": "Não disponível",
            "gateway": "Não disponível",
            "dns_servers": "Não disponível",
            "dhcp_enabled": "Não disponível",
        }
        try:
            result = subprocess.run(
                ["ipconfig", "/all"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
            if result.returncode == 0:
                output = result.stdout
                sections = re.split(r"\r?\n\r?\n", output)
                for section in sections:
                    if (
                        "wi-fi" in section.lower()
                        or "wireless" in section.lower()
                        or "wlan" in section.lower()
                    ):
                        dhcp_match = re.search(
                            r"DHCP (?:ativado|habilitado)[ .]*:?\s*(.+)",
                            section,
                            re.IGNORECASE,
                        )
                        if dhcp_match:
                            data["dhcp_enabled"] = (
                                "Sim" if "sim" in dhcp_match.group(1).lower() else "Não"
                            )
                        ip_match = re.search(
                            r"Endereço IPv4[ .]*:?\s*([0-9.]+)", section, re.IGNORECASE
                        )
                        if ip_match:
                            data["ipv4"] = ip_match.group(1)
                        ip6_match = re.search(
                            r"Endereço IPv6[ .]*:?\s*([0-9a-f:]+)",
                            section,
                            re.IGNORECASE,
                        )
                        if ip6_match:
                            data["ipv6"] = ip6_match.group(1)
                        mask_match = re.search(
                            r"Máscara de sub-rede[ .]*:?\s*([0-9.]+)",
                            section,
                            re.IGNORECASE,
                        )
                        if mask_match:
                            data["subnet_mask"] = mask_match.group(1)
                        gw_match = re.search(
                            r"Gateway padrão[ .]*:?\s*([0-9.]+)", section, re.IGNORECASE
                        )
                        if gw_match:
                            data["gateway"] = gw_match.group(1)
                        dns_list = []
                        dns_matches = re.findall(
                            r"Servidores? DNS[ .]*:?\s*([0-9.]+)",
                            section,
                            re.IGNORECASE,
                        )
                        for dns in dns_matches[:3]:
                            dns_list.append(dns)
                        if dns_list:
                            data["dns_servers"] = ", ".join(dns_list)
                        break
        except:
            pass
        return data

    def get_security_info(self) -> Dict:
        data = {
            "akm": "Não disponível",
            "pmf": "Não disponível",
            "wps": "Não disponível",
            "hidden": "Não disponível",
        }
        if not self.network:
            return data
        try:
            result = subprocess.run(
                [
                    "netsh",
                    "wlan",
                    "show",
                    "profile",
                    f"name={self.network.ssid}",
                    "key=clear",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
            if result.returncode == 0:
                output = result.stdout
                akm_match = re.search(
                    r"Gerenciamento de chaves\s*:\s*(.+)$",
                    output,
                    re.MULTILINE | re.IGNORECASE,
                )
                if akm_match:
                    data["akm"] = akm_match.group(1).strip()
                pmf_match = re.search(
                    r"PMF\s*:\s*(.+)$", output, re.MULTILINE | re.IGNORECASE
                )
                if pmf_match:
                    data["pmf"] = pmf_match.group(1).strip()
                wps_match = re.search(
                    r"WPS\s*:\s*(.+)$", output, re.MULTILINE | re.IGNORECASE
                )
                if wps_match:
                    data["wps"] = wps_match.group(1).strip()
                hidden_match = re.search(
                    r"SSID\s+oculto\s*:\s*(.+)$", output, re.MULTILINE | re.IGNORECASE
                )
                if hidden_match:
                    hidden_val = hidden_match.group(1).strip().lower()
                    data["hidden"] = (
                        "Sim" if "sim" in hidden_val or "true" in hidden_val else "Não"
                    )
        except:
            pass
        return data

    def get_frequency_info(self) -> Dict:
        data = {"frequencies": "Não disponível", "channels": "Não disponível"}
        if not self.network:
            return data
        freqs = self.freq_detector.get_network_frequencies(self.network.ssid)
        if freqs:
            bands = list(set([f.band for f in freqs if f.band]))
            data["frequencies"] = ", ".join(bands) if bands else "Desconhecido"
        return data