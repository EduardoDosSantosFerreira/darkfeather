"""
Worker para operações assíncronas do Mobile Hotspot
Arquivo: core/hotspot_worker.py
"""

from PySide6.QtCore import QObject, Signal, QRunnable, Slot
import traceback
import time
from typing import Optional

from core.hotspot import MobileHotspotController, HotspotStatus, HotspotConfig


class HotspotWorkerSignals(QObject):
    """Sinais para comunicação com a UI"""
    status_updated = Signal(str)  # status text
    config_loaded = Signal(dict)  # config dict
    operation_completed = Signal(bool, str)  # success, message
    error_occurred = Signal(str)  # error message
    fallback_triggered = Signal()  # quando fallback é acionado


class HotspotStatusWorker(QRunnable):
    """
    Worker para verificar status periodicamente
    """
    
    def __init__(self, controller: MobileHotspotController):
        super().__init__()
        self.controller = controller
        self.signals = HotspotWorkerSignals()
        self._running = True
    
    @Slot()
    def run(self):
        """Loop de verificação de status"""
        while self._running:
            try:
                # Obter status
                status = self.controller.get_status()
                self.signals.status_updated.emit(status.value)
                
                # Se status mudou drasticamente, pode precisar de ação
                if status == HotspotStatus.ERROR:
                    self.signals.fallback_triggered.emit()
                
                # Aguardar antes da próxima verificação
                for _ in range(10):  # 10 * 0.1 = 1 segundo
                    if not self._running:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                self.signals.error_occurred.emit(str(e))
                time.sleep(2)
    
    def stop(self):
        """Para o worker"""
        self._running = False


class HotspotOperationWorker(QRunnable):
    """
    Worker para executar operações do hotspot
    """
    
    def __init__(self, controller: MobileHotspotController, operation: str, **kwargs):
        super().__init__()
        self.controller = controller
        self.operation = operation
        self.kwargs = kwargs
        self.signals = HotspotWorkerSignals()
    
    @Slot()
    def run(self):
        """Executa a operação"""
        try:
            success = False
            message = ""
            
            if self.operation == "start":
                success = self.controller.start_hotspot()
                message = "Hotspot iniciado" if success else "Falha ao iniciar hotspot"
                
            elif self.operation == "stop":
                success = self.controller.stop_hotspot()
                message = "Hotspot parado" if success else "Falha ao parar hotspot"
                
            elif self.operation == "configure":
                ssid = self.kwargs.get("ssid", "")
                password = self.kwargs.get("password", "")
                success = self.controller.configure_hotspot(ssid, password)
                message = "Configuração salva" if success else "Falha ao salvar configuração"
                
            elif self.operation == "get_config":
                config = self.controller.get_config()
                if config:
                    self.signals.config_loaded.emit(config.to_dict())
                    success = True
                else:
                    self.signals.error_occurred.emit("Não foi possível carregar configuração")
                    success = False
                    
            elif self.operation == "open_settings":
                success = self.controller.open_settings()
                message = "Configurações abertas" if success else "Falha ao abrir configurações"
            
            # Emitir resultado
            self.signals.operation_completed.emit(success, message)
            
            # Se falhou, sugerir fallback
            if not success and self.operation in ["start", "stop", "configure"]:
                self.signals.fallback_triggered.emit()
                
        except Exception as e:
            error_msg = f"Erro na operação {self.operation}: {str(e)}"
            self.signals.error_occurred.emit(error_msg)
            self.signals.operation_completed.emit(False, error_msg)
            self.signals.fallback_triggered.emit()