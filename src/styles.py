import tkinter as tk
from tkinter import ttk
from config import Config


class Styles:
    @staticmethod
    def configure_styles():
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except Exception:
            pass

        bg_primary = Config.COLORS["primary_bg"]
        bg_secondary = Config.COLORS["secondary_bg"]
        text_primary = Config.COLORS["text_primary"]
        text_secondary = Config.COLORS["text_secondary"]
        primary_color = Config.COLORS["primary_color"]
        border_color = Config.COLORS["border_color"]

        # FRAME STYLES
        style.configure(
            "TFrame",
            background=bg_primary,
            relief=tk.FLAT,
        )
        style.configure(
            "Card.TFrame",
            background=bg_primary,
            relief=tk.RAISED,
            borderwidth=1,
        )

        # LABEL STYLES
        style.configure(
            "TLabel",
            background=bg_primary,
            foreground=text_primary,
            font=Config.FONT_DEFAULT,
        )
        style.configure(
            "Title.TLabel",
            font=Config.FONT_TITLE,
            background=bg_primary,
            foreground=text_primary,
        )
        style.configure(
            "Header.TLabel",
            font=Config.FONT_HEADER,
            background=bg_primary,
            foreground=text_primary,
        )
        style.configure(
            "Info.TLabel",
            font=Config.FONT_SMALL,
            background=bg_secondary,
            foreground=text_secondary,
        )
        style.configure(
            "ShopTitle.TLabel",
            font=Config.FONT_TITLE,
            background=primary_color,
            foreground="#FFFFFF",
        )

        # BUTTON STYLES
        style.configure(
            "TButton",
            font=Config.FONT_BUTTON,
            padding=8,
        )
        style.map(
            "TButton",
            foreground=[("pressed", text_primary), ("active", text_primary)],
            background=[("pressed", "#1f6b3d"), ("active", "#3fa86f")],
        )

        # Основная кнопка (зелёная, как в ТЗ - 2E8B57)
        style.configure(
            "Accent.TButton",
            font=Config.FONT_BUTTON,
            foreground="#FFFFFF",
            background=primary_color,
            padding=8,
        )
        style.map(
            "Accent.TButton",
            foreground=[("pressed", "#FFFFFF"), ("active", "#FFFFFF")],
            background=[("pressed", "#1f6b3d"), ("active", primary_color)],
        )

        # Вторая кнопка - ОДНОГО ЦВЕТА с Accent.TButton
        style.configure(
            "Secondary.TButton",
            font=Config.FONT_BUTTON,
            foreground="#FFFFFF",
            background=primary_color,
            padding=8,
        )
        style.map(
            "Secondary.TButton",
            foreground=[("pressed", "#FFFFFF"), ("active", "#FFFFFF")],
            background=[("pressed", "#1f6b3d"), ("active", primary_color)],
        )

        # ENTRY STYLES
        style.configure(
            "TEntry",
            font=Config.FONT_INPUT,
            padding=5,
        )

        # COMBOBOX STYLES
        style.configure(
            "TCombobox",
            font=Config.FONT_INPUT,
            padding=5,
        )

        # TREEVIEW STYLES
        style.configure(
            "Treeview",
            font=Config.FONT_DEFAULT,
            rowheight=25,
            background=bg_primary,
            foreground=text_primary,
            fieldbackground=bg_primary,
            borderwidth=1,
        )
        style.configure(
            "Treeview.Heading",
            font=Config.FONT_HEADER,
            background=bg_secondary,
            foreground=text_primary,
            borderwidth=1,
        )
        style.map(
            "Treeview",
            background=[("selected", primary_color)],
            foreground=[("selected", "#FFFFFF")],
        )

        # LABELFRAME STYLES
        style.configure(
            "TLabelframe",
            background=bg_primary,
            foreground=text_primary,
            font=Config.FONT_HEADER,
            bordercolor=border_color,
            relief=tk.GROOVE,
            borderwidth=2,
        )
        style.configure(
            "TLabelframe.Label",
            background=bg_primary,
            foreground=text_primary,
            font=Config.FONT_HEADER,
        )

        # SEPARATOR STYLES
        style.configure(
            "TSeparator",
            background=border_color,
        )

        # SCROLLBAR STYLES
        style.configure(
            "TScrollbar",
            background=primary_color,
        )
