# core/__init__.py - Adicionar módulos de hotspot

"""Módulo central para DarkFeather WiFi Analysis"""

from core.scanner import WifiScanner, WifiNetwork
from core.frequency import FrequencyDetector, FrequencyInfo, RealFrequencyDetector
from core.system import is_admin, run_netsh_command, get_all_wifi_profiles
from core.security import SecurityAnalyzer
from core.network_info import NetworkInfoCollector
from core.hotspot import MobileHotspotController, HotspotStatus, HotspotConfig  # NOVO
from core.hotspot_worker import HotspotStatusWorker, HotspotOperationWorker  # NOVO

__all__ = [
    'WifiScanner',
    'WifiNetwork',
    'FrequencyDetector',
    'FrequencyInfo',
    'RealFrequencyDetector',
    'is_admin',
    'run_netsh_command',
    'get_all_wifi_profiles',
    'SecurityAnalyzer',
    'NetworkInfoCollector',
    'MobileHotspotController',    # NOVO
    'HotspotStatus',              # NOVO
    'HotspotConfig',              # NOVO
    'HotspotStatusWorker',        # NOVO
    'HotspotOperationWorker'      # NOVO
]