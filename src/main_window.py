import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
from PIL import Image, ImageTk
import os
from database import Database
from config import Config
from styles import Styles
from order_window import OrderWindow
from product_window import ProductWindow


class MainWindow:
    """Главное окно приложения с карточками товаров"""

    def __init__(self, user_data):
        self.user_data = user_data
        self.db = Database()
        self.window = tk.Tk()
        self.window.title("ООО Обувь - Система управления товарами")
        self.window.geometry("1200x700")
        Styles.configure_styles()
        self.product_edit_window = None
        self.orders_window = None
        self._build_header()
        self._build_toolbar()
        self._build_cards_area()
        self.load_products()
        self.window.mainloop()

    # ---------- ШАПКА ----------

    def _build_header(self):
        top_frame = ttk.Frame(self.window)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        # Лого
        try:
            if os.path.exists(Config.LOGO_PATH):
                img = Image.open(Config.LOGO_PATH)
                img.thumbnail((50, 50))
                photo = ImageTk.PhotoImage(img)
                logo_label = ttk.Label(top_frame, image=photo)
                logo_label.image = photo
                logo_label.pack(side=tk.LEFT, padx=5)
        except Exception:
            pass

        # Заголовок
        ttk.Label(
            top_frame,
            text="ООО Обувь - Система управления товарами",
            style="Title.TLabel",
        ).pack(side=tk.LEFT, padx=10)

        ttk.Separator(self.window, orient="horizontal").pack(fill=tk.X)

        # Правый фрейм (ФИО + Кнопка Выход)
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, padx=10)

        # ФИО
        ttk.Label(
            right_frame,
            text=self.user_data["full_name"],
            style="Header.TLabel",
        ).pack(side=tk.LEFT, padx=5)

        # Кнопка Выход
        ttk.Button(
            right_frame,
            text="Выход",
            style="Accent.TButton",
            command=self.logout,
        ).pack(side=tk.RIGHT, padx=5)

    # ---------- ПАНЕЛЬ КНОПОК И ФИЛЬТРОВ ----------

    def _build_toolbar(self):

        # Фильтры только для менеджера и администратора
        if self.user_data["role"] in ["Менеджер", "Администратор"]:
            filter_frame = ttk.LabelFrame(
                self.window, text="Поиск и фильтры", padding=10
            )
            filter_frame.pack(fill=tk.X, padx=10, pady=5)

            # Поиск
            ttk.Label(filter_frame, text="Поиск:", style="TLabel").pack(
                side=tk.LEFT, padx=5
            )
            self.search_var = tk.StringVar()
            search_entry = ttk.Entry(
                filter_frame, textvariable=self.search_var, width=30
            )
            search_entry.pack(side=tk.LEFT, padx=5)
            search_entry.bind("<KeyRelease>", lambda e: self.load_products())

            # Поставщик
            ttk.Label(filter_frame, text="Поставщик:", style="TLabel").pack(
                side=tk.LEFT, padx=5
            )
            self.supplier_var = tk.StringVar(value="Все поставщики")
            self.supplier_combo = ttk.Combobox(
                filter_frame,
                textvariable=self.supplier_var,
                width=25,
                state="readonly",
            )
            self.supplier_combo.pack(side=tk.LEFT, padx=5)
            self.supplier_combo.bind(
                "<<ComboboxSelected>>", lambda e: self.load_products()
            )

            # Сортировка по количеству
            ttk.Label(filter_frame, text="Сортировка:", style="TLabel").pack(
                side=tk.LEFT, padx=5
            )
            self.sort_var = tk.StringVar(value="Нет")
            sort_combo = ttk.Combobox(
                filter_frame,
                textvariable=self.sort_var,
                values=["Нет", "По возрастанию", "По убыванию"],
                state="readonly",
                width=15,
            )
            sort_combo.pack(side=tk.LEFT, padx=5)
            sort_combo.bind("<<ComboboxSelected>>", lambda e: self.load_products())

            self._load_suppliers()

        else:
            self.search_var = tk.StringVar(value="")
            self.supplier_var = tk.StringVar(value="Все поставщики")
            self.sort_var = tk.StringVar(value="Нет")
            self.supplier_combo = None

        # Нижняя панель кнопок
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        if self.user_data["role"] == "Администратор":
            ttk.Button(
                btn_frame,
                text="➕ Добавить товар",
                style="Accent.TButton",
                command=self.add_product,
            ).pack(side=tk.LEFT, padx=5)

        if self.user_data["role"] in ["Менеджер", "Администратор"]:
            ttk.Button(
                btn_frame,
                text="📋 Заказы",
                style="Accent.TButton",
                command=self.show_orders,
            ).pack(side=tk.LEFT, padx=5)

    # ---------- ОБЛАСТЬ КАРТОЧЕК ----------

    def _build_cards_area(self):
        container = ttk.Frame(self.window)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(container, highlightthickness=0, bg="white")
        scrollbar = ttk.Scrollbar(
            container, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.cards_frame = tk.Frame(self.canvas, bg="white")
        self.canvas_window_id = self.canvas.create_window(
            (0, 0), window=self.cards_frame, anchor="nw"
        )
        self.cards_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        # Растягиваем внутренний фрейм по ширине канваса
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_canvas_configure(self, event):
        """Растягивать фрейм с карточками по ширине canvas"""
        self.canvas.itemconfig(self.canvas_window_id, width=event.width)

    # ---------- ЗАГРУЗКА ДАННЫХ ----------

       # ---------- ЗАГРУЗКА ДАННЫХ ----------

    def _load_suppliers(self):
        try:
            rows = self.db.execute_query(
                "SELECT DISTINCT supplier FROM products ORDER BY supplier"
            )
            values = ["Все поставщики"]
            if rows:
                values += [r[0] for r in rows if r[0]]
            if self.supplier_combo:
                self.supplier_combo["values"] = values
                self.supplier_combo.current(0)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки поставщиков: {e}")

    def _query_products(self):
        """Получить товары с учётом фильтров/поиска/сортировки"""
        search = self.search_var.get().strip().lower()
        supplier = self.supplier_var.get()
        sort = self.sort_var.get()

        query = (
            "SELECT id, article, name, category, description, "
            "manufacturer, supplier, price, unit, stock, discount, photo_path "
            "FROM products WHERE 1=1"
        )

        params = []

        # фильтр по поставщику
        if supplier != "Все поставщики":
            query += " AND supplier = %s"
            params.append(supplier)

        # ПОИСК ПО НЕСКОЛЬКИМ СЛОВАМ
        if search:
            # разбиваем строку: "туфли kari rieker" -> ["туфли","kari","rieker"]
            terms = [t for t in search.split() if t]

            for term in terms:
                p = f"%{term}%"
                # для каждого слова добавляем блок (OR по полям, AND между словами)
                query += (
                    " AND ("
                    "LOWER(article) LIKE %s OR "
                    "LOWER(name) LIKE %s OR "
                    "LOWER(category) LIKE %s OR "
                    "LOWER(manufacturer) LIKE %s OR "
                    "LOWER(supplier) LIKE %s OR "
                    "LOWER(description) LIKE %s)"
                )
                params += [p] * 6

        # сортировка
        if sort == "По возрастанию":
            query += " ORDER BY stock ASC"
        elif sort == "По убыванию":
            query += " ORDER BY stock DESC"
        else:
            query += " ORDER BY article"

        return self.db.execute_query(query, params if params else None)

    def load_products(self):
        """Перерисовать список карточек товаров"""
        for child in self.cards_frame.winfo_children():
            child.destroy()

        try:
            rows = self._query_products()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки товаров: {e}")
            return

        if not rows:
            ttk.Label(self.cards_frame, text="Товары не найдены").pack(
                anchor="w", pady=5
            )
            return

        for row in rows:
            (
                prod_id,
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
            ) = row

            self._create_product_card(
                prod_id,
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
            )


    # ---------- КАРТОЧКА ТОВАРА ----------

    def _create_product_card(
        self,
        prod_id,
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
    ):

        # Цвет фона по условиям ТЗ
        bg_color = "white"
        if discount and discount > 15:
            bg_color = "#2E8B57"

        # высота 160px + pack_propagate
        card = tk.Frame(self.cards_frame, bd=1, relief=tk.SOLID, bg=bg_color, height=160)
        card.pack(fill=tk.X, pady=5)
        card.pack_propagate(False)

        # Левая часть — фото
        left = tk.Frame(card, width=150, height=160, bg=bg_color)
        left.pack(side=tk.LEFT, fill=tk.BOTH)
        left.pack_propagate(False)

        img_label = tk.Label(left, bg=bg_color)
        img_label.pack(expand=True)

        img = self._load_product_image(photo_path)
        img_label.configure(image=img)
        img_label.image = img

        # Центральная часть — текст
        center = tk.Frame(card, bg=bg_color)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        title_text = f"{category} | {name}"
        tk.Label(
            center,
            text=title_text,
            font=Config.FONT_HEADER,
            bg=bg_color,
        ).pack(anchor="w")

        lines = [
            f"Описание товара: {description or '-'}",
            f"Производитель: {manufacturer}",
            f"Поставщик: {supplier}",
        ]

        price_line = self._format_price_line(price, discount)
        lines.append(price_line)

        lines.append(f"Единица измерения: {unit}")
        lines.append(f"Количество на складе: {stock}")

        for ln in lines:
            # Если линия содержит цену — сложная обработка
            if ln.startswith("Цена:"):
                self._create_price_label(center, ln, bg_color)
            elif "Количество на складе:" in ln:
                # Количество голубым если нет на складе
                qty_color = "#0066CC" if stock == 0 else "black"
                tk.Label(
                    center,
                    text=ln,
                    bg=bg_color,
                    fg=qty_color,
                    anchor="w",
                    justify="left",
                    font=Config.FONT_DEFAULT,
                ).pack(anchor="w")
            else:
                tk.Label(
                    center,
                    text=ln,
                    bg=bg_color,
                    fg="black",
                    anchor="w",
                    justify="left",
                    font=Config.FONT_DEFAULT,
                ).pack(anchor="w")

        # Правая часть — действующая скидка (на доп. фоне)
        right = tk.Frame(
            card, width=140, height=160, bd=1, relief=tk.SOLID, bg="#7FFF00"
        )
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        tk.Label(
            right,
            text="Действующая\nскидка",
            font=Config.FONT_HEADER,
            justify="center",
            bg="#7FFF00",
        ).pack(pady=(10, 5))

        tk.Label(
            right,
            text=f"{discount or 0} %",
            font=Config.FONT_TITLE,
            fg="black",
            bg="#7FFF00",
        ).pack()

        # Клик по карточке для администратора
        if self.user_data["role"] == "Администратор":
            card.bind("<Button-1>", lambda e, pid=prod_id: self.edit_product(pid))
            for w in (left, center, right):
                w.bind(
                    "<Button-1>",
                    lambda e, pid=prod_id: self.edit_product(pid),
                )

    def _create_price_label(self, parent, price_text, bg_color):
        """Создать метку с ценой: слово 'Цена:' чёрное, старая цена красная зачёркнутая, новая чёрная"""
        # Парсим текст вида "Цена: 100.00 → 85.00"
        # или "Цена: 100.00"
        
        if " → " in price_text:
            # Есть скидка
            parts = price_text.split(" → ")
            price_part = parts[0]  # "Цена: 100.00"
            new_price = parts[1].strip()  # "85.00"
            
            # Отделяем слово "Цена:" от старой цены
            old_price = price_part.replace("Цена: ", "").strip()
            
            # Создаём контейнер для обеих цен
            price_container = tk.Frame(parent, bg=bg_color)
            price_container.pack(anchor="w")
            
            # Слово "Цена:" (чёрное, обычное)
            tk.Label(
                price_container,
                text="Цена: ",
                bg=bg_color,
                fg="black",
                font=Config.FONT_DEFAULT,
            ).pack(side=tk.LEFT, anchor="w")
            
            # Старая цена (красная, зачёркнутая)
            tk.Label(
                price_container,
                text=old_price,
                bg=bg_color,
                fg="#FF0000",
                font=(Config.FONT_DEFAULT[0], Config.FONT_DEFAULT[1], "overstrike"),
            ).pack(side=tk.LEFT, anchor="w")
            
            # Стрелка и новая цена (чёрная)
            tk.Label(
                price_container,
                text=f" → {new_price}",
                bg=bg_color,
                fg="black",
                font=Config.FONT_DEFAULT,
            ).pack(side=tk.LEFT, anchor="w")
        else:
            # Нет скидки — просто обычная цена
            tk.Label(
                parent,
                text=price_text,
                bg=bg_color,
                fg="black",
                anchor="w",
                font=Config.FONT_DEFAULT,
            ).pack(anchor="w")

    def _load_product_image(self, photo_path):
        """Загрузить фото товара или картинку-заглушку"""
        candidates = []

        if photo_path:
            # 1) как есть
            candidates.append(str(photo_path))

            # 2) только имя файла
            base = os.path.basename(str(photo_path)).strip()
            if base:
                candidates.append(
                    os.path.join(Config.DATA_DIR, "product_images", base)
                )

            # 3) без расширения -> .jpg
            root, ext = os.path.splitext(base)
            if not ext:
                candidates.append(
                    os.path.join(
                        Config.DATA_DIR,
                        "product_images",
                        f"{root}.jpg",
                    )
                )

        path = None
        for p in candidates:
            if p and os.path.exists(p):
                path = p
                break

        if not path:
            if os.path.exists(Config.PLACEHOLDER_IMAGE):
                path = Config.PLACEHOLDER_IMAGE
            else:
                return tk.PhotoImage()

        try:
            img = Image.open(path)
            img = img.resize((120, 100), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return tk.PhotoImage()

    def _format_price_line(self, price, discount):
        """Строка цены по ТЗ"""
        price_dec = Decimal(price)
        if discount and discount > 0:
            disc_dec = Decimal(discount)
            final_price = price_dec * (Decimal(1) - disc_dec / Decimal(100))
            return f"Цена: {price_dec:.2f} → {final_price:.2f}"
        return f"Цена: {price_dec:.2f}"

    # ---------- ОБРАБОТЧИКИ СОБЫТИЙ ----------

    def add_product(self):
        """Добавить новый товар"""
        if self.product_edit_window:
            messagebox.showwarning(
                "Внимание ⚠️", "Окно редактирования товара уже открыто!"
            )
            return

        def on_save():
            self.product_edit_window = None
            self.load_products()

        self.product_edit_window = ProductWindow(self.window, None, on_save)

    def edit_product(self, product_id):
        """Редактировать существующий товар"""
        if self.product_edit_window:
            messagebox.showwarning(
                "Внимание ⚠️", "Окно редактирования уже открыто"
            )
            return

        try:
            row = self.db.execute_query(
                "SELECT id, article, name, category, description, "
                "manufacturer, supplier, price, unit, stock, discount, "
                "photo_path FROM products WHERE id = %s",
                (product_id,),
            )

            if not row:
                return

            product_data = row[0]

            def on_save():
                self.product_edit_window = None
                self.load_products()

            self.product_edit_window = ProductWindow(
                self.window, product_data, on_save
            )

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки товара: {e}")

    def show_orders(self):
        """Показать окно заказов"""
        if self.user_data["role"] not in ["Менеджер", "Администратор"]:
            return

        if self.orders_window:
            messagebox.showwarning(
                "Внимание ⚠️", "Окно заказов уже открыто!"
            )
            return

        self.orders_window = OrderWindow(
            self.window, self.user_data["role"], self.db
        )

        self.window.wait_window(self.orders_window.window)
        self.orders_window = None

    def logout(self):
        """Выход из приложения"""
        if messagebox.askyesno("Выход ⚠️", "Вы уверены, что хотите выйти?"):
            self.window.destroy()
