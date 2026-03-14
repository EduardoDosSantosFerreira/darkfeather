"""
Módulo para coleta de informações avançadas de rede
"""
import subprocess
import re
import socket
import struct
import time
from typing import Dict, List, Optional, Tuple
import ctypes
from ctypes import wintypes


class NetworkInfoCollector:
    """
    Coletor de informações avançadas de rede usando APIs do Windows
    """
    
    @staticmethod
    def get_interface_detailed() -> Dict[str, str]:
        """
        Obtém informações detalhadas da interface de rede
        """
        info = {
            "name": "N/A",
            "description": "N/A",
            "mac": "N/A",
            "ipv4": "N/A",
            "ipv6": "N/A",
            "subnet": "N/A",
            "gateway": "N/A",
            "dns": "N/A",
            "dhcp": "N/A",
            "mtu": "N/A",
            "speed": "N/A",
            "bytes_sent": "N/A",
            "bytes_received": "N/A",
            "packets_sent": "N/A",
            "packets_received": "N/A"
        }
        
        try:
            # Usar ipconfig para informações básicas
            result = subprocess.run(
                ["ipconfig", "/all"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                output = result.stdout
                sections = re.split(r'\r?\n\r?\n', output)
                
                for section in sections:
                    if "wi-fi" in section.lower() or "wireless" in section.lower() or "wlan" in section.lower():
                        
                        # Descrição
                        desc_match = re.search(r'Descrição[ .]*:?\s*(.+)', section, re.IGNORECASE)
                        if desc_match:
                            info["description"] = desc_match.group(1).strip()
                        
                        # MAC
                        mac_match = re.search(r'Endereço físico[ .]*:?\s*([0-9A-Fa-f:-]+)', section, re.IGNORECASE)
                        if mac_match:
                            info["mac"] = mac_match.group(1).strip().upper()
                        
                        # DHCP
                        dhcp_match = re.search(r'DHCP (?:ativado|habilitado)[ .]*:?\s*(.+)', section, re.IGNORECASE)
                        if dhcp_match:
                            info["dhcp"] = "Sim" if "sim" in dhcp_match.group(1).lower() else "Não"
                        
                        # IPv4
                        ip_match = re.search(r'Endereço IPv4[ .]*:?\s*([0-9.]+)', section, re.IGNORECASE)
                        if ip_match:
                            info["ipv4"] = ip_match.group(1)
                        
                        # IPv6
                        ip6_match = re.search(r'Endereço IPv6[ .]*:?\s*([0-9a-f:]+)', section, re.IGNORECASE)
                        if ip6_match:
                            info["ipv6"] = ip6_match.group(1)
                        
                        # Máscara
                        mask_match = re.search(r'Máscara de sub-rede[ .]*:?\s*([0-9.]+)', section, re.IGNORECASE)
                        if mask_match:
                            info["subnet"] = mask_match.group(1)
                        
                        # Gateway
                        gw_match = re.search(r'Gateway padrão[ .]*:?\s*([0-9.]+)', section, re.IGNORECASE)
                        if gw_match:
                            info["gateway"] = gw_match.group(1)
                        
                        # DNS
                        dns_list = []
                        dns_matches = re.findall(r'Servidores? DNS[ .]*:?\s*([0-9.]+)', section, re.IGNORECASE)
                        for dns in dns_matches[:3]:
                            dns_list.append(dns)
                        
                        if dns_list:
                            info["dns"] = ", ".join(dns_list)
                        
                        # MTU
                        mtu_match = re.search(r'MTU[ .]*:?\s*(\d+)', section, re.IGNORECASE)
                        if mtu_match:
                            info["mtu"] = mtu_match.group(1)
                        
                        break
        
        except Exception as e:
            pass
        
        return info
    
    @staticmethod
    def get_wlan_statistics() -> Dict[str, str]:
        """
        Obtém estatísticas da conexão WLAN atual
        """
        stats = {
            "signal": "N/A",
            "tx_rate": "N/A",
            "rx_rate": "N/A",
            "channel": "N/A",
            "frequency": "N/A",
            "band": "N/A",
            "bssid": "N/A",
            "phy": "N/A",
            "auth": "N/A",
            "cipher": "N/A"
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
                
                # Sinal
                signal_match = re.search(r'Sinal\s*:\s*(\d+)%', output, re.MULTILINE | re.IGNORECASE)
                if signal_match:
                    stats["signal"] = signal_match.group(1) + "%"
                
                # RSSI
                rssi_match = re.search(r'RSSI\s*:\s*(-?\d+)', output, re.MULTILINE | re.IGNORECASE)
                if rssi_match:
                    stats["rssi"] = rssi_match.group(1) + " dBm"
                
                # Taxas
                tx_match = re.search(r'Velocidade de transmissão[^:]*:\s*(\d+[.,]?\d*)\s*\(?[Mm]bps\)?', 
                                     output, re.MULTILINE | re.IGNORECASE)
                if tx_match:
                    stats["tx_rate"] = tx_match.group(1).replace(',', '.') + " Mbps"
                
                rx_match = re.search(r'Velocidade de recebimento[^:]*:\s*(\d+[.,]?\d*)\s*\(?[Mm]bps\)?', 
                                     output, re.MULTILINE | re.IGNORECASE)
                if rx_match:
                    stats["rx_rate"] = rx_match.group(1).replace(',', '.') + " Mbps"
                
                # Canal
                channel_match = re.search(r'Canal\s*:\s*(\d+)', output, re.MULTILINE | re.IGNORECASE)
                if channel_match:
                    stats["channel"] = channel_match.group(1)
                
                # BSSID
                bssid_match = re.search(r'BSSID\s*:\s*([0-9A-Fa-f:-]+)', output, re.MULTILINE | re.IGNORECASE)
                if bssid_match:
                    stats["bssid"] = bssid_match.group(1).strip().upper()
                
                # PHY
                phy_match = re.search(r'Tipo de rádio\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
                if phy_match:
                    stats["phy"] = phy_match.group(1).strip()
                
                # Autenticação
                auth_match = re.search(r'Autenticação\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
                if auth_match:
                    stats["auth"] = auth_match.group(1).strip()
                
                # Criptografia
                cipher_match = re.search(r'Cifra\s*:\s*(.+)$', output, re.MULTILINE | re.IGNORECASE)
                if cipher_match:
                    stats["cipher"] = cipher_match.group(1).strip()
        
        except Exception as e:
            pass
        
        return stats
    
    @staticmethod
    def get_arp_table() -> List[Dict[str, str]]:
        """
        Obtém a tabela ARP do sistema
        """
        arp_entries = []
        
        try:
            result = subprocess.run(
                ["arp", "-a"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    match = re.search(r'([0-9.]+)\s+([0-9a-f-]+)\s+(\S+)', line, re.IGNORECASE)
                    if match:
                        arp_entries.append({
                            "ip": match.group(1),
                            "mac": match.group(2).replace('-', ':').upper(),
                            "type": match.group(3)
                        })
        
        except Exception:
            pass
        
        return arp_entries
    
    @staticmethod
    def get_route_table() -> List[Dict[str, str]]:
        """
        Obtém a tabela de roteamento
        """
        routes = []
        
        try:
            result = subprocess.run(
                ["route", "print"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                in_table = False
                
                for line in lines:
                    if "IPv4 Tabela de Rotas" in line or "IPv4 Route Table" in line:
                        in_table = True
                        continue
                    
                    if in_table and line.strip() and "===" not in line:
                        parts = line.split()
                        if len(parts) >= 5 and parts[0][0].isdigit():
                            routes.append({
                                "destination": parts[0],
                                "netmask": parts[1],
                                "gateway": parts[2],
                                "interface": parts[3],
                                "metric": parts[4]
                            })
        
        except Exception:
            pass
        
        return routes
    
    @staticmethod
    def get_connection_uptime() -> Optional[int]:
        """
        Obtém o tempo de conexão em segundos
        """
        try:
            result = subprocess.run(
                ["netstat", "-e"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                # Não é possível obter uptime diretamente do netstat
                # Retornar None por enquanto
                pass
        
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def ping_test(host: str = "8.8.8.8", count: int = 4) -> Dict[str, float]:
        """
        Realiza teste de ping para um host
        """
        results = {
            "min": None,
            "max": None,
            "avg": None,
            "loss": 100
        }
        
        try:
            result = subprocess.run(
                ["ping", "-n", str(count), host],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Estatísticas de tempo
                stats_match = re.search(r'M[íi]nimo[ =]+(\d+)ms[ ,]+M[áa]ximo[ =]+(\d+)ms[ ,]+M[ée]dio[ =]+(\d+)ms', 
                                        output, re.IGNORECASE)
                if stats_match:
                    results["min"] = float(stats_match.group(1))
                    results["max"] = float(stats_match.group(2))
                    results["avg"] = float(stats_match.group(3))
                
                # Perda de pacotes
                loss_match = re.search(r'(\d+)%[^0-9]*perd[ai]d[ao]', output, re.IGNORECASE)
                if loss_match:
                    results["loss"] = float(loss_match.group(1))
        
        except Exception:
            pass
        
        return results