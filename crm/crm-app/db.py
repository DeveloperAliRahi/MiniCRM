import sqlite3, os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "contacts.db")

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    _ensure_schema(conn, cursor)
    return conn, cursor

def _ensure_schema(conn, cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        website TEXT,
        status TEXT,
        notes TEXT,
        date_added TEXT,
        date_called TEXT,
        date_emailed TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        subject TEXT,
        body TEXT
    )
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM templates")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO templates (name, subject, body) VALUES (?, ?, ?)",
            ("Follow-up", "Following up with {{name}}",
             "Hi {{name}},\n\nJust following up on our previous conversation.\n\nBest,\nAli")
        )
        conn.commit()

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_all_contacts(cursor):
    cursor.execute("""
        SELECT id, name, email, phone, website, status,
               date_added, date_called, date_emailed, 'Email' AS action
        FROM contacts ORDER BY id DESC
    """)
    return cursor.fetchall()

def get_contact_by_id(cursor, cid):
    cursor.execute("""
        SELECT name, email, phone, website, status, notes,
               date_added, date_called, date_emailed
        FROM contacts WHERE id=?
    """, (cid,))
    return cursor.fetchone()

def insert_contact(cursor, conn, data):
    cursor.execute("""
        INSERT INTO contacts (name, email, phone, website, status, notes, date_added, date_called, date_emailed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()

def update_contact(cursor, conn, data):
    cursor.execute("""
        UPDATE contacts
        SET name=?, email=?, phone=?, website=?, status=?, notes=?,
            date_called=?, date_emailed=?
        WHERE id=?
    """, data)
    conn.commit()

def delete_contact(cursor, conn, cid):
    cursor.execute("DELETE FROM contacts WHERE id=?", (cid,))
    conn.commit()

# Templates
def list_templates(cursor):
    cursor.execute("SELECT id, name, subject, body FROM templates ORDER BY name ASC")
    return cursor.fetchall()

def get_template_by_id(cursor, tid):
    cursor.execute("SELECT id, name, subject, body FROM templates WHERE id=?", (tid,))
    return cursor.fetchone()

def upsert_template(cursor, conn, tid, name, subject, body):
    if tid:
        cursor.execute("UPDATE templates SET name=?, subject=?, body=? WHERE id=?", (name, subject, body, tid))
    else:
        cursor.execute("INSERT INTO templates (name, subject, body) VALUES (?, ?, ?)", (name, subject, body))
    conn.commit()

def delete_template(cursor, conn, tid):
    cursor.execute("DELETE FROM templates WHERE id=?", (tid,))
    conn.commit()
