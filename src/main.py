#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Главный файл приложения "ООО Обувь"
Система управления товарами и заказами
"""

import sys
import os
import traceback

# Добавляем текущую папку в sys.path для импорта локальных модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print(f"📁 Рабочая папка: {current_dir}")
print(f"📁 sys.path: {sys.path[:2]}")


def main():
    """Главная функция приложения"""
    try:
        print("\n" + "=" * 60)
        print("📂 ООО Обувь - Система управления товарами")
        print("=" * 60)

        # --------- ЗАГРУЗКА МОДУЛЕЙ ---------
        print("\n📥 Загрузка модулей...")

        try:
            from database import Database
            print("✓ database.py загружен")
        except ImportError as e:
            print(f"✗ Ошибка загрузки database.py: {e}")
            raise

        try:
            from import_data import DataImporter
            print("✓ import_data.py загружен")
        except ImportError as e:
            print(f"✗ Ошибка загрузки import_data.py: {e}")
            raise

        try:
            from login_window import LoginWindow
            print("✓ login_window.py загружен")
        except ImportError as e:
            print(f"✗ Ошибка загрузки login_window.py: {e}")
            raise

        try:
            from main_window import MainWindow
            print("✓ main_window.py загружен")
        except ImportError as e:
            print(f"✗ Ошибка загрузки main_window.py: {e}")
            raise

        # --------- ИНИЦИАЛИЗАЦИЯ БД И ДАННЫХ ---------
        print("\n🔄 Инициализация базы данных...")
        db = Database()
        print("✓ БД подключена")

        print("📥 Импорт данных...")
        importer = DataImporter()
        importer.import_all_data()
        print("✓ Данные импортированы")

        print("\n✅ Система готова к работе!")
        print("=" * 60 + "\n")

        # --------- ГЛАВНЫЙ ЦИКЛ: АВТОРИЗАЦИЯ -> ГЛАВНОЕ ОКНО ---------
        while True:
            logged_in = {"ok": False, "user_data": None}

            # Колбэк, вызывается LoginWindow ТОЛЬКО при успешном входе
            def on_login_success(role, full_name, login):
                logged_in["ok"] = True
                logged_in["user_data"] = {
                    "user_id": None,
                    "role": role,  # 'Гость' / 'Клиент' / 'Менеджер' / 'Администратор'
                    "full_name": full_name,
                    "login": login,
                }

            print("🔐 Открытие окна авторизации...\n")
            login_window = LoginWindow(on_login_success)
            login_window.run()  # Ждём, пока окно логина закроется

            # Если окно логина закрыли крестиком — выходим из приложения
            if not logged_in["ok"]:
                break

            # Иначе запускаем главное окно.
            MainWindow(logged_in["user_data"])
            print("👋 Приложение закрыто пользователем.")

    except ImportError as e:
        print(f"\n❌ ОШИБКА ИМПОРТА: {e}")
        print("\n🔍 Диагностика:")
        print(f" Текущая папка: {os.path.dirname(os.path.abspath(__file__))}")
        print(f" Файлы в папке: {os.listdir(current_dir)[:10]}")
        print("\n💡 Проверьте, что все файлы .py находятся в одной папке с main.py")
        traceback.print_exc()
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
