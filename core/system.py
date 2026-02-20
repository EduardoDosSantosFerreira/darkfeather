"""
Funções de sistema para interagir com o Windows
"""

import subprocess
import re
import ctypes
import os
import time  # Import adicionado
from typing import List, Dict, Any


def is_admin() -> bool:
    """Verifica se o programa está rodando como administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_netsh_command(command: List[str]) -> str:
    """
    Executa um comando netsh de forma robusta
    """
    try:
        # Tentar com diferentes codificações
        encodings = ['utf-8', 'latin-1', 'cp850', 'cp1252']
        
        for encoding in encodings:
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding=encoding,
                    errors='ignore',
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                
                if result.returncode == 0:
                    return result.stdout
            except UnicodeDecodeError:
                continue
            except Exception:
                continue
        
        return ""
    except Exception:
        return ""


def get_all_wifi_profiles() -> List[Dict[str, Any]]:
    """
    Extrai todas as redes WiFi salvas no Windows
    """
    profiles = []
    
    try:
        output = run_netsh_command(["netsh", "wlan", "show", "profiles"])
        
        if not output:
            return []
        
        # Extrair nomes dos perfis
        profile_names = []
        lines = output.split('\n')
        for line in lines:
            if ':' in line and ('perfil' in line.lower() or 'profile' in line.lower()):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    name = parts[1].strip()
                    if name and name not in profile_names:
                        profile_names.append(name)
        
        for profile_name in profile_names:
            if not profile_name:
                continue
            
            profile_info = extract_profile_details(profile_name)
            if profile_info:
                profiles.append(profile_info)
    
    except Exception as e:
        print(f"Erro ao listar perfis: {e}")
    
    return profiles


def extract_profile_details(profile_name: str) -> Dict[str, Any]:
    """
    Extrai detalhes de um perfil específico
    """
    try:
        output = run_netsh_command([
            "netsh", "wlan", "show", "profile", f"name={profile_name}", "key=clear"
        ])
        
        if not output:
            return None
        
        # Extrair informações
        auth = extract_field(output, [
            r"Autenticação\s*:\s*(.*?)$",
            r"Authentication\s*:\s*(.*?)$"
        ]) or "Desconhecido"
        
        cipher = extract_field(output, [
            r"Cifra\s*:\s*(.*?)$",
            r"Cipher\s*:\s*(.*?)$"
        ]) or "Desconhecido"
        
        key_content = extract_field(output, [
            r"Conteúdo da Chave\s*:\s*(.*?)$",
            r"Key Content\s*:\s*(.*?)$"
        ]) or ""
        
        # Determinar qualidade
        quality = "Excelente"
        auth_lower = auth.lower()
        if "enterprise" in auth_lower:
            quality = "Bom"
        elif "open" in auth_lower or "aberto" in auth_lower:
            quality = "Fraco"
        
        # Converter para HEX
        key_hex = ""
        if key_content and key_content != "********":
            try:
                key_hex = key_content.encode('utf-8').hex()
                if len(key_hex) > 32:
                    key_hex = key_hex[:32] + "..."
            except:
                pass
        
        return {
            "SSID": profile_name,
            "Autenticação": auth,
            "Qualidade": quality,
            "Criptografia": cipher,
            "Chave (ASCII)": key_content if key_content else "********",
            "Chave (HEX)": f"[Hex {key_hex}]" if key_hex else "",
            "Última Conexão": time.strftime("%Y-%m-%d %H:%M")
        }
        
    except Exception:
        return None


def extract_field(text: str, patterns: List[str]) -> str:
    """Extrai um campo do texto usando múltiplos padrões"""
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""