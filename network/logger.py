"""
Logger para registrar conexões e eventos da rede
Arquivo: logs/logger.py
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class NetworkLogger:
    """
    Logger específico para eventos de rede
    Cria arquivos de log diários na pasta logs/
    """
    
    def __init__(self, nome: str = "network"):
        self.nome = nome
        
        # Criar pasta de logs se não existir
        self.log_dir = Path(__file__).parent
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar logger
        self.logger = logging.getLogger(f"darkfeather_{nome}")
        self.logger.setLevel(logging.DEBUG)
        
        # Remover handlers existentes
        self.logger.handlers.clear()
        
        # Handler para arquivo (rotação diária)
        arquivo_log = self.log_dir / f"{nome}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(arquivo_log, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Formato do log
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        
        # Handler para console (opcional)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def conexao(self, endereco: str, cliente_id: Optional[int] = None):
        """Registra nova conexão"""
        if cliente_id:
            self.logger.info(f"🔗 CONEXÃO | Cliente {cliente_id} | {endereco}")
        else:
            self.logger.info(f"🔗 CONEXÃO | {endereco}")
    
    def desconexao(self, endereco: str, cliente_id: Optional[int] = None, motivo: str = ""):
        """Registra desconexão"""
        msg = f"🔌 DESCONEXÃO | {endereco}"
        if cliente_id:
            msg = f"🔌 DESCONEXÃO | Cliente {cliente_id} | {endereco}"
        if motivo:
            msg += f" | {motivo}"
        self.logger.info(msg)
    
    def mensagem(self, origem: str, destino: str, tipo: str, tamanho: int):
        """Registra envio de mensagem"""
        self.logger.debug(f"📨 MENSAGEM | {origem} → {destino} | {tipo} | {tamanho} bytes")
    
    def erro(self, local: str, erro: str):
        """Registra erro"""
        self.logger.error(f"❌ ERRO | {local} | {erro}")
    
    def info(self, mensagem: str):
        """Registra informação genérica"""
        self.logger.info(f"ℹ️ {mensagem}")
    
    def debug(self, mensagem: str):
        """Registra debug"""
        self.logger.debug(f"🐞 {mensagem}")