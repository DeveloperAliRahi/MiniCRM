import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from db import *
from utils import open_email_mac_mail, confirm_delete

STATUSES = ["Called", "Emailed", "Called and Emailed", "Not Contacted"]

def start_gui():
    conn, cursor = connect_db()
    root = tk.Tk()
    root.title("Ali's Mini CRM")
    root.configure(bg="#f5f5f5")
    screen_width = root.winfo_screenwidth()
    root.geometry(f"{min(1300, screen_width-50)}x800")

    notebook = ttk.Notebook(root)
    contacts_tab = ttk.Frame(notebook)
    templates_tab = ttk.Frame(notebook)
    notebook.add(contacts_tab, text="Contacts")
    notebook.add(templates_tab, text="Templates")
    notebook.pack(fill="both", expand=True)

    # -------------- CONTACTS --------------
    selected_contact_id = tk.StringVar()

    form = tk.LabelFrame(contacts_tab, text="Add / Edit Contact", bg="#f5f5f5", padx=10, pady=10)
    form.pack(fill="x", padx=10, pady=10)

    tk.Label(form, text="Name:").grid(row=0, column=0, sticky="e")
    name_entry = tk.Entry(form, width=30)
    name_entry.grid(row=0, column=1)

    tk.Label(form, text="Email:").grid(row=0, column=2, sticky="e")
    email_entry = tk.Entry(form, width=30)
    email_entry.grid(row=0, column=3)

    tk.Label(form, text="Phone:").grid(row=1, column=0, sticky="e")
    phone_entry = tk.Entry(form, width=30)
    phone_entry.grid(row=1, column=1)

    tk.Label(form, text="Website:").grid(row=1, column=2, sticky="e")
    website_entry = tk.Entry(form, width=30)
    website_entry.grid(row=1, column=3)

    tk.Label(form, text="Status:").grid(row=2, column=0, sticky="e")
    status_combo = ttk.Combobox(form, values=STATUSES, width=27, state="readonly")
    status_combo.grid(row=2, column=1)
    status_combo.set("Not Contacted")

    tk.Label(form, text="Notes:").grid(row=3, column=0, sticky="ne")
    notes_text = tk.Text(form, height=4, width=70)
    notes_text.grid(row=3, column=1, columnspan=3, padx=5, pady=5)

    # Date pickers (hidden by default)
    date_called_label = tk.Label(form, text="Date Called:")
    date_called_entry = DateEntry(form, width=20, state="readonly")

    date_emailed_label = tk.Label(form, text="Date Emailed:")
    date_emailed_entry = DateEntry(form, width=20, state="readonly")

    def update_date_visibility(event=None):
        choice = status_combo.get()
        if choice in ("Called", "Called and Emailed"):
            date_called_label.grid(row=4, column=0, sticky="e")
            date_called_entry.grid(row=4, column=1, padx=5)
        else:
            date_called_label.grid_forget()
            date_called_entry.grid_forget()
        if choice in ("Emailed", "Called and Emailed"):
            date_emailed_label.grid(row=4, column=2, sticky="e")
            date_emailed_entry.grid(row=4, column=3, padx=5)
        else:
            date_emailed_label.grid_forget()
            date_emailed_entry.grid_forget()
    status_combo.bind("<<ComboboxSelected>>", update_date_visibility)

    # Buttons
    btns = tk.Frame(contacts_tab, bg="#f5f5f5")
    btns.pack(fill="x", pady=10)
    tk.Button(btns, text="Save / Update", bg="#e0e0e0", fg="black", command=lambda: save_contact()).pack(side="left", padx=10)
    tk.Button(btns, text="Clear", bg="#e0e0e0", fg="black", command=lambda: clear_form()).pack(side="left", padx=10)
    tk.Button(btns, text="Delete", bg="#e0e0e0", fg="black", command=lambda: delete_selected()).pack(side="left", padx=10)

    # Table
    cols = ("ID","Name","Email","Phone","Website","Status","Date Added","Date Called","Date Emailed","Action")
    tree = ttk.Treeview(contacts_tab, columns=cols, show="headings")
    for c in cols: tree.heading(c, text=c)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Set column widths dynamically
    total_width = min(1300, screen_width-50)
    per_col = int(total_width / len(cols))
    for c in cols: tree.column(c, width=per_col, anchor="center")

    def load_contacts():
        tree.delete(*tree.get_children())
        for row in get_all_contacts(cursor):
            tree.insert("", "end", values=row)

    def clear_form():
        selected_contact_id.set("")
        for w in [name_entry, email_entry, phone_entry, website_entry]:
            w.delete(0, tk.END)
        status_combo.set("Not Contacted")
        notes_text.delete("1.0", tk.END)
        date_called_label.grid_forget()
        date_called_entry.grid_forget()
        date_emailed_label.grid_forget()
        date_emailed_entry.grid_forget()

    def save_contact():
        name, email, phone, website = name_entry.get().strip(), email_entry.get().strip(), phone_entry.get().strip(), website_entry.get().strip()
        status = status_combo.get()
        notes = notes_text.get("1.0", tk.END).strip()
        date_added = now_str()
        date_called = date_called_entry.get_date().strftime("%Y-%m-%d") if date_called_label.winfo_ismapped() else None
        date_emailed = date_emailed_entry.get_date().strftime("%Y-%m-%d") if date_emailed_label.winfo_ismapped() else None

        if selected_contact_id.get():
            update_contact(cursor, conn, (name,email,phone,website,status,notes,date_called,date_emailed,selected_contact_id.get()))
        else:
            insert_contact(cursor, conn, (name,email,phone,website,status,notes,date_added,date_called,date_emailed))
        load_contacts()
        clear_form()

    def delete_selected():
        if not selected_contact_id.get():
            messagebox.showwarning("No selection","Select a contact first.")
            return
        if confirm_delete():
            delete_contact(cursor, conn, selected_contact_id.get())
            load_contacts()
            clear_form()

    def on_tree_click(event):
        item = tree.identify_row(event.y)
        col = tree.identify_column(event.x)
        if not item: return
        values = tree.item(item,"values")
        selected_contact_id.set(values[0])
        if col == "#10":
            open_action(values[0])
        else:
            rec = get_contact_by_id(cursor, values[0])
            if rec:
                name_entry.delete(0,tk.END); name_entry.insert(0,rec[0])
                email_entry.delete(0,tk.END); email_entry.insert(0,rec[1])
                phone_entry.delete(0,tk.END); phone_entry.insert(0,rec[2])
                website_entry.delete(0,tk.END); website_entry.insert(0,rec[3])
                status_combo.set(rec[4]); notes_text.delete("1.0",tk.END); notes_text.insert("1.0",rec[5])
                update_date_visibility()

    def open_action(cid):
        rec = get_contact_by_id(cursor, cid)
        if not rec or not rec[1]:
            messagebox.showwarning("Missing email", "No email for this contact.")
            return
        templates = list_templates(cursor)
        tpl = templates[0]
        subject = tpl[2].replace("{{name}}", rec[0] or "")
        body = tpl[3].replace("{{name}}", rec[0] or "")
        open_email_mac_mail(rec[1], subject, body)

    tree.bind("<ButtonRelease-1>", on_tree_click)

    # TEMPLATES TAB
    tpl_list = tk.Listbox(templates_tab, width=40)
    tpl_list.pack(side="left", fill="y", padx=10, pady=10)
    tpl_text = tk.Text(templates_tab)
    tpl_text.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_tpl():
        tpl_list.delete(0, tk.END)
        for t in list_templates(cursor):
            tpl_list.insert(tk.END, f"{t[0]} — {t[1]}")

    refresh_tpl()
    load_contacts()
    root.mainloop()
