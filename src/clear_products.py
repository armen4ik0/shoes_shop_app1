from database import Database

db = Database()
db.execute_update("DELETE FROM products;")
print("✓ Таблица products очищена")
db.close()
