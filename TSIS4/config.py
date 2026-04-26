import json
import os
from pathlib import Path

# --- Размеры экрана и сетки ---
WIDTH = 600
HEIGHT = 600
CELL = 30
GRID_W = WIDTH // CELL
GRID_H = HEIGHT // CELL

# --- Цвета (RGB) ---
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
BLACK = (0, 0, 0)

# Цвета объектов
RED = (255, 0, 0)          # Обычная еда
DARK_RED = (120, 0, 0)     # Ядовитая еда
GREEN = (0, 200, 0)        # Змейка / Еда +1
YELLOW = (255, 220, 0)     # Тело змейки
BLUE = (0, 100, 255)       # Speed Boost
PURPLE = (160, 0, 200)     # Slow Motion
ORANGE = (255, 140, 0)     # Shield

# --- Настройки (JSON) ---
SETTINGS_FILE = Path("settings.json")

DEFAULT_SETTINGS = {
    "snake_color": [0, 255, 0],  # По умолчанию зеленый
    "grid": True,
    "sound": True
}

def load_settings():
    """Загружает настройки из файла или создает стандартные."""
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            settings = json.load(file)
        
        # Проверка: если в файле не хватает каких-то ключей, добавляем их
        for key, value in DEFAULT_SETTINGS.items():
            if key not in settings:
                settings[key] = value
        return settings
    except (json.JSONDecodeError, Exception):
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Сохраняет текущие настройки в settings.json."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)

# --- Настройки игрового процесса ---
BASE_FPS = 8
FPS_STEP = 1  # На сколько увеличивается скорость с каждым уровнем
POWERUP_DURATION = 5000  # 5 секунд действия бонуса
POWERUP_LIFETIME = 8000  # 8 секунд бонус лежит на поле