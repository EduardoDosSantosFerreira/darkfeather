"""
Cliente TCP para rede local - VERSÃO ULTRA SIMPLIFICADA
Arquivo: network/client.py
"""

import socket
import threading
import json
import time
from typing import Optional, Callable
from datetime import datetime

from network.protocol import Protocolo, Comandos


class ClienteTCP:
    """
    Cliente TCP ultra simplificado - sem callbacks complexos
    """
    
    def __init__(self, host: str = '127.0.0.1', porta: int = 8888):
        self.host = host
        self.porta = porta
        self.socket_cliente = None
        self.conectado = False
        self.cliente_id = 0
        self.nome = f"Cliente_{id(self)}"
        
        # Callbacks
        self.on_mensagem = None
        self.on_lista_clientes = None
        self.on_desconectado = None
    
    def conectar(self) -> bool:
        """Conecta ao servidor"""
        try:
            # Criar socket
            self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_cliente.settimeout(3)
            self.socket_cliente.connect((self.host, self.porta))
            self.socket_cliente.setblocking(False)
            
            self.conectado = True
            
            # Iniciar thread de recebimento
            thread = threading.Thread(target=self._loop_receber, daemon=True)
            thread.start()
            
            # Registrar automaticamente
            self._registrar()
            
            return True
            
        except Exception as e:
            print(f"Erro conexão: {e}")
            return False
    
    def _loop_receber(self):
        """Loop de recebimento simplificado"""
        buffer = bytearray()
        
        while self.conectado:
            try:
                dados = self.socket_cliente.recv(4096)
                
                if not dados:
                    break
                
                buffer.extend(dados)
                
                while len(buffer) >= 4:
                    msg = Protocolo.decodificar(bytes(buffer))
                    if msg is None:
                        break
                    
                    # Calcular tamanho
                    dados_json = json.dumps(msg).encode('utf-8')
                    tamanho = 4 + len(dados_json)
                    buffer = buffer[tamanho:]
                    
                    # Processar mensagem
                    self._processar_mensagem(msg)
                    
            except BlockingIOError:
                time.sleep(0.05)
                continue
            except Exception as e:
                print(f"Erro receive: {e}")
                break
        
        self._desconectar()
    
    def _processar_mensagem(self, msg: dict):
        """Processa mensagem recebida"""
        try:
            comando = msg.get('comando')
            
            if comando == Comandos.CONEXAO_ACEITA:
                self.cliente_id = msg.get('cliente_id', 0)
                print(f"Conectado como ID {self.cliente_id}")
                
            elif comando == Comandos.MENSAGEM_RECEBIDA:
                if self.on_mensagem:
                    origem = msg.get('origem', '')
                    conteudo = msg.get('mensagem', '')
                    tipo = msg.get('tipo', 'publica')
                    self.on_mensagem(origem, conteudo, tipo)
                    
            elif comando == Comandos.LISTA_CLIENTES:
                if self.on_lista_clientes:
                    self.on_lista_clientes(msg.get('clientes', []))
                    
        except Exception as e:
            print(f"Erro processar: {e}")
    
    def _registrar(self):
        """Registra no servidor"""
        self._enviar({
            'comando': Comandos.REGISTRAR,
            'nome': self.nome
        })
    
    def enviar_mensagem(self, mensagem: str, destino: str = 'todos'):
        """Envia mensagem"""
        self._enviar({
            'comando': Comandos.ENVIAR_MENSAGEM,
            'destino': destino,
            'conteudo': mensagem
        })
    
    def listar_clientes(self):
        """Solicita lista de clientes"""
        self._enviar({
            'comando': Comandos.LISTAR_CLIENTES
        })
    
    def _enviar(self, dados: dict):
        """Envia dados"""
        if not self.conectado:
            return
        
        try:
            dados_bytes = Protocolo.codificar(dados)
            if dados_bytes:
                self.socket_cliente.send(dados_bytes)
        except Exception as e:
            print(f"Erro enviar: {e}")
            self._desconectar()
    
    def _desconectar(self):
        """Desconecta"""
        if not self.conectado:
            return
        
        self.conectado = False
        if self.socket_cliente:
            try:
                self.socket_cliente.close()
            except:
                pass
        
        if self.on_desconectado:
            self.on_desconectado()
    
    def desconectar(self):
        """Desconecta voluntariamente"""
        self._enviar({'comando': Comandos.DESCONECTAR})
        self._desconectar()