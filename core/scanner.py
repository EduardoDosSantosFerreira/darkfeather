"""
Scanner de redes WiFi REAL para a aplicação DarkFeather WiFi Analysis
Usa netsh do Windows para obter dados reais do sistema
"""

import subprocess
import re
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from PySide6.QtCore import QObject, Signal, QRunnable, Slot
import traceback

from core.frequency import RealFrequencyDetector, FrequencyInfo
from core.network_info import NetworkInfoCollector


@dataclass
class WifiNetwork:
    """Modelo de dados para rede WiFi real - EXPANDIDO"""
    ssid: str
    auth: str
    encryption: str
    password: Optional[str] = None
    password_hex: Optional[str] = None
    last_connection: Optional[str] = None
    signal_quality: str = "Desconhecido"
    frequencies: List[FrequencyInfo] = field(default_factory=list)
    
    # Novos campos
    bssid: Optional[str] = None
    channel: Optional[int] = None
    band: Optional[str] = None
    frequency_mhz: Optional[int] = None
    rssi_dbm: Optional[int] = None
    signal_percent: Optional[int] = None
    link_speed_tx: Optional[str] = None
    link_speed_rx: Optional[str] = None
    phy_type: Optional[str] = None
    channel_width: Optional[int] = None
    interface_name: Optional[str] = None
    interface_mac: Optional[str] = None
    interface_guid: Optional[str] = None
    ipv4: Optional[str] = None
    ipv6: Optional[str] = None
    subnet_mask: Optional[str] = None
    gateway: Optional[str] = None
    dns_servers: Optional[str] = None
    dhcp_enabled: Optional[str] = None
    akm: Optional[str] = None
    pmf: Optional[str] = None
    wps: Optional[str] = None
    hidden: Optional[str] = None
    vendor: Optional[str] = None
    
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
    
    @property
    def is_connected(self) -> bool:
        """Verifica se a rede está atualmente conectada"""
        return self.bssid is not None


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
        self.network_info = NetworkInfoCollector()
    
    @Slot()
    def run(self):
        """Executa o scan em thread separada"""
        try:
            self.signals.progress.emit("Iniciando scan de redes Wi-Fi...")
            
            # Escaneia frequências primeiro
            self.signals.progress.emit("Detectando frequências das redes...")
            freq_data = self.freq_detector.scan_current_networks()
            
            # Obtém informações da interface atual
            self.signals.progress.emit("Obtendo informações da interface...")
            interface_info = self.get_interface_detailed()
            
            # Depois obtém os perfis
            networks = self.scan_real_networks(freq_data, interface_info)
            
            self.signals.finished.emit(networks)
        except Exception as e:
            error_msg = f"Erro no scan: {str(e)}"
            print(error_msg)
            self.signals.error.emit(f"Falha ao escanear redes: {str(e)}")
    
    def scan_real_networks(self, freq_data: Dict[str, List[FrequencyInfo]], 
                          interface_info: Dict) -> List[WifiNetwork]:
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
        
        # Obtém informações da conexão atual
        current_connection = self.get_current_connection_info()
        
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
                    
                    # Adicionar informações da interface
                    network.interface_name = interface_info.get("name")
                    network.interface_mac = interface_info.get("mac")
                    network.interface_guid = interface_info.get("guid")
                    
                    # Se for a rede atual, adicionar informações de conexão
                    if current_connection and current_connection.get("ssid") == profile_name:
                        network.bssid = current_connection.get("bssid")
                        network.channel = current_connection.get("channel")
                        network.band = current_connection.get("band")
                        network.frequency_mhz = current_connection.get("frequency")
                        network.rssi_dbm = current_connection.get("rssi")
                        network.signal_percent = current_connection.get("signal")
                        network.link_speed_tx = current_connection.get("tx_rate")
                        network.link_speed_rx = current_connection.get("rx_rate")
                        network.phy_type = current_connection.get("phy")
                        network.channel_width = current_connection.get("channel_width")
                    
                    networks.append(network)
                
                time.sleep(0.05)
                
            except Exception as e:
                print(f"Erro ao processar perfil {profile_name}: {e}")
                continue
        
        # Ordenar por nome
        networks.sort(key=lambda x: x.ssid.lower())
        
        self.signals.progress.emit(f"Processadas {len(networks)} redes")
        return networks
    
    def get_interface_detailed(self) -> Dict:
        """Obtém informações detalhadas da interface"""
        info = {
            "name": "Não disponível",
            "mac": "Não disponível",
            "guid": "Não disponível",
            "status": "Não disponível"
        }
        
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                name_match = re.search(r'Nome\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
                if name_match:
                    info["name"] = name_match.group(1).strip()
                
                mac_match = re.search(r'Endereço físico\s*:\s*([0-9A-Fa-f:-]+)', output, re.MULTILINE | re.IGNORECASE)
                if mac_match:
                    info["mac"] = mac_match.group(1).strip().upper()
                
                guid_match = re.search(r'GUID do perfil\s*:\s*({[0-9A-F-]+})', output, re.MULTILINE | re.IGNORECASE)
                if guid_match:
                    info["guid"] = guid_match.group(1).strip()
                
                state_match = re.search(r'Estado\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
                if state_match:
                    info["status"] = state_match.group(1).strip()
        
        except Exception:
            pass
        
        return info
    
    def get_current_connection_info(self) -> Dict:
        """Obtém informações da conexão atual"""
        info = {
            "ssid": None,
            "bssid": None,
            "channel": None,
            "band": None,
            "frequency": None,
            "rssi": None,
            "signal": None,
            "tx_rate": None,
            "rx_rate": None,
            "phy": None,
            "channel_width": None
        }
        
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # SSID
                ssid_match = re.search(r'SSID\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
                if ssid_match:
                    info["ssid"] = ssid_match.group(1).strip()
                
                # BSSID
                bssid_match = re.search(r'BSSID\s*:\s*([0-9A-Fa-f:-]+)', output, re.MULTILINE | re.IGNORECASE)
                if bssid_match:
                    info["bssid"] = bssid_match.group(1).strip().upper()
                
                # Sinal
                signal_match = re.search(r'Sinal\s*:\s*(\d+)%', output, re.MULTILINE | re.IGNORECASE)
                if signal_match:
                    info["signal"] = int(signal_match.group(1))
                
                # RSSI
                rssi_match = re.search(r'RSSI\s*:\s*(-?\d+)', output, re.MULTILINE | re.IGNORECASE)
                if rssi_match:
                    info["rssi"] = int(rssi_match.group(1))
                
                # Canal e frequência
                channel_match = re.search(r'Canal\s*:\s*(\d+)', output, re.MULTILINE | re.IGNORECASE)
                if channel_match:
                    channel = int(channel_match.group(1))
                    info["channel"] = channel
                    
                    if 1 <= channel <= 14:
                        info["band"] = "2.4 GHz"
                        info["frequency"] = 2412 + (channel - 1) * 5 if channel <= 11 else 2484
                    elif 36 <= channel <= 165:
                        info["band"] = "5 GHz"
                        freq_map = {36:5180,40:5200,44:5220,48:5240,52:5260,56:5280,60:5300,64:5320,
                                   100:5500,104:5520,108:5540,112:5560,116:5580,120:5600,124:5620,128:5640,
                                   132:5660,136:5680,140:5700,144:5720,149:5745,153:5765,157:5785,161:5805,165:5825}
                        info["frequency"] = freq_map.get(channel)
                    else:
                        info["band"] = "6 GHz"
                
                # Taxas
                tx_match = re.search(r'Velocidade de transmissão[^:]*:\s*(\d+[.,]?\d*)\s*\(?[Mm]bps\)?', 
                                     output, re.MULTILINE | re.IGNORECASE)
                if tx_match:
                    info["tx_rate"] = tx_match.group(1).replace(',', '.') + " Mbps"
                
                rx_match = re.search(r'Velocidade de recebimento[^:]*:\s*(\d+[.,]?\d*)\s*\(?[Mm]bps\)?', 
                                     output, re.MULTILINE | re.IGNORECASE)
                if rx_match:
                    info["rx_rate"] = rx_match.group(1).replace(',', '.') + " Mbps"
                
                # PHY
                phy_match = re.search(r'Tipo de rádio\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
                if phy_match:
                    info["phy"] = phy_match.group(1).strip()
        
        except Exception:
            pass
        
        return info
    
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
            
            # Extrair AKM
            akm = self.extract_field(output, [
                r"Gerenciamento de chaves\s*:\s*(.+)$"
            ])
            
            # Extrair PMF
            pmf = self.extract_field(output, [
                r"PMF\s*:\s*(.+)$"
            ])
            
            # Extrair WPS
            wps = self.extract_field(output, [
                r"WPS\s*:\s*(.+)$"
            ])
            
            # Extrair SSID oculto
            hidden = self.extract_field(output, [
                r"SSID\s+oculto\s*:\s*(.+)$"
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
            
            # Obter última conexão do perfil
            last_connection = self.get_profile_last_connection(profile_name)
            
            return WifiNetwork(
                ssid=profile_name,
                auth=auth,
                encryption=encryption,
                password=password if password and password not in ["********", "Nenhuma"] else None,
                password_hex=f"[Hex {password_hex}]" if password_hex else None,
                last_connection=last_connection,
                signal_quality=signal_quality,
                frequencies=[],
                akm=akm,
                pmf=pmf,
                wps=wps,
                hidden=hidden
            )
            
        except Exception as e:
            print(f"Erro ao processar {profile_name}: {e}")
            return None
    
    def get_profile_last_connection(self, profile_name: str) -> Optional[str]:
        """Tenta obter a última conexão do perfil"""
        try:
            # Tentar obter do arquivo XML do perfil
            result = subprocess.run(
                ["netsh", "wlan", "show", "profiles", profile_name],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                output = result.stdout
                # Procurar por data de aplicação
                applied_match = re.search(r'Aplicado[^:]*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
                if applied_match:
                    return applied_match.group(1).strip()
        except:
            pass
        
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