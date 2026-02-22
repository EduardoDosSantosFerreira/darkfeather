"""
Tela independente de análise de segurança - Layout Otimizado
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QSizePolicy, QMessageBox,
    QFileDialog, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import qtawesome as qta
import json
from datetime import datetime

from ui.security.widgets import SecurityCard, VulnerabilityBadge
from ui.security.security_analyzer import SecurityAnalyzerUI
from ui.theme import UIThemeManager
from ui.risk_badge import RiskBadge


class SecuritySummaryCard(QFrame):
    """Card de resumo compacto"""
    
    def __init__(self, report, parent=None):
        super().__init__(parent)
        self.report = report
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Linha de score
        score_row = QHBoxLayout()
        score_row.setSpacing(8)
        
        score = self.report.health_score
        if score >= 80:
            color = "#10b981"
            status = "Bom"
        elif score >= 50:
            color = "#f59e0b"
            status = "Atenção"
        else:
            color = "#ef4444"
            status = "Crítico"
        
        score_label = QLabel(f"{score}%")
        score_label.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 700;")
        score_row.addWidget(score_label)
        
        status_label = QLabel(status)
        status_label.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: 500;")
        score_row.addWidget(status_label)
        
        score_row.addStretch()
        layout.addLayout(score_row)
        
        # Métricas em linha
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(16)
        
        metrics = [
            ("Total", self.report.total_networks, "#64748b"),
            ("Críticas", self.report.critical_count, "#ef4444"),
            ("Altas", self.report.high_count, "#f97316"),
            ("Médias", self.report.medium_count, "#f59e0b")
        ]
        
        for label, value, color in metrics:
            item = QLabel(f"<b>{value}</b> {label}")
            item.setTextFormat(Qt.RichText)
            item.setStyleSheet(f"color: {color}; font-size: 12px;")
            metrics_row.addWidget(item)
        
        metrics_row.addStretch()
        layout.addLayout(metrics_row)


class SecurityDetailsPanel(QFrame):
    """Painel de detalhes simplificado"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_analysis = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)
        
        self.show_placeholder()
    
    def show_placeholder(self):
        self.clear_content()
        
        placeholder = QLabel("Selecione uma rede")
        placeholder.setStyleSheet("color: #94a3b8; font-size: 13px; padding: 24px;")
        placeholder.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(placeholder)
    
    def show_analysis(self, analysis):
        self.current_analysis = analysis
        self.clear_content()
        
        # Cabeçalho
        header = QHBoxLayout()
        
        name_label = QLabel(analysis.ssid)
        name_font = QFont()
        name_font.setPointSize(15)
        name_font.setWeight(QFont.Weight.DemiBold)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #0f172a;")
        header.addWidget(name_label)
        
        header.addStretch()
        
        risk_badge = RiskBadge(analysis.risk_level.value, analysis.risk_score)
        header.addWidget(risk_badge)
        
        self.main_layout.addLayout(header)
        
        # Info linha única
        info = QLabel(f"{analysis.auth} • {analysis.encryption}")
        info.setStyleSheet("color: #475569; font-size: 12px; padding: 4px 0;")
        self.main_layout.addWidget(info)
        
        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #e2e8f0; max-height: 1px;")
        self.main_layout.addWidget(sep)
        
        # Vulnerabilidades
        if analysis.vulnerabilities:
            vuln_count = QLabel(f"Vulnerabilidades ({len(analysis.vulnerabilities)})")
            vuln_count.setStyleSheet("color: #991b1b; font-size: 12px; font-weight: 600;")
            self.main_layout.addWidget(vuln_count)
            
            for vuln in analysis.vulnerabilities[:2]:
                v = QLabel(f"• {vuln.type.value}")
                v.setStyleSheet("color: #334155; font-size: 11px; padding-left: 8px;")
                self.main_layout.addWidget(v)
        else:
            safe = QLabel("✅ Nenhuma vulnerabilidade")
            safe.setStyleSheet("color: #10b981; font-size: 12px;")
            self.main_layout.addWidget(safe)
        
        self.main_layout.addStretch()
    
    def clear_content(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class SecurityWindow(QDialog):
    """
    Tela de análise de segurança - Layout otimizado
    """
    
    def __init__(self, networks, parent=None):
        super().__init__(parent)
        self.networks = networks
        self.theme = UIThemeManager()
        self.selected_analysis = None
        self.report = None
        self.setup_ui()
        self.analyze_networks()
    
    def setup_ui(self):
        self.setWindowTitle("DarkFeather - Análise de Segurança")
        self.setMinimumSize(1000, 700)
        self.setModal(False)
        
        self.setPalette(self.theme.get_palette())
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)
        
        # Header
        self.setup_header(main_layout)
        
        # Summary
        self.summary_container = QWidget()
        self.summary_layout = QVBoxLayout(self.summary_container)
        self.summary_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.summary_container)
        
        # Content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)
        
        self.setup_networks_panel(content_layout)
        self.setup_details_panel(content_layout)
        
        main_layout.addLayout(content_layout, 1)
        
        # Footer
        self.setup_footer(main_layout)
    
    def setup_header(self, parent_layout):
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 4)
        
        title = QLabel("Análise de Segurança")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Medium)
        title.setFont(title_font)
        title.setStyleSheet("color: #0f172a;")
        header.addWidget(title)
        
        header.addStretch()
        
        self.btn_refresh = QPushButton(" Reanalisar")
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='#ffffff'))
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setFixedSize(120, 32)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                padding: 0 12px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.btn_refresh.clicked.connect(self.analyze_networks)
        header.addWidget(self.btn_refresh)
        
        parent_layout.addLayout(header)
    
    def setup_networks_panel(self, parent_layout):
        panel = QWidget()
        panel.setMinimumWidth(300)
        panel.setMaximumWidth(380)
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(8)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("Redes")
        title.setStyleSheet("font-size: 14px; font-weight: 600; color: #0f172a;")
        header.addWidget(title)
        
        self.network_count = QLabel("0")
        self.network_count.setStyleSheet("color: #64748b; font-size: 11px; background-color: #f1f5f9; padding: 2px 8px; border-radius: 10px;")
        header.addWidget(self.network_count)
        header.addStretch()
        
        panel_layout.addLayout(header)
        
        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollBar:vertical { width: 4px; }")
        
        scroll_content = QWidget()
        self.cards_layout = QVBoxLayout(scroll_content)
        self.cards_layout.setContentsMargins(0, 0, 2, 0)
        self.cards_layout.setSpacing(4)
        self.cards_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        panel_layout.addWidget(scroll)
        
        parent_layout.addWidget(panel)
    
    def setup_details_panel(self, parent_layout):
        self.details_panel = SecurityDetailsPanel()
        parent_layout.addWidget(self.details_panel, 1)
    
    def setup_footer(self, parent_layout):
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 8, 0, 0)
        footer.setSpacing(8)
        
        self.btn_report = QPushButton(" Relatório")
        self.btn_report.setIcon(qta.icon('fa5s.file-alt', color='#ffffff'))
        self.btn_report.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_report.setFixedSize(110, 32)
        self.btn_report.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.btn_report.clicked.connect(self.generate_full_report)
        footer.addWidget(self.btn_report)
        
        self.btn_export = QPushButton(" CSV")
        self.btn_export.setIcon(qta.icon('fa5s.file-csv', color='#334155'))
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.setFixedSize(80, 32)
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f8fafc;
            }
        """)
        self.btn_export.clicked.connect(self.export_vulnerabilities)
        footer.addWidget(self.btn_export)
        
        footer.addStretch()
        
        self.btn_close = QPushButton(" Fechar")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setFixedSize(80, 32)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #334155;
                border: none;
                border-radius: 6px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.btn_close.clicked.connect(self.close)
        footer.addWidget(self.btn_close)
        
        parent_layout.addLayout(footer)
    
    def analyze_networks(self):
        if not self.networks:
            return
        
        self.report = SecurityAnalyzerUI.analyze_environment(self.networks)
        self.update_summary()
        self.update_networks_list()
        self.network_count.setText(str(len(self.report.networks_analysis)))
        
        if self.report.networks_analysis:
            self.details_panel.show_analysis(self.report.networks_analysis[0])
    
    def update_summary(self):
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if self.report:
            self.summary_layout.addWidget(SecuritySummaryCard(self.report))
    
    def update_networks_list(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for analysis in self.report.networks_analysis:
            card = SecurityCard(analysis)
            card.clicked.connect(self.on_network_selected)
            self.cards_layout.addWidget(card)
        
        self.cards_layout.addStretch()
    
    def on_network_selected(self, analysis):
        self.details_panel.show_analysis(analysis)
    
    def generate_full_report(self):
        if not self.report:
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório",
            f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                report_data = {
                    "timestamp": datetime.now().isoformat(),
                    "summary": {
                        "health_score": self.report.health_score,
                        "total_networks": self.report.total_networks,
                        "critical": self.report.critical_count,
                        "high": self.report.high_count,
                        "medium": self.report.medium_count
                    },
                    "networks": [n.to_dict() for n in self.report.networks_analysis]
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2)
                
                QMessageBox.information(self, "Sucesso", f"Relatório salvo")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))
    
    def export_vulnerabilities(self):
        if not self.report:
            return
        
        import csv
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar",
            f"vulnerabilities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Rede', 'Vulnerabilidade', 'Nível'])
                    
                    for net in self.report.networks_analysis:
                        for vuln in net.vulnerabilities:
                            writer.writerow([
                                net.ssid,
                                vuln.type.value,
                                vuln.risk_level.value
                            ])
                
                QMessageBox.information(self, "Sucesso", f"Exportado")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))