"""
Widgets específicos para a tela de segurança
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
import qtawesome as qta

from ui.risk_badge import RiskBadge
from ui.security.models import NetworkSecurityAnalysis, Vulnerability


class VulnerabilityBadge(QFrame):
    """Badge para exibir uma vulnerabilidade específica"""
    
    def __init__(self, vulnerability: Vulnerability, parent=None):
        super().__init__(parent)
        self.vulnerability = vulnerability
        self.setup_ui()
    
    def setup_ui(self):
        self.setObjectName("vulnerabilityBadge")
        
        # Cor baseada no nível
        level_colors = {
            "Crítico": "#ef4444",
            "Alto": "#f97316",
            "Médio": "#f59e0b",
            "Baixo": "#10b981"
        }
        color = level_colors.get(self.vulnerability.risk_level.value, "#94a3b8")
        
        self.setStyleSheet(f"""
            QFrame#vulnerabilityBadge {{
                background-color: {color}10;
                border: 1px solid {color}30;
                border-radius: 8px;
                margin: 2px 0;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Linha superior
        top_row = QHBoxLayout()
        
        type_label = QLabel(self.vulnerability.type.value)
        type_font = QFont()
        type_font.setWeight(QFont.Weight.DemiBold)
        type_label.setFont(type_font)
        type_label.setStyleSheet(f"color: {color};")
        top_row.addWidget(type_label)
        
        top_row.addStretch()
        
        level_badge = QLabel(f"  {self.vulnerability.risk_level.value}  ")
        level_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {color}20;
                color: {color};
                border-radius: 10px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 600;
            }}
        """)
        top_row.addWidget(level_badge)
        
        layout.addLayout(top_row)
        
        # Descrição (curta)
        desc_short = self.vulnerability.description[:80] + "..." if len(self.vulnerability.description) > 80 else self.vulnerability.description
        desc_label = QLabel(desc_short)
        desc_label.setStyleSheet("color: #475569; font-size: 11px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)


class SecurityCard(QFrame):
    """Card de rede na tela de segurança - com espaçamento melhorado"""
    
    clicked = Signal(object)
    
    def __init__(self, analysis: NetworkSecurityAnalysis, parent=None):
        super().__init__(parent)
        self.analysis = analysis
        self.setup_ui()
        self.setup_shadow()
    
    def setup_ui(self):
        self.setObjectName("securityCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(110)
        
        self.setStyleSheet("""
            QFrame#securityCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QFrame#securityCard:hover {
                background-color: #f8fafc;
                border-color: #94a3b8;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Ícone de status
        self.status_icon = QLabel()
        if self.analysis.critical_count > 0:
            icon = qta.icon('fa5s.times-circle', color='#ef4444')
        elif self.analysis.high_count > 0:
            icon = qta.icon('fa5s.exclamation-triangle', color='#f97316')
        else:
            icon = qta.icon('fa5s.check-circle', color='#10b981')
        self.status_icon.setPixmap(icon.pixmap(32, 32))
        layout.addWidget(self.status_icon)
        
        # Informações
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name_label = QLabel(self.analysis.ssid)
        name_font = QFont()
        name_font.setPointSize(13)
        name_font.setWeight(QFont.Weight.DemiBold)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #0f172a;")
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)
        
        security_label = QLabel(f"{self.analysis.auth}  •  {self.analysis.encryption}")
        security_label.setStyleSheet("color: #64748b; font-size: 11px;")
        info_layout.addWidget(security_label)
        
        layout.addLayout(info_layout, 1)
        
        # Badge de risco
        self.risk_badge = RiskBadge(
            self.analysis.risk_level.value,
            self.analysis.risk_score
        )
        layout.addWidget(self.risk_badge)
        
        # Contador de vulnerabilidades
        if self.analysis.vulnerabilities:
            vuln_count = len(self.analysis.vulnerabilities)
            count_label = QLabel(f"{vuln_count}")
            count_label.setStyleSheet("""
                QLabel {
                    color: #ef4444;
                    font-size: 12px;
                    font-weight: 600;
                    background-color: #fee2e2;
                    padding: 4px 8px;
                    border-radius: 12px;
                    min-width: 24px;
                    text-align: center;
                }
            """)
            layout.addWidget(count_label)
    
    def setup_shadow(self):
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(0, 0, 0, 15))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.analysis)
        super().mousePressEvent(event)