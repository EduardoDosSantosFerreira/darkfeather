import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os

# Variáveis globais para manter referências dos ícones
_global_icons = {}

def _get_native_icon(icon_name, size):
    """Cria ícones nativos usando caracteres Unicode ou símbolos"""
    icons = {
        "logo": "🪶",  # Pena (pode ajustar para outro símbolo)
        "search": "🛜",
        "reset": "🔄",
        "copy": "📚",  # Símbolo de cópia
    }
    return icons.get(icon_name, "")

def setup_ui(root):
    # Configurar ícone da janela usando ícone padrão
    try:
        root.iconbitmap(default='')  # Isso usará o ícone padrão do Tkinter
    except:
        pass  # Se falhar, continuamos sem ícone

    root.configure(bg="#111111")

    style = ttk.Style(root)
    style.theme_use("default")
    style.configure(
        "Treeview",
        background="#111111",
        foreground="white",
        fieldbackground="#111111",
        rowheight=28,
        font=("Segoe UI", 10),
    )
    style.map("Treeview", background=[("selected", "#333333")])
    style.configure(
        "Treeview.Heading",
        background="#1a1a1a",
        foreground="white",
        font=("Segoe UI", 10, "bold"),
    )

    # Frame de cabeçalho com fundo branco
    header_frame = tk.Frame(root, bg="#ffffff")
    header_frame.pack(pady=(15, 5), fill="x")

    # Logo usando símbolo Unicode
    logo_symbol = _get_native_icon("logo", 1)
    logo_label = tk.Label(
        header_frame, 
        text=logo_symbol, 
        bg="#ffffff",
        font=("Segoe UI", 24)
    )
    logo_label.pack(side="left", padx=(20, 10))

    header = tk.Label(
        header_frame,
        text="DarkFeather",
        font=("Segoe UI", 16, "bold"),
        fg="black",
        bg="#ffffff",
    )
    header.pack(side="left")

    btn_frame = tk.Frame(root, bg="#111111")
    btn_frame.pack(pady=10)

    # Botão de busca com ícone Unicode
    search_symbol = _get_native_icon("search", 1)
    btn_search = tk.Button(
        btn_frame,
        text=f" {search_symbol} Buscar e Atualizar",
        bg="white",
        fg="black",
        font=("Segoe UI", 13, "bold"),
        relief="flat",
        padx=14,
        pady=7,
        cursor="hand2",
    )
    btn_search.pack(side="left", padx=10)

    # Botão de reset com ícone Unicode
    reset_symbol = _get_native_icon("reset", 1)
    btn_reset = tk.Button(
        btn_frame,
        text=f" {reset_symbol} Resetar UI",
        bg="#ffffff",
        fg="#000000",
        font=("Segoe UI", 13, "bold"),
        relief="flat",
        padx=14,
        pady=7,
        cursor="hand2",
    )
    btn_reset.pack(side="left", padx=10)

    columns = [
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

    tree_frame = tk.Frame(root, bg="#111111")
    tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=160, anchor="w")

    scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)

    tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    return tree, btn_search, btn_reset

def create_copy_window(root, value):
    top = tk.Toplevel(root)
    top.title("Copiar Informação")
    top.configure(bg="#111111")
    top.geometry("500x120")
    top.resizable(False, False)

    # Ícone de cópia Unicode
    copy_symbol = _get_native_icon("copy", 1)

    label = tk.Label(
        top, text="Clique para copiar:", font=("Segoe UI", 12), bg="#111111", fg="white"
    )
    label.pack(pady=(10, 0))

    entry = tk.Entry(
        top,
        font=("Segoe UI", 13),
        fg="black",
        bg="white",
        relief="flat",
        justify="left",
    )
    entry.insert(0, value)
    entry.configure(state="readonly")
    entry.pack(padx=20, pady=10, fill="x")

    btn = tk.Button(
        top,
        text=f" {copy_symbol} Copiar",
        font=("Segoe UI", 12, "bold"),
        bg="white",
        fg="black",
        relief="flat",
        padx=10,
        pady=5,
        cursor="hand2",
    )
    btn.pack(pady=(0, 10))

    return btn