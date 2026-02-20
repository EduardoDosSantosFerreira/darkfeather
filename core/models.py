"""
Modelos de dados para a aplicação DarkFeather WiFi Analysis
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class WiFiNetwork:
    """
    Modelo representando uma rede WiFi
    """
    ssid: str
    auth: str
    quality: str
    encryption: str
    password_ascii: str = "********"
    password_hex: str = ""
    last_connection: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WiFiNetwork':
        """Cria uma instância a partir de um dicionário"""
        return cls(
            ssid=data.get("SSID", "Desconhecido"),
            auth=data.get("Autenticação", "Desconhecido"),
            quality=data.get("Qualidade", "Desconhecido"),
            encryption=data.get("Criptografia", "Desconhecido"),
            password_ascii=data.get("Chave (ASCII)", "********"),
            password_hex=data.get("Chave (HEX)", ""),
            last_connection=data.get("Última Conexão", "")
        )
    
    def to_dict(self) -> dict:
        """Converte a instância para dicionário"""
        return {
            "SSID": self.ssid,
            "Autenticação": self.auth,
            "Qualidade": self.quality,
            "Criptografia": self.encryption,
            "Chave (ASCII)": self.password_ascii,
            "Chave (HEX)": self.password_hex,
            "Última Conexão": self.last_connection
        }