# gui/app.py
import tkinter as tk
from tkinter import ttk
from db import connect_db
from templates import TemplateManager
from gui.common import apply_theme
from gui.contact_view import ContactView
from gui.template_view import TemplateView

class CRMApp:
    def __init__(self):
        self.conn, self.cursor = connect_db()
        self.tm = TemplateManager(self.conn, self.cursor)

        self.root = tk.Tk()
        self.root.title("Ali's Mini CRM")
        screen_width = self.root.winfo_screenwidth()
        width = min(1300, screen_width - 80)
        height = 820
        self.root.geometry(f"{width}x{height}")

        # apply theme / styling
        apply_theme(self.root)

    def run(self):
        notebook = ttk.Notebook(self.root)
        contacts_tab = ttk.Frame(notebook)
        templates_tab = ttk.Frame(notebook)
        notebook.add(contacts_tab, text="Contacts")
        notebook.add(templates_tab, text="Templates")
        notebook.pack(fill="both", expand=True)

        # create views
        self.contact_view = ContactView(contacts_tab, self.conn, self.cursor, self.tm)
        self.contact_view.pack(fill="both", expand=True)

        self.template_view = TemplateView(templates_tab, self.tm, on_templates_changed=self.contact_view.refresh_templates)
        self.template_view.pack(fill="both", expand=True)

        # start
        self.root.mainloop()
