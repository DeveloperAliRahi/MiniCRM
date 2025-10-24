# gui/template_view.py
import tkinter as tk
from tkinter import messagebox
from gui.common import style_tk_widget

class TemplateView(tk.Frame):
    def __init__(self, parent, template_manager, on_templates_changed=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.tm = template_manager
        self.on_templates_changed = on_templates_changed
        self.current_tpl_id = tk.StringVar(value="")
        self._build_ui()
        self.refresh_tpl_list()

    def _build_ui(self):
        left = tk.Frame(self, padx=10, pady=10)
        left.pack(side="left", fill="y")
        right = tk.Frame(self, padx=10, pady=10)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="Templates").pack(anchor="w")
        self.tpl_list = tk.Listbox(left, height=20, width=36)
        self.tpl_list.pack(fill="y", pady=5)
        self.tpl_list.bind("<<ListboxSelect>>", self._on_select)
        style_tk_widget(self.tpl_list)

        tk.Button(left, text="New", command=self.new_tpl).pack(fill="x", pady=3)
        tk.Button(left, text="Save", command=self.save_tpl).pack(fill="x", pady=3)
        tk.Button(left, text="Delete", command=self.delete_tpl).pack(fill="x", pady=3)

        tk.Label(right, text="Name:").grid(row=0, column=0, sticky="e")
        self.tpl_name = tk.Entry(right, width=60)
        self.tpl_name.grid(row=0, column=1, padx=5, pady=3)
        style_tk_widget(self.tpl_name)

        tk.Label(right, text="Subject:").grid(row=1, column=0, sticky="e")
        self.tpl_subject = tk.Entry(right, width=60)
        self.tpl_subject.grid(row=1, column=1, padx=5, pady=3)
        style_tk_widget(self.tpl_subject)

        tk.Label(right, text="Body:").grid(row=2, column=0, sticky="ne")
        self.tpl_body = tk.Text(right, width=80, height=18)
        self.tpl_body.grid(row=2, column=1, padx=5, pady=3)
        style_tk_widget(self.tpl_body)

    def refresh_tpl_list(self):
        self.tpl_list.delete(0, tk.END)
        self._ids = []
        for row in self.tm.list():
            tid, name, subject, body = row
            self._ids.append(tid)
            self.tpl_list.insert(tk.END, name)

    def _on_select(self, event=None):
        sel = self.tpl_list.curselection()
        if not sel:
            self._clear_fields()
            return
        idx = sel[0]
        tid = self._ids[idx]
        rec = self.tm.get(tid)
        if rec:
            _id, name, subject, body = rec
            self.current_tpl_id.set(str(_id))
            self.tpl_name.delete(0, tk.END); self.tpl_name.insert(0, name or "")
            self.tpl_subject.delete(0, tk.END); self.tpl_subject.insert(0, subject or "")
            self.tpl_body.delete("1.0", tk.END); self.tpl_body.insert("1.0", body or "")

    def new_tpl(self):
        self.current_tpl_id.set("")
        self.tpl_list.selection_clear(0, tk.END)
        self._clear_fields()

    def _clear_fields(self):
        self.tpl_name.delete(0, tk.END)
        self.tpl_subject.delete(0, tk.END)
        self.tpl_body.delete("1.0", tk.END)

    def save_tpl(self):
        name = self.tpl_name.get().strip()
        subject = self.tpl_subject.get().strip()
        body = self.tpl_body.get("1.0", tk.END).strip()
        if not name:
            messagebox.showwarning("Missing name", "Please provide a template name.")
            return
        tid = self.current_tpl_id.get()
        if tid:
            self.tm.update(int(tid), name, subject, body)
            messagebox.showinfo("Saved", "Template updated.")
        else:
            new_id = self.tm.create(name, subject, body)
            self.current_tpl_id.set(str(new_id))
            messagebox.showinfo("Saved", "Template created.")
        self.refresh_tpl_list()
        # select created/updated
        for i, t in enumerate(self._ids):
            if str(t) == self.current_tpl_id.get():
                self.tpl_list.selection_clear(0, tk.END)
                self.tpl_list.selection_set(i)
                self.tpl_list.see(i)
                break
        if self.on_templates_changed:
            self.on_templates_changed()

    def delete_tpl(self):
        tid = self.current_tpl_id.get()
        if not tid:
            messagebox.showwarning("No template", "Select a template to delete.")
            return
        if messagebox.askyesno("Delete?", "Delete this template?"):
            self.tm.delete(int(tid))
            self.new_tpl()
            self.refresh_tpl_list()
            if self.on_templates_changed:
                self.on_templates_changed()
