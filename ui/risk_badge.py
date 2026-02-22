"""
Widgets de exibição de risco de segurança
"""
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QToolTip
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFont


class RiskBadge(QLabel):
    """Badge para exibir nível de risco"""
    
    COLORS = {
        "Baixo": {
            "bg": "#10b98120",  # verde com transparência
            "text": "#10b981",
            "icon": "🟢"
        },
        "Médio": {
            "bg": "#f59e0b20",  # laranja com transparência
            "text": "#f59e0b",
            "icon": "🟡"
        },
        "Alto": {
            "bg": "#ef444420",  # vermelho com transparência
            "text": "#ef4444",
            "icon": "🔴"
        }
    }
    
    def __init__(self, risk_level: str, risk_score: int, parent=None):
        super().__init__(parent)
        self.risk_level = risk_level
        self.risk_score = risk_score
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a aparência do badge"""
        color = self.COLORS.get(self.risk_level, self.COLORS["Médio"])
        
        # Texto do badge
        text = f"{color['icon']} {self.risk_level} ({self.risk_score})"
        self.setText(text)
        
        # Estilo
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color['bg']};
                color: {color['text']};
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)
        
        # Alinhamento
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Tamanho fixo mínimo
        self.setMinimumWidth(80)


class RiskWidget(QWidget):
    """Widget combinado com badge e tooltip de detalhes"""
    
    def __init__(self, network, analysis, parent=None):
        super().__init__(parent)
        self.network = network
        self.analysis = analysis
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Badge de risco
        self.badge = RiskBadge(analysis["risk_level"], analysis["risk_score"])
        layout.addWidget(self.badge)
        
        # Configurar tooltip
        self.setToolTip(self._generate_tooltip())
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    
    def _generate_tooltip(self) -> str:
        """Gera tooltip com detalhes da análise"""
        lines = []
        lines.append(f"<b>{self.network.ssid}</b>")
        lines.append(f"<b>Risco:</b> {self.analysis['risk_level']} ({self.analysis['risk_score']}/100)")
        
        if self.analysis["flags"]:
            lines.append("<b>Observações:</b>")
            for flag in self.analysis["flags"]:
                lines.append(f"  • {flag}")
        
        if self.analysis["recommendations"]:
            lines.append("<b>Recomendações:</b>")
            for rec in self.analysis["recommendations"]:
                lines.append(f"  → {rec}")
        
        return "<br>".join(lines)
    
    def enterEvent(self, event: QEvent):
        """Mostra tooltip personalizado ao entrar"""
        QToolTip.showText(self.mapToGlobal(self.rect().center()), self.toolTip(), self)
        super().enterEvent(event)
    
    def leaveEvent(self, event: QEvent):
        """Esconde tooltip ao sair"""
        QToolTip.hideText()
        super().leaveEvent(event)


class SecurityStatusWidget(QWidget):
    """Widget de status geral de segurança"""
    
    def __init__(self, environment_summary: dict, parent=None):
        super().__init__(parent)
        self.environment = environment_summary
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(16)
        
        # Score de saúde
        health_score = self.environment.get("health_score", 0)
        health_status = self.environment.get("health_status", "N/A")
        
        # Cor baseada no status
        if health_status == "Bom":
            color = "#10b981"
        elif health_status == "Atenção":
            color = "#f59e0b"
        else:
            color = "#ef4444"
        
        # Label do score
        self.score_label = QLabel(f"Saúde: {health_score}%")
        self.score_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 14px;
                font-weight: 600;
                background-color: {color}20;
                border-radius: 16px;
                padding: 6px 16px;
            }}
        """)
        layout.addWidget(self.score_label)
        
        # Contadores
        self.counts_label = QLabel(
            f"🔴 {self.environment.get('high_risk', 0)}  "
            f"🟡 {self.environment.get('medium_risk', 0)}  "
            f"🟢 {self.environment.get('low_risk', 0)}"
        )
        self.counts_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 13px;
                font-weight: 500;
            }
        """)
        layout.addWidget(self.counts_label)
        
        layout.addStretch()