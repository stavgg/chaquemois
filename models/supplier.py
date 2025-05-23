import sqlite3

class Supplier:
    def __init__(self, id, name, contact_email):
        self.id = id
        self.name = name
        self.contact_email = contact_email

    @staticmethod
    def get_all():
        conn = sqlite3.connect("chaquemois_variations.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, contact_email FROM Supplier")
        rows = cursor.fetchall()
        conn.close()
        return [Supplier(*row) for row in rows]
