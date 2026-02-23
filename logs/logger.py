"""
Logger específico para a feature de rede
Arquivo: logs/logger.py
"""

import logging
from pathlib import Path
from datetime import datetime


class NetworkLogger:
    """Logger separado da auditoria principal"""
    
    def __init__(self, nome: str = "network"):
        self.nome = nome
        
        # Criar pasta de logs se não existir
        self.log_dir = Path(__file__).parent
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar logger
        self.logger = logging.getLogger(f"darkfeather_{nome}")
        self.logger.setLevel(logging.INFO)
        
        # Remover handlers existentes
        self.logger.handlers.clear()
        
        # Handler para arquivo
        arquivo_log = self.log_dir / f"{nome}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(arquivo_log, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Formato do log
        formatter = logging.Formatter(
            '%(asctime)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        
        # Handler para console (opcional)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, mensagem: str):
        """Registra informação"""
        self.logger.info(f"ℹ️ {mensagem}")
    
    def erro(self, mensagem: str):
        """Registra erro"""
        self.logger.error(f"❌ {mensagem}")
    
    def conexao(self, mensagem: str):
        """Registra conexão"""
        self.logger.info(f"🔗 {mensagem}")
    
    def desconexao(self, mensagem: str):
        """Registra desconexão"""
        self.logger.info(f"🔌 {mensagem}")
    
    def mensagem(self, mensagem: str):
        """Registra mensagem"""
        self.logger.info(f"📨 {mensagem}")
    
    def debug(self, mensagem: str):
        """Registra debug"""
        self.logger.debug(f"🐞 {mensagem}")