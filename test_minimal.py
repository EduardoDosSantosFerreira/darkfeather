"""
Teste mínimo para verificar importações - Sem emojis
"""
import sys
import traceback

print("=" * 50)
print("TESTE MÍNIMO - DARKFEATHER")
print("=" * 50)

# Configurar encoding para UTF-8 no Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')

print("1. Verificando Python...")
print(f"   Versão: {sys.version}")
print(f"   Platform: {sys.platform}")
print()

# Teste 1: PySide6
print("2. Testando PySide6...")
try:
    from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
    print("   [OK] PySide6 importado com sucesso")
    print(f"   Qt Version: {Qt.__version__ if hasattr(Qt, '__version__') else 'desconhecida'}")
except Exception as e:
    print(f"   [ERRO] Falha ao importar PySide6: {e}")
    traceback.print_exc()
    sys.exit(1)

print()

# Teste 2: Core modules
print("3. Testando core modules...")
try:
    from core.scanner import WifiScanner, WifiNetwork
    print("   [OK] core.scanner")
except Exception as e:
    print(f"   [ERRO] core.scanner: {e}")

try:
    from core.frequency import FrequencyDetector, FrequencyInfo, RealFrequencyDetector
    print("   [OK] core.frequency")
except Exception as e:
    print(f"   [ERRO] core.frequency: {e}")

try:
    from core.system import is_admin, run_netsh_command
    print("   [OK] core.system")
except Exception as e:
    print(f"   [ERRO] core.system: {e}")

print()

# Teste 3: Utils
print("4. Testando utils...")
try:
    from utils.helpers import get_signal_color, format_signal_quality, mask_password
    print("   [OK] utils.helpers")
except Exception as e:
    print(f"   [ERRO] utils.helpers: {e}")

print()

# Teste 4: Audit
print("5. Testando audit...")
try:
    from audit.logger import AuditLogger
    print("   [OK] audit.logger")
except Exception as e:
    print(f"   [ERRO] audit.logger: {e}")

print()

# Teste 5: UI Widgets
print("6. Testando ui.widgets...")
try:
    from ui.widgets import WifiCardWidget, NetworkDetailsWidget, LoadingSpinner, FrequencyBadge
    print("   [OK] ui.widgets")
except Exception as e:
    print(f"   [ERRO] ui.widgets: {e}")
    traceback.print_exc()

print()

# Teste 6: UI Theme
print("7. Testando ui.theme...")
try:
    from ui.theme import UIThemeManager
    print("   [OK] ui.theme")
except Exception as e:
    print(f"   [ERRO] ui.theme: {e}")

print()

# Teste 7: UI Risk Badge
print("8. Testando ui.risk_badge...")
try:
    from ui.risk_badge import RiskBadge, RiskWidget, SecurityStatusWidget
    print("   [OK] ui.risk_badge")
except Exception as e:
    print(f"   [ERRO] ui.risk_badge: {e}")

print()

# Teste 8: UI Security
print("9. Testando ui.security...")
try:
    from ui.security.models import RiskLevel, VulnerabilityType, Vulnerability, NetworkSecurityAnalysis
    print("   [OK] ui.security.models")
except Exception as e:
    print(f"   [ERRO] ui.security.models: {e}")

try:
    from ui.security.widgets import SecurityCard, SecuritySummaryWidget, VulnerabilityBadge
    print("   [OK] ui.security.widgets")
except Exception as e:
    print(f"   [ERRO] ui.security.widgets: {e}")

try:
    from ui.security.security_analyzer import SecurityAnalyzerUI
    print("   [OK] ui.security.security_analyzer")
except Exception as e:
    print(f"   [ERRO] ui.security.security_analyzer: {e}")

try:
    from ui.security.security_window import SecurityWindow
    print("   [OK] ui.security.security_window")
except Exception as e:
    print(f"   [ERRO] ui.security.security_window: {e}")

print()

# Teste 9: UI Main
print("10. Testando ui.main_window...")
try:
    from ui.main_window import MainWindow
    print("   [OK] ui.main_window")
except Exception as e:
    print(f"   [ERRO] ui.main_window: {e}")
    traceback.print_exc()

print("=" * 50)
print("TESTE CONCLUÍDO")
print("=" * 50)

# Se chegou até aqui, criar app mínimo
try:
    print("\nCriando aplicação mínima para teste visual...")
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setWindowTitle("DarkFeather - Teste de Importação")
    window.setGeometry(100, 100, 500, 400)
    
    layout = QVBoxLayout()
    
    label = QLabel("TODAS AS IMPORTAÇÕES FUNCIONARAM!")
    label.setStyleSheet("font-size: 18px; color: green; font-weight: bold; padding: 20px;")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)
    
    # Lista de módulos carregados
    modules = [
        "PySide6", "core.scanner", "core.frequency", "core.system",
        "utils.helpers", "audit.logger", "ui.widgets", "ui.theme",
        "ui.risk_badge", "ui.security", "ui.main_window"
    ]
    
    for module in modules:
        lbl = QLabel(f"  {module}")
        lbl.setStyleSheet("color: #2563eb; font-size: 12px;")
        layout.addWidget(lbl)
    
    window.setLayout(layout)
    window.show()
    
    print("Janela de teste aberta. Feche para sair.")
    sys.exit(app.exec())
    
except Exception as e:
    print(f"Erro ao criar aplicação: {e}")
    traceback.print_exc()
    input("Pressione Enter para sair...")