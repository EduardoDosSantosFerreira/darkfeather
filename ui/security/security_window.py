"""
Tela de análise de segurança - Versão simplificada
Design original com cores restauradas
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QMessageBox,
    QFileDialog, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import qtawesome as qta
from datetime import datetime

from core.security import SecurityAnalyzer
from core.scanner import WifiNetwork
from ui.theme import UIThemeManager


class SecurityWindow(QDialog):
    """Janela de análise de segurança"""
    
    def __init__(self, networks, parent=None):
        super().__init__(parent)
        self.networks = networks
        self.analyses = {}
        self.theme = UIThemeManager()
        
        self.setWindowTitle("DarkFeather - Análise de Segurança")
        self.setMinimumSize(900, 600)
        self.setPalette(self.theme.get_palette())
        self.setStyleSheet(self.get_style())
        
        self.setup_ui()
        self.analyze_all()
    
    def get_style(self) -> str:
        """Retorna o estilo da janela"""
        return """
            QDialog {
                background-color: #f8fafc;
            }
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QLabel {
                color: #0f172a;
            }
            QPushButton {
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
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
        """
    
    def setup_ui(self):
        """Configura interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("🔒 Análise de Segurança")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        header.addWidget(title)
        
        header.addStretch()
        
        self.btn_export = QPushButton(" Exportar Relatório")
        self.btn_export.setIcon(qta.icon('fa5s.file-export', color='#ffffff'))
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.btn_export.clicked.connect(self.export_report)
        header.addWidget(self.btn_export)
        
        layout.addLayout(header)
        
        # Summary cards
        self.summary_frame = QFrame()
        self.summary_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        self.summary_layout = QHBoxLayout(self.summary_frame)
        layout.addWidget(self.summary_frame)
        
        # Networks list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.cards_layout = QVBoxLayout(scroll_content)
        self.cards_layout.setSpacing(8)
        self.cards_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)
        
        # Close button
        btn_close = QPushButton(" Fechar")
        btn_close.setIcon(qta.icon('fa5s.times', color='#334155'))
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #334155;
                border: 1px solid #cbd5e1;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)
    
    def analyze_all(self):
        """Analisa todas as redes"""
        high = medium = low = 0
        
        for net in self.networks:
            analysis = SecurityAnalyzer.analyze_network(net)
            self.analyses[net.ssid] = analysis
            
            if analysis["risk_level"] == "Alto":
                high += 1
            elif analysis["risk_level"] == "Médio":
                medium += 1
            else:
                low += 1
            
            self.add_network_card(net, analysis)
        
        # Update summary
        self.update_summary(high, medium, low)
    
    def update_summary(self, high: int, medium: int, low: int):
        """Atualiza cards de resumo"""
        # Clear existing
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        metrics = [
            ("🔴 Alto Risco", high, "#ef4444"),
            ("🟡 Médio Risco", medium, "#f59e0b"),
            ("🟢 Baixo Risco", low, "#10b981"),
            ("📊 Total", len(self.networks), "#2563eb")
        ]
        
        for label, value, color in metrics:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 12px;
                    min-width: 100px;
                }}
            """)
            
            card_layout = QVBoxLayout(card)
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 700;")
            value_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(value_label)
            
            label_label = QLabel(label)
            label_label.setStyleSheet("color: #64748b; font-size: 11px;")
            label_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(label_label)
            
            self.summary_layout.addWidget(card)
        
        self.summary_layout.addStretch()
    
    def add_network_card(self, net: WifiNetwork, analysis: dict):
        """Adiciona card de rede"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
            }
            QFrame:hover {
                background-color: #f8fafc;
                border-color: #94a3b8;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Header
        header = QHBoxLayout()
        
        name = QLabel(net.ssid)
        name_font = QFont()
        name_font.setWeight(QFont.Weight.DemiBold)
        name.setFont(name_font)
        header.addWidget(name)
        
        header.addStretch()
        
        # Risk badge
        risk_color = "#ef4444" if analysis["risk_level"] == "Alto" else "#f59e0b" if analysis["risk_level"] == "Médio" else "#10b981"
        risk_badge = QLabel(f"  {analysis['risk_level']} ({analysis['risk_score']})  ")
        risk_badge.setStyleSheet(f"""
            background-color: {risk_color}20;
            color: {risk_color};
            border-radius: 12px;
            padding: 4px 8px;
            font-weight: 600;
            font-size: 11px;
        """)
        header.addWidget(risk_badge)
        
        layout.addLayout(header)
        
        # Details
        details = QLabel(f"{net.auth} | {net.encryption}")
        details.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(details)
        
        # Vulnerabilities
        if analysis["flags"]:
            vuln_text = "⚠️ " + " • ".join(analysis["flags"][:2])
            if len(analysis["flags"]) > 2:
                vuln_text += f" +{len(analysis['flags'])-2}"
            vuln_label = QLabel(vuln_text)
            vuln_label.setStyleSheet("color: #ef4444; font-size: 11px;")
            layout.addWidget(vuln_label)
        
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
    
    def export_report(self):
        """Exporta relatório"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório",
            f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("RELATÓRIO DE SEGURANÇA DARKFEATHER\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                
                for net in self.networks:
                    analysis = self.analyses.get(net.ssid, {})
                    f.write(f"Rede: {net.ssid}\n")
                    f.write(f"  Autenticação: {net.auth}\n")
                    f.write(f"  Criptografia: {net.encryption}\n")
                    f.write(f"  Risco: {analysis.get('risk_level', 'N/A')} ({analysis.get('risk_score', 0)}/100)\n")
                    
                    if analysis.get('flags'):
                        f.write("  Observações:\n")
                        for flag in analysis['flags']:
                            f.write(f"    • {flag}\n")
                    
                    if analysis.get('recommendations'):
                        f.write("  Recomendações:\n")
                        for rec in analysis['recommendations']:
                            f.write(f"    → {rec}\n")
                    
                    f.write("-"*40 + "\n")
            
            QMessageBox.information(self, "Sucesso", "Relatório exportado com sucesso!")