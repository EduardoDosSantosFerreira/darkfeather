import subprocess
import re
import ctypes
import time
import os


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_netsh_command(command):
    """
    Executa um comando netsh e trata erros de forma robusta
    """
    try:
        # Tentar com diferentes codificações
        encodings = ["utf-8", "latin-1", "cp850", "cp1252"]

        for encoding in encodings:
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding=encoding,
                    errors="ignore",
                    creationflags=(
                        subprocess.CREATE_NO_WINDOW
                        if hasattr(subprocess, "CREATE_NO_WINDOW")
                        else 0
                    ),
                )

                if result.returncode == 0:
                    return result.stdout
                elif "não existe" in result.stderr or "not found" in result.stderr:
                    return ""  # Perfil não encontrado
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Erro com encoding {encoding}: {e}")
                continue

        # Se todas as codificações falharem, tentar com binary
        result = subprocess.run(
            command,
            capture_output=True,
            binary=True,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if hasattr(subprocess, "CREATE_NO_WINDOW")
                else 0
            ),
        )

        # Tentar decodificar ignorando erros
        return result.stdout.decode("utf-8", errors="ignore")

    except Exception as e:
        print(f"Erro ao executar comando: {e}")
        return ""


def get_all_wifi_profiles():
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
        # Listar todos os perfis - método alternativo
        output = run_netsh_command(["netsh", "wlan", "show", "profiles"])

        if not output:
            print(
                "Não foi possível obter lista de perfis. Tentando método alternativo..."
            )
            # Tentar método alternativo via PowerShell
            output = run_netsh_command(
                ["powershell", "-Command", "netsh wlan show profiles"]
            )

        if not output:
            print("Ainda sem sucesso. Verificando interfaces...")
            # Verificar interfaces de rede
            interfaces = run_netsh_command(["netsh", "wlan", "show", "interfaces"])
            print(
                f"Interfaces encontradas: {interfaces[:200] if interfaces else 'Nenhuma'}"
            )
            return []

        # Padrões para diferentes idiomas
        profile_patterns = [
            r":\s(.*?)$",  # Português/Inglês
            r"Perfil\s+:\s+(.*?)$",  # Português completo
            r"Profile\s+:\s+(.*?)$",  # Inglês completo
            r"Todos os perfis de usuário\s+:\s+(.*?)$",  # Português alternativo
            r"All User Profile\s+:\s+(.*?)$",  # Inglês alternativo
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

            # Pequena pausa para não sobrecarregar
            time.sleep(0.1)

        # Ordenar por SSID
        profiles.sort(key=lambda x: x.get("SSID", "").lower())

    except Exception as e:
        print(f"Erro ao listar perfis: {e}")
        import traceback

        traceback.print_exc()

    return profiles


def extract_profile_details(profile_name):
    """
    Extrai detalhes completos de um perfil WiFi específico
    Versão robusta com suporte a múltiplos idiomas
    """
    try:
        # Limpar nome do perfil (remover caracteres especiais)
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

        # Extrair SSID (geralmente é o próprio nome do perfil)
        ssid = clean_name

        # Padrões para diferentes idiomas e formatos
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
                        key_content = line.split(":", 1)[1].strip()
                        break

        # Converter para HEX se houver conteúdo
        key_hex = ""
        if key_content and key_content not in ["********", "Nenhuma", "None", ""]:
            try:
                key_hex = key_content.encode("utf-8").hex()
                # Limitar tamanho para exibição
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

        # Última conexão (simulada - em um caso real, viria do sistema)
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


def get_profile_file_path(profile_name):
    """
    Tenta encontrar o arquivo XML do perfil
    """
    try:
        # Caminho padrão dos perfis WiFi no Windows
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


def check_wifi_status():
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
