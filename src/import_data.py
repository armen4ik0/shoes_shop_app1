import pandas as pd
import os

from config import Config
from database import Database


class DataImporter:
    """Класс для импорта данных из Excel файлов"""

    def __init__(self):
        self.db = Database()
        self.data_dir = Config.DATA_DIR

    def import_all_data(self):
        """Импорт всех данных из Excel файлов"""
        print("=" * 50)
        print("Начинаем импорт данных...")
        print("=" * 50)

        self.import_users()
        self.import_pickup_points()
        self.import_products()
        self.import_orders()

        print("=" * 50)
        print("✓ Импорт данных успешно завершен!")
        print("=" * 50)

    def import_users(self):
        """Импорт пользователей"""
        try:
            file_path = os.path.join(self.data_dir, "user_import.xlsx")
            if not os.path.exists(file_path):
                print(f"⚠ Файл не найден: {file_path}")
                return

            df = pd.read_excel(file_path)
            print("\n📥 Импорт пользователей...")
            print(f" Найдено записей: {len(df)}")

            for _, row in df.iterrows():
                try:
                    query = """
                        INSERT INTO users (role, full_name, login, password)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (login) DO NOTHING;
                    """
                    self.db.execute_update(
                        query,
                        (
                            str(row["Роль сотрудника"]),
                            str(row["ФИО"]),
                            str(row["Логин"]),
                            str(row["Пароль"]),
                        ),
                    )
                except Exception as e:
                    print(f" ⚠ Ошибка при импорте пользователя: {e}")

            print(" ✓ Импортировано пользователей")
        except Exception as e:
            print(f"✗ Ошибка импорта пользователей: {e}")

    def import_pickup_points(self):
        """Импорт пунктов выдачи"""
        try:
            possible_names = [
                "Punkty-vydachi_import.xlsx",
                "Пункты выдачи_import.xlsx",
                "Пункты выдачи_import.xlsx",
            ]

            file_path = None
            for name in possible_names:
                path = os.path.join(self.data_dir, name)
                if os.path.exists(path):
                    file_path = path
                    break

            if not file_path:
                print(
                    f"⚠ Файл пунктов выдачи не найден (проверены: {possible_names})"
                )
                return

            df = pd.read_excel(file_path, header=None)
            df.columns = ["address"]

            print("\n📥 Импорт пунктов выдачи...")
            print(f" Найдено записей: {len(df)}")

            for _, row in df.iterrows():
                try:
                    query = """
                        INSERT INTO pickup_points (address)
                        VALUES (%s)
                        ON CONFLICT (address) DO NOTHING;
                    """
                    self.db.execute_update(query, (str(row["address"]),))
                except Exception as e:
                    print(f" ⚠ Ошибка при импорте пункта: {e}")

            print(" ✓ Импортировано пунктов выдачи")
        except Exception as e:
            print(f"✗ Ошибка импорта пунктов выдачи: {e}")

    def import_products(self):
        """Импорт товаров"""
        try:
            file_path = os.path.join(self.data_dir, "Tovar.xlsx")
            if not os.path.exists(file_path):
                print(f"⚠ Файл не найден: {file_path}")
                return

            df = pd.read_excel(file_path)
            print("\n📥 Импорт товаров...")
            print(f" Найдено записей: {len(df)}")

            if "Фото" not in df.columns:
                df["Фото"] = ""

            for index, row in df.iterrows():
                try:
                    article = str(row["Артикул"])
                    name = str(row["Наименование товара"])
                    unit = str(row["Единица измерения"])
                    price = float(row["Цена"])
                    supplier = str(row["Поставщик"])
                    manufacturer = str(row["Производитель"])
                    category = str(row["Категория товара"])
                    discount = int(row["Действующая скидка"])
                    stock = int(row["Кол-во на складе"])
                    description = (
                        str(row["Описание товара"])
                        if pd.notna(row["Описание товара"])
                        else ""
                    )
                    photo = (
                        str(row["Фото"]) if pd.notna(row["Фото"]) else ""
                    )

                    photo_path = ""
                    if photo.strip():
                        photo_path = os.path.join(
                            Config.DATA_DIR,
                            "product_images",
                            photo.strip(),
                        )

                    query = """
                        INSERT INTO products
                        (article, name, category, description, manufacturer, supplier,
                         price, unit, stock, discount, photo_path)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (article) DO NOTHING;
                    """
                    self.db.execute_update(
                        query,
                        (
                            article,
                            name,
                            category,
                            description,
                            manufacturer,
                            supplier,
                            price,
                            unit,
                            stock,
                            discount,
                            photo_path,
                        ),
                    )
                except Exception as e:
                    print(
                        f" ⚠ Ошибка при импорте товара строка {index + 2}: {e}"
                    )

            print(" ✓ Импортировано товаров")
        except Exception as e:
            print(f"✗ Ошибка импорта товаров: {e}")

    def import_orders(self):
        """Импорт заказов"""
        try:
            possible_names = [
                "Zakaz_import.xlsx",
                "Заказ_import.xlsx",
                "orders.xlsx",
            ]

            file_path = None
            for name in possible_names:
                path = os.path.join(self.data_dir, name)
                if os.path.exists(path):
                    file_path = path
                    break

            if not file_path:
                print(
                    f"⚠ Файл заказов не найден (проверены: {possible_names})"
                )
                return

            df = pd.read_excel(file_path)
            print("\n📥 Импорт заказов...")
            print(f" Найдено записей: {len(df)}")

            for _, row in df.iterrows():
                try:
                    pickup_point_id = None

                    if pd.notna(row["Адрес пункта выдачи"]):
                        addr = str(row["Адрес пункта выдачи"]).strip()
                        try:
                            # ищем по адресу без лишних пробелов
                            query_point = (
                                "SELECT id FROM pickup_points "
                                "WHERE TRIM(address) = %s"
                            )
                            result = self.db.execute_query(
                                query_point, (addr,)
                            )
                            if result:
                                pickup_point_id = result[0][0]
                            else:
                                print(
                                    f" ⚠ Пункт выдачи не найден по адресу: '{addr}'"
                                )
                        except Exception as e:
                            print(
                                f" ⚠ Ошибка поиска пункта выдачи '{addr}': {e}"
                            )

                    order_date = str(row["Дата заказа"])
                    delivery_date = str(row["Дата доставки"])

                    query = """
                        INSERT INTO orders
                        (order_number, order_articles, order_date, delivery_date,
                         pickup_point_id, client_name, pickup_code, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (order_number) DO NOTHING;
                    """
                    self.db.execute_update(
                        query,
                        (
                            int(row["Номер заказа"]),
                            str(row["Артикул заказа"]),
                            order_date,
                            delivery_date,
                            pickup_point_id,
                            str(row["ФИО авторизированного клиента"]),
                            str(row["Код для получения"]),
                            str(row["Статус заказа"]),
                        ),
                    )
                except Exception as e:
                    print(f" ⚠ Ошибка при импорте заказа: {e}")

            print(" ✓ Импортировано заказов")
        except Exception as e:
            print(f"✗ Ошибка импорта заказов: {e}")


if __name__ == "__main__":
    importer = DataImporter()
    importer.import_all_data()
