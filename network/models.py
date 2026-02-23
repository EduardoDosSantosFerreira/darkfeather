"""
Modelos de dados para a rede local
Arquivo: network/models.py
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple


@dataclass
class ClienteInfo:
    """Informações de um cliente conectado"""
    id: int
    endereco: Tuple[str, int]
    nome: Optional[str] = None
    conectado_em: datetime = None
    ultima_atividade: datetime = None
    
    def __post_init__(self):
        if self.conectado_em is None:
            self.conectado_em = datetime.now()
            self.ultima_atividade = self.conectado_em
    
    def atualizar_atividade(self):
        """Atualiza timestamp da última atividade"""
        self.ultima_atividade = datetime.now()


@dataclass
class Mensagem:
    """Modelo de mensagem trocada entre cliente/servidor"""
    tipo: str  # 'texto', 'arquivo', 'comando', 'resposta'
    origem: str
    destino: str  # 'servidor', 'todos', ou ID específico
    conteudo: any
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def para_dict(self) -> dict:
        """Converte para dicionário para envio via socket"""
        return {
            'tipo': self.tipo,
            'origem': self.origem,
            'destino': self.destino,
            'conteudo': self.conteudo,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def de_dict(cls, dados: dict) -> 'Mensagem':
        """Cria mensagem a partir de dicionário"""
        return cls(
            tipo=dados['tipo'],
            origem=dados['origem'],
            destino=dados['destino'],
            conteudo=dados['conteudo']
        )