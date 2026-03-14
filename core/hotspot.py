"""
Módulo de controle do Mobile Hotspot do Windows usando WinRT
Arquivo: core/hotspot.py
"""

import asyncio
import sys
import subprocess
import platform
import logging
from typing import Optional, Dict, Any
from enum import Enum

# Configurar logger
logger = logging.getLogger("darkfeather.hotspot")


class HotspotStatus(Enum):
    """Estados possíveis do Mobile Hotspot"""
    UNKNOWN = "Desconhecido"
    DISABLED = "Desativado"
    ENABLED = "Ativado"
    STARTING = "Iniciando"
    STOPPING = "Parando"
    ERROR = "Erro"
    NOT_AVAILABLE = "N/A neste sistema"
    NO_PERMISSION = "Sem permissão"


class HotspotConfig:
    """Configuração do Mobile Hotspot"""
    
    def __init__(self, ssid: str = "", password: str = ""):
        self.ssid = ssid
        self.password = password
        self.band = "auto"  # auto, 24, 5, 6
        self.max_clients = 8
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "ssid": self.ssid,
            "password": self.password,
            "band": self.band,
            "max_clients": self.max_clients
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HotspotConfig':
        return cls(
            ssid=data.get("ssid", ""),
            password=data.get("password", "")
        )


class MobileHotspotController:
    """
    Controlador do Mobile Hotspot usando WinRT
    Fallback automático para Configurações do Windows em caso de falha
    """
    
    def __init__(self):
        self._winrt_available = False
        self._tethering_manager = None
        self._configuration = None
        self._network_adapter = None
        self._current_status = HotspotStatus.UNKNOWN
        self._event_loop = None
        self._initialize_winrt()
    
    def _initialize_winrt(self) -> bool:
        """
        Tenta inicializar a API WinRT
        Retorna True se bem-sucedido
        """
        # Verificar se é Windows
        if platform.system() != "Windows":
            logger.warning("Sistema não é Windows. Hotspot desabilitado.")
            self._current_status = HotspotStatus.NOT_AVAILABLE
            return False
        
        try:
            # Importar winrt apenas se disponível
            import winrt.windows.networking.networkoperators as wno
            import winrt.windows.networking.connectivity as wnc
            import winrt.windows.foundation as wf
            
            # Obter o adaptador de rede atual
            connection_profile = wnc.NetworkInformation.get_internet_connection_profile()
            if not connection_profile:
                logger.error("Nenhum perfil de conexão de internet encontrado")
                return False
            
            self._network_adapter = connection_profile.network_adapter
            if not self._network_adapter:
                logger.error("Nenhum adaptador de rede encontrado")
                return False
            
            # Criar tethering manager
            self._tethering_manager = wno.NetworkOperatorTetheringManager.create_from_network_adapter(
                self._network_adapter
            )
            
            # Obter configuração atual
            self._configuration = self._tethering_manager.get_current_access_point_configuration()
            
            self._winrt_available = True
            self._current_status = self._get_status_from_state()
            logger.info("WinRT inicializado com sucesso")
            return True
            
        except ImportError:
            logger.warning("WinRT não instalado. Use 'pip install winrt' para habilitar controle direto.")
            self._current_status = HotspotStatus.NOT_AVAILABLE
            return False
            
        except Exception as e:
            logger.error(f"Erro ao inicializar WinRT: {str(e)}")
            self._current_status = HotspotStatus.ERROR
            return False
    
    def _get_status_from_state(self) -> HotspotStatus:
        """Obtém o status atual baseado no estado do tethering"""
        if not self._winrt_available or not self._tethering_manager:
            return HotspotStatus.NOT_AVAILABLE
        
        try:
            state = self._tethering_manager.tethering_operational_state
            
            from winrt.windows.networking.networkoperators import TetheringOperationalState as State
            
            if state == State.TURNING_ON:
                return HotspotStatus.STARTING
            elif state == State.TURNING_OFF:
                return HotspotStatus.STOPPING
            elif state == State.ON:
                return HotspotStatus.ENABLED
            elif state == State.OFF:
                return HotspotStatus.DISABLED
            elif state == State.IN_TRANSITION:
                return HotspotStatus.STARTING
            else:
                return HotspotStatus.UNKNOWN
                
        except Exception as e:
            logger.error(f"Erro ao obter status: {str(e)}")
            return HotspotStatus.ERROR
    
    def get_status(self) -> HotspotStatus:
        """Retorna o status atual do hotspot"""
        if not self._winrt_available:
            return self._current_status
        
        self._current_status = self._get_status_from_state()
        return self._current_status
    
    def get_config(self) -> Optional[HotspotConfig]:
        """Obtém a configuração atual do hotspot"""
        if not self._winrt_available or not self._configuration:
            return None
        
        try:
            ssid = self._configuration.ssid
            password = self._configuration.passphrase
            
            # Tentar obter a senha de alguma forma (a API não expõe diretamente)
            # Fallback: tentar ler do registro ou netsh
            
            return HotspotConfig(
                ssid=ssid if ssid else "",
                password=password if password else ""
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter configuração: {str(e)}")
            return None
    
    def _run_fallback_command(self, command: str) -> bool:
        """
        Executa um comando de fallback quando a API falha
        Retorna True se o comando foi executado com sucesso
        """
        try:
            if command == "open_settings":
                # Abrir as configurações do Mobile Hotspot
                subprocess.run(
                    ["start", "ms-settings:network-mobilehotspot"],
                    shell=True,
                    capture_output=True
                )
                return True
                
            elif command == "start":
                # Tentar iniciar via netsh (fallback)
                result = subprocess.run(
                    ["netsh", "wlan", "start", "hostednetwork"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return result.returncode == 0
                
            elif command == "stop":
                # Tentar parar via netsh (fallback)
                result = subprocess.run(
                    ["netsh", "wlan", "stop", "hostednetwork"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return result.returncode == 0
                
            elif command == "configure":
                # Configurar via netsh (fallback limitado)
                # Nota: netsh hostednetwork é limitado, mas serve como fallback
                return False
                
        except Exception as e:
            logger.error(f"Erro no fallback {command}: {str(e)}")
            return False
        
        return False
    
    def start_hotspot(self) -> bool:
        """
        Inicia o Mobile Hotspot
        Retorna True se iniciado com sucesso ou fallback acionado
        """
        if not self._winrt_available:
            # Fallback: abrir configurações
            self._run_fallback_command("open_settings")
            self._current_status = HotspotStatus.ERROR
            return False
        
        try:
            # Criar evento assíncrono
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Iniciar tethering
            operation = self._tethering_manager.start_tethering_async()
            
            # Aguardar conclusão (simplificado - em produção usar threads)
            result = loop.run_until_complete(operation)
            
            from winrt.windows.networking.networkoperators import TetheringOperationStatus as Status
            
            if result.status == Status.SUCCESS:
                self._current_status = HotspotStatus.ENABLED
                logger.info("Hotspot iniciado com sucesso")
                return True
            else:
                logger.error(f"Falha ao iniciar hotspot: {result.status}")
                self._run_fallback_command("open_settings")
                self._current_status = HotspotStatus.ERROR
                return False
                
        except Exception as e:
            logger.error(f"Exceção ao iniciar hotspot: {str(e)}")
            self._run_fallback_command("open_settings")
            self._current_status = HotspotStatus.ERROR
            return False
    
    def stop_hotspot(self) -> bool:
        """
        Para o Mobile Hotspot
        Retorna True se parado com sucesso ou fallback acionado
        """
        if not self._winrt_available:
            # Fallback: abrir configurações
            self._run_fallback_command("open_settings")
            self._current_status = HotspotStatus.ERROR
            return False
        
        try:
            # Criar evento assíncrono
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Parar tethering
            operation = self._tethering_manager.stop_tethering_async()
            
            # Aguardar conclusão
            result = loop.run_until_complete(operation)
            
            from winrt.windows.networking.networkoperators import TetheringOperationStatus as Status
            
            if result.status == Status.SUCCESS:
                self._current_status = HotspotStatus.DISABLED
                logger.info("Hotspot parado com sucesso")
                return True
            else:
                logger.error(f"Falha ao parar hotspot: {result.status}")
                self._run_fallback_command("open_settings")
                self._current_status = HotspotStatus.ERROR
                return False
                
        except Exception as e:
            logger.error(f"Exceção ao parar hotspot: {str(e)}")
            self._run_fallback_command("open_settings")
            self._current_status = HotspotStatus.ERROR
            return False
    
    def configure_hotspot(self, ssid: str, password: str) -> bool:
        """
        Configura SSID e senha do Mobile Hotspot
        Retorna True se configurado com sucesso ou fallback acionado
        """
        if not self._winrt_available:
            # Fallback: abrir configurações
            self._run_fallback_command("open_settings")
            return False
        
        # Validações básicas
        if len(password) < 8:
            logger.warning("Senha muito curta (mínimo 8 caracteres)")
            return False
        
        if not ssid or len(ssid) > 32:
            logger.warning("SSID inválido (1-32 caracteres)")
            return False
        
        try:
            # Importar classes necessárias
            import winrt.windows.networking.networkoperators as wno
            from winrt.windows.foundation import AsyncOperation
            
            # Criar nova configuração
            config = wno.NetworkOperatorTetheringAccessPointConfiguration()
            config.ssid = ssid
            config.passphrase = password
            config.band = 0  # auto
            
            # Aplicar configuração
            self._tethering_manager.configure_access_point_async(config)
            
            # Atualizar configuração local
            self._configuration = config
            
            logger.info(f"Hotspot configurado: SSID={ssid}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao configurar hotspot: {str(e)}")
            self._run_fallback_command("open_settings")
            return False
    
    def open_settings(self):
        """Abre as configurações do Mobile Hotspot no Windows"""
        try:
            subprocess.run(
                ["start", "ms-settings:network-mobilehotspot"],
                shell=True,
                capture_output=True
            )
            logger.info("Configurações do Mobile Hotspot abertas")
            return True
        except Exception as e:
            logger.error(f"Erro ao abrir configurações: {str(e)}")
            return False
    
    def is_available(self) -> bool:
        """Verifica se o controle direto via WinRT está disponível"""
        return self._winrt_available
    
    def get_status_text(self) -> str:
        """Retorna texto descritivo do status"""
        status = self.get_status()
        return status.value