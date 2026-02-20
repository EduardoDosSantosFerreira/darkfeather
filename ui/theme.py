"""
Gerenciador de temas para a aplicação DarkFeather WiFi Analysis
"""

from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt


class UIThemeManager:
    """
    Gerencia o tema e estilos da interface
    """
    
    def __init__(self):
        self.colors = {
            'bg_primary': '#f3f4f6',
            'bg_secondary': '#ffffff',
            'bg_tertiary': '#f8fafc',
            'text_primary': '#0f172a',
            'text_secondary': '#334155',
            'text_tertiary': '#64748b',
            'text_muted': '#94a3b8',
            'border_light': '#e2e8f0',
            'border_medium': '#cbd5e1',
            'primary': '#2563eb',
            'primary_hover': '#1d4ed8',
            'primary_pressed': '#1e40af',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#3b82f6'
        }
    
    def get_main_window_style(self) -> str:
        """Retorna o estilo da janela principal"""
        return f"""
            QMainWindow {{
                background-color: {self.colors['bg_primary']};
            }}
            QWidget#centralWidget {{
                background-color: {self.colors['bg_primary']};
            }}
        """
    
    def get_button_style(self, button_type: str = "default") -> str:
        """Retorna estilo para botões"""
        if button_type == "primary":
            return f"""
                QPushButton {{
                    background-color: {self.colors['primary']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 12px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['primary_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {self.colors['primary_pressed']};
                }}
                QPushButton:disabled {{
                    background-color: {self.colors['border_light']};
                    color: {self.colors['text_muted']};
                }}
            """
        elif button_type == "secondary":
            return f"""
                QPushButton {{
                    background-color: {self.colors['bg_secondary']};
                    color: {self.colors['text_secondary']};
                    border: 1px solid {self.colors['border_light']};
                    border-radius: 8px;
                    font-weight: 500;
                    font-size: 12px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['bg_tertiary']};
                    border-color: {self.colors['border_medium']};
                }}
                QPushButton:pressed {{
                    background-color: {self.colors['border_light']};
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {self.colors['text_secondary']};
                    border: none;
                    border-radius: 8px;
                    font-weight: 500;
                    font-size: 12px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['bg_tertiary']};
                }}
                QPushButton:pressed {{
                    background-color: {self.colors['border_light']};
                }}
            """
    
    def get_palette(self) -> QPalette:
        """Retorna a paleta de cores da aplicação"""
        palette = QPalette()
        
        palette.setColor(QPalette.ColorRole.Window, QColor(self.colors['bg_primary']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(self.colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Base, QColor(self.colors['bg_secondary']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(self.colors['bg_tertiary']))
        palette.setColor(QPalette.ColorRole.Text, QColor(self.colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Button, QColor(self.colors['bg_secondary']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(self.colors['text_secondary']))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(self.colors['primary']))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        return palette