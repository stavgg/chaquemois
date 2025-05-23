import sqlite3
import random

# התחברות למסד הנתונים
conn = sqlite3.connect("db.db")
cursor = conn.cursor()

# עדכון רמות מלאי ורמות הזמנה מחדש בסגנון חנות בוטיק
cursor.execute("SELECT VariationID FROM ProductVariation")
variations = cursor.fetchall()

for (variation_id,) in variations:
    # רמת הזמנה בין 2 ל־6
    reorder_level = random.randint(2, 6)

    # תרחישי מלאי – מותאם לבוטיק (נמוך, גבול, גבוה - עד 15)
    stock_scenario = random.choices(
        ['low', 'borderline', 'high'],
        weights=[0.4, 0.2, 0.4],  # יותר חוסרים
        k=1
    )[0]

    if stock_scenario == 'low':
        stock = random.randint(0, reorder_level - 1)
    elif stock_scenario == 'borderline':
        stock = reorder_level
    else:  # high
        stock = random.randint(reorder_level + 1, min(reorder_level + 10, 15))

    cursor.execute("""
        UPDATE ProductVariation
        SET StockLevel = ?, ReorderLevel = ?
        WHERE VariationID = ?
    """, (stock, reorder_level, variation_id))

# שמירה וסגירה
conn.commit()
cursor.execute("SELECT COUNT(*) FROM ProductVariation WHERE StockLevel < ReorderLevel")
reorder_needed = cursor.fetchone()[0]
conn.close()

print(f"✓ Boutique-style inventory updated. {reorder_needed} variations need reordering.")