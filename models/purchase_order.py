import sqlite3

class PurchaseOrder:
    def __init__(self, id, supplier_id, product_variation_id, quantity, status, created_at):
        self.id = id
        self.supplier_id = supplier_id
        self.product_variation_id = product_variation_id
        self.quantity = quantity
        self.status = status
        self.created_at = created_at

    @staticmethod
    def create(supplier_id, product_variation_id, quantity):
        conn = sqlite3.connect("chaquemois_variations.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO PurchaseOrder (supplier_id, product_variation_id, quantity)
            VALUES (?, ?, ?)
        """, (supplier_id, product_variation_id, quantity))
        conn.commit()
        conn.close()
