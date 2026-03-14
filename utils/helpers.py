"""
Funções utilitárias para a aplicação DarkFeather WiFi Analysis
"""

from typing import Dict, Any, Tuple
from core.scanner import WifiNetwork


def network_to_dict(network: WifiNetwork) -> Dict[str, Any]:
    """Converte objeto WifiNetwork para dicionário"""
    return {
        "SSID": network.ssid,
        "Autenticação": network.auth,
        "Qualidade": network.signal_quality,
        "Criptografia": network.encryption,
        "Chave (ASCII)": network.password if network.password else "********",
        "Chave (HEX)": network.password_hex if network.password_hex else "",
        "Última Conexão": network.last_connection if network.last_connection else "N/A"
    }


def get_signal_color(quality: str) -> str:
    """
    Retorna a cor correspondente à qualidade do sinal
    """
    colors = {
        "Excelente": "#10b981",
        "Bom": "#f59e0b",
        "Regular": "#f97316",
        "Fraco": "#ef4444",
        "Desconhecido": "#94a3b8"
    }
    return colors.get(quality, "#94a3b8")


def format_signal_quality(quality: str) -> Tuple[str, str]:
    """
    Formata a qualidade do sinal para exibição
    Retorna (texto_formatado, cor)
    """
    color = get_signal_color(quality)
    
    indicators = {
        "Excelente": "🟢",
        "Bom": "🟡",
        "Regular": "🟠",
        "Fraco": "🔴",
        "Desconhecido": "⚪"
    }
    
    indicator = indicators.get(quality, "⚪")
    return f"{indicator} {quality}", color


def mask_password(password: str, show_last: int = 4) -> str:
    """
    Mascara uma senha, mostrando apenas os últimos caracteres
    """
    if not password or password == "********":
        return "********"
    
    if len(password) <= show_last:
        return "*" * len(password)
    
    return "*" * (len(password) - show_last) + password[-show_last:]