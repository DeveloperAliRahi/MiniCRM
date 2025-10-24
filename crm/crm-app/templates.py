# templates.py
# TemplateManager to keep template logic separate from GUI

class TemplateManager:
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        self._ensure_table()

    def _ensure_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                subject TEXT,
                body TEXT
            )
        """)
        self.conn.commit()

    def list(self):
        self.cursor.execute("SELECT id, name, subject, body FROM templates ORDER BY name ASC")
        return self.cursor.fetchall()

    def get(self, tid):
        self.cursor.execute("SELECT id, name, subject, body FROM templates WHERE id=?", (tid,))
        return self.cursor.fetchone()

    def create(self, name, subject, body):
        self.cursor.execute("INSERT INTO templates (name, subject, body) VALUES (?, ?, ?)", (name, subject, body))
        self.conn.commit()
        return self.cursor.lastrowid

    def update(self, tid, name, subject, body):
        self.cursor.execute("UPDATE templates SET name=?, subject=?, body=? WHERE id=?", (name, subject, body, tid))
        self.conn.commit()

    def delete(self, tid):
        self.cursor.execute("DELETE FROM templates WHERE id=?", (tid,))
        self.conn.commit()
