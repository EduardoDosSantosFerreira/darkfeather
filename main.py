import tkinter as tk
import sys
import ctypes
from ui import setup_ui, create_copy_window
from system import is_admin, extract_profiles

def main():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    root = tk.Tk()
    root.title("DarkFeather - Wireless Connection PRO")
    root.geometry("1280x600")
    
    # Definir ícone mínimo (fallback caso a UI não consiga carregar)
    try:
        root.iconbitmap(default='darkfeather.ico')
    except:
        pass

    tree, btn_search, btn_reset = setup_ui(root)
    profile_data = []

    def show_profiles():
        tree.delete(*tree.get_children())
        nonlocal profile_data
        profile_data = extract_profiles()
        for profile in profile_data:
            values = [profile[col] for col in tree["columns"]]
            tree.insert("", "end", values=values)

    def reset_ui():
        tree.delete(*tree.get_children())

    def copy_cell(event):
        item_id = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        if not item_id or not column:
            return
        col_index = int(column[1:]) - 1
        value = tree.item(item_id, "values")[col_index]

        btn = create_copy_window(root, value)
        btn.configure(command=lambda: copy_to_clipboard(value, btn.winfo_toplevel()))

    def copy_to_clipboard(value, window):
        root.clipboard_clear()
        root.clipboard_append(value)
        root.update()
        window.destroy()

    btn_search.config(command=show_profiles)
    btn_reset.config(command=reset_ui)
    tree.bind("<Double-1>", copy_cell)

    # Centralizar a janela na tela
    root.eval('tk::PlaceWindow . center')
    
    root.mainloop()

if __name__ == "__main__":
    main()