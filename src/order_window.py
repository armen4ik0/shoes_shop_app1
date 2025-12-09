"""Окно управления заказами с красивым макетом"""

import tkinter as tk
from tkinter import ttk, messagebox
from config import Config
from styles import Styles


class OrderWindow:
    """Окно управления заказами"""

    def __init__(self, parent, user_role, db):
        self.parent = parent
        self.user_role = user_role
        self.db = db
        self.window = tk.Toplevel(parent)
        self.window.title("ООО «Обувь» – Заказы")
        self.window.geometry("1200x700")
        Styles.configure_styles()
        self._build_ui()
        self.window.after(100, self.load_orders)

    # ---------- ПОСТРОЕНИЕ UI ----------

    def _build_ui(self):
        """Построить интерфейс"""

        # Панель фильтров
        filter_frame = ttk.LabelFrame(self.window, text="Фильтры", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="Статус:").pack(side=tk.LEFT, padx=5)

        self.status_var = tk.StringVar(value="Все статусы")
        status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=["Все статусы"] + Config.ORDER_STATUSES,
            state="readonly",
            width=20,
        )
        status_combo.pack(side=tk.LEFT, padx=5)
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.load_orders())

        # Кнопки действий
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        if self.user_role == "Администратор":
            ttk.Button(
                btn_frame,
                text="➕ Новый заказ",
                style="Accent.TButton",
                command=self.add_order,
            ).pack(side=tk.LEFT, padx=5)

        # Область карточек заказов
        self._build_cards_area()

    def _build_cards_area(self):
        """Построить область со скроллингом"""
        container = tk.Frame(self.window)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas для скролла
        self.canvas = tk.Canvas(
            container,
            bg="#F5F5F5",
            highlightthickness=0,
            relief=tk.FLAT,
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Скроллбар
        scrollbar = ttk.Scrollbar(
            container,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.config(yscrollcommand=scrollbar.set)

        # Frame для карточек внутри canvas
        self.cards_frame = tk.Frame(self.canvas, bg="#F5F5F5")
        self.canvas_window_id = self.canvas.create_window(
            (0, 0),
            window=self.cards_frame,
            anchor="nw",
        )

        # Обновить размер скролла при изменении размера фрейма
        self.cards_frame.bind("<Configure>", self._on_frame_configure)

        # Подгоняем ширину фрейма под ширину канваса
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Привязка скролла к колесу мыши
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    # ---------- СКРОЛЛ И РАЗМЕРЫ ----------

    def _on_frame_configure(self, event=None):
        """Обновить область скролла при изменениях во фрейме"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Растягивать фрейм с карточками по ширине canvas"""
        self.canvas.itemconfig(self.canvas_window_id, width=event.width)

    def _on_mousewheel(self, event):
        """Обработать скролл мышью"""
        if hasattr(event, "delta") and event.delta:
            if event.delta < 0:
                self.canvas.yview_scroll(3, "units")
            elif event.delta > 0:
                self.canvas.yview_scroll(-3, "units")
        else:
            if event.num == 5:
                self.canvas.yview_scroll(3, "units")
            elif event.num == 4:
                self.canvas.yview_scroll(-3, "units")

    # ---------- ЗАГРУЗКА И ОТРИСОВКА ЗАКАЗОВ ----------

    def load_orders(self):
        """Загрузить заказы и перерисовать карточки"""

        # Очистить старые карточки
        for child in self.cards_frame.winfo_children():
            child.destroy()

        try:
            status = self.status_var.get()
            base_query = """
            SELECT
                o.id,
                o.order_number,
                o.client_name,
                o.order_articles,
                o.order_date,
                o.delivery_date,
                p.address,
                o.pickup_code,
                o.status
            FROM orders o
            LEFT JOIN pickup_points p ON o.pickup_point_id = p.id
            """

            if status == "Все статусы":
                query = base_query + " ORDER BY o.order_number DESC"
                rows = self.db.execute_query(query)
            else:
                query = (
                    base_query + " WHERE o.status = %s ORDER BY o.order_number DESC"
                )
                rows = self.db.execute_query(query, (status,))

            if not rows:
                label = tk.Label(
                    self.cards_frame,
                    text="Заказы не найдены",
                    bg="#F5F5F5",
                    font=("Segoe UI", 10),
                )
                label.pack(anchor="w", pady=10, padx=10)
                return

            for row in rows:
                (
                    order_id,
                    order_num,
                    client_name,
                    articles,
                    order_date,
                    delivery_date,
                    pickup_addr,
                    pickup_code,
                    status_val,
                ) = row

                self._create_order_card(
                    order_id,
                    order_num,
                    client_name,
                    articles,
                    order_date,
                    delivery_date,
                    pickup_addr,
                    status_val,
                )

        except Exception as e:
            print(f"Ошибка загрузки заказов: {e}")
            label = tk.Label(
                self.cards_frame,
                text=f"Ошибка: {e}",
                bg="#F5F5F5",
                fg="red",
                font=("Segoe UI", 10),
            )
            label.pack(anchor="w", pady=10, padx=10)

    def _create_order_card(
        self,
        order_id,
        order_num,
        client_name,
        articles,
        order_date,
        delivery_date,
        pickup_addr,
        status,
    ):
        """Создать карточку заказа как на макете"""

        # Основная карточка (контейнер)
        card = tk.Frame(self.cards_frame, bg="white", relief=tk.SOLID, bd=1)
        card.pack(fill=tk.X, expand=True)

        # Левая часть (основная инфо) и правая (дата доставки)
        left_frame = tk.Frame(card, bg="white")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        right_frame = tk.Frame(card, bg="white", relief=tk.SOLID, bd=1, width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=0, pady=0)
        right_frame.pack_propagate(False)

        # ===== ЛЕВАЯ ЧАСТЬ =====

        # Строка 1: Артикулы заказа
        tk.Label(
            left_frame,
            text="Артикул заказа",
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#333333",
        ).pack(anchor="w", pady=(0, 2))

        tk.Label(
            left_frame,
            text=articles,
            font=("Segoe UI", 10),
            bg="white",
            fg="#000000",
        ).pack(anchor="w", pady=(0, 8))

        # Строка 2: Статус заказа
        tk.Label(
            left_frame,
            text="Статус заказа",
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#333333",
        ).pack(anchor="w", pady=(0, 2))

        tk.Label(
            left_frame,
            text=status,
            font=("Segoe UI", 10),
            bg="white",
            fg="#000000",
        ).pack(anchor="w", pady=(0, 8))

        # Строка 3: Адрес пункта выдачи
        tk.Label(
            left_frame,
            text="Адрес пункта выдачи (текст)",
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#333333",
        ).pack(anchor="w", pady=(0, 2))

        tk.Label(
            left_frame,
            text=pickup_addr,
            font=("Segoe UI", 10),
            bg="white",
            fg="#000000",
            wraplength=600,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        # Строка 4: Дата заказа
        tk.Label(
            left_frame,
            text="Дата заказа",
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#333333",
        ).pack(anchor="w", pady=(0, 2))

        tk.Label(
            left_frame,
            text=str(order_date),
            font=("Segoe UI", 10),
            bg="white",
            fg="#000000",
        ).pack(anchor="w")

        # ===== ПРАВАЯ ЧАСТЬ =====

        tk.Label(
            right_frame,
            text="Дата доставки",
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#333333",
            justify="center",
        ).pack(pady=(12, 5), expand=True, fill=tk.X)

        tk.Label(
            right_frame,
            text=str(delivery_date),
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#000000",
            justify="center",
        ).pack(expand=True, fill=tk.X, pady=(5, 12))

        # ===== ДВОЙНОЙ КЛИК ДЛЯ РЕДАКТИРОВАНИЯ =====
        
        card.bind("<Double-Button-1>", lambda e: self.edit_order(order_id))
        left_frame.bind("<Double-Button-1>", lambda e: self.edit_order(order_id))
        right_frame.bind("<Double-Button-1>", lambda e: self.edit_order(order_id))

    def add_order(self):
        """Добавить новый заказ"""
        self._show_order_dialog(order_id=None)

    def edit_order(self, order_id):
        """Редактировать заказ"""
        self._show_order_dialog(order_id=order_id)

    def _show_order_dialog(self, order_id=None):
        """Показать диалог добавления/редактирования заказа"""
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Новый заказ" if order_id is None else "Редактировать заказ")
        edit_window.geometry("500x650")
        edit_window.resizable(False, False)
        Styles.configure_styles()

        if order_id:
            try:
                query = """
                SELECT order_number, order_articles, order_date, delivery_date,
                pickup_point_id, client_name, pickup_code, status
                FROM orders WHERE id = %s
                """
                result = self.db.execute_query(query, (order_id,))
                if result:
                    (
                        order_num,
                        articles,
                        o_date,
                        d_date,
                        pp_id,
                        client,
                        code,
                        order_status,
                    ) = result[0]
                else:
                    order_num = articles = o_date = d_date = pp_id = client = code = order_status = ""
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки заказа: {e}")
                return
        else:
            order_num = articles = o_date = d_date = pp_id = client = code = order_status = ""

        # Форма
        form_frame = ttk.Frame(edit_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        fields = {
            "Номер заказа": ("order_num_var", str(order_num) if order_id else ""),
            "Артикулы товаров": ("articles_var", str(articles) if articles else ""),
            "Дата заказа": ("order_date_var", str(o_date) if o_date else ""),
            "Дата доставки": ("delivery_date_var", str(d_date) if d_date else ""),
            "Клиент": ("client_var", str(client) if client else ""),
            "Код получения": ("code_var", str(code) if code else ""),
            "Статус": ("status_var", str(order_status) if order_status else "Обработка"),
        }

        edit_vars = {}

        for label, (var_name, default_val) in fields.items():
            ttk.Label(form_frame, text=label, style="TLabel").pack(
                anchor="w", pady=(10, 2)
            )

            var = tk.StringVar(value=default_val)
            edit_vars[var_name] = var

            if label == "Статус":
                combo = ttk.Combobox(
                    form_frame,
                    textvariable=var,
                    values=Config.ORDER_STATUSES,
                    state="readonly",
                    width=50,
                )
                combo.pack(anchor="w", fill="x", pady=(0, 5))
            else:
                entry = ttk.Entry(form_frame, textvariable=var, width=50)
                entry.pack(anchor="w", fill="x", pady=(0, 5))

        # Кнопки
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill="x", pady=20)

        def save_order():
            try:
                if order_id:
                    query = """
                    UPDATE orders SET
                        order_number=%s,
                        order_articles=%s,
                        order_date=%s,
                        delivery_date=%s,
                        client_name=%s,
                        pickup_code=%s,
                        status=%s
                    WHERE id=%s
                    """
                    self.db.execute_update(
                        query,
                        (
                            edit_vars["order_num_var"].get(),
                            edit_vars["articles_var"].get(),
                            edit_vars["order_date_var"].get(),
                            edit_vars["delivery_date_var"].get(),
                            edit_vars["client_var"].get(),
                            edit_vars["code_var"].get(),
                            edit_vars["status_var"].get(),
                            order_id,
                        ),
                    )
                else:
                    query = """
                    INSERT INTO orders
                    (order_number, order_articles, order_date, delivery_date, client_name, pickup_code, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    self.db.execute_update(
                        query,
                        (
                            edit_vars["order_num_var"].get(),
                            edit_vars["articles_var"].get(),
                            edit_vars["order_date_var"].get(),
                            edit_vars["delivery_date_var"].get(),
                            edit_vars["client_var"].get(),
                            edit_vars["code_var"].get(),
                            edit_vars["status_var"].get(),
                        ),
                    )

                messagebox.showinfo("Успех", "Заказ сохранён")
                edit_window.destroy()
                self.load_orders()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")

        ttk.Button(
            btn_frame,
            text="💾 Сохранить",
            style="Accent.TButton",
            command=save_order,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="❌ Отмена",
            style="Secondary.TButton",
            command=edit_window.destroy,
        ).pack(side=tk.LEFT, padx=5)

        # Кнопка удаления (если это редактирование)
        if order_id:
            def delete_order_confirm():
                if messagebox.askyesno("Удаление ⚠️", "Вы уверены, что хотите удалить этот заказ?"):
                    try:
                        query = "DELETE FROM orders WHERE id = %s"
                        self.db.execute_update(query, (order_id,))
                        messagebox.showinfo("Успех", "Заказ удалён")
                        edit_window.destroy()
                        self.load_orders()
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Ошибка при удалении: {e}")

            ttk.Button(
                btn_frame,
                text="🗑️ Удалить",
                style="Secondary.TButton",
                command=delete_order_confirm,
            ).pack(side=tk.LEFT, padx=5)
    