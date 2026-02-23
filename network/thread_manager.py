"""
Gerenciador de threads para evitar bloqueios
"""
import threading
import queue
from typing import Callable, Any


class ThreadManager:
    """Gerencia threads e filas de forma segura"""
    
    def __init__(self):
        self.threads = []
        self.stop_events = {}
        self.queues = {}
    
    def criar_thread(self, nome: str, alvo: Callable, args: tuple = ()) -> threading.Thread:
        """Cria e inicia uma thread monitorada"""
        stop_event = threading.Event()
        self.stop_events[nome] = stop_event
        
        thread = threading.Thread(
            target=alvo,
            args=args + (stop_event,),
            daemon=True,
            name=nome
        )
        thread.start()
        self.threads.append(thread)
        return thread
    
    def criar_fila(self, nome: str) -> queue.Queue:
        """Cria uma fila nomeada"""
        fila = queue.Queue()
        self.queues[nome] = fila
        return fila
    
    def parar_todas(self):
        """Para todas as threads"""
        for nome, event in self.stop_events.items():
            event.set()
        
        for thread in self.threads:
            thread.join(timeout=1.0)