import os

class Config:

    """Конфигурация приложения"""

    # PostgreSQL подключение
    DATABASE_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'shoes_shop',
        'user': 'postgres',
        'password': '112211',
        'client_encoding': 'UTF8'
    }

    # Пути к файлам (относительно src/)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')

    # Иконки и изображения
    ICON_PATH = os.path.join(RESOURCES_DIR, 'icon.png')
    LOGO_PATH = os.path.join(RESOURCES_DIR, 'logo.png')
    PLACEHOLDER_IMAGE = os.path.join(RESOURCES_DIR, 'picture.png')

    # Роли пользователей
    ROLES = {
        'guest': 'Гость',
        'client': 'Клиент',
        'manager': 'Менеджер',
        'admin': 'Администратор'
    }

    # Статусы заказов
    ORDER_STATUSES = ['Обработка', 'В пути', 'Доставлен', 'Отменен']

    # Единицы измерения
    UNITS = ['пара', 'пары', 'шт', 'упаковка']

    COLORS = {
        'primary_bg': '#FFFFFF',          # Белый фон
        'secondary_bg': '#7FFF00',        # Лайм (дополнительный фон)
        'accent_color': '#00FA9A',        # Мятный (акцентирование)
        'text_primary': '#000000',        # Чёрный текст
        'text_secondary': '#000000',      # Чёрный для вторичного текста
        'primary_color': '#2E8B57',       # Тёмно-зелёный акцент
        'border_color': '#CCCCCC',        # Серая граница
        'high_discount': '#2E8B57',       # Зелёный для высокой скидки (>15%)
        'out_of_stock': '#ADD8E6',        # Голубой для отсутствия товара
        'price_old': '#FF0000',           # Красный для старой цены (перечёркнутой)
        'price_new': '#000000'            # Чёрный для новой цены
    }

    # Шрифты (Times New Roman согласно ТЗ) - УМЕНЬШЕНЫ для карточек
    FONT_DEFAULT = ('Times New Roman', 10)       # ✅ 12 → 9 (основной текст)
    FONT_TITLE = ('Times New Roman', 14, 'bold')    # ✅ 14 → 11 (заголовок)
    FONT_HEADER = ('Times New Roman', 12, 'bold')   # ✅ 12 → 10 (подзаголовок)
    FONT_LABEL = ('Times New Roman', 11)         # ✅ 11 → 9 (метки)
    FONT_BUTTON = ('Times New Roman', 11)       # ✅ 11 → 10 (кнопки)
    FONT_INPUT = ('Times New Roman', 11)        # ✅ 11 → 10 (поля ввода)
    FONT_SMALL = ('Times New Roman', 10)         # ✅ 10 → 8 (мелкий текст)
