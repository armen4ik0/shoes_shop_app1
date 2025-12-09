import sqlite3
import sys
import os
from src.config import DATABASE_FILE

class DBConnector:
    """
    Класс для управления подключением к базе данных SQLite.
    """
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        """Устанавливает соединение с базой данных."""
        try:
            # Проверка, существует ли файл базы данных
            if not os.path.exists(DATABASE_FILE):
                print(f"Ошибка: Файл базы данных '{DATABASE_FILE}' не найден. Сначала запустите import_data.py.")
                return False
                
            self.conn = sqlite3.connect(DATABASE_FILE)
            self.conn.execute("PRAGMA foreign_keys = ON;")
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False

    def close(self):
        """Закрывает соединение с базой данных."""
        if self.conn:
            self.conn.close()

    def fetch_products(self):
        """Получает основные данные о товарах с присоединением справочников."""
        if not self.conn:
            return []
        try:
            self.cursor.execute("""
                SELECT 
                    p.product_article, 
                    p.product_name, 
                    p.product_cost,
                    p.product_discount,
                    p.product_quantity,
                    c.category_name,
                    m.manufacturer_name
                FROM products p
                LEFT JOIN categories c ON p.product_category_id = c.category_id
                LEFT JOIN manufacturers m ON p.product_manufacturer_id = m.manufacturer_id
                ORDER BY p.product_article
            """)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении товаров: {e}")
            return []

    def get_column_names(self):
        """Возвращает названия столбцов для таблицы товаров."""
        return [
            "Артикул", 
            "Наименование", 
            "Цена", 
            "Скидка (%)", 
            "В наличии", 
            "Категория", 
            "Производитель"
        ]

# Проверяем, что config доступен
try:
    from src.config import DATABASE_FILE
except ImportError:
    print("Ошибка: Файл src/config.py не найден или не содержит DATABASE_FILE.")
    sys.exit(1)