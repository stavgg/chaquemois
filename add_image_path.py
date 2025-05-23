import sqlite3

conn = sqlite3.connect("chaquemois_variations.db")
cursor = conn.cursor()

# הוספת עמודה image_path אם לא קיימת
try:
    cursor.execute("ALTER TABLE ProductVariation ADD COLUMN image_path TEXT;")
    print("✓ העמודה image_path נוספה לטבלה ProductVariation.")
except sqlite3.OperationalError:
    print("⚠️ העמודה image_path כבר קיימת.")

conn.commit()
conn.close()
