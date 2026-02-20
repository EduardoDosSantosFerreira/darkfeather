"""
DarkFeather - WiFi Analysis
Professional PySide6 Application for WiFi Network Analysis
"""

import sys
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFontDatabase
from PySide6.QtCore import Qt
from ui.main_window import MainWindow
from core.system import is_admin
from core.scanner import WifiScanner  # Corrigido: importando do local correto

def setup_application_fonts():
    """Configura a fonte padrão da aplicação"""
    font_db = QFontDatabase()
    
    # Tentar usar Segoe UI (Windows) ou Inter como fallback
    fonts = ["Segoe UI", "Inter", "Roboto", "Arial"]
    for font in fonts:
        if font in font_db.families():
            QApplication.setFont(QFontDatabase.font(font, "Regular", 10))
            break

def main():
    """Ponto de entrada principal da aplicação"""
    
    # Verificar privilégios de administrador
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()
    
    # Criar aplicação
    app = QApplication(sys.argv)
    app.setApplicationName("DarkFeather WiFi Analysis")
    app.setOrganizationName("DarkFeather")
    app.setApplicationVersion("2.0.0")
    
    # Configurar atributos da aplicação
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Configurar fonte
    setup_application_fonts()
    
    # Definir ícone da aplicação
    try:
        app.setWindowIcon(QIcon("resources/icon.ico"))
    except:
        pass
    
    # Criar e mostrar janela principal
    window = MainWindow()
    window.show()
    
    # Executar aplicação
    sys.exit(app.exec())

if __name__ == "__main__":
    main()