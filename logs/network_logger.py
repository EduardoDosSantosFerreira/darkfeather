"""
Logger específico para a feature de rede
"""
import logging
from pathlib import Path
from datetime import datetime


class NetworkLogger:
    """Logger separado da auditoria principal"""
    
    def __init__(self):
        self.log_dir = Path(__file__).parent
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger("darkfeather_network")
        self.logger.setLevel(logging.INFO)
        
        # Handler para arquivo
        arquivo = self.log_dir / f"network_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(arquivo, encoding='utf-8')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(message)s',
            datefmt='%H:%M:%S'
        ))
        self.logger.addHandler(handler)
    
    def log(self, msg): self.logger.info(msg)
    def erro(self, msg): self.logger.error(f"❌ {msg}")
    def conexao(self, msg): self.logger.info(f"🔗 {msg}")
    def mensagem(self, msg): self.logger.info(f"📨 {msg}")