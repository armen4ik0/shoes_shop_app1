import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from PIL import Image, ImageTk
from database import Database
from config import Config


class ProductWindow:
    """Окно добавления/редактирования товара"""

    def __init__(self, parent, product_data=None, on_save=None):
        self.parent = parent
        self.product_data = product_data
        self.on_save = on_save
        self.db = Database()

        # Определяем роль пользователя из parent (если нужно)
        self.user_role = "Администратор"
        if hasattr(parent, "user_role"):
            self.user_role = parent.user_role
        elif hasattr(parent, "parent") and hasattr(parent.parent, "user_role"):
            self.user_role = parent.parent.user_role

        # Путь к текущему фото
        self.current_photo_path = product_data[11] if product_data else ""

        # Сразу открываем диалог товара (БЕЗ окна со списком)
        self._show_product_dialog(self.product_data)

    def _show_product_dialog(self, product_data):
        """Диалог добавления/редактирования товара с фото"""

        dialog = tk.Toplevel(self.parent)
        dialog.title("Редактирование товара" if product_data else "Добавление товара")
        dialog.geometry("800x750")
        dialog.resizable(False, False)
        dialog.update_idletasks()

        parent_x = self.parent.winfo_x() if hasattr(self.parent, "winfo_x") else 100
        parent_y = self.parent.winfo_y() if hasattr(self.parent, "winfo_y") else 100
        x = parent_x + 150
        y = parent_y + 50
        dialog.geometry(f"+{x}+{y}")

        def on_closing():
            if self.on_save:
                self.on_save()
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_closing)

        # ---------- ГЛАВНЫЙ ФРЕЙМ ----------

        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))

        # ---------- ЛЕВАЯ ЧАСТЬ (ФОРМА) ----------

        canvas = tk.Canvas(
            left_frame,
            bg=Config.COLORS["primary_bg"],
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(
            left_frame,
            orient=tk.VERTICAL,
            command=canvas.yview,
        )
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # product_data: (id, article, name, category, description,
        # manufacturer, supplier, price, unit, stock, discount, photo_path)

        fields = {
            "article": (
                "Артикул*",
                "entry",
                product_data[1] if product_data else "",
            ),
            "name": (
                "Название*",
                "entry",
                product_data[2] if product_data else "",
            ),
            "category": (
                "Категория*",
                "combobox",
                product_data[3] if product_data else "",
            ),
            "description": (
                "Описание",
                "text",
                product_data[4] if product_data else "",
            ),
            "manufacturer": (
                "Производитель*",
                "combobox",
                product_data[5] if product_data else "",
            ),
            "supplier": (
                "Поставщик*",
                "entry",
                product_data[6] if product_data else "",
            ),
            "price": (
                "Цена (руб.)*",
                "entry",
                str(product_data[7]) if product_data else "",
            ),
            "unit": (
                "Единица*",
                "combobox",
                product_data[8] if product_data else "",
            ),
            "stock": (
                "На складе*",
                "entry",
                str(product_data[9]) if product_data else "",
            ),
            "discount": (
                "Скидка (%)*",
                "entry",
                str(product_data[10]) if product_data else "0",
            ),
        }

        entries = {}
        row = 0

        for field_name, (label_text, field_type, value) in fields.items():
            ttk.Label(
                scrollable_frame,
                text=label_text,
                style="TLabel",
            ).grid(row=row, column=0, sticky="w", pady=8)

            if field_type == "entry":
                entry = ttk.Entry(scrollable_frame, width=30)
                entry.insert(0, value)
                if field_name == "article" and product_data:
                    entry.config(state="readonly")
                entry.grid(row=row, column=1, sticky="ew", padx=10, pady=8)
                entries[field_name] = entry

            elif field_type == "combobox":
                combo = ttk.Combobox(scrollable_frame, width=27, state="readonly")

                if field_name == "category":
                    q = "SELECT DISTINCT category FROM products ORDER BY category"
                    res = self.db.execute_query(q)
                    combo["values"] = [r[0] for r in res] if res else []
                elif field_name == "manufacturer":
                    q = "SELECT DISTINCT manufacturer FROM products ORDER BY manufacturer"
                    res = self.db.execute_query(q)
                    combo["values"] = [r[0] for r in res] if res else []
                elif field_name == "unit":
                    combo["values"] = Config.UNITS

                combo.set(value)
                combo.grid(row=row, column=1, sticky="ew", padx=10, pady=8)
                entries[field_name] = combo

            elif field_type == "text":
                text = tk.Text(
                    scrollable_frame,
                    height=3,
                    width=27,
                    font=Config.FONT_SMALL,
                )
                text.insert("1.0", value)
                text.grid(row=row, column=1, sticky="ew", padx=10, pady=8)
                entries[field_name] = text

            row += 1

        scrollable_frame.columnconfigure(1, weight=1)

        # ---------- ПРАВАЯ ЧАСТЬ (ФОТО) ----------

        ttk.Label(
            right_frame,
            text="Фотография товара:",
            font=Config.FONT_HEADER,
        ).pack(pady=(0, 10))

        photo_frame = ttk.Frame(right_frame, relief=tk.SOLID, borderwidth=1)
        photo_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.photo_canvas = tk.Canvas(
            photo_frame,
            bg="#E0E0E0",
            width=300,
            height=300,
            highlightthickness=0,
        )
        self.photo_canvas.pack(padx=10, pady=10)

        def load_photo_preview():
            self.photo_canvas.delete("all")
            if self.current_photo_path and os.path.exists(self.current_photo_path):
                try:
                    img = Image.open(self.current_photo_path)
                    img.thumbnail((280, 280), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.photo_canvas.create_image(150, 150, image=photo)
                    self.photo_canvas.image = photo
                except Exception:
                    self.photo_canvas.create_text(
                        150,
                        150,
                        text="❌ Ошибка\nзагрузки фото",
                        fill="red",
                    )
            else:
                self.photo_canvas.create_text(150, 150, text="Нет фото", fill="gray")

        load_photo_preview()

        photo_button_frame = ttk.Frame(right_frame)
        photo_button_frame.pack(fill=tk.X)

        def browse_photo():
            file_path = filedialog.askopenfilename(
                title="Выберите фотографию",
                filetypes=[
                    ("Image Files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                    ("All Files", "*.*"),
                ],
            )
            if file_path:
                self.current_photo_path = file_path
                load_photo_preview()

        def clear_photo():
            self.current_photo_path = ""
            load_photo_preview()

        ttk.Button(
            photo_button_frame,
            text="📁 Обзор",
            command=browse_photo,
            width=12,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            photo_button_frame,
            text="🗑️ Удалить",
            command=clear_photo,
            width=12,
        ).pack(side=tk.LEFT, padx=2)

        # ---------- КНОПКИ СОХРАНЕНИЯ ----------

        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=15, pady=10)

        def save_product():
            try:
                data = {}
                for field_name, widget in entries.items():
                    if isinstance(widget, tk.Text):
                        data[field_name] = widget.get("1.0", "end-1c").strip()
                    else:
                        data[field_name] = widget.get().strip()

                required = [
                    "article",
                    "name",
                    "category",
                    "manufacturer",
                    "supplier",
                    "price",
                    "unit",
                    "stock",
                    "discount",
                ]

                for field in required:
                    if not data[field]:
                        messagebox.showerror("Ошибка", f"Поле '{field}' обязательно")
                        return

                try:
                    price = float(data["price"])
                    stock = int(data["stock"])
                    discount = int(data["discount"])

                    if price < 0:
                        messagebox.showerror("Ошибка", "Цена не может быть отрицательной")
                        return
                    if stock < 0:
                        messagebox.showerror(
                            "Ошибка",
                            "Количество не может быть отрицательным",
                        )
                        return
                    if discount < 0 or discount > 100:
                        messagebox.showerror(
                            "Ошибка",
                            "Скидка должна быть от 0 до 100%",
                        )
                        return
                except ValueError:
                    messagebox.showerror(
                        "Ошибка",
                        "Проверьте значения цены, количества и скидки",
                    )
                    return

                if product_data:
                    query = """
                    UPDATE products SET
                        name=%s,
                        category=%s,
                        description=%s,
                        manufacturer=%s,
                        supplier=%s,
                        price=%s,
                        unit=%s,
                        stock=%s,
                        discount=%s,
                        photo_path=%s
                    WHERE article=%s
                    """
                    ok = self.db.execute_update(
                        query,
                        (
                            data["name"],
                            data["category"],
                            data["description"],
                            data["manufacturer"],
                            data["supplier"],
                            float(data["price"]),
                            data["unit"],
                            int(data["stock"]),
                            int(data["discount"]),
                            self.current_photo_path,
                            data["article"],
                        ),
                    )
                    if ok:
                        messagebox.showinfo("Успех", "Товар обновлён")
                        on_closing()
                    else:
                        messagebox.showerror("Ошибка", "Не удалось обновить товар")
                else:
                    query = """
                    INSERT INTO products
                        (article, name, category, description, manufacturer,
                         supplier, price, unit, stock, discount, photo_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    ok = self.db.execute_update(
                        query,
                        (
                            data["article"],
                            data["name"],
                            data["category"],
                            data["description"],
                            data["manufacturer"],
                            data["supplier"],
                            float(data["price"]),
                            data["unit"],
                            int(data["stock"]),
                            int(data["discount"]),
                            self.current_photo_path,
                        ),
                    )
                    if ok:
                        messagebox.showinfo("Успех", "Товар добавлен")
                        on_closing()
                    else:
                        messagebox.showerror("Ошибка", "Не удалось добавить товар")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {e}")

        ttk.Button(
            button_frame,
            text="✓ Сохранить",
            style="Accent.TButton",
            command=save_product,
            width=18,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="✕ Отмена",
            style="Secondary.TButton",
            command=on_closing,
            width=18,
        ).pack(side=tk.LEFT, padx=5)
