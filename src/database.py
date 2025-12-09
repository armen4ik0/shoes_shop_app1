import psycopg2
from config import Config

class Database:
    """Класс для работы с PostgreSQL"""
    
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        """Подключение к БД"""
        try:
            config = Config.DATABASE_CONFIG.copy()
            config['client_encoding'] = 'UTF8'
            self.conn = psycopg2.connect(**config)
            print("✓ Подключение к БД успешно")
            self.create_tables()
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            raise
    
    def create_tables(self):
        """Создать таблицы если их нет"""
        try:
            with self.conn.cursor() as cur:
                # Таблица пользователей
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        role VARCHAR(50),
                        full_name VARCHAR(255),
                        login VARCHAR(100) UNIQUE,
                        password VARCHAR(255)
                    );
                """)
                
                # Таблица пунктов выдачи
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS pickup_points (
                        id SERIAL PRIMARY KEY,
                        address VARCHAR(255) UNIQUE
                    );
                """)
                
                # Таблица товаров
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id SERIAL PRIMARY KEY,
                        article VARCHAR(100) UNIQUE,
                        name VARCHAR(255),
                        category VARCHAR(100),
                        description TEXT,
                        manufacturer VARCHAR(100),
                        supplier VARCHAR(100),
                        price DECIMAL(10,2),
                        unit VARCHAR(50),
                        stock INTEGER,
                        discount INTEGER,
                        photo_path VARCHAR(255)
                    );
                """)
                
                # Таблица заказов
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        id SERIAL PRIMARY KEY,
                        order_number INTEGER UNIQUE,
                        order_articles VARCHAR(255),
                        order_date VARCHAR(50),
                        delivery_date VARCHAR(50),
                        pickup_point_id INTEGER REFERENCES pickup_points(id),
                        client_name VARCHAR(255),
                        pickup_code VARCHAR(100),
                        status VARCHAR(50)
                    );
                """)
                
                self.conn.commit()
                print("✓ Таблицы созданы")
        except Exception as e:
            print(f"⚠ Таблицы уже существуют: {e}")
            self.conn.rollback()
    
    def execute_query(self, query, params=None):
        """Выполнить SELECT запрос"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """Выполнить INSERT/UPDATE/DELETE запрос"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Ошибка обновления: {e}")
            return False
    
    def close(self):
        """Закрыть подключение"""
        if self.conn:
            self.conn.close()