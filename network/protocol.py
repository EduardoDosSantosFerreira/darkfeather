"""
Protocolo de comunicação da rede local
Arquivo: network/protocol.py
"""

import json
import struct
from typing import Dict, Any, Optional


class Protocolo:
    """
    Gerencia o protocolo de comunicação entre cliente e servidor
    Formato: [4 bytes: tamanho][dados JSON]
    """
    
    CABECALHO_SIZE = 4  # 4 bytes para o tamanho
    
    @staticmethod
    def codificar(dados: Dict[str, Any]) -> bytes:
        """
        Codifica um dicionário para envio via socket
        Formato: [4 bytes de tamanho][dados JSON]
        """
        try:
            # Converter para JSON
            json_str = json.dumps(dados, ensure_ascii=False)
            dados_bytes = json_str.encode('utf-8')
            
            # Calcular tamanho e criar cabeçalho
            tamanho = len(dados_bytes)
            cabecalho = struct.pack('!I', tamanho)  # !I = network byte order, unsigned int
            
            # Retornar cabeçalho + dados
            return cabecalho + dados_bytes
        except Exception as e:
            print(f"Erro ao codificar: {e}")
            return b''
    
    @staticmethod
    def decodificar(dados: bytes) -> Optional[Dict[str, Any]]:
        """
        Decodifica dados recebidos do socket
        Retorna o dicionário ou None se incompleto
        """
        if len(dados) < Protocolo.CABECALHO_SIZE:
            return None
        
        try:
            # Extrair tamanho do cabeçalho
            tamanho = struct.unpack('!I', dados[:Protocolo.CABECALHO_SIZE])[0]
            
            # Verificar se temos todos os dados
            if len(dados) < Protocolo.CABECALHO_SIZE + tamanho:
                return None
            
            # Extrair dados JSON
            dados_json = dados[Protocolo.CABECALHO_SIZE:Protocolo.CABECALHO_SIZE + tamanho]
            
            return json.loads(dados_json.decode('utf-8'))
        except Exception as e:
            print(f"Erro ao decodificar: {e}")
            return None


class Comandos:
    """Constantes para comandos de rede"""
    
    # Comandos de cliente para servidor
    REGISTRAR = 'registrar'
    ENVIAR_MENSAGEM = 'enviar_mensagem'
    ENVIAR_ARQUIVO = 'enviar_arquivo'
    LISTAR_CLIENTES = 'listar_clientes'
    DESCONECTAR = 'desconectar'
    PING = 'ping'
    
    # Comandos de servidor para cliente
    CONEXAO_ACEITA = 'conexao_aceita'
    CONEXAO_RECUSADA = 'conexao_recusada'
    MENSAGEM_RECEBIDA = 'mensagem_recebida'
    LISTA_CLIENTES = 'lista_clientes'
    ARQUIVO_RECEBIDO = 'arquivo_recebido'
    PONG = 'pong'
    ERRO = 'erro'
    
    # Tipos de mensagem
    MSG_PRIVADA = 'privada'
    MSG_PUBLICA = 'publica'
    MSG_SERVIDOR = 'servidor'