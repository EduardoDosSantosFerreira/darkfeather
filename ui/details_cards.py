"""
Componentes de card para a interface de detalhes moderna
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPainter
import qtawesome as qta


class MetricCard(QFrame):
    """Card para métricas com design moderno"""
    
    def __init__(self, title: str, value: str, unit: str, color: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.unit = unit
        self.color = color
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedSize(140, 90)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.color}10, stop:1 {self.color}05);
                border: 1px solid {self.color}30;
                border-radius: 16px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        
        # Valor grande
        value_container = QHBoxLayout()
        value_container.setSpacing(2)
        
        value_label = QLabel(self.value)
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setWeight(QFont.Weight.Bold)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {self.color};")
        value_container.addWidget(value_label)
        
        if self.unit:
            unit_label = QLabel(self.unit)
            unit_font = QFont()
            unit_font.setPointSize(12)
            unit_font.setWeight(QFont.Weight.Normal)
            unit_label.setFont(unit_font)
            unit_label.setStyleSheet(f"color: {self.color}80; margin-top: 6px;")
            value_container.addWidget(unit_label)
        
        value_container.addStretch()
        layout.addLayout(value_container)
        
        # Título
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 500;")
        layout.addWidget(title_label)


class InfoCard(QFrame):
    """Card para informações em formato de lista"""
    
    def __init__(self, title: str, items: list, parent=None):
        super().__init__(parent)
        self.title = title
        self.items = items
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Título
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.Medium)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0f172a;")
        layout.addWidget(title_label)
        
        # Items
        for key, value in self.items:
            if value and value != "N/A" and value != "Não disponível":
                row = QHBoxLayout()
                row.setContentsMargins(0, 4, 0, 4)
                
                key_label = QLabel(key)
                key_label.setStyleSheet("color: #64748b; font-size: 12px;")
                key_label.setFixedWidth(80)
                row.addWidget(key_label)
                
                value_label = QLabel(str(value))
                value_label.setStyleSheet("color: #0f172a; font-size: 12px; font-weight: 500;")
                value_label.setWordWrap(True)
                value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                row.addWidget(value_label, 1)
                
                layout.addLayout(row)
        
        layout.addStretch()


class StatusBadge(QLabel):
    """Badge para status com cores semânticas"""
    
    COLORS = {
        "Excelente": {"bg": "#10b98120", "text": "#10b981", "icon": "●"},
        "Bom": {"bg": "#3b82f620", "text": "#3b82f6", "icon": "●"},
        "Regular": {"bg": "#f59e0b20", "text": "#f59e0b", "icon": "●"},
        "Fraco": {"bg": "#ef444420", "text": "#ef4444", "icon": "●"},
        "Desconhecido": {"bg": "#94a3b820", "text": "#64748b", "icon": "○"}
    }
    
    def __init__(self, status: str, parent=None):
        super().__init__(parent)
        self.status = status
        self.setup_ui()
    
    def setup_ui(self):
        color = self.COLORS.get(self.status, self.COLORS["Desconhecido"])
        
        self.setText(f"{color['icon']} {self.status}")
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color['bg']};
                color: {color['text']};
                border-radius: 20px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)


class SecurityBadge(QFrame):
    """Badge para informações de segurança"""
    
    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        self.label = label
        self.value = value
        self.setup_ui()
    
    def setup_ui(self):
        is_good = "sim" in self.value.lower() or "ativado" in self.value.lower() or "suportado" in self.value.lower()
        color = "#10b981" if is_good else "#f59e0b" if "não" in self.value.lower() else "#64748b"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color}10;
                border: 1px solid {color}30;
                border-radius: 12px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)
        
        # Ícone
        icon = qta.icon('fa5s.shield-alt' if is_good else 'fa5s.exclamation-triangle', color=color)
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(14, 14))
        layout.addWidget(icon_label)
        
        # Texto
        text = QLabel(f"{self.label}: {self.value}")
        text.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 500;")
        layout.addWidget(text)


class FrequencyIndicator(QFrame):
    """Indicador visual de frequências"""
    
    def __init__(self, frequencies: str, parent=None):
        super().__init__(parent)
        self.frequencies = frequencies
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border-radius: 12px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)
        
        # Ícone
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.signal', color='#3b82f6').pixmap(14, 14))
        layout.addWidget(icon_label)
        
        # Texto
        text = QLabel(self.frequencies)
        text.setStyleSheet("color: #0f172a; font-size: 11px; font-weight: 500;")
        layout.addWidget(text)


class SignalStrengthIndicator(QWidget):
    """Indicador visual de força do sinal"""
    
    def __init__(self, strength: int, parent=None):
        super().__init__(parent)
        self.strength = min(100, max(0, strength))
        self.setFixedSize(40, 20)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Determinar cor baseada na força
        if self.strength >= 80:
            color = QColor("#10b981")
        elif self.strength >= 60:
            color = QColor("#3b82f6")
        elif self.strength >= 40:
            color = QColor("#f59e0b")
        else:
            color = QColor("#ef4444")
        
        # Desenhar barras
        bar_width = 6
        spacing = 2
        x = 0
        
        for i in range(4):
            height = 6 + (i * 4)
            y = self.height() - height
            
            if self.strength >= (i + 1) * 25:
                painter.setBrush(color)
                painter.setPen(color)
            else:
                painter.setBrush(QColor("#e2e8f0"))
                painter.setPen(QColor("#e2e8f0"))
            
            painter.drawRoundedRect(x, y, bar_width, height, 2, 2)
            x += bar_width + spacing