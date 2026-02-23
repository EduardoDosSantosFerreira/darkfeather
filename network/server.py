"""
Servidor TCP para rede local - VERSÃO CORRIGIDA
Arquivo: network/server.py
"""

import socket
import threading
import queue
import json
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime

from network.protocol import Protocolo, Comandos
from logs.logger import NetworkLogger


class ServidorTCP:
    """
    Servidor TCP que gerencia múltiplos clientes
    """
    
    def __init__(self, host: str = '0.0.0.0', porta: int = 8888):
        self.host = host
        self.porta = porta
        self.logger = NetworkLogger("servidor")
        
        # Socket principal
        self.socket_servidor = None
        self.rodando = False
        
        # Controle de clientes
        self.clientes: Dict[int, Dict] = {}  # id -> informações
        self.proximo_id = 1
        self.lock_clientes = threading.Lock()
        
        # Filas de mensagens
        self.fila_mensagens = queue.Queue()
        
        # Callbacks para eventos
        self.on_cliente_conectado: Optional[Callable] = None
        self.on_cliente_desconectado: Optional[Callable] = None
        
        self.logger.info(f"🚀 Servidor inicializado - {host}:{porta}")
    
    def iniciar(self) -> bool:
        """
        Inicia o servidor e começa a aceitar conexões
        """
        try:
            # Criar socket
            self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_servidor.bind((self.host, self.porta))
            self.socket_servidor.listen(5)
            self.socket_servidor.setblocking(False)
            
            self.rodando = True
            
            # Thread principal de aceitação
            thread_aceitar = threading.Thread(target=self._loop_aceitar, daemon=True)
            thread_aceitar.start()
            
            # Thread de processamento de mensagens
            thread_processar = threading.Thread(target=self._processar_mensagens, daemon=True)
            thread_processar.start()
            
            self.logger.info(f"✅ Servidor iniciado em {self.host}:{self.porta}")
            return True
            
        except Exception as e:
            self.logger.erro(f"iniciar: {str(e)}")
            return False
    
    def _loop_aceitar(self):
        """Loop principal para aceitar novas conexões"""
        while self.rodando:
            try:
                # Aceitar nova conexão
                cliente_socket, endereco = self.socket_servidor.accept()
                
                # Configurar socket do cliente
                cliente_socket.setblocking(False)
                
                # Registrar novo cliente
                with self.lock_clientes:
                    cliente_id = self.proximo_id
                    self.proximo_id += 1
                    
                    self.clientes[cliente_id] = {
                        'socket': cliente_socket,
                        'endereco': endereco,
                        'nome': f"Cliente_{cliente_id}",
                        'buffer': b''
                    }
                
                self.logger.conexao(f"Cliente {cliente_id} conectado de {endereco[0]}:{endereco[1]}")
                
                # Iniciar thread para este cliente
                thread_cliente = threading.Thread(
                    target=self._gerenciar_cliente,
                    args=(cliente_id,),
                    daemon=True
                )
                thread_cliente.start()
                
                # Notificar via callback
                if self.on_cliente_conectado:
                    self.on_cliente_conectado(cliente_id, endereco)
                
                # Enviar confirmação de conexão
                self._enviar_para_cliente(cliente_id, {
                    'comando': Comandos.CONEXAO_ACEITA,
                    'cliente_id': cliente_id,
                    'mensagem': f'Conectado ao servidor'
                })
                
            except BlockingIOError:
                time.sleep(0.1)
                continue
            except Exception as e:
                if self.rodando:
                    self.logger.erro(f"aceitar_conexao: {str(e)}")
                break
    
    def _gerenciar_cliente(self, cliente_id: int):
        """
        Gerencia um cliente específico
        """
        cliente = self.clientes.get(cliente_id)
        if not cliente:
            return
        
        socket_cliente = cliente['socket']
        buffer = bytearray()
        
        while self.rodando and cliente_id in self.clientes:
            try:
                # Receber dados
                dados = socket_cliente.recv(4096)
                
                if not dados:
                    self._remover_cliente(cliente_id, "conexão encerrada")
                    break
                
                # Adicionar ao buffer
                buffer.extend(dados)
                
                # Processar mensagens completas
                while len(buffer) >= 4:
                    mensagem_dict = Protocolo.decodificar(bytes(buffer))
                    
                    if mensagem_dict is None:
                        break
                    
                    # Calcular tamanho da mensagem processada
                    dados_json = json.dumps(mensagem_dict).encode('utf-8')
                    tamanho_total = 4 + len(dados_json)
                    buffer = buffer[tamanho_total:]
                    
                    # Processar mensagem
                    self._processar_mensagem_cliente(cliente_id, mensagem_dict)
                
            except BlockingIOError:
                time.sleep(0.05)
                continue
            except ConnectionResetError:
                self._remover_cliente(cliente_id, "conexão resetada")
                break
            except Exception as e:
                self.logger.erro(f"cliente_{cliente_id}: {str(e)}")
                self._remover_cliente(cliente_id, f"erro: {str(e)}")
                break
    
    def _processar_mensagem_cliente(self, cliente_id: int, dados: dict):
        """
        Processa uma mensagem recebida de um cliente
        """
        cliente = self.clientes.get(cliente_id)
        if not cliente:
            return
        
        comando = dados.get('comando')
        
        if comando == Comandos.REGISTRAR:
            # Registrar nome do cliente
            nome = dados.get('nome', f"Cliente_{cliente_id}")
            cliente['nome'] = nome
            self.logger.info(f"📝 Cliente {cliente_id} registrado como '{nome}'")
            
            # Notificar todos que um novo cliente entrou
            self._broadcast({
                'comando': Comandos.MENSAGEM_RECEBIDA,
                'origem': 'SERVIDOR',
                'mensagem': f"👤 {nome} entrou no chat",
                'tipo': 'sistema'
            })
            
        elif comando == Comandos.ENVIAR_MENSAGEM:
            # Enviar mensagem
            destino = dados.get('destino', 'todos')
            conteudo = dados.get('conteudo', '')
            
            # Criar mensagem
            mensagem = {
                'comando': Comandos.MENSAGEM_RECEBIDA,
                'origem': cliente['nome'],
                'mensagem': conteudo,
                'tipo': 'publica' if destino == 'todos' else 'privada'
            }
            
            if destino == 'todos':
                # Broadcast para todos
                self._broadcast(mensagem)
                self.logger.mensagem(f"{cliente['nome']}: {conteudo[:50]}")
            else:
                # Mensagem privada
                try:
                    destino_id = int(destino)
                    if self._enviar_para_cliente(destino_id, mensagem):
                        self.logger.mensagem(f"Privado: {cliente['nome']} → {destino_id}")
                    else:
                        self._enviar_para_cliente(cliente_id, {
                            'comando': Comandos.ERRO,
                            'mensagem': f'Cliente {destino} não encontrado'
                        })
                except ValueError:
                    self._enviar_para_cliente(cliente_id, {
                        'comando': Comandos.ERRO,
                        'mensagem': f'Destino inválido: {destino}'
                    })
            
        elif comando == Comandos.LISTAR_CLIENTES:
            # Enviar lista de clientes
            self._enviar_lista_clientes(cliente_id)
            
        elif comando == Comandos.DESCONECTAR:
            self._remover_cliente(cliente_id, "solicitado pelo cliente")
    
    def _processar_mensagens(self):
        """Processa fila de mensagens (não usado no momento)"""
        while self.rodando:
            time.sleep(0.1)
    
    def _enviar_para_cliente(self, cliente_id: int, dados: dict) -> bool:
        """
        Envia dados para um cliente específico
        """
        with self.lock_clientes:
            cliente = self.clientes.get(cliente_id)
            if not cliente:
                return False
            
            try:
                dados_bytes = Protocolo.codificar(dados)
                if dados_bytes:
                    cliente['socket'].send(dados_bytes)
                    return True
                return False
            except Exception as e:
                self.logger.erro(f"enviar_para_{cliente_id}: {str(e)}")
                return False
    
    def _broadcast(self, dados: dict, ignore_cliente: Optional[int] = None):
        """
        Envia dados para todos os clientes conectados
        """
        with self.lock_clientes:
            for cliente_id in list(self.clientes.keys()):
                if ignore_cliente and cliente_id == ignore_cliente:
                    continue
                self._enviar_para_cliente(cliente_id, dados)
    
    def _enviar_lista_clientes(self, cliente_id: int):
        """
        Envia lista de clientes conectados para um cliente
        """
        with self.lock_clientes:
            lista = []
            for cid, info in self.clientes.items():
                lista.append({
                    'id': cid,
                    'nome': info['nome'],
                    'endereco': f"{info['endereco'][0]}:{info['endereco'][1]}"
                })
        
        self._enviar_para_cliente(cliente_id, {
            'comando': Comandos.LISTA_CLIENTES,
            'clientes': lista
        })
    
    def _remover_cliente(self, cliente_id: int, motivo: str = ""):
        """
        Remove um cliente da lista e fecha sua conexão
        """
        with self.lock_clientes:
            cliente = self.clientes.pop(cliente_id, None)
            
        if cliente:
            try:
                cliente['socket'].close()
            except:
                pass
            
            nome = cliente['nome']
            endereco = cliente['endereco']
            self.logger.desconexao(f"Cliente {cliente_id} ({nome}) - {motivo}")
            
            # Notificar outros clientes
            self._broadcast({
                'comando': Comandos.MENSAGEM_RECEBIDA,
                'origem': 'SERVIDOR',
                'mensagem': f"👋 {nome} saiu do chat",
                'tipo': 'sistema'
            })
            
            if self.on_cliente_desconectado:
                self.on_cliente_desconectado(cliente_id, motivo)
    
    def parar(self):
        """Para o servidor e fecha todas as conexões"""
        self.logger.info("🛑 Parando servidor...")
        self.rodando = False
        
        # Fechar todas as conexões
        with self.lock_clientes:
            for cliente_id, cliente in list(self.clientes.items()):
                try:
                    cliente['socket'].close()
                except:
                    pass
            self.clientes.clear()
        
        # Fechar socket do servidor
        if self.socket_servidor:
            try:
                self.socket_servidor.close()
            except:
                pass
        
        self.logger.info("✅ Servidor parado")
    
    def listar_clientes(self) -> List[Dict]:
        """Retorna lista de clientes conectados"""
        with self.lock_clientes:
            return [
                {
                    'id': cid,
                    'nome': info['nome'],
                    'endereco': info['endereco']
                }
                for cid, info in self.clientes.items()
            ]
    
    def enviar_mensagem_para_todos(self, mensagem: str):
        """Envia mensagem para todos os clientes"""
        self._broadcast({
            'comando': Comandos.MENSAGEM_RECEBIDA,
            'origem': 'SERVIDOR',
            'mensagem': mensagem,
            'tipo': 'publica'
        })
        self.logger.info(f"📢 Broadcast: {mensagem}")