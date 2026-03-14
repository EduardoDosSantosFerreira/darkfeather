"""
Gerenciador de temas para a aplicação DarkFeather WiFi Analysis
TEMA ORIGINAL
"""

from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt


class UIThemeManager:
    """
    Gerencia o tema e estilos da interface - TEMA ORIGINAL
    """
    
    def __init__(self):
        self.colors = {
            'bg_primary': '#f8fafc',      # Fundo principal cinza claro
            'bg_secondary': '#ffffff',      # Fundo branco
            'bg_tertiary': '#f1f5f9',       # Fundo cinza para cards
            'text_primary': '#0f172a',      # Texto principal preto
            'text_secondary': '#334155',     # Texto secundário cinza escuro
            'text_tertiary': '#64748b',      # Texto terciário cinza
            'text_muted': '#94a3b8',         # Texto muted
            'border_light': '#e2e8f0',       # Borda clara
            'border_medium': '#cbd5e1',      # Borda média
            'primary': '#2563eb',            # Azul principal
            'primary_hover': '#1d4ed8',      # Azul hover
            'primary_pressed': '#1e40af',    # Azul pressed
            'success': '#10b981',             # Verde
            'warning': '#f59e0b',             # Laranja
            'danger': '#ef4444',               # Vermelho
            'info': '#3b82f6',                  # Azul info
            'purple': '#8b5cf6',                # Roxo
            'pink': '#ec4899'                    # Rosa
        }
    
    def get_main_window_style(self) -> str:
        return f"""
            QMainWindow {{
                background-color: {self.colors['bg_primary']};
            }}
            QWidget#centralWidget {{
                background-color: {self.colors['bg_primary']};
            }}
        """
    
    def get_button_style(self, button_type: str = "default") -> str:
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
            """
        else:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {self.colors['text_secondary']};
                    border: 1px solid {self.colors['border_light']};
                    border-radius: 8px;
                    font-weight: 500;
                    font-size: 12px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['bg_tertiary']};
                }}
            """
    
    def get_palette(self) -> QPalette:
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