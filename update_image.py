import sqlite3

image_map = {
    1: "images/טי שירט שחורה.webp",
    2: "images/טי שירט לבנה.webp",
    3: "images/טייץ מתרחב אדום.webp",
    4: "images/טייץ מתרחב שחור.webp",
    5: "images/שמלת ערב בורדו.webp",
    6: "images/שמלת ערב ירוקה.webp",
    7: "images/שמלת ערב שחורה.webp",
}

conn = sqlite3.connect("chaquemois_variations.db")
cursor = conn.cursor()

for variation_id, path in image_map.items():
    cursor.execute("""
        UPDATE ProductVariation
        SET image_path = ?
        WHERE id = ?
    """, (path, variation_id))

conn.commit()
conn.close()
print("✓ נתיבי תמונות עודכנו במסד בהצלחה.")
