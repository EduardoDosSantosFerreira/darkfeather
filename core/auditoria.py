"""
Módulo de auditoria - Gerencia a persistência de redes e senhas
Arquivo: raiz/core/auditoria.py
"""

import os
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime

from core.scanner import WifiNetwork


class Auditoria:
    """
    Gerencia a persistência de redes Wi-Fi e senhas em arquivo TXT
    Localização: raiz/keys/auditoria.txt
    """
    
    def __init__(self):
        # Definir caminhos
        self.raiz = Path(__file__).parent.parent  # sobe um nível de core/
        self.keys_dir = self.raiz / "keys"
        self.arquivo_auditoria = self.keys_dir / "auditoria.txt"
        
        # Garantir que a pasta keys existe
        self._garantir_estrutura()
    
    def _garantir_estrutura(self):
        """Cria a pasta keys e o arquivo auditoria.txt se não existirem"""
        self.keys_dir.mkdir(exist_ok=True)
        
        if not self.arquivo_auditoria.exists():
            with open(self.arquivo_auditoria, 'w', encoding='utf-8') as f:
                f.write("# AUDITORIA DE REDES WI-FI\n")
                f.write(f"# Arquivo gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("# Formato: SSID | SENHA | DATA_REGISTRO\n")
                f.write("#" + "="*60 + "\n\n")
    
    def _ler_auditoria_atual(self) -> Dict[str, Dict]:
        """
        Lê o arquivo de auditoria e retorna dicionário com redes já registradas
        Retorna: {ssid: {"senha": senha, "data": data}}
        """
        redes_registradas = {}
        
        if not self.arquivo_auditoria.exists():
            return redes_registradas
        
        try:
            with open(self.arquivo_auditoria, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            for linha in linhas:
                linha = linha.strip()
                # Ignorar linhas de comentário e linhas vazias
                if not linha or linha.startswith('#'):
                    continue
                
                # Formato esperado: SSID | SENHA | DATA
                partes = linha.split('|')
                if len(partes) >= 2:
                    ssid = partes[0].strip()
                    senha = partes[1].strip() if len(partes) > 1 else ""
                    data = partes[2].strip() if len(partes) > 2 else ""
                    
                    redes_registradas[ssid] = {
                        "senha": senha,
                        "data": data
                    }
        except Exception as e:
            print(f"Erro ao ler auditoria: {e}")
        
        return redes_registradas
    
    def _formatar_senha(self, network: WifiNetwork) -> str:
        """Retorna a senha formatada ou indicação de ausência"""
        if network.password:
            return network.password
        elif network.password_hex:
            return f"[HEX] {network.password_hex}"
        else:
            return "******** (não disponível no perfil)"
    
    def atualizar(self, networks: List[WifiNetwork]) -> Path:
        """
        Atualiza o arquivo de auditoria com as redes detectadas
        
        Args:
            networks: Lista de redes escaneadas
        
        Returns:
            Path: Caminho do arquivo atualizado
        """
        # Ler redes já registradas
        redes_registradas = self._ler_auditoria_atual()
        
        # Conjunto para rastrear SSIDs processados
        ssids_processados = set()
        
        # Atualizar com novas redes
        for network in networks:
            ssid = network.ssid
            senha = self._formatar_senha(network)
            data_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
            
            if ssid in redes_registradas:
                # Rede já existe - verificar se senha mudou
                senha_anterior = redes_registradas[ssid]["senha"]
                
                # Se senha mudou, atualizar com nova data
                if senha_anterior != senha and senha != "******** (não disponível no perfil)":
                    redes_registradas[ssid] = {
                        "senha": senha,
                        "data": f"{data_atual} (atualizada)"
                    }
            else:
                # Rede nova - adicionar
                redes_registradas[ssid] = {
                    "senha": senha,
                    "data": data_atual
                }
            
            ssids_processados.add(ssid)
        
        # Reescrever arquivo completo
        with open(self.arquivo_auditoria, 'w', encoding='utf-8') as f:
            # Cabeçalho
            f.write("# AUDITORIA DE REDES WI-FI\n")
            f.write(f"# Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("# Total de redes: {}\n".format(len(redes_registradas)))
            f.write("#" + "="*60 + "\n\n")
            
            # Ordenar por SSID
            for ssid in sorted(redes_registradas.keys()):
                info = redes_registradas[ssid]
                f.write(f"{ssid} | {info['senha']} | {info['data']}\n")
        
        return self.arquivo_auditoria
    
    def obter_resumo(self) -> Dict:
        """
        Retorna resumo da auditoria atual
        """
        redes = self._ler_auditoria_atual()
        
        return {
            "total_redes": len(redes),
            "com_senha": sum(1 for r in redes.values() if r["senha"] and "********" not in r["senha"]),
            "sem_senha": sum(1 for r in redes.values() if not r["senha"] or "********" in r["senha"]),
            "arquivo": str(self.arquivo_auditoria)
        }
    
    def abrir_pasta(self):
        """Abre a pasta keys no explorador de arquivos"""
        import subprocess
        import platform
        
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{self.keys_dir}"')
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", self.keys_dir])
        else:  # Linux
            subprocess.Popen(["xdg-open", self.keys_dir])