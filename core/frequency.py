"""
Módulo de detecção de frequência real de redes WiFi
Utiliza APIs do Windows para obter dados reais do sistema
"""
import subprocess
import re
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FrequencyInfo:
    """Informações reais de frequência de uma rede"""
    ssid: str
    frequency_mhz: Optional[int] = None
    channel: Optional[int] = None
    band: Optional[str] = None  # "2.4 GHz", "5 GHz", "6 GHz"
    bssid: Optional[str] = None
    signal_percent: Optional[int] = None
    channel_width: Optional[int] = None  # Largura do canal em MHz
    
    @property
    def band_color(self) -> str:
        """Retorna a cor do badge baseado na banda"""
        if self.band == "2.4 GHz":
            return "#3b82f6"  # Azul
        elif self.band == "5 GHz":
            return "#8b5cf6"  # Roxo
        elif self.band == "6 GHz":
            return "#ec4899"  # Rosa
        return "#94a3b8"  # Cinza


class FrequencyDetector:
    """
    Detector real de frequência WiFi
    Utiliza netsh wlan show networks mode=bssid para obter dados reais
    """
    
    # Mapeamento de canais para frequências (MHz)
    CHANNEL_TO_FREQ = {
        # 2.4 GHz
        1: 2412, 2: 2417, 3: 2422, 4: 2427, 5: 2432,
        6: 2437, 7: 2442, 8: 2447, 9: 2452, 10: 2457,
        11: 2462, 12: 2467, 13: 2472, 14: 2484,
        # 5 GHz
        36: 5180, 40: 5200, 44: 5220, 48: 5240,
        52: 5260, 56: 5280, 60: 5300, 64: 5320,
        100: 5500, 104: 5520, 108: 5540, 112: 5560,
        116: 5580, 120: 5600, 124: 5620, 128: 5640,
        132: 5660, 136: 5680, 140: 5700, 144: 5720,
        149: 5745, 153: 5765, 157: 5785, 161: 5805, 165: 5825,
        # 6 GHz
        1: 5955, 5: 5975, 9: 5995, 13: 6015, 17: 6035,
        21: 6055, 25: 6075, 29: 6095, 33: 6115, 37: 6135,
        41: 6155, 45: 6175, 49: 6195, 53: 6215, 57: 6235,
        61: 6255, 65: 6275, 69: 6295, 73: 6315, 77: 6335,
        81: 6355, 85: 6375, 89: 6395, 93: 6415, 97: 6435,
        101: 6455, 105: 6475, 109: 6495, 113: 6515, 117: 6535,
        121: 6555, 125: 6575, 129: 6595, 133: 6615, 137: 6635,
        141: 6655, 145: 6675, 149: 6695, 153: 6715, 157: 6735,
        161: 6755, 165: 6775, 169: 6795, 173: 6815, 177: 6835,
        181: 6855, 185: 6875, 189: 6895, 193: 6915, 197: 6935,
        201: 6955, 205: 6975, 209: 6995, 213: 7015, 217: 7035,
        221: 7055, 225: 7075, 229: 7095, 233: 7115
    }
    
    # Largura de canal por banda
    CHANNEL_WIDTH = {
        "2.4 GHz": 20,
        "5 GHz": [20, 40, 80, 160],
        "6 GHz": [20, 40, 80, 160, 320]
    }
    
    @classmethod
    def get_band_from_channel(cls, channel: int) -> str:
        """Determina a banda baseada no canal"""
        if 1 <= channel <= 14:
            return "2.4 GHz"
        elif 36 <= channel <= 165:
            return "5 GHz"
        elif channel >= 1 and channel <= 233 and channel not in range(1, 15) and channel not in range(36, 166):
            return "6 GHz"
        return "2.4 GHz"
    
    @classmethod
    def run_netsh_bssid(cls) -> str:
        """
        Executa netsh wlan show networks mode=bssid
        Este comando mostra todas as redes com detalhes de BSSID, canal e sinal
        """
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            if result.returncode == 0:
                return result.stdout
            return ""
        except Exception as e:
            return ""
    
    @classmethod
    def parse_bssid_output(cls, output: str) -> Dict[str, List[FrequencyInfo]]:
        """
        Parseia a saída do netsh bssid e retorna dicionário de frequências
        """
        frequencies = {}
        
        if not output:
            return frequencies
        
        lines = output.split('\n')
        i = 0
        current_ssid = None
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Encontra SSID
            if "SSID" in line and ":" in line and "BSSID" not in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    ssid_part = parts[1].strip()
                    if ssid_part and not ssid_part.startswith(" "):
                        current_ssid = ssid_part
                        i += 1
                        continue
            
            # Processa BSSID e informações
            if current_ssid and "BSSID" in line and ":" in line:
                bssid_parts = line.split(':', 1)
                if len(bssid_parts) > 1:
                    bssid = bssid_parts[1].strip()
                    
                    # Pula para próxima linha para pegar o canal
                    i += 1
                    channel = None
                    signal = None
                    channel_width = None
                    
                    # Procura canal nas próximas linhas
                    while i < len(lines) and "BSSID" not in lines[i]:
                        current_line = lines[i].strip()
                        
                        if "Canal" in current_line or "Channel" in current_line:
                            channel_match = re.search(r':\s*(\d+)', current_line)
                            if channel_match:
                                channel = int(channel_match.group(1))
                        
                        if "Sinal" in current_line or "Signal" in current_line:
                            signal_match = re.search(r':\s*(\d+)%', current_line)
                            if signal_match:
                                signal = int(signal_match.group(1))
                        
                        # Tentar detectar largura de canal
                        if "Largura" in current_line or "Width" in current_line:
                            width_match = re.search(r':\s*(\d+)', current_line)
                            if width_match:
                                channel_width = int(width_match.group(1))
                        
                        i += 1
                    
                    # Se encontrou canal, adiciona frequência
                    if channel:
                        band = cls.get_band_from_channel(channel)
                        freq = cls.CHANNEL_TO_FREQ.get(channel, None)
                        
                        freq_info = FrequencyInfo(
                            ssid=current_ssid,
                            frequency_mhz=freq,
                            channel=channel,
                            band=band,
                            bssid=bssid,
                            signal_percent=signal,
                            channel_width=channel_width
                        )
                        
                        if current_ssid not in frequencies:
                            frequencies[current_ssid] = []
                        
                        # Evitar duplicatas do mesmo canal
                        if not any(f.channel == channel for f in frequencies[current_ssid]):
                            frequencies[current_ssid].append(freq_info)
                    
                    continue
            i += 1
        
        return frequencies
    
    @classmethod
    def scan_frequencies(cls) -> Dict[str, List[FrequencyInfo]]:
        """
        Escaneia frequências reais de todas as redes visíveis
        """
        output = cls.run_netsh_bssid()
        return cls.parse_bssid_output(output)


class RealFrequencyDetector:
    """
    Detector de frequência que usa dados reais do sistema
    """
    
    def __init__(self):
        self.cache = {}
        self.last_scan = 0
        self.cache_ttl = 30  # segundos
    
    def scan_current_networks(self) -> Dict[str, List[FrequencyInfo]]:
        """
        Escaneia redes atualmente visíveis com frequências reais
        """
        current_time = time.time()
        
        # Usa cache se ainda válido
        if current_time - self.last_scan < self.cache_ttl and self.cache:
            return self.cache
        
        # Escaneia frequências reais
        self.cache = FrequencyDetector.scan_frequencies()
        self.last_scan = current_time
        
        return self.cache
    
    def get_network_frequencies(self, ssid: str) -> List[FrequencyInfo]:
        """
        Obtém frequências reais para uma rede específica
        """
        networks = self.scan_current_networks()
        
        # Busca exata
        if ssid in networks:
            return networks[ssid]
        
        # Busca case-insensitive
        for net_ssid, infos in networks.items():
            if net_ssid.lower() == ssid.lower():
                return infos
        
        return []
    
    def clear_cache(self):
        """Limpa o cache de frequências"""
        self.cache = {}
        self.last_scan = 0