import tkinter as tk
from tkinter import messagebox, ttk
import os
from PIL import Image, ImageTk
from config import Config
from database import Database


class LoginWindow:
    """Окно авторизации пользователя"""

    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.db = Database()
        self.window = tk.Tk()
        self.window.title("ООО Обувь - Авторизация")
        self.window.geometry("500x600")
        self.window.resizable(False, False)

        # Центрируем окно на экране
        self._center_window()

        # Устанавливаем иконку приложения
        self._set_icon()

        # Настраиваем стили
        from styles import Styles
        Styles.configure_styles()

        self._setup_ui()

    def _center_window(self):
        """Центрирование окна на экране"""
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = 500
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _set_icon(self):
        """Установка иконки окна"""
        try:
            icon_paths = [
                Config.ICON_PATH,
                os.path.join('resources', 'icon.png'),
                os.path.join('resources', 'Icon.png'),
            ]

            for path in icon_paths:
                if os.path.exists(path):
                    try:
                        if path.endswith('.ico'):
                            self.window.iconbitmap(path)
                        else:
                            # Для PNG используем PhotoImage
                            icon_img = Image.open(path)
                            icon_img = icon_img.resize((32, 32), Image.Resampling.LANCZOS)
                            icon_photo = ImageTk.PhotoImage(icon_img)
                            self.window.iconphoto(True, icon_photo)
                        break
                    except:
                        continue
        except Exception as e:
            print(f"⚠ Ошибка установки иконки: {e}")

    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Основной контейнер
        main_frame = ttk.Frame(self.window, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ==================== ЛОГОТИП КОМПАНИИ ====================
        logo_frame = ttk.Frame(main_frame, style='TFrame')
        logo_frame.pack(fill=tk.X, pady=(0, 20))

        logo_loaded = False
        try:
            logo_paths = [Config.LOGO_PATH, Config.ICON_PATH]
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    try:
                        img = Image.open(logo_path)
                        img = img.resize((120, 120), Image.Resampling.LANCZOS)
                        logo_photo = ImageTk.PhotoImage(img)
                        logo_label = tk.Label(
                            logo_frame,
                            image=logo_photo,
                            background=Config.COLORS['primary_bg']
                        )
                        logo_label.image = logo_photo
                        logo_label.pack()
                        logo_loaded = True
                        break
                    except:
                        continue
        except:
            pass

        # Текстовый логотип если изображение не загрузилось
        if not logo_loaded:
            tk.Label(
                logo_frame,
                text="ООО ОБУВЬ",
                font=Config.FONT_TITLE,
                background=Config.COLORS['primary_bg'],
                # ✅ ИСПРАВЛЕНО: Используем правильный ключ 'primary_color' вместо 'accent'
                foreground=Config.COLORS['primary_color']
            ).pack()

        # ==================== ФОРМА АВТОРИЗАЦИИ ====================
        form_frame = ttk.Frame(main_frame, style='TFrame')
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        inner_frame = ttk.Frame(form_frame, style='TFrame')
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Заголовок формы
        ttk.Label(
            inner_frame,
            text="ВХОД В СИСТЕМУ",
            style='Title.TLabel'
        ).pack(pady=(0, 30))

        # Поле логина
        ttk.Label(
            inner_frame,
            text="Логин (email):",
            style='TLabel'
        ).pack(anchor='w', pady=(0, 5))

        self.login_entry = ttk.Entry(inner_frame, width=40)
        self.login_entry.pack(anchor='w', fill='x', pady=(0, 15))

        # Поле пароля
        ttk.Label(
            inner_frame,
            text="Пароль:",
        ).pack(anchor='w', pady=(0, 5))

        self.password_entry = ttk.Entry(inner_frame, width=40, show='*')
        self.password_entry.pack(anchor='w', fill='x', pady=(0, 25))

        # Привязываем Enter для входа
        self.password_entry.bind('<Return>', lambda e: self._login())

        # ==================== КНОПКИ ====================
        button_frame = ttk.Frame(inner_frame, style='TFrame')
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="ВОЙТИ",
            style='Accent.TButton',
            command=self._login,
            width=20
        ).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(
            button_frame,
            text="Гость",
            style='Secondary.TButton',
            command=self._login_as_guest,
            width=20
        ).pack(side=tk.LEFT, padx=5, pady=5)

        # ==================== СПРАВКА ====================
        info_frame = ttk.Frame(inner_frame, style='TFrame')
        info_frame.pack(fill=tk.X, pady=(30, 0))


    def _login(self):
        """Обработка входа"""
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()

        if not login or not password:
            messagebox.showerror(
                "Ошибка",
                "Пожалуйста, введите логин и пароль"
            )
            return

        try:
            query = """
                SELECT role, full_name FROM users
                WHERE login = %s AND password = %s;
            """
            result = self.db.execute_query(query, (login, password))

            if result:
                role, full_name = result[0]
                self.window.destroy()
                self.on_login_success(role, full_name, login)
            else:
                messagebox.showerror(
                    "Ошибка",
                    "Неверный логин или пароль"
                )
        except Exception as e:
            messagebox.showerror(
                "Ошибка подключения",
                f"Ошибка при подключении к БД:\n{str(e)}"
            )

    def _login_as_guest(self):
        """Вход как гость"""
        self.window.destroy()
        self.on_login_success('Гость', 'Гость', '')

    def run(self):
        """Запуск окна авторизации"""
        self.window.mainloop()
