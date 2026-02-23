"""
DarkFeather - WiFi Analysis
Versão FINAL - Todas as importações funcionando
"""

import sys
import ctypes

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')

print("Iniciando DarkFeather...")

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from core.system import is_admin
from ui.main_window import MainWindow


def main():
    """Ponto de entrada principal"""
    
    # Verificar privilégios de administrador
    if not is_admin():
        print("Solicitando privilégios de administrador...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()
    
    # Criar aplicação
    app = QApplication(sys.argv)
    app.setApplicationName("DarkFeather WiFi Analysis")
    app.setApplicationVersion("2.0.0")
    
    # Configurar fonte
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Criar e mostrar janela principal
    window = MainWindow()
    window.show()
    
    print("Interface iniciada!")
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")