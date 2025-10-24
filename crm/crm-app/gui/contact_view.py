# gui/contact_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from db import get_all_contacts, get_contact_by_id, insert_contact, update_contact, delete_contact, now_str
from gui.common import style_tk_widget, choose_template_dialog
from utils import open_email_mac_mail, confirm_delete

class ContactView(tk.Frame):
    def __init__(self, parent, conn, cursor, template_manager, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.conn = conn
        self.cursor = cursor
        self.tm = template_manager
        self.selected_contact_id = tk.StringVar()

        self._build_ui()
        self.refresh_templates()
        self.load_contacts()

    def _build_ui(self):
        # Form
        form = tk.LabelFrame(self, text="Add / Edit Contact", padx=10, pady=10)
        form.pack(fill="x", padx=10, pady=8)

        tk.Label(form, text="Name:").grid(row=0, column=0, sticky="e")
        self.name_entry = tk.Entry(form, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=3)
        style_tk_widget(self.name_entry)

        tk.Label(form, text="Email:").grid(row=0, column=2, sticky="e")
        self.email_entry = tk.Entry(form, width=30)
        self.email_entry.grid(row=0, column=3, padx=5, pady=3)
        style_tk_widget(self.email_entry)

        tk.Label(form, text="Phone:").grid(row=1, column=0, sticky="e")
        self.phone_entry = tk.Entry(form, width=30)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=3)
        style_tk_widget(self.phone_entry)

        tk.Label(form, text="Website:").grid(row=1, column=2, sticky="e")
        self.website_entry = tk.Entry(form, width=30)
        self.website_entry.grid(row=1, column=3, padx=5, pady=3)
        style_tk_widget(self.website_entry)

        tk.Label(form, text="Status:").grid(row=2, column=0, sticky="e")
        self.status_combo = ttk.Combobox(form, values=["Called","Emailed","Called and Emailed","Not Contacted"], width=27, state="readonly")
        self.status_combo.grid(row=2, column=1, padx=5, pady=3)
        self.status_combo.set("Not Contacted")
        self.status_combo.bind("<<ComboboxSelected>>", self._update_date_visibility)

        tk.Label(form, text="Notes:").grid(row=3, column=0, sticky="ne")
        self.notes_text = tk.Text(form, height=4, width=70)
        self.notes_text.grid(row=3, column=1, columnspan=3, padx=5, pady=3)
        style_tk_widget(self.notes_text)

        # date fields
        self.date_called_label = tk.Label(form, text="Date Called:")
        self.date_called_entry = DateEntry(form, width=18, state="readonly")
        style_tk_widget(self.date_called_entry)

        self.date_emailed_label = tk.Label(form, text="Date Emailed:")
        self.date_emailed_entry = DateEntry(form, width=18, state="readonly")
        style_tk_widget(self.date_emailed_entry)

        # Buttons
        btns = tk.Frame(self, pady=6)
        btns.pack(fill="x")
        self.save_btn = tk.Button(btns, text="Save / Update", command=self.save_contact)
        self.clear_btn = tk.Button(btns, text="Clear", command=self.clear_form)
        self.delete_btn = tk.Button(btns, text="Delete", command=self.delete_selected)
        for b in (self.save_btn, self.clear_btn, self.delete_btn):
            b.pack(side="left", padx=8, pady=4)
            style_tk_widget(b)

        # Table
        columns = ("ID","Name","Email","Phone","Website","Status","Date Added","Date Called","Date Emailed","Action")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=14)
        widths = {"ID": 60, "Name":180, "Email":220, "Phone":120, "Website":160, "Status":140, "Date Added":140, "Date Called":120, "Date Emailed":120, "Action":100}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths.get(col,120), anchor="center" if col in ("ID","Status","Action") else "w")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)

    # ---- methods ----
    def _update_date_visibility(self, event=None):
        choice = self.status_combo.get()
        if choice in ("Called", "Called and Emailed"):
            self.date_called_label.grid(row=4, column=0, sticky="e")
            self.date_called_entry.grid(row=4, column=1, padx=5, pady=3)
        else:
            self.date_called_label.grid_forget(); self.date_called_entry.grid_forget()
        if choice in ("Emailed", "Called and Emailed"):
            self.date_emailed_label.grid(row=4, column=2, sticky="e")
            self.date_emailed_entry.grid(row=4, column=3, padx=5, pady=3)
        else:
            self.date_emailed_label.grid_forget(); self.date_emailed_entry.grid_forget()

    def load_contacts(self):
        self.tree.delete(*self.tree.get_children())
        rows = get_all_contacts(self.cursor)
        for r in rows:
            self.tree.insert("", "end", values=r)

    def refresh_templates(self):
        # placeholder: template changes don't require automatic tree refresh,
        # but keep method to satisfy external callers
        pass

    def clear_form(self):
        self.selected_contact_id.set("")
        for w in (self.name_entry, self.email_entry, self.phone_entry, self.website_entry):
            w.delete(0, tk.END)
        self.status_combo.set("Not Contacted")
        self.notes_text.delete("1.0", tk.END)
        self.date_called_label.grid_forget(); self.date_called_entry.grid_forget()
        self.date_emailed_label.grid_forget(); self.date_emailed_entry.grid_forget()
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def save_contact(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        website = self.website_entry.get().strip()
        status = self.status_combo.get()
        notes = self.notes_text.get("1.0", tk.END).strip()
        if not name and not email:
            messagebox.showwarning("Missing", "Provide at least a name or email.")
            return
        date_called = self.date_called_entry.get_date().strftime("%Y-%m-%d") if self.date_called_label.winfo_ismapped() else None
        date_emailed = self.date_emailed_entry.get_date().strftime("%Y-%m-%d") if self.date_emailed_label.winfo_ismapped() else None
        if self.selected_contact_id.get():
            update_contact(self.cursor, self.conn, (name,email,phone,website,status,notes,date_called,date_emailed,self.selected_contact_id.get()))
            messagebox.showinfo("Updated","Contact updated.")
        else:
            date_added = now_str()
            insert_contact(self.cursor, self.conn, (name,email,phone,website,status,notes,date_added,date_called,date_emailed))
            messagebox.showinfo("Added","Contact added.")
        self.load_contacts()
        self.clear_form()

    def delete_selected(self):
        cid = self.selected_contact_id.get()
        if not cid:
            messagebox.showwarning("No selection","Select a contact.")
            return
        if confirm_delete():
            delete_contact(self.cursor, self.conn, cid)
            self.load_contacts()
            self.clear_form()

    def on_tree_click(self, event):
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not item:
            return
        values = self.tree.item(item, "values")
        if not values:
            return
        cid = values[0]
        if col == "#10":
            self.open_action(cid)
            return
        # toggle selection/deselect
        current_sel = self.tree.selection()
        if current_sel and current_sel[0] == item:
            self.tree.selection_remove(item)
            self.clear_form()
            return
        self.tree.selection_set(item)
        self.selected_contact_id.set(cid)
        rec = get_contact_by_id(self.cursor, cid)
        if rec:
            self.name_entry.delete(0, tk.END); self.name_entry.insert(0, rec[0] or "")
            self.email_entry.delete(0, tk.END); self.email_entry.insert(0, rec[1] or "")
            self.phone_entry.delete(0, tk.END); self.phone_entry.insert(0, rec[2] or "")
            self.website_entry.delete(0, tk.END); self.website_entry.insert(0, rec[3] or "")
            self.status_combo.set(rec[4] or "Not Contacted")
            self.notes_text.delete("1.0", tk.END); self.notes_text.insert("1.0", rec[5] or "")
            self._update_date_visibility()
            if rec[7]:
                try: self.date_called_entry.set_date(rec[7])
                except Exception: pass
            if rec[8]:
                try: self.date_emailed_entry.set_date(rec[8])
                except Exception: pass

    def open_action(self, cid):
        rec = get_contact_by_id(self.cursor, cid)
        if not rec:
            messagebox.showwarning("Not found", "Contact not found.")
            return
        name, email = rec[0], rec[1]
        if not email:
            messagebox.showwarning("Missing email", "No email for this contact.")
            return
        tpl = choose_template_dialog(self.winfo_toplevel(), self.tm)
        if not tpl:
            return
        subject, body = tpl
        subject = (subject or "").replace("{{name}}", name or "")
        body = (body or "").replace("{{name}}", name or "")
        open_email_mac_mail(email, subject, body)
