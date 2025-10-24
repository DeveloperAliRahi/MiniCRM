# gui/common.py
"""
GUI shared helpers and theme.

This file:
 - forces a neutral light/grey QuickBooks-like theme so Dark Mode won't change it
 - exposes style_tk_widget() for plain tk widgets
 - exposes apply_tree_row_striping() to stripe treeview rows
 - exposes choose_template_dialog(root, template_manager) used by ContactView
"""

import subprocess
import tkinter as tk
from tkinter import ttk, font, messagebox

# Palette dictionary populated by apply_theme()
PALETTE = {}

def apply_theme(root):
    """
    Set a neutral light/grey palette and configure ttk styles.
    Call once after creating root = tk.Tk()
    """
    # QuickBooks-like light palette
    BG          = "#F2F3F4"
    PANEL       = "#DEDFE0"
    ENTRY_BG    = "#FFFFFF"
    FG          = "#202124"
    MUTED_FG    = "#4B4F52"
    BTN_BG      = "#D5D8DA"
    BTN_FG      = "#202124"
    SELECT_BG   = "#C7CBCD"
    HEADING_FG  = "#1B1D1E"

    PALETTE.update({
        "BG":BG, "PANEL":PANEL, "ENTRY_BG":ENTRY_BG, "FG":FG,
        "MUTED_FG":MUTED_FG, "BTN_BG":BTN_BG, "BTN_FG":BTN_FG,
        "SELECT_BG":SELECT_BG, "HEADING_FG":HEADING_FG
    })

    root.configure(bg=BG)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        # If clam not available, ignore
        pass

    # Basic ttk styling
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("TLabelFrame", background=BG, foreground=FG)
    style.configure("TLabelframe", background=BG, foreground=FG)
    style.configure("TNotebook", background=BG)
    style.configure("TNotebook.Tab", background=PANEL, foreground=FG)
    style.configure("TButton", background=BTN_BG, foreground=BTN_FG)
    style.configure("TCombobox", fieldbackground=ENTRY_BG, background=ENTRY_BG, foreground=FG)
    style.configure("Treeview", background=ENTRY_BG, fieldbackground=ENTRY_BG, foreground=FG)
    style.configure("Treeview.Heading", background=PANEL, foreground=HEADING_FG, font=('TkDefaultFont', 10, 'bold'))

    style.map("TButton",
              background=[("active", BTN_BG)],
              foreground=[("active", BTN_FG)])
    style.map("Treeview",
              background=[("selected", SELECT_BG)],
              foreground=[("selected", FG)])

    try:
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=10)
    except Exception:
        pass

def style_tk_widget(w):
    """
    Apply palette to plain tkinter widgets (Entry, Text, Listbox, Button).
    Call this after creating a tk widget.
    """
    try:
        ENTRY_BG = PALETTE.get("ENTRY_BG", "#FFFFFF")
        FG = PALETTE.get("FG", "#202124")
        SELECT_BG = PALETTE.get("SELECT_BG", "#C7CBCD")
        BTN_BG = PALETTE.get("BTN_BG", "#D5D8DA")
        BTN_FG = PALETTE.get("BTN_FG", "#202124")
    except Exception:
        ENTRY_BG, FG, SELECT_BG, BTN_BG, BTN_FG = "#fff", "#000", "#cfd0d0", "#ddd", "#000"

    try:
        # Entries
        if isinstance(w, tk.Entry):
            w.configure(bg=ENTRY_BG, fg=FG, insertbackground=FG, highlightthickness=1, relief="solid")
        # Text widgets
        elif isinstance(w, tk.Text):
            w.configure(bg=ENTRY_BG, fg=FG, insertbackground=FG, relief="solid")
        # Listbox
        elif isinstance(w, tk.Listbox):
            w.configure(bg=ENTRY_BG, fg=FG, selectbackground=SELECT_BG, selectforeground=FG, relief="solid")
        # Buttons (tk.Button)
        elif isinstance(w, tk.Button):
            w.configure(bg=BTN_BG, fg=BTN_FG, activebackground=BTN_BG, activeforeground=BTN_FG, relief="raised")
        # ttk widgets are handled by ttk.Style in apply_theme
    except Exception:
        # Ignore styling errors
        pass

def apply_tree_row_striping(tree, even_bg="#FFFFFF", odd_bg="#F3F3F3"):
    """
    Add alternating row colors to a Treeview for readability.
    Call this after inserting rows into the tree.
    """
    try:
        tree.tag_configure("evenrow", background=even_bg)
        tree.tag_configure("oddrow", background=odd_bg)
        for i, iid in enumerate(tree.get_children()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree.item(iid, tags=(tag,))
    except Exception:
        pass

def choose_template_dialog(root, template_manager):
    """
    Modal dialog for choosing a template.
    Arguments:
        - root: the application root (Toplevel parent)
        - template_manager: an instance with list() and get(tid)
    Returns:
        (subject, body) or None
    """
    try:
        templates = template_manager.list()
    except Exception as e:
        messagebox.showerror("Templates Error", f"Could not load templates: {e}")
        return None

    if not templates:
        messagebox.showwarning("No templates", "Create a template first in the Templates tab.")
        return None

    dlg = tk.Toplevel(root)
    dlg.title("Choose Template")
    dlg.geometry("520x380")
    dlg.transient(root)
    dlg.grab_set()

    tk.Label(dlg, text="Select a template:").pack(anchor="w", padx=10, pady=8)
    box = tk.Listbox(dlg, height=14)
    box.pack(fill="both", expand=True, padx=10, pady=5)

    modal_ids = []
    for t in templates:
        modal_ids.append(t[0])
        name = t[1] if t[1] else "(no name)"
        box.insert(tk.END, name)

    result = {"tpl": None}

    def use_selected():
        sel = box.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Choose a template.")
            return
        idx = sel[0]
        tid = modal_ids[idx]
        try:
            rec = template_manager.get(tid)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load template: {e}")
            return
        result["tpl"] = rec
        dlg.destroy()

    btn_row = tk.Frame(dlg)
    btn_row.pack(fill="x", padx=10, pady=8)
    tk.Button(btn_row, text="Use Template", bg=PALETTE.get("BTN_BG", "#D5D8DA"),
              fg=PALETTE.get("BTN_FG", "#202124"), command=use_selected).pack(side="left")
    tk.Button(btn_row, text="Cancel", bg=PALETTE.get("BTN_BG", "#D5D8DA"),
              fg=PALETTE.get("BTN_FG", "#202124"), command=dlg.destroy).pack(side="right")

    dlg.wait_window()
    if result["tpl"]:
        _, _, subject, body = result["tpl"]
        return subject or "", body or ""
    return None
