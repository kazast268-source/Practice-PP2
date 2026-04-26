"""
Практика 11 – Игра 2: Змейка (Snake)
Дополнения из Практики 8:
  1. Случайная генерация еды с разным весом (ценностью)
  2. Еда, которая исчезает по таймеру
  3. Подробные комментарии по всему коду
"""

import pygame
import random
import sys

# ──────────────────────────────────────────────
# КОНСТАНТЫ
# ──────────────────────────────────────────────
CELL        = 20           # Размер одной ячейки сетки в пикселях
COLS        = 30           # Количество колонок в сетке
ROWS        = 28           # Количество строк (игровая зона)
SCREEN_W    = COLS * CELL  # 600
SCREEN_H    = ROWS * CELL + 50  # +50 для панели HUD сверху
HUD_H       = 50           # Высота панели счета сверху
FPS         = 10           # Змейка перемещается столько раз в секунду

# Векторы направления
UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)

# Цвета (R, G, B)
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
BG          = (30,  30,  30)    # Фон сетки
GRID_LINE   = (45,  45,  45)    # Ненавязчивые линии сетки
SNAKE_HEAD  = (0,   210, 80)    # Ярко-зеленая голова
SNAKE_BODY  = (0,   160, 60)    # Темно-зеленое тело
SNAKE_EYE   = (255, 255, 255)
RED         = (220, 50,  50)
YELLOW      = (255, 220, 0)
ORANGE      = (255, 140, 0)
PURPLE      = (180, 60,  200)
SILVER      = (192, 192, 192)

# ──────────────────────────────────────────────
# ТИПЫ ЕДЫ
# Каждая запись: название, ценность, цвет, шанс появления, время жизни (кадры)
# Меньшее время жизни → еда исчезает быстрее
# ──────────────────────────────────────────────
FOOD_TYPES = [
    {"label": "Яблоко",   "value": 1, "colour": RED,    "weight": 50, "lifetime": None },  # Бессмертное
    {"label": "Апельсин", "value": 2, "colour": ORANGE, "weight": 30, "lifetime": 50   },  # ~5 сек при FPS 10
    {"label": "Виноград", "value": 3, "colour": PURPLE, "weight": 15, "lifetime": 30   },  # ~3 сек
    {"label": "Звезда",   "value": 5, "colour": YELLOW, "weight": 5,  "lifetime": 20   },  # ~2 сек (редкая!)
]

MAX_FOOD_ON_SCREEN = 4    # Максимальное кол-во еды на экране одновременно

# ──────────────────────────────────────────────
# ПОМОЩНИК – взвешенный случайный выбор
# ──────────────────────────────────────────────
def weighted_choice(items):
    """Выбирает элемент из списка пропорционально его 'весу' (шансу)."""
    total   = sum(i["weight"] for i in items)
    roll    = random.randint(1, total)
    running = 0
    for item in items:
        running += item["weight"]
        if roll <= running:
            return item
    return items[-1]

# ──────────────────────────────────────────────
# КЛАССЫ
# ──────────────────────────────────────────────

class Food:
    """Объект еды с ценностью и опциональным таймером исчезновения."""

    def __init__(self, occupied_cells):
        """
        Создание еды в случайной свободной ячейке.
        `occupied_cells` – занятые координаты (голова, тело, другая еда).
        """
        # Выбираем тип еды через взвешенный рандом
        ftype         = weighted_choice(FOOD_TYPES)
        self.label    = ftype["label"]
        self.value    = ftype["value"]
        self.colour   = ftype["colour"]
        self.lifetime = ftype["lifetime"]   # None = бессмертная
        self.age      = 0                   # сколько кадров еда уже лежит

        # Ищем свободную ячейку
        all_cells = {(c, r) for c in range(COLS) for r in range(ROWS)}
        free_cells = list(all_cells - occupied_cells)
        self.pos  = random.choice(free_cells) if free_cells else (COLS // 2, ROWS // 2)

    def update(self):
        """Увеличивает возраст. Возвращает True, если время жизни истекло."""
        if self.lifetime is not None:
            self.age += 1
            return self.age >= self.lifetime
        return False

    def time_fraction(self):
        """Возвращает долю оставшегося времени (1.0 = свежая, 0.0 = вот-вот исчезнет)."""
        if self.lifetime is None:
            return None
        return max(0.0, 1.0 - self.age / self.lifetime)

    def draw(self, surface):
        """Отрисовка еды в виде круга; исчезающая еда мерцает/тускнеет."""
        col, row = self.pos
        px = col * CELL + CELL // 2
        py = row * CELL + CELL // 2 + HUD_H

        # Эффект прозрачности для временной еды
        fraction = self.time_fraction()
        if fraction is not None:
            surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
            alpha = int(80 + 175 * fraction)   # затухание от 255 до 80
            r, g, b = self.colour
            pygame.draw.circle(surf, (r, g, b, alpha), (CELL // 2, CELL // 2), CELL // 2 - 2)
            surface.blit(surf, (col * CELL, row * CELL + HUD_H))
            # Рисуем кольцо таймера вокруг временной еды
            pygame.draw.circle(surface, (*WHITE, alpha), (px, py), CELL // 2 - 1, 2)
        else:
            pygame.draw.circle(surface, self.colour, (px, py), CELL // 2 - 2)

        # Пишем ценность еды внутри круга
        font_s = pygame.font.SysFont("arial", 11, bold=True)
        txt    = font_s.render(str(self.value), True, WHITE if self.colour != YELLOW else BLACK)
        surface.blit(txt, txt.get_rect(center=(px, py)))


class Snake:
    """Класс змейки, управляемой игроком."""

    def __init__(self):
        # Начало в центре, длина 3 сегмента, направление ВПРАВО
        mid_col, mid_row = COLS // 2, ROWS // 2
        self.body      = [(mid_col - i, mid_row) for i in range(3)] 
        self.direction = RIGHT
        self.grew      = False   # Флаг: True, если змейка только что съела еду

    def change_direction(self, new_dir):
        """Меняет направление, если оно не противоположно текущему."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def move(self):
        """Продвигает змейку на одну ячейку."""
        head       = self.body[0]
        new_head   = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)   # добавляем новую голову
        if not self.grew:
            self.body.pop()             # удаляем хвост, если ничего не съели
        else:
            self.grew = False           # сбрасываем флаг роста

    def head(self):
        return self.body[0]

    def is_dead(self):
        """Проверка столкновения со стеной или самим собой."""
        hx, hy = self.head()
        if not (0 <= hx < COLS and 0 <= hy < ROWS):
            return True
        if self.head() in self.body[1:]:
            return True
        return False

    def occupied_cells(self):
        """Возвращает множество координат, занятых телом змейки."""
        return set(self.body)

    def draw(self, surface):
        """Отрисовка всех сегментов; у головы есть глаза."""
        for i, (col, row) in enumerate(self.body):
            px = col * CELL
            py = row * CELL + HUD_H
            colour = SNAKE_HEAD if i == 0 else SNAKE_BODY
            pygame.draw.rect(surface, colour, (px + 1, py + 1, CELL - 2, CELL - 2), border_radius=4)

        # Отрисовка глаз
        hx, hy = self.body[0]
        cx = hx * CELL + CELL // 2
        cy = hy * CELL + CELL // 2 + HUD_H
        dx, dy = self.direction
        perp = (-dy, dx) # перпендикуляр для смещения глаз
        for side in (+1, -1):
            ex = cx + dx * 4 + perp[0] * side * 4
            ey = cy + dy * 4 + perp[1] * side * 4
            pygame.draw.circle(surface, SNAKE_EYE, (ex, ey), 3)
            pygame.draw.circle(surface, BLACK,     (ex + dx, ey + dy), 1)


# ──────────────────────────────────────────────
# СОСТОЯНИЕ ИГРЫ
# ──────────────────────────────────────────────

class SnakeGame:
    """Главный контроллер игры Змейка."""

    FOOD_SPAWN_INTERVAL = 25   # Каждые N кадров пытаемся создать новую еду

    def __init__(self):
        pygame.init()
        self.screen   = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Змейка – Практика 11")
        self.clock    = pygame.time.Clock()
        self.font     = pygame.font.SysFont("arial", 22, bold=True)
        self.big_font = pygame.font.SysFont("arial", 48, bold=True)
        self.small_font = pygame.font.SysFont("arial", 13)
        self.reset()

    def reset(self):
        """Инициализация новой игры."""
        self.snake     = Snake()
        self.foods     = []          # Список объектов еды
        self.score     = 0
        self.frame     = 0
        self.game_over = False
        self.running   = True
        self._try_spawn_food()

    # ── Главный цикл ──────────────────────────────

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self._handle_events()
            if not self.game_over:
                self._update()
            self._draw()
        pygame.quit()
        sys.exit()

    # ── События ─────────────────────────────────

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if   event.key in (pygame.K_UP,    pygame.K_w): self.snake.change_direction(UP)
                elif event.key in (pygame.K_DOWN,  pygame.K_s): self.snake.change_direction(DOWN)
                elif event.key in (pygame.K_LEFT,  pygame.K_a): self.snake.change_direction(LEFT)
                elif event.key in (pygame.K_RIGHT, pygame.K_d): self.snake.change_direction(RIGHT)
                elif event.key == pygame.K_r and self.game_over: self.reset()
                elif event.key == pygame.K_ESCAPE: self.running = False

    # ── Обновление ─────────────────────────────────

    def _update(self):
        self.frame += 1
        self.snake.move()

        if self.snake.is_dead():
            self.game_over = True
            return

        # Проверка: съела ли голова еду
        head = self.snake.head()
        for food in self.foods[:]:
            if food.pos == head:
                self.score     += food.value   # Добавляем очки за вес еды
                self.snake.grew = True         # Змейка вырастет на след. шаге
                self.foods.remove(food)

        # Обновление таймеров еды
        for food in self.foods[:]:
            expired = food.update()
            if expired:
                self.foods.remove(food)

        # Периодически создаем новую еду
        if self.frame % self.FOOD_SPAWN_INTERVAL == 0:
            self._try_spawn_food()

    def _try_spawn_food(self):
        """Создает еду, если не превышен лимит."""
        if len(self.foods) < MAX_FOOD_ON_SCREEN:
            occupied = self.snake.occupied_cells() | {f.pos for f in self.foods}
            self.foods.append(Food(occupied))

    # ── Отрисовка ───────────────────────────────────

    def _draw(self):
        self.screen.fill(BG)

        # Рисуем сетку
        for c in range(COLS):
            for r in range(ROWS):
                pygame.draw.rect(self.screen, GRID_LINE,
                                 (c * CELL, r * CELL + HUD_H, CELL, CELL), 1)

        for food in self.foods:
            food.draw(self.screen)

        self.snake.draw(self.screen)
        self._draw_hud()
        self._draw_legend()

        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_hud(self):
        """Верхняя панель: счет и длина."""
        pygame.draw.rect(self.screen, (20, 20, 20), (0, 0, SCREEN_W, HUD_H))
        pygame.draw.line(self.screen, YELLOW, (0, HUD_H), (SCREEN_W, HUD_H), 2)

        score_txt  = self.font.render(f"Счет: {self.score}", True, YELLOW)
        length_txt = self.font.render(f"Длина: {len(self.snake.body)}", True, WHITE)
        ctrl_txt   = self.small_font.render("Стрелки/WASD = ход  |  R = рестарт  |  ESC = выход", True, SILVER)

        self.screen.blit(score_txt,  (10, 12))
        self.screen.blit(length_txt, (200, 12))
        self.screen.blit(ctrl_txt,   (10, HUD_H - 16))

    def _draw_legend(self):
        """Легенда типов еды в правой части HUD."""
        x = SCREEN_W - 195
        pygame.draw.rect(self.screen, (20, 20, 20), (x - 5, 0, 200, HUD_H - 18))
        for i, ft in enumerate(FOOD_TYPES):
            lx = x + (i % 2) * 95
            ly = 6 + (i // 2) * 18
            pygame.draw.circle(self.screen, ft["colour"], (lx + 7, ly + 7), 7)
            label = f"{ft['label']} +{ft['value']}"
            if ft["lifetime"]:
                label += f" ({ft['lifetime']}к)"
            txt = self.small_font.render(label, True, ft["colour"])
            self.screen.blit(txt, (lx + 18, ly))

    def _draw_game_over(self):
        """Экран окончания игры."""
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        go   = self.big_font.render("ИГРА ОКОНЧЕНА", True, RED)
        sc   = self.font.render(f"Счет: {self.score}  |  Длина: {len(self.snake.body)}", True, YELLOW)
        rst  = self.font.render("Нажми  R  для рестарта  |  ESC для выхода", True, WHITE)

        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        self.screen.blit(go,  go.get_rect(center=(cx, cy - 50)))
        self.screen.blit(sc,  sc.get_rect(center=(cx, cy + 10)))
        self.screen.blit(rst, rst.get_rect(center=(cx, cy + 50)))

# ──────────────────────────────────────────────
# ТОЧКА ВХОДА
# ──────────────────────────────────────────────
if __name__ == "__main__":
    game = SnakeGame()
    game.run()