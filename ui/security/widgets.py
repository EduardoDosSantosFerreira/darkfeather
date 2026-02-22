"""
Widgets específicos para a tela de segurança
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
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
        """Configura a interface do badge"""
        self.setObjectName("vulnerabilityBadge")
        self.setStyleSheet("""
            QFrame#vulnerabilityBadge {
                background-color: #fef2f2;
                border: 1px solid #fee2e2;
                border-radius: 8px;
                margin: 2px 0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Linha superior com tipo e nível
        top_row = QHBoxLayout()
        
        # Ícone e tipo
        icon_label = QLabel()
        if self.vulnerability.risk_level.value in ["Crítico", "Alto"]:
            icon_label.setPixmap(qta.icon('fa5s.exclamation-triangle', color='#ef4444').pixmap(16, 16))
        else:
            icon_label.setPixmap(qta.icon('fa5s.exclamation-circle', color='#f59e0b').pixmap(16, 16))
        top_row.addWidget(icon_label)
        
        type_label = QLabel(self.vulnerability.type.value)
        type_font = QFont()
        type_font.setWeight(QFont.Weight.DemiBold)
        type_label.setFont(type_font)
        type_label.setStyleSheet("color: #1e293b;")
        top_row.addWidget(type_label)
        
        top_row.addStretch()
        
        # Badge de nível
        level_colors = {
            "Crítico": "#ef4444",
            "Alto": "#f97316",
            "Médio": "#f59e0b",
            "Baixo": "#10b981"
        }
        color = level_colors.get(self.vulnerability.risk_level.value, "#94a3b8")
        
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
        
        # Descrição
        desc_label = QLabel(self.vulnerability.description)
        desc_label.setStyleSheet("color: #475569; font-size: 11px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Recomendação
        rec_label = QLabel(f"→ {self.vulnerability.recommendation}")
        rec_label.setStyleSheet("color: #2563eb; font-size: 11px; font-style: italic;")
        rec_label.setWordWrap(True)
        layout.addWidget(rec_label)


class SecurityCard(QFrame):
    """Card de rede na tela de segurança"""
    
    clicked = Signal(object)  # Emite a análise da rede
    
    def __init__(self, analysis: NetworkSecurityAnalysis, parent=None):
        super().__init__(parent)
        self.analysis = analysis
        self.setup_ui()
        self.setup_shadow()
    
    def setup_ui(self):
        """Configura a interface do card"""
        self.setObjectName("securityCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(100)
        
        self.setStyleSheet("""
            QFrame#securityCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QFrame#securityCard:hover {
                background-color: #f8fafc;
                border-color: #cbd5e1;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Ícone de status
        self.status_icon = QLabel()
        if self.analysis.critical_count > 0:
            self.status_icon.setPixmap(qta.icon('fa5s.times-circle', color='#ef4444').pixmap(32, 32))
        elif self.analysis.high_count > 0:
            self.status_icon.setPixmap(qta.icon('fa5s.exclamation-triangle', color='#f97316').pixmap(32, 32))
        else:
            self.status_icon.setPixmap(qta.icon('fa5s.check-circle', color='#10b981').pixmap(32, 32))
        layout.addWidget(self.status_icon)
        
        # Informações
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # Nome da rede
        name_label = QLabel(self.analysis.ssid)
        name_font = QFont()
        name_font.setPointSize(13)
        name_font.setWeight(QFont.Weight.DemiBold)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #0f172a;")
        info_layout.addWidget(name_label)
        
        # Tipo de segurança
        security_label = QLabel(f"{self.analysis.auth} • {self.analysis.encryption}")
        security_label.setStyleSheet("color: #64748b; font-size: 11px;")
        info_layout.addWidget(security_label)
        
        layout.addLayout(info_layout, stretch=1)
        
        # Badge de risco
        self.risk_badge = RiskBadge(
            self.analysis.risk_level.value,
            self.analysis.risk_score
        )
        layout.addWidget(self.risk_badge)
        
        # Contador de vulnerabilidades
        if self.analysis.vulnerabilities:
            vuln_count = len(self.analysis.vulnerabilities)
            count_label = QLabel(f"{vuln_count} vuln")
            count_label.setStyleSheet("""
                QLabel {
                    color: #64748b;
                    font-size: 11px;
                    padding: 4px 8px;
                    background-color: #f1f5f9;
                    border-radius: 12px;
                }
            """)
            layout.addWidget(count_label)
    
    def setup_shadow(self):
        """Configura sombra do card"""
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor
        
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(0, 0, 0, 20))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
    
    def mousePressEvent(self, event):
        """Evento de clique do mouse"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.analysis)
        super().mousePressEvent(event)


class SecuritySummaryWidget(QWidget):
    """Widget de resumo da segurança"""
    
    def __init__(self, report, parent=None):
        super().__init__(parent)
        self.report = report
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do resumo"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(16)
        
        # Score card
        score_card = self._create_score_card()
        layout.addWidget(score_card)
        
        # Stats card
        stats_card = self._create_stats_card()
        layout.addWidget(stats_card)
        
        # Recommendations card
        rec_card = self._create_recommendations_card()
        layout.addWidget(rec_card)
    
    def _create_score_card(self) -> QFrame:
        """Cria card de score de saúde"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Título
        title = QLabel("Saúde do Ambiente")
        title.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(title)
        
        # Score
        score = self.report.health_score
        status = self.report.health_status
        
        if status == "Bom":
            color = "#10b981"
        elif status == "Atenção":
            color = "#f59e0b"
        else:
            color = "#ef4444"
        
        score_label = QLabel(f"{score}%")
        score_label.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: 600;")
        layout.addWidget(score_label)
        
        status_label = QLabel(status)
        status_label.setStyleSheet(f"color: {color}; font-size: 14px;")
        layout.addWidget(status_label)
        
        return card
    
    def _create_stats_card(self) -> QFrame:
        """Cria card de estatísticas"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Título
        title = QLabel("Visão Geral")
        title.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(title)
        
        # Grid de estatísticas
        grid = QVBoxLayout()
        grid.setSpacing(4)
        
        stats = [
            ("🔴 Críticas", self.report.critical_count, "#ef4444"),
            ("🟠 Altas", self.report.high_count, "#f97316"),
            ("🟡 Médias", self.report.medium_count, "#f59e0b"),
            ("🟢 Baixas", self.report.low_count, "#10b981"),
            ("📡 Redes Abertas", self.report.open_networks, "#ef4444"),
            ("⚠️ WEP", self.report.wep_networks, "#ef4444")
        ]
        
        for label, value, color in stats:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #64748b; font-size: 11px;")
            row.addWidget(lbl)
            
            val = QLabel(str(value))
            val.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 600;")
            row.addWidget(val)
            
            grid.addLayout(row)
        
        layout.addLayout(grid)
        
        return card
    
    def _create_recommendations_card(self) -> QFrame:
        """Cria card de recomendações"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Título
        title = QLabel("Recomendações")
        title.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(title)
        
        # Lista de recomendações
        if self.report.global_recommendations:
            for rec in self.report.global_recommendations[:3]:  # Top 3
                rec_label = QLabel(f"• {rec}")
                rec_label.setStyleSheet("color: #2563eb; font-size: 11px;")
                rec_label.setWordWrap(True)
                layout.addWidget(rec_label)
        else:
            empty = QLabel("Nenhuma recomendação")
            empty.setStyleSheet("color: #94a3b8; font-size: 11px; font-style: italic;")
            layout.addWidget(empty)
        
        layout.addStretch()
        
        return card