"""
Scanner de redes WiFi REAL para a aplicação DarkFeather WiFi Analysis
Usa netsh do Windows para obter dados reais do sistema
"""

import subprocess
import re
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal, QRunnable, Slot
import traceback

from core.frequency import RealFrequencyDetector, FrequencyInfo


@dataclass
class WifiNetwork:
    """Modelo de dados para rede WiFi real"""
    ssid: str
    auth: str
    encryption: str
    password: Optional[str] = None
    password_hex: Optional[str] = None
    last_connection: Optional[str] = None
    signal_quality: str = "Desconhecido"
    frequencies: List[FrequencyInfo] = None
    
    def __post_init__(self):
        if self.frequencies is None:
            self.frequencies = []
    
    @property
    def bands(self) -> List[str]:
        """Retorna lista de bandas (2.4 GHz, 5 GHz, 6 GHz)"""
        return list(set([f.band for f in self.frequencies if f.band]))
    
    @property
    def has_5ghz(self) -> bool:
        return "5 GHz" in self.bands
    
    @property
    def has_6ghz(self) -> bool:
        return "6 GHz" in self.bands
    
    @property
    def has_24ghz(self) -> bool:
        return "2.4 GHz" in self.bands


class WifiScannerWorker(QRunnable):
    """
    Worker para executar o scan em thread separada
    """
    
    class Signals(QObject):
        finished = Signal(object)  # List[WifiNetwork]
        error = Signal(str)
        progress = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.signals = self.Signals()
        self.freq_detector = RealFrequencyDetector()
    
    @Slot()
    def run(self):
        """Executa o scan em thread separada"""
        try:
            self.signals.progress.emit("Iniciando scan de redes Wi-Fi...")
            
            # Escaneia frequências primeiro
            self.signals.progress.emit("Detectando frequências das redes...")
            freq_data = self.freq_detector.scan_current_networks()
            
            # Depois obtém os perfis
            networks = self.scan_real_networks(freq_data)
            
            self.signals.finished.emit(networks)
        except Exception as e:
            error_msg = f"Erro no scan: {str(e)}"
            print(error_msg)
            self.signals.error.emit(f"Falha ao escanear redes: {str(e)}")
    
    def scan_real_networks(self, freq_data: Dict[str, List[FrequencyInfo]]) -> List[WifiNetwork]:
        """
        Escaneia redes WiFi REAIS do Windows
        """
        networks = []
        
        # Listar todos os perfis reais
        profiles = self.get_real_profiles()
        
        if not profiles:
            print("Nenhum perfil WiFi encontrado no sistema")
            return []
        
        self.signals.progress.emit(f"Encontrados {len(profiles)} perfis")
        
        # Para cada perfil, obter detalhes reais
        for profile_name in profiles:
            try:
                network = self.get_real_network_details(profile_name)
                
                # Adicionar frequências reais
                if network:
                    if profile_name in freq_data:
                        network.frequencies = freq_data[profile_name]
                    else:
                        # Tenta buscar por SSID similar
                        for freq_ssid, freqs in freq_data.items():
                            if freq_ssid.lower() == profile_name.lower():
                                network.frequencies = freqs
                                break
                    
                    networks.append(network)
                
                time.sleep(0.05)  # Pequena pausa
                
            except Exception as e:
                print(f"Erro ao processar perfil {profile_name}: {e}")
                continue
        
        # Ordenar por nome
        networks.sort(key=lambda x: x.ssid.lower())
        
        self.signals.progress.emit(f"Processadas {len(networks)} redes")
        return networks
    
    def get_real_profiles(self) -> List[str]:
        """
        Obtém lista REAL de perfis WiFi do Windows
        """
        profiles = []
        
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "profiles"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode != 0:
                return []
            
            output = result.stdout
            
            # Extrair nomes dos perfis
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                if ':' in line:
                    if 'perfil' in line.lower() or 'profile' in line.lower():
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            name = parts[1].strip()
                            if name and name not in profiles:
                                profiles.append(name)
            
            # Se não encontrou, tentar regex
            if not profiles:
                pattern = r":\s+(.+)$"
                matches = re.findall(pattern, output, re.MULTILINE)
                profiles = [m.strip() for m in matches if m.strip()]
            
        except Exception as e:
            print(f"Erro ao listar perfis: {e}")
        
        return profiles
    
    def get_real_network_details(self, profile_name: str) -> Optional[WifiNetwork]:
        """
        Obtém detalhes REAIS de uma rede específica
        """
        try:
            # Comando com key=clear para obter a senha
            cmd = [
                "netsh", "wlan", "show", "profile",
                f"name={profile_name}", "key=clear"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode != 0:
                return None
            
            output = result.stdout
            
            # Extrair autenticação
            auth = self.extract_field(output, [
                r"Autenticação\s*:\s*(.+)$",
                r"Authentication\s*:\s*(.+)$"
            ])
            if not auth:
                auth = "Desconhecido"
            
            # Extrair criptografia
            encryption = self.extract_field(output, [
                r"Cifra\s*:\s*(.+)$",
                r"Cipher\s*:\s*(.+)$"
            ])
            if not encryption:
                encryption = "Desconhecido"
            
            # Extrair senha
            password = self.extract_field(output, [
                r"Conteúdo da Chave\s*:\s*(.+)$",
                r"Key Content\s*:\s*(.+)$"
            ])
            
            # Gerar HEX da senha
            password_hex = None
            if password and password not in ["********", "Nenhuma", ""]:
                try:
                    password_hex = password.encode('utf-8').hex().upper()
                    if len(password_hex) > 32:
                        password_hex = password_hex[:32] + "..."
                except:
                    password_hex = None
            
            # Determinar qualidade
            signal_quality = self.determine_signal_quality(auth, password)
            
            return WifiNetwork(
                ssid=profile_name,
                auth=auth,
                encryption=encryption,
                password=password if password and password not in ["********", "Nenhuma"] else None,
                password_hex=f"[Hex {password_hex}]" if password_hex else None,
                last_connection=None,
                signal_quality=signal_quality,
                frequencies=[]
            )
            
        except Exception as e:
            print(f"Erro ao processar {profile_name}: {e}")
            return None
    
    def extract_field(self, text: str, patterns: List[str]) -> Optional[str]:
        """Extrai campo usando múltiplos padrões"""
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if value and value not in ["Nenhuma", "None", ""]:
                    return value
        return None
    
    def determine_signal_quality(self, auth: str, password: Optional[str]) -> str:
        """Determina qualidade baseado no tipo de segurança"""
        auth_lower = auth.lower()
        
        if "enterprise" in auth_lower:
            return "Bom"
        elif "wpa2" in auth_lower and password:
            return "Excelente"
        elif "wpa" in auth_lower:
            return "Bom"
        elif "wep" in auth_lower:
            return "Regular"
        elif "open" in auth_lower or "aberto" in auth_lower:
            return "Fraco"
        else:
            return "Desconhecido"


class WifiScanner(QObject):
    """
    Serviço de scan REAL de Wi-Fi
    """
    
    scan_finished = Signal(list)
    scan_error = Signal(str)
    scan_progress = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.thread_pool = None
        self.last_networks = []
    
    def scan_networks(self):
        """Inicia scan REAL em thread separada"""
        from PySide6.QtCore import QThreadPool
        
        self.thread_pool = QThreadPool.globalInstance()
        
        worker = WifiScannerWorker()
        worker.signals.finished.connect(self.on_scan_finished)
        worker.signals.error.connect(self.on_scan_error)
        worker.signals.progress.connect(self.on_scan_progress)
        
        self.thread_pool.start(worker)
    
    def on_scan_finished(self, networks):
        self.last_networks = networks
        self.scan_finished.emit(networks)
    
    def on_scan_error(self, error_msg):
        self.scan_error.emit(error_msg)
    
    def on_scan_progress(self, progress_msg):
        self.scan_progress.emit(progress_msg)