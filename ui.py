from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QDialog,
    QLineEdit,
    QScrollArea,
    QHeaderView,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QColor


class CopyDialog(QDialog):
    def __init__(self, value, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Copiar Informação")
        self.setFixedSize(450, 180)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 5px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
                padding: 5px;
            }
            QLineEdit {
                background-color: #333;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 8px;
                font-size: 14px;
                selection-background-color: #4a90d9;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                margin: 10px 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        label = QLabel("Clique no botão para copiar:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.entry = QLineEdit()
        self.entry.setText(value)
        self.entry.setReadOnly(True)
        layout.addWidget(self.entry)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.copy_btn = QPushButton("📋 Copiar para Área de Transferência")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(self.copy_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.entry.text())
        self.copy_btn.setText("✔ Copiado!")
        self.copy_btn.setStyleSheet("background-color: #2E7D32;")


class WiFiProfileViewerUI(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.profile_data = []
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("DarkFeather - Wireless Connection PRO")
        self.setGeometry(100, 100, 1400, 850)
        self.setup_styles()

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Header
        header = QLabel("🦅 DarkFeather - Visualizador de Perfis Wi-Fi")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(
            """
            color: #fff;
            margin: 10px 0;
            padding: 10px;
            border-bottom: 2px solid #444;
        """
        )
        main_layout.addWidget(header)

        # Buttons
        btn_frame = QWidget()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(10)

        self.btn_search = QPushButton("🔍 Buscar e Atualizar")
        self.btn_search.clicked.connect(self.controller.show_profiles)
        self.btn_search.setFixedHeight(45)

        self.btn_reset = QPushButton("🧹 Limpar Tabela")
        self.btn_reset.clicked.connect(self.reset_ui)
        self.btn_reset.setFixedHeight(45)

        btn_layout.addWidget(self.btn_search)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()

        main_layout.addWidget(btn_frame)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(
            [
                "SSID",
                "Senha (ASCII)",
                "Senha (HEX)",
                "Adaptador",
                "GUID Adaptador",
                "Autenticação",
                "Criptografia",
                "Tipo de Conexão",
                "Modificado em",
                "Caminho do Perfil",
            ]
        )

        # Table configuration
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)

        # Enable horizontal scrolling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table)

        main_layout.addWidget(scroll_area)

        # Connect double click event
        self.table.cellDoubleClicked.connect(self.copy_cell)

        # Set button styles
        self.set_button_style(self.btn_search, "#4CAF50")
        self.set_button_style(self.btn_reset, "#f44336")

        # Status Bar
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet(
            """
            QStatusBar {
                color: #aaa;
                background-color: #333;
                border-top: 1px solid #444;
                padding-left: 8px;
            }
        """
        )

    def setup_styles(self):
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2b2b2b;
            }
            QTableWidget {
                background-color: #333;
                color: #e0e0e0;
                gridline-color: #444;
                font-size: 12px;
                border: 1px solid #444;
                border-radius: 3px;
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: #e0e0e0;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444;
            }
            QTableWidget::item:selected {
                background-color: #4a90d9;
                color: white;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background: #333;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """
        )

    def set_button_style(self, button, color):
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }}
            QPushButton:hover {{
                background-color: {'#45a049' if color == '#4CAF50' else 
                                 '#d32f2f' if color == '#f44336' else 
                                 '#1976D2'};
            }}
            QPushButton:pressed {{
                background-color: {'#3d8b40' if color == '#4CAF50' else 
                                  '#b71c1c' if color == '#f44336' else 
                                  '#0D47A1'};
            }}
        """
        )

    def display_profiles(self, profiles):
        self.table.setRowCount(0)
        self.profile_data = profiles
        self.table.setRowCount(len(profiles))

        for row, profile in enumerate(profiles):
            for col, key in enumerate(
                [
                    "SSID",
                    "Senha (ASCII)",
                    "Senha (HEX)",
                    "Adaptador",
                    "GUID Adaptador",
                    "Autenticação",
                    "Criptografia",
                    "Tipo de Conexão",
                    "Modificado em",
                    "Caminho do Perfil",
                ]
            ):
                value = str(profile.get(key, ""))

                # Abrevia o caminho do perfil
                if key == "Caminho do Perfil" and value:
                    parts = value.split("\\")
                    if len(parts) > 4:
                        value = f"{parts[0]}\\{parts[1]}\\...\\{parts[-2]}\\{parts[-1]}"

                item = QTableWidgetItem(value)

                # Alinhamento e estilo para diferentes colunas
                if key in ["Senha (ASCII)", "Senha (HEX)"]:
                    item.setForeground(QColor("#FF9800"))  # Laranja para senhas
                    item.setFont(QFont("Consolas", 10))
                elif key == "SSID":
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))

                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()
        self.status_bar.showMessage(
            f"Mostrando {len(profiles)} perfis Wi-Fi | Atualizado em {self.controller.get_current_time()}"
        )

    def reset_ui(self):
        self.table.setRowCount(0)
        self.status_bar.showMessage("Pronto")

    def copy_cell(self, row, column):
        item = self.table.item(row, column)
        if item:
            # Recupera o valor original se for o caminho abreviado
            if column == 9 and "..." in item.text():  # Coluna "Caminho do Perfil"
                original_value = self.profile_data[row].get("Caminho do Perfil", "")
                dialog = CopyDialog(original_value, self)
            else:
                dialog = CopyDialog(item.text(), self)
            dialog.exec_()
