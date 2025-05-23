import sqlite3

db_path = "/Users/stavgreidi/Documents/pro/db.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# מחיקה אם קיים
cursor.execute("DROP TABLE IF EXISTS ProductVariation")
cursor.execute("DROP TABLE IF EXISTS Product")

# יצירת טבלת מוצרים
cursor.execute("""
CREATE TABLE Product (
    ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL
)
""")

# יצירת טבלת וריאציות
cursor.execute("""
CREATE TABLE ProductVariation (
    VariationID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductID INTEGER NOT NULL,
    Color TEXT,
    Size TEXT,
    StockLevel INTEGER,
    ReorderLevel INTEGER,
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
)
""")

# הכנסת מוצרים לדוגמה
cursor.execute("INSERT INTO Product (Name) VALUES ('T-Shirt')")
cursor.execute("INSERT INTO Product (Name) VALUES ('Evening Dress')")
cursor.execute("INSERT INTO Product (Name) VALUES ('Flared Tights')")

# הכנסת וריאציות לדוגמה
variations = [
    (1, 'White', 'S', 4, 2),
    (1, 'Black', 'M', 2, 2),
    (2, 'Burgundy', 'M', 5, 2),
    (2, 'Green', 'L', 2, 2),
    (3, 'Red', 'M', 1, 2),
    (3, 'Black', 'L', 4, 2)
]

cursor.executemany("""
INSERT INTO ProductVariation (ProductID, Color, Size, StockLevel, ReorderLevel)
VALUES (?, ?, ?, ?, ?)
""", variations)

conn.commit()
conn.close()

print("✓ Database created successfully.")
