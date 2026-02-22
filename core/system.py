"""
Funções de sistema para interagir com o Windows
"""

import subprocess
import re
import ctypes
import os
import time
import socket
from typing import List, Dict, Any, Optional, Tuple


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
                elif "não existe" in result.stderr or "not found" in result.stderr:
                    return ""
            except UnicodeDecodeError:
                continue
            except Exception:
                continue
        
        return ""
    except Exception:
        return ""


def get_all_wifi_profiles() -> List[Dict[str, Any]]:
    """
    Extrai todas as redes WiFi salvas no Windows com suas chaves
    Versão robusta com suporte a múltiplos idiomas
    """
    profiles = []

    # Verificar se o serviço WLAN AutoConfig está rodando
    try:
        service_check = subprocess.run(
            ["sc", "query", "WlanSvc"],
            capture_output=True,
            text=True,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if hasattr(subprocess, "CREATE_NO_WINDOW")
                else 0
            ),
        )

        if (
            "RUNNING" not in service_check.stdout
            and "RUNNING" not in service_check.stderr
        ):
            print("Serviço WLAN AutoConfig não está rodando. Tentando iniciar...")
            subprocess.run(["net", "start", "WlanSvc"], capture_output=True)
            time.sleep(2)
    except:
        pass

    try:
        # Listar todos os perfis
        output = run_netsh_command(["netsh", "wlan", "show", "profiles"])

        if not output:
            print("Não foi possível obter lista de perfis.")
            return []

        # Padrões para diferentes idiomas
        profile_patterns = [
            r":\s(.*?)$",
            r"Perfil\s+:\s+(.*?)$",
            r"Profile\s+:\s+(.*?)$",
            r"Todos os perfis de usuário\s+:\s+(.*?)$",
            r"All User Profile\s+:\s+(.*?)$",
        ]

        profile_names = []
        for pattern in profile_patterns:
            found = re.findall(pattern, output, re.MULTILINE | re.IGNORECASE)
            if found:
                profile_names = [name.strip() for name in found if name.strip()]
                if profile_names:
                    break

        # Se não encontrou com regex, tentar método linha por linha
        if not profile_names:
            lines = output.split("\n")
            for line in lines:
                if ":" in line and (
                    "perfil" in line.lower() or "profile" in line.lower()
                ):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        name = parts[1].strip()
                        if name and name not in profile_names:
                            profile_names.append(name)

        # Remover duplicatas e vazios
        profile_names = list(dict.fromkeys([p for p in profile_names if p]))

        print(f"Encontrados {len(profile_names)} perfis")

        for profile_name in profile_names:
            if not profile_name or profile_name.lower() in ["", " ", "todos", "all"]:
                continue

            profile_info = extract_profile_details(profile_name)
            if profile_info:
                profiles.append(profile_info)

            time.sleep(0.1)

        # Ordenar por SSID
        profiles.sort(key=lambda x: x.get("SSID", "").lower())

    except Exception as e:
        print(f"Erro ao listar perfis: {e}")
        import traceback
        traceback.print_exc()

    return profiles


def extract_profile_details(profile_name: str) -> Optional[Dict[str, Any]]:
    """
    Extrai detalhes completos de um perfil WiFi específico
    Versão robusta com suporte a múltiplos idiomas
    """
    try:
        clean_name = profile_name.strip()

        # Buscar detalhes do perfil com a chave
        output = run_netsh_command(
            ["netsh", "wlan", "show", "profile", f"name={clean_name}", "key=clear"]
        )

        if not output:
            # Tentar com aspas
            output = run_netsh_command(
                [
                    "netsh",
                    "wlan",
                    "show",
                    "profile",
                    f'name="{clean_name}"',
                    "key=clear",
                ]
            )

        if not output:
            print(f"Não foi possível obter detalhes para: {clean_name}")
            return None

        ssid = clean_name

        # Padrões para diferentes idiomas
        auth_patterns = [
            r"Autenticação\s*:\s*(.*?)$",
            r"Authentication\s*:\s*(.*?)$",
            r"Método de autenticação\s*:\s*(.*?)$",
        ]

        cipher_patterns = [
            r"Cifra\s*:\s*(.*?)$",
            r"Cipher\s*:\s*(.*?)$",
            r"Codificação\s*:\s*(.*?)$",
            r"Encryption\s*:\s*(.*?)$",
        ]

        key_patterns = [
            r"Conteúdo da Chave\s*:\s*(.*?)$",
            r"Key Content\s*:\s*(.*?)$",
            r"Senha\s*:\s*(.*?)$",
            r"Password\s*:\s*(.*?)$",
        ]

        # Autenticação
        auth = "Desconhecido"
        for pattern in auth_patterns:
            match = re.search(pattern, output, re.MULTILINE | re.IGNORECASE)
            if match:
                auth = match.group(1).strip()
                break

        # Criptografia
        cipher = "Desconhecido"
        for pattern in cipher_patterns:
            match = re.search(pattern, output, re.MULTILINE | re.IGNORECASE)
            if match:
                cipher = match.group(1).strip()
                break

        # Chave de segurança (senha)
        key_content = ""
        for pattern in key_patterns:
            match = re.search(pattern, output, re.MULTILINE | re.IGNORECASE)
            if match:
                key_content = match.group(1).strip()
                break

        # Se não encontrou a chave, tentar em linhas específicas
        if not key_content:
            lines = output.split("\n")
            for i, line in enumerate(lines):
                if any(
                    k in line.lower()
                    for k in ["chave", "key", "senha", "password", "conteúdo"]
                ):
                    if ":" in line:
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            key_content = parts[1].strip()
                            break

        # Converter para HEX se houver conteúdo
        key_hex = ""
        if key_content and key_content not in ["********", "Nenhuma", "None", ""]:
            try:
                key_hex = key_content.encode("utf-8").hex().upper()
                if len(key_hex) > 32:
                    key_hex = key_hex[:32] + "..."
            except:
                key_hex = "[Erro na conversão]"

        # Determinar qualidade baseado no tipo de segurança
        signal_quality = "Excelente"
        auth_lower = auth.lower()
        if "enterprise" in auth_lower:
            signal_quality = "Bom"
        elif "open" in auth_lower or "aberto" in auth_lower or "none" in auth_lower:
            signal_quality = "Fraco"
        elif "wep" in auth_lower:
            signal_quality = "Regular"

        # Última conexão
        last_connection = time.strftime("%Y-%m-%d %H:%M")

        # Tentar obter dados do arquivo de perfil
        profile_path = get_profile_file_path(clean_name)
        if profile_path and os.path.exists(profile_path):
            mod_time = os.path.getmtime(profile_path)
            last_connection = time.strftime("%Y-%m-%d %H:%M", time.localtime(mod_time))

        # Montar dicionário com informações
        info = {
            "SSID": ssid,
            "Autenticação": auth,
            "Qualidade": signal_quality,
            "Criptografia": cipher,
            "Chave (ASCII)": (
                key_content if key_content and key_content != "********" else "********"
            ),
            "Chave (HEX)": f"[Hex {key_hex}]" if key_hex else "",
            "Última Conexão": last_connection,
        }

        return info

    except Exception as e:
        print(f"Erro ao extrair detalhes de {profile_name}: {e}")
        return None


def get_profile_file_path(profile_name: str) -> Optional[str]:
    """
    Tenta encontrar o arquivo XML do perfil
    """
    try:
        base_path = r"C:\ProgramData\Microsoft\Wlansvc\Profiles\Interfaces"
        if os.path.exists(base_path):
            for interface in os.listdir(base_path):
                interface_path = os.path.join(base_path, interface)
                if os.path.isdir(interface_path):
                    for file in os.listdir(interface_path):
                        if file.endswith(".xml"):
                            file_path = os.path.join(interface_path, file)
                            try:
                                with open(file_path, "r", encoding="utf-16") as f:
                                    content = f.read()
                                    if profile_name in content:
                                        return file_path
                            except:
                                pass
    except:
        pass
    return None


def get_adapter_info() -> Dict[str, str]:
    """
    Obtém informações detalhadas do adaptador de rede
    """
    info = {
        "name": "Não disponível",
        "description": "Não disponível",
        "mac": "Não disponível",
        "guid": "Não disponível",
        "status": "Não disponível",
        "driver": "Não disponível",
        "vendor": "Não disponível"
    }
    
    try:
        # Usar wmic para obter informações do adaptador
        result = subprocess.run(
            ["wmic", "nic", "where", "NetEnabled=TRUE", "get", "Name,Description,MACAddress,GUID,Status,DriverVersion"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if "Wi-Fi" in line or "Wireless" in line or "WLAN" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        info["name"] = parts[0] if len(parts) > 0 else "Desconhecido"
                        info["mac"] = parts[1] if len(parts) > 1 else "Desconhecido"
                        info["guid"] = parts[2] if len(parts) > 2 else "Desconhecido"
                        info["status"] = parts[3] if len(parts) > 3 else "Desconhecido"
                        info["driver"] = parts[4] if len(parts) > 4 else "Desconhecido"
                    break
    except:
        pass
    
    return info


def get_dns_servers() -> List[str]:
    """
    Obtém servidores DNS configurados
    """
    dns_servers = []
    
    try:
        result = subprocess.run(
            ["nslookup", "localhost"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if "Address:" in line and "#53" not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        ip = parts[1].strip()
                        if ip and ip not in dns_servers:
                            dns_servers.append(ip)
    except:
        pass
    
    return dns_servers


def get_host_info() -> Dict[str, str]:
    """
    Obtém informações do host
    """
    return {
        "hostname": socket.gethostname(),
        "fqdn": socket.getfqdn(),
        "domain": os.environ.get('USERDOMAIN', 'Desconhecido'),
        "user": os.environ.get('USERNAME', 'Desconhecido')
    }


def check_wifi_status() -> Tuple[bool, str]:
    """
    Verifica se o WiFi está habilitado e funcionando
    """
    try:
        output = run_netsh_command(["netsh", "wlan", "show", "interfaces"])

        if "não há" in output.lower() or "there is no" in output.lower():
            return False, "Nenhuma interface WiFi encontrada"

        if "desconectado" in output.lower() or "disconnected" in output.lower():
            return True, "WiFi disponível mas desconectado"

        if "conectado" in output.lower() or "connected" in output.lower():
            return True, "WiFi conectado"

        return True, "WiFi disponível"

    except:
        return False, "Não foi possível verificar status do WiFi"