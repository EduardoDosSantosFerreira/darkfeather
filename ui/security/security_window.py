"""
Tela independente de análise de segurança - Layout Limpo e Moderno
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QDialog, QSizePolicy, QMessageBox,
    QFileDialog, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor
import qtawesome as qta
import json
from datetime import datetime

from ui.security.widgets import SecurityCard, VulnerabilityBadge
from ui.security.security_analyzer import SecurityAnalyzerUI
from ui.theme import UIThemeManager
from ui.risk_badge import RiskBadge


class SecuritySummaryCard(QFrame):
    """Card de resumo compacto e legível - sem bordas"""
    
    def __init__(self, report, parent=None):
        super().__init__(parent)
        self.report = report
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(16)
        
        # Linha de score
        score_row = QHBoxLayout()
        
        score = self.report.health_score
        if score >= 80:
            color = "#059669"
            status = "Bom"
        elif score >= 50:
            color = "#d97706"
            status = "Atenção"
        else:
            color = "#dc2626"
            status = "Crítico"
        
        score_label = QLabel(f"{score}%")
        score_label.setStyleSheet(f"color: {color}; font-size: 36px; font-weight: 700;")
        score_row.addWidget(score_label)
        
        status_label = QLabel(status)
        status_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 600; margin-left: 8px;")
        score_row.addWidget(status_label)
        
        score_row.addStretch()
        layout.addLayout(score_row)
        
        # Métricas em linha
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(24)
        
        metrics = [
            ("Total", self.report.total_networks, "#3b82f6"),
            ("Críticas", self.report.critical_count, "#dc2626"),
            ("Altas", self.report.high_count, "#ea580c"),
            ("Médias", self.report.medium_count, "#d97706"),
        ]
        
        for label, value, color in metrics:
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(2)
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 700;")
            container_layout.addWidget(value_label)
            
            name_label = QLabel(label)
            name_label.setStyleSheet("color: #475569; font-size: 13px; font-weight: 500;")
            container_layout.addWidget(name_label)
            
            metrics_row.addWidget(container)
        
        metrics_row.addStretch()
        layout.addLayout(metrics_row)


class SecurityDetailsPanel(QFrame):
    """Painel de detalhes - limpo e sem bordas"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_analysis = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 12px;
            }
            .section-title {
                font-size: 15px;
                font-weight: 600;
                color: #1e293b;
                padding: 8px 0;
            }
            .info-label {
                color: #64748b;
                font-size: 13px;
            }
            .info-value {
                color: #1e293b;
                font-size: 13px;
                font-weight: 500;
            }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(16)
        
        self.show_placeholder()
    
    def show_placeholder(self):
        self.clear_content()
        
        placeholder = QLabel("Selecione uma rede para ver detalhes")
        placeholder.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 40px;")
        placeholder.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(placeholder)
    
    def show_analysis(self, analysis):
        self.current_analysis = analysis
        self.clear_content()
        
        # Cabeçalho
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        name_label = QLabel(analysis.ssid)
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setWeight(QFont.Weight.DemiBold)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #0f172a;")
        name_label.setWordWrap(True)
        header_layout.addWidget(name_label, 1)
        
        risk_badge = RiskBadge(analysis.risk_level.value, analysis.risk_score)
        header_layout.addWidget(risk_badge)
        
        self.main_layout.addWidget(header)
        
        # Info de segurança
        security_info = QLabel(f"{analysis.auth}  •  {analysis.encryption}")
        security_info.setStyleSheet("color: #475569; font-size: 13px; padding: 4px 0;")
        self.main_layout.addWidget(security_info)
        
        # Separador sutil
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #e2e8f0; max-height: 1px;")
        self.main_layout.addWidget(sep)
        
        # Vulnerabilidades
        if analysis.vulnerabilities:
            vuln_title = QLabel(f"Vulnerabilidades ({len(analysis.vulnerabilities)})")
            vuln_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #991b1b; margin-bottom: 8px;")
            self.main_layout.addWidget(vuln_title)
            
            for vuln in analysis.vulnerabilities[:3]:
                v_frame = QFrame()
                v_frame.setStyleSheet("""
                    QFrame {
                        background-color: #fef2f2;
                        border-radius: 8px;
                        margin: 4px 0;
                    }
                """)
                
                v_layout = QVBoxLayout(v_frame)
                v_layout.setContentsMargins(12, 8, 12, 8)
                v_layout.setSpacing(4)
                
                v_type = QLabel(vuln.type.value)
                v_type.setStyleSheet("color: #991b1b; font-size: 12px; font-weight: 600;")
                v_layout.addWidget(v_type)
                
                v_desc = QLabel(vuln.description[:60] + "..." if len(vuln.description) > 60 else vuln.description)
                v_desc.setStyleSheet("color: #475569; font-size: 11px;")
                v_desc.setWordWrap(True)
                v_layout.addWidget(v_desc)
                
                self.main_layout.addWidget(v_frame)
            
            if len(analysis.vulnerabilities) > 3:
                more = QLabel(f"... e mais {len(analysis.vulnerabilities) - 3}")
                more.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
                more.setAlignment(Qt.AlignCenter)
                self.main_layout.addWidget(more)
        else:
            safe = QLabel("✅ Nenhuma vulnerabilidade detectada")
            safe.setStyleSheet("color: #10b981; font-size: 13px; padding: 16px;")
            safe.setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(safe)
    
    def clear_content(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class SecurityWindow(QDialog):
    """
    Tela de análise de segurança - Layout limpo e moderno
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
        self.setMinimumSize(1100, 750)
        self.setModal(False)
        
        self.setPalette(self.theme.get_palette())
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Header
        self.setup_header(main_layout)
        
        # Summary
        self.summary_container = QWidget()
        self.summary_layout = QVBoxLayout(self.summary_container)
        self.summary_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.summary_container)
        
        # Content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        self.setup_networks_panel(content_layout)
        self.setup_details_panel(content_layout)
        
        main_layout.addLayout(content_layout, 1)
        
        # Footer
        self.setup_footer(main_layout)
    
    def setup_header(self, parent_layout):
        header = QHBoxLayout()
        
        title = QLabel("Análise de Segurança")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setWeight(QFont.Weight.Medium)
        title.setFont(title_font)
        title.setStyleSheet("color: #0f172a;")
        header.addWidget(title)
        
        header.addStretch()
        
        self.btn_refresh = QPushButton(" Reanalisar")
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='#ffffff'))
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setFixedSize(130, 36)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.btn_refresh.clicked.connect(self.analyze_networks)
        header.addWidget(self.btn_refresh)
        
        parent_layout.addLayout(header)
    
    def setup_networks_panel(self, parent_layout):
        panel = QFrame()
        panel.setMinimumWidth(350)
        panel.setMaximumWidth(450)
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 12px;
            }
        """)
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 16, 16, 16)
        panel_layout.setSpacing(12)
        
        # Header do painel
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Redes Analisadas")
        title.setStyleSheet("font-size: 15px; font-weight: 600; color: #0f172a;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.network_count = QLabel("0")
        self.network_count.setStyleSheet("""
            color: #64748b;
            font-size: 12px;
            background-color: #e2e8f0;
            padding: 4px 12px;
            border-radius: 16px;
            font-weight: 500;
        """)
        header_layout.addWidget(self.network_count)
        
        panel_layout.addWidget(header_widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
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
        """)
        
        scroll_content = QWidget()
        self.cards_layout = QVBoxLayout(scroll_content)
        self.cards_layout.setContentsMargins(0, 0, 4, 0)
        self.cards_layout.setSpacing(8)
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
        
        self.btn_report = QPushButton(" Gerar Relatório")
        self.btn_report.setIcon(qta.icon('fa5s.file-alt', color='#ffffff'))
        self.btn_report.setCursor(Qt.PointingHandCursor)
        self.btn_report.setFixedSize(150, 36)
        self.btn_report.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.btn_report.clicked.connect(self.generate_full_report)
        footer.addWidget(self.btn_report)
        
        self.btn_export = QPushButton(" Exportar CSV")
        self.btn_export.setIcon(qta.icon('fa5s.file-csv', color='#334155'))
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.setFixedSize(130, 36)
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #334155;
                border: none;
                border-radius: 8px;
                font-weight: 500;
                font-size: 13px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.btn_export.clicked.connect(self.export_vulnerabilities)
        footer.addWidget(self.btn_export)
        
        footer.addStretch()
        
        self.btn_close = QPushButton(" Fechar")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setFixedSize(100, 36)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #334155;
                border: none;
                border-radius: 8px;
                font-weight: 500;
                font-size: 13px;
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
                        "health_status": self.report.health_status,
                        "total_networks": self.report.total_networks,
                        "critical": self.report.critical_count,
                        "high": self.report.high_count,
                        "medium": self.report.medium_count,
                        "open_networks": self.report.open_networks
                    },
                    "networks": [n.to_dict() for n in self.report.networks_analysis]
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Sucesso", "Relatório salvo com sucesso!")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao salvar relatório: {str(e)}")
    
    def export_vulnerabilities(self):
        if not self.report:
            return
        
        import csv
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Vulnerabilidades",
            f"vulnerabilities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Rede', 'Vulnerabilidade', 'Nível', 'Recomendação'])
                    
                    for net in self.report.networks_analysis:
                        for vuln in net.vulnerabilities:
                            writer.writerow([
                                net.ssid,
                                vuln.type.value,
                                vuln.risk_level.value,
                                vuln.recommendation
                            ])
                
                QMessageBox.information(self, "Sucesso", "Vulnerabilidades exportadas com sucesso!")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao exportar: {str(e)}")