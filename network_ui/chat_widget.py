"""
Widget de chat para comunicação em rede local
Arquivo: network_ui/chat_widget.py
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel, QFrame,
    QListWidget, QListWidgetItem, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor
import qtawesome as qta
from datetime import datetime
import traceback


class UserListItem(QWidget):
    """Item da lista de usuários conectados"""
    
    clicked = Signal(str, int)  # nome, id
    
    def __init__(self, user_id: int, nome: str, endereco: str, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.nome = nome
        self.endereco = endereco
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Status (online)
        status_label = QLabel("●")
        status_label.setStyleSheet("color: #10b981; font-size: 14px;")
        layout.addWidget(status_label)
        
        # Informações do usuário
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        nome_label = QLabel(f"{self.nome}")
        nome_label.setStyleSheet("color: #0f172a; font-weight: 600; font-size: 12px;")
        info_layout.addWidget(nome_label)
        
        endereco_label = QLabel(f"ID: {self.user_id} • {self.endereco}")
        endereco_label.setStyleSheet("color: #64748b; font-size: 10px;")
        info_layout.addWidget(endereco_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Botão para mensagem privada
        self.btn_privado = QPushButton()
        self.btn_privado.setIcon(qta.icon('fa5s.lock', color='#64748b'))
        self.btn_privado.setFixedSize(24, 24)
        self.btn_privado.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.btn_privado.setToolTip("Enviar mensagem privada")
        self.btn_privado.clicked.connect(self.on_clicked)
        layout.addWidget(self.btn_privado)
    
    def on_clicked(self):
        try:
            self.clicked.emit(self.nome, self.user_id)
        except Exception as e:
            print(f"Erro no click do usuário: {e}")


class ChatWidget(QWidget):
    """
    Widget de chat reutilizável para comunicação em rede
    """
    
    mensagem_enviada = Signal(str, str)  # mensagem, destino
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.usuario_atual = None
        self.user_id_atual = None
        self.destino_atual = 'todos'
        self.destino_nome = 'Todos'
        self.usuarios = {}
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        
        # Painel esquerdo - Lista de usuários
        self.users_widget = QWidget()
        users_layout = QVBoxLayout(self.users_widget)
        users_layout.setContentsMargins(0, 0, 0, 0)
        
        users_title = QLabel("👥 Usuários Online")
        users_title.setStyleSheet("font-weight: 600; color: #0f172a; padding: 4px;")
        users_layout.addWidget(users_title)
        
        self.users_list = QListWidget()
        self.users_list.setFrameShape(QFrame.NoFrame)
        self.users_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        users_layout.addWidget(self.users_list)
        
        splitter.addWidget(self.users_widget)
        
        # Painel direito - Chat
        self.chat_widget = QWidget()
        chat_layout = QVBoxLayout(self.chat_widget)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(8)
        
        # Área de destino atual
        self.destino_bar = QFrame()
        self.destino_bar.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
            }
        """)
        destino_layout = QHBoxLayout(self.destino_bar)
        destino_layout.setContentsMargins(8, 4, 8, 4)
        
        self.destino_icon = QLabel("📢")
        destino_layout.addWidget(self.destino_icon)
        
        self.destino_label = QLabel("Enviando para: <b>Todos</b>")
        self.destino_label.setStyleSheet("color: #0f172a; font-size: 12px;")
        destino_layout.addWidget(self.destino_label)
        
        destino_layout.addStretch()
        
        self.btn_limpar_destino = QPushButton(" Mudar")
        self.btn_limpar_destino.setIcon(qta.icon('fa5s.sync-alt', color='#64748b'))
        self.btn_limpar_destino.setFixedSize(60, 24)
        self.btn_limpar_destino.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.btn_limpar_destino.clicked.connect(self.voltar_para_todos)
        destino_layout.addWidget(self.btn_limpar_destino)
        
        chat_layout.addWidget(self.destino_bar)
        
        # Área de mensagens
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        self.messages_area.setFrameShape(QFrame.NoFrame)
        self.messages_area.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                font-size: 13px;
            }
        """)
        chat_layout.addWidget(self.messages_area)
        
        # Área de entrada
        input_widget = QFrame()
        input_widget.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
            }
        """)
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(8, 4, 8, 4)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Digite sua mensagem...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: none;
                background-color: transparent;
                padding: 8px;
                font-size: 13px;
            }
        """)
        self.input_field.returnPressed.connect(self.enviar_mensagem)
        input_layout.addWidget(self.input_field)
        
        self.btn_enviar = QPushButton()
        self.btn_enviar.setIcon(qta.icon('fa5s.paper-plane', color='#ffffff'))
        self.btn_enviar.setFixedSize(32, 32)
        self.btn_enviar.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        self.btn_enviar.clicked.connect(self.enviar_mensagem)
        self.btn_enviar.setEnabled(False)
        input_layout.addWidget(self.btn_enviar)
        
        chat_layout.addWidget(input_widget)
        
        splitter.addWidget(self.chat_widget)
        
        # Configurar tamanhos do splitter
        splitter.setSizes([200, 600])
        layout.addWidget(splitter)
    
    def set_usuario_atual(self, usuario: str, user_id: int):
        """Define o usuário atual"""
        try:
            self.usuario_atual = usuario
            self.user_id_atual = user_id
            self.btn_enviar.setEnabled(True)
            self.adicionar_mensagem_sistema(f"👤 Você entrou como {usuario}")
        except Exception as e:
            print(f"Erro set_usuario_atual: {e}")
    
    def atualizar_usuarios(self, usuarios: list):
        """Atualiza a lista de usuários conectados"""
        try:
            self.users_list.clear()
            self.usuarios.clear()
            
            for user in usuarios:
                user_id = user['id']
                nome = user['nome']
                endereco = user.get('endereco', 'desconhecido')
                
                # Não mostrar a si mesmo
                if user_id == self.user_id_atual:
                    continue
                
                # Criar item personalizado
                item = QListWidgetItem(self.users_list)
                widget = UserListItem(user_id, nome, str(endereco))
                widget.clicked.connect(lambda n, i: self.iniciar_conversa_privada(n, i))
                
                item.setSizeHint(widget.sizeHint())
                self.users_list.addItem(item)
                self.users_list.setItemWidget(item, widget)
                
                self.usuarios[user_id] = nome
        except Exception as e:
            print(f"Erro atualizar_usuarios: {e}")
            traceback.print_exc()
    
    def adicionar_mensagem(self, mensagem: str, origem: str, tipo: str = 'publica'):
        """Adiciona uma mensagem à área de chat"""
        try:
            if not origem or not mensagem:
                return
            
            is_me = (origem == self.usuario_atual)
            timestamp = datetime.now().strftime("%H:%M")
            
            # Formatar mensagem
            if tipo == 'sistema':
                html = f"""
                <div style='text-align: center; color: #64748b; font-style: italic; margin: 8px;'>
                    ⚙️ {mensagem}
                </div>
                """
            elif tipo == 'privada':
                if is_me:
                    html = f"""
                    <div style='text-align: right; margin: 4px;'>
                        <div style='background-color: #2563eb; color: white; border-radius: 12px; padding: 8px 12px; display: inline-block; max-width: 70%;'>
                            <div><b>Você</b> <span style='color: #ffffff80; font-size: 10px;'> {timestamp}</span></div>
                            <div style='margin-top: 4px;'>{mensagem}</div>
                            <div style='font-size: 9px; color: #ffffff80; margin-top: 4px;'>🔒 Privado</div>
                        </div>
                    </div>
                    """
                else:
                    html = f"""
                    <div style='text-align: left; margin: 4px;'>
                        <div style='background-color: #7c3aed; color: white; border-radius: 12px; padding: 8px 12px; display: inline-block; max-width: 70%;'>
                            <div><b>{origem}</b> <span style='color: #ffffff80; font-size: 10px;'> {timestamp}</span></div>
                            <div style='margin-top: 4px;'>{mensagem}</div>
                            <div style='font-size: 9px; color: #ffffff80; margin-top: 4px;'>🔒 Privado</div>
                        </div>
                    </div>
                    """
            else:  # pública
                if is_me:
                    html = f"""
                    <div style='text-align: right; margin: 4px;'>
                        <div style='background-color: #2563eb; color: white; border-radius: 12px; padding: 8px 12px; display: inline-block; max-width: 70%;'>
                            <div><b>Você</b> <span style='color: #ffffff80; font-size: 10px;'> {timestamp}</span></div>
                            <div style='margin-top: 4px;'>{mensagem}</div>
                        </div>
                    </div>
                    """
                else:
                    html = f"""
                    <div style='text-align: left; margin: 4px;'>
                        <div style='background-color: #f1f5f9; color: #0f172a; border-radius: 12px; padding: 8px 12px; display: inline-block; max-width: 70%;'>
                            <div><b>{origem}</b> <span style='color: #64748b; font-size: 10px;'> {timestamp}</span></div>
                            <div style='margin-top: 4px;'>{mensagem}</div>
                        </div>
                    </div>
                    """
            
            # Adicionar ao final
            cursor = self.messages_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertHtml(html)
            cursor.insertText("\n")
            
            # Rolar para o final
            self.messages_area.ensureCursorVisible()
        except Exception as e:
            print(f"Erro adicionar_mensagem: {e}")
    
    def adicionar_mensagem_sistema(self, mensagem: str):
        """Adiciona uma mensagem do sistema"""
        try:
            if not mensagem:
                return
            
            html = f"""
            <div style='text-align: center; color: #64748b; font-style: italic; margin: 8px;'>
                ⚙️ {mensagem}
            </div>
            """
            
            cursor = self.messages_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertHtml(html)
            cursor.insertText("\n")
            self.messages_area.ensureCursorVisible()
        except Exception as e:
            print(f"Erro mensagem sistema: {e}")
    
    def iniciar_conversa_privada(self, nome: str, user_id: int):
        """Inicia uma conversa privada com um usuário"""
        try:
            self.destino_atual = str(user_id)
            self.destino_nome = nome
            self.destino_icon.setText("🔒")
            self.destino_label.setText(f"Enviando para: <b>{nome}</b> (privado)")
            self.adicionar_mensagem_sistema(f"🔒 Agora enviando mensagens privadas para {nome}")
        except Exception as e:
            print(f"Erro iniciar conversa: {e}")
    
    def voltar_para_todos(self):
        """Volta para o modo público"""
        try:
            self.destino_atual = 'todos'
            self.destino_nome = 'Todos'
            self.destino_icon.setText("📢")
            self.destino_label.setText("Enviando para: <b>Todos</b>")
            self.adicionar_mensagem_sistema("📢 Agora enviando mensagens públicas")
        except Exception as e:
            print(f"Erro voltar para todos: {e}")
    
    def enviar_mensagem(self):
        """Envia a mensagem digitada"""
        try:
            mensagem = self.input_field.text().strip()
            if not mensagem:
                return
            
            # Emitir sinal
            self.mensagem_enviada.emit(mensagem, self.destino_atual)
            
            # Mostrar a mensagem localmente
            self.adicionar_mensagem(mensagem, self.usuario_atual, 
                                   'privada' if self.destino_atual != 'todos' else 'publica')
            
            # Limpar campo
            self.input_field.clear()
        except Exception as e:
            print(f"Erro enviar mensagem: {e}")
    
    def limpar_chat(self):
        """Limpa todas as mensagens"""
        try:
            self.messages_area.clear()
        except Exception as e:
            print(f"Erro limpar chat: {e}")
    
    def set_conectado(self, conectado: bool):
        """Habilita/desabilita a interface baseado no estado da conexão"""
        try:
            self.btn_enviar.setEnabled(conectado)
            self.input_field.setEnabled(conectado)
            
            if not conectado:
                self.limpar_chat()
                self.users_list.clear()
                self.voltar_para_todos()
        except Exception as e:
            print(f"Erro set_conectado: {e}")