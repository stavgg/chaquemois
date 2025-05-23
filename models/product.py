import sqlite3

class Product:
    def __init__(self, id, name, category):
        self.id = id
        self.name = name
        self.category = category

    @staticmethod
    def get_all():
        conn = sqlite3.connect("chaquemois_variations.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category FROM Product")
        rows = cursor.fetchall()
        conn.close()
        return [Product(*row) for row in rows]

