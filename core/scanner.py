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


class WifiScannerWorker(QRunnable):
    """
    Worker para executar o scan em thread separada
    Não bloqueia a UI
    """
    
    class Signals(QObject):
        finished = Signal(object)  # List[WifiNetwork]
        error = Signal(str)
        progress = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.signals = self.Signals()
    
    @Slot()
    def run(self):
        """Executa o scan em thread separada"""
        try:
            self.signals.progress.emit("Iniciando scan de redes Wi-Fi...")
            networks = self.scan_real_networks()
            self.signals.finished.emit(networks)
        except Exception as e:
            error_msg = f"Erro no scan: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)  # Log para debug
            self.signals.error.emit(f"Falha ao escanear redes: {str(e)}")
    
    def scan_real_networks(self) -> List[WifiNetwork]:
        """
        Escaneia redes WiFi REAIS do Windows
        SEM dados mockados
        """
        networks = []
        
        # Passo 1: Listar todos os perfis reais
        profiles = self.get_real_profiles()
        
        if not profiles:
            print("Nenhum perfil WiFi encontrado no sistema")
            return []
        
        self.signals.progress.emit(f"Encontrados {len(profiles)} perfis")
        
        # Passo 2: Para cada perfil, obter detalhes reais
        for profile_name in profiles:
            network = self.get_real_network_details(profile_name)
            if network:
                networks.append(network)
            
            # Pequena pausa para não sobrecarregar
            time.sleep(0.1)
        
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
            # Comando real do Windows
            result = subprocess.run(
                ["netsh", "wlan", "show", "profiles"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode != 0:
                print(f"Erro ao executar netsh: {result.stderr}")
                return []
            
            output = result.stdout
            
            # Extrair nomes dos perfis (funciona em português e inglês)
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                
                # Padrões para diferentes idiomas
                if ':' in line:
                    if 'perfil' in line.lower() or 'profile' in line.lower():
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            name = parts[1].strip()
                            if name and name not in profiles:
                                profiles.append(name)
                    elif 'todos os perfis de usuário' in line.lower() or 'all user profile' in line.lower():
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            name = parts[1].strip()
                            if name and name not in profiles:
                                profiles.append(name)
            
            # Se não encontrou com o método acima, tentar regex
            if not profiles:
                # Padrões regex para diferentes formatos
                patterns = [
                    r":\s+(.+)$",
                    r"Perfil\s+:\s+(.+)$",
                    r"Profile\s+:\s+(.+)$",
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, output, re.MULTILINE)
                    if matches:
                        profiles = [m.strip() for m in matches if m.strip()]
                        break
            
            print(f"Perfis encontrados: {profiles}")
            
        except Exception as e:
            print(f"Exceção ao listar perfis: {e}")
            traceback.print_exc()
        
        return profiles
    
    def get_real_network_details(self, profile_name: str) -> Optional[WifiNetwork]:
        """
        Obtém detalhes REAIS de uma rede específica
        """
        try:
            # Comando real com key=clear para obter a senha
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
                print(f"Erro ao obter detalhes de {profile_name}")
                return None
            
            output = result.stdout
            
            # Extrair autenticação
            auth = self.extract_field(output, [
                r"Autenticação\s*:\s*(.+)$",
                r"Authentication\s*:\s*(.+)$",
                r"Método de autenticação\s*:\s*(.+)$"
            ]) or "Desconhecido"
            
            # Extrair criptografia
            encryption = self.extract_field(output, [
                r"Cifra\s*:\s*(.+)$",
                r"Cipher\s*:\s*(.+)$",
                r"Codificação\s*:\s*(.+)$"
            ]) or "Desconhecido"
            
            # Extrair senha REAL
            password = self.extract_field(output, [
                r"Conteúdo da Chave\s*:\s*(.+)$",
                r"Key Content\s*:\s*(.+)$",
                r"Senha\s*:\s*(.+)$",
                r"Password\s*:\s*(.+)$"
            ])
            
            # Se não encontrou com os padrões, tentar buscar em linhas específicas
            if not password:
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    if any(k in line.lower() for k in ['chave', 'key', 'senha', 'password']):
                        if ':' in line:
                            password = line.split(':', 1)[1].strip()
                            break
            
            # Gerar HEX da senha se disponível
            password_hex = None
            if password and password != "********" and password != "Nenhuma":
                try:
                    password_hex = password.encode('utf-8').hex()
                    if len(password_hex) > 32:
                        password_hex = password_hex[:32] + "..."
                except:
                    pass
            
            # Determinar qualidade do sinal baseado no tipo de segurança
            signal_quality = self.determine_signal_quality(auth, password)
            
            # Tentar obter última conexão (pode não estar disponível)
            last_connection = self.get_last_connection_time(profile_name)
            
            return WifiNetwork(
                ssid=profile_name,
                auth=auth,
                encryption=encryption,
                password=password if password and password != "********" else None,
                password_hex=f"[Hex {password_hex}]" if password_hex else None,
                last_connection=last_connection,
                signal_quality=signal_quality
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
        """
        Determina qualidade baseado em características reais da rede
        """
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
    
    def get_last_connection_time(self, profile_name: str) -> Optional[str]:
        """
        Tenta obter a última conexão (pode não estar disponível via netsh)
        """
        try:
            # Tentar obter informações adicionais
            cmd = ["netsh", "wlan", "show", "profiles", profile_name]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            # Procurar por data de modificação
            output = result.stdout
            for line in output.split('\n'):
                if "aplicado" in line.lower() or "applied" in line.lower():
                    return line.strip()
        except:
            pass
        
        # Se não conseguir, retorna None (o sistema pode mostrar "Não disponível")
        return None


class WifiScanner(QObject):
    """
    Serviço de scan REAL de Wi-Fi
    Opera em thread separada para não travar a UI
    """
    
    scan_finished = Signal(list)  # List[WifiNetwork]
    scan_error = Signal(str)
    scan_progress = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.thread_pool = None
        self.last_networks = []
    
    def scan_networks(self):
        """
        Inicia scan REAL em thread separada
        """
        from PySide6.QtCore import QThreadPool
        
        self.thread_pool = QThreadPool.globalInstance()
        
        # Criar worker
        worker = WifiScannerWorker()
        worker.signals.finished.connect(self.on_scan_finished)
        worker.signals.error.connect(self.on_scan_error)
        worker.signals.progress.connect(self.on_scan_progress)
        
        # Executar
        self.thread_pool.start(worker)
    
    def on_scan_finished(self, networks):
        """Callback quando scan termina com sucesso"""
        self.last_networks = networks
        self.scan_finished.emit(networks)
    
    def on_scan_error(self, error_msg):
        """Callback quando ocorre erro no scan"""
        print(f"Erro no scan: {error_msg}")
        self.scan_error.emit(error_msg)
    
    def on_scan_progress(self, progress_msg):
        """Callback para progresso do scan"""
        print(f"Progresso: {progress_msg}")
        self.scan_progress.emit(progress_msg)
    
    def get_last_networks(self):
        """Retorna últimas redes escaneadas"""
        return self.last_networks