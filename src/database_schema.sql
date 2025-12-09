-- ===============================================
-- БД для "ООО Обувь"
-- Система управления товарами и заказами
-- ===============================================

-- Создание базы данных
CREATE DATABASE IF NOT EXISTS shoe_shop_db;

-- Подключитесь к базе данных
\c shoe_shop_db;

-- ===============================================
-- ТАБЛИЦА: users (Пользователи)
-- ===============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    login VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_login ON users(login);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ===============================================
-- ТАБЛИЦА: pickup_points (Пункты выдачи)
-- ===============================================
CREATE TABLE IF NOT EXISTS pickup_points (
    id SERIAL PRIMARY KEY,
    address VARCHAR(500) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pickup_points_address ON pickup_points(address);

-- ===============================================
-- ТАБЛИЦА: products (Товары)
-- ===============================================
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    article VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    manufacturer VARCHAR(100) NOT NULL,
    supplier VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    unit VARCHAR(20) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    discount INTEGER NOT NULL DEFAULT 0 CHECK (discount >= 0 AND discount <= 100),
    photo_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_article ON products(article);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_supplier ON products(supplier);
CREATE INDEX IF NOT EXISTS idx_products_manufacturer ON products(manufacturer);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);

-- ===============================================
-- ТАБЛИЦА: orders (Заказы)
-- ===============================================
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_number INTEGER UNIQUE NOT NULL,
    order_articles VARCHAR(500) NOT NULL,
    order_date DATE NOT NULL,
    delivery_date DATE NOT NULL,
    pickup_point_id INTEGER REFERENCES pickup_points(id) ON DELETE SET NULL,
    client_name VARCHAR(255) NOT NULL,
    pickup_code VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orders_order_number ON orders(order_number);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_pickup_point ON orders(pickup_point_id);
CREATE INDEX IF NOT EXISTS idx_orders_client_name ON orders(client_name);

-- ===============================================
-- ОГРАНИЧЕНИЯ ЦЕЛОСТНОСТИ
-- ===============================================

-- Констрейнт на дату доставки
ALTER TABLE orders
ADD CONSTRAINT check_delivery_date_after_order_date
CHECK (delivery_date >= order_date);

-- ===============================================
-- КОММЕНТАРИИ К ТАБЛИЦАМ
-- ===============================================

COMMENT ON TABLE users IS 'Таблица пользователей системы';
COMMENT ON TABLE pickup_points IS 'Таблица пунктов выдачи заказов';
COMMENT ON TABLE products IS 'Таблица товаров (обуви)';
COMMENT ON TABLE orders IS 'Таблица заказов';

-- ===============================================
-- ПРЕДСТАВЛЕНИЯ (VIEWS)
-- ===============================================

-- Представление: товары на складе
CREATE VIEW IF NOT EXISTS products_in_stock AS
SELECT 
    id, article, name, category, manufacturer, supplier,
    price, stock, discount
FROM products
WHERE stock > 0;

-- Представление: товары со скидкой > 15%
CREATE VIEW IF NOT EXISTS discounted_products AS
SELECT 
    id, article, name, category, price,
    discount, (price * (1 - discount / 100.0)) AS final_price,
    stock
FROM products
WHERE discount > 15;

-- Представление: статистика заказов
CREATE VIEW IF NOT EXISTS order_statistics AS
SELECT 
    DATE_TRUNC('day', order_date)::DATE AS order_day,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'Доставлен' THEN 1 ELSE 0 END) AS delivered,
    SUM(CASE WHEN status = 'Отменен' THEN 1 ELSE 0 END) AS cancelled
FROM orders
GROUP BY DATE_TRUNC('day', order_date)
ORDER BY order_day DESC;

CREATE OR REPLACE FUNCTION update_product_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER product_update_timestamp
BEFORE UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION update_product_timestamp();

CREATE TRIGGER order_update_timestamp
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION update_order_timestamp();

CREATE OR REPLACE FUNCTION update_order_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

