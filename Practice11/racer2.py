import pygame
import random
import sys

# ──────────────────────────────────────────────
# КОНСТАНТЫ
# ──────────────────────────────────────────────
SCREEN_W, SCREEN_H = 480, 700   # Размер окна в пикселях
FPS               = 60          # Ограничение кадров в секунду

# Границы дороги (игровая зона)
ROAD_LEFT  = 80
ROAD_RIGHT = 400

# Цвета (R, G, B)
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GREY       = (80,  80,  80)
DARK_GREY  = (50,  50,  50)
YELLOW     = (255, 220, 0)
RED        = (220, 40,  40)
BLUE       = (30,  120, 255)
GREEN      = (50,  200, 80)
ORANGE     = (255, 160, 0)
SILVER     = (192, 192, 192)

# Настройки ускорения врагов
COINS_PER_SPEEDUP = 5          # Каждые 5 собранных монет → враги ускоряются
SPEEDUP_AMOUNT    = 0.5        # На сколько пикселей/кадр увеличивается скорость

# Определения типов монет: (метка, ценность_очков, цвет, шанс_появления)
# "weight" (шанс) управляет частотой появления (чем выше, тем чаще выпадает)
COIN_TYPES = [
    {"label": "БРОНЗА", "value": 1, "colour": (180, 100, 30), "weight": 60},
    {"label": "СЕРЕБРО", "value": 2, "colour": SILVER,         "weight": 30},
    {"label": "ЗОЛОТО",  "value": 3, "colour": YELLOW,         "weight": 10},
]

# ──────────────────────────────────────────────
# ПОМОЩНИК – взвешенный случайный выбор
# ──────────────────────────────────────────────
def weighted_choice(items):
    """Возвращает один элемент из списка, используя ключ 'weight' как вероятность."""
    total   = sum(i["weight"] for i in items)
    roll    = random.randint(1, total)
    running = 0
    for item in items:
        running += item["weight"]
        if roll <= running:
            return item
    return items[-1]  # запасной вариант

# ──────────────────────────────────────────────
# КЛАССЫ
# ──────────────────────────────────────────────

class PlayerCar:
    """Машина, которой управляет игрок."""
    WIDTH  = 40
    HEIGHT = 70

    def __init__(self):
        # Начальная позиция по центру дороги
        self.rect  = pygame.Rect(
            (ROAD_LEFT + ROAD_RIGHT) // 2 - self.WIDTH // 2,
            SCREEN_H - self.HEIGHT - 20,
            self.WIDTH, self.HEIGHT
        )
        self.colour = BLUE
        # Базовая скорость движения игрока
        self.speed  = 5

    def update(self, keys):
        """Перемещение влево/вправо при нажатии стрелок или WASD."""
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > ROAD_LEFT:
            self.rect.x -= int(self.speed)
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < ROAD_RIGHT:
            self.rect.x += int(self.speed)

    def draw(self, surface):
        """Отрисовка машины игрока."""
        pygame.draw.rect(surface, self.colour, self.rect, border_radius=6)
        # Лобовое стекло
        wshield = pygame.Rect(self.rect.x + 5, self.rect.y + 8, self.WIDTH - 10, 18)
        pygame.draw.rect(surface, (180, 220, 255), wshield, border_radius=3)
        # Колеса
        for wx, wy in [(self.rect.x - 5, self.rect.y + 8),
                       (self.rect.right - 5, self.rect.y + 8),
                       (self.rect.x - 5, self.rect.bottom - 22),
                       (self.rect.right - 5, self.rect.bottom - 22)]:
            pygame.draw.rect(surface, BLACK, (wx, wy, 10, 14), border_radius=3)


class EnemyCar:
    """Встречная машина врага, которая едет вниз."""
    WIDTH  = 40
    HEIGHT = 70

    def __init__(self, base_speed):
        # Случайный выбор полосы
        self.rect = pygame.Rect(
            random.randint(ROAD_LEFT, ROAD_RIGHT - self.WIDTH),
            -self.HEIGHT,
            self.WIDTH, self.HEIGHT
        )
        self.colour = random.choice([RED, GREEN, ORANGE, (150, 50, 200)])
        # Скорость немного варьируется для каждого врага для разнообразия
        self.speed  = base_speed + random.uniform(-0.3, 0.3)

    def update(self):
        """Движение врага вниз в каждом кадре."""
        self.rect.y += self.speed

    def is_off_screen(self):
        """Возвращает True, когда машина уехала за нижнюю границу экрана."""
        return self.rect.top > SCREEN_H

    def draw(self, surface):
        """Отрисовка вражеской машины."""
        pygame.draw.rect(surface, self.colour, self.rect, border_radius=6)
        wshield = pygame.Rect(self.rect.x + 5, self.rect.y + 8, self.WIDTH - 10, 18)
        pygame.draw.rect(surface, (255, 230, 180), wshield, border_radius=3)
        for wx, wy in [(self.rect.x - 5, self.rect.y + 8),
                       (self.rect.right - 5, self.rect.y + 8),
                       (self.rect.x - 5, self.rect.bottom - 22),
                       (self.rect.right - 5, self.rect.bottom - 22)]:
            pygame.draw.rect(surface, BLACK, (wx, wy, 10, 14), border_radius=3)


class Coin:
    """Монета, которую можно собрать (ценность зависит от веса)."""
    RADIUS = 12

    def __init__(self, speed):
        # Выбираем тип монеты на основе вероятности
        self.ctype  = weighted_choice(COIN_TYPES)
        self.colour = self.ctype["colour"]
        self.value  = self.ctype["value"]   # Сколько очков дает монета
        self.label  = self.ctype["label"]
        self.speed  = speed                 # Падает с той же скоростью, что и враги
        self.rect   = pygame.Rect(
            random.randint(ROAD_LEFT + self.RADIUS, ROAD_RIGHT - self.RADIUS),
            -self.RADIUS * 2,
            self.RADIUS * 2, self.RADIUS * 2
        )

    def update(self):
        """Движение монеты вниз."""
        self.rect.y += self.speed

    def is_off_screen(self):
        return self.rect.top > SCREEN_H

    def draw(self, surface):
        """Отрисовка монеты в виде круга с числом внутри."""
        cx = self.rect.centerx
        cy = self.rect.centery
        pygame.draw.circle(surface, self.colour, (cx, cy), self.RADIUS)
        pygame.draw.circle(surface, BLACK, (cx, cy), self.RADIUS, 2)
        # Отображаем номинал монеты в центре
        font_s = pygame.font.SysFont("arial", 11, bold=True)
        txt    = font_s.render(str(self.value), True, BLACK)
        surface.blit(txt, txt.get_rect(center=(cx, cy)))


class Road:
    """Прокручивающийся фон дороги."""
    STRIPE_W = 8
    STRIPE_H = 40
    GAP      = 30

    def __init__(self):
        self.offset = 0          # Смещение разметки по вертикали
        self.speed  = 4          # Скорость прокрутки

    def update(self):
        """Скроллинг разметки вниз."""
        self.offset = (self.offset + self.speed) % (self.STRIPE_H + self.GAP)

    def draw(self, surface):
        # Поверхность дороги
        pygame.draw.rect(surface, DARK_GREY, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_H))
        # Боковые линии
        pygame.draw.line(surface, YELLOW, (ROAD_LEFT, 0),  (ROAD_LEFT, SCREEN_H),  4)
        pygame.draw.line(surface, YELLOW, (ROAD_RIGHT, 0), (ROAD_RIGHT, SCREEN_H), 4)
        # Центральная пунктирная линия
        cx = (ROAD_LEFT + ROAD_RIGHT) // 2
        y  = -self.STRIPE_H + self.offset
        while y < SCREEN_H:
            pygame.draw.rect(surface, WHITE, (cx - self.STRIPE_W // 2, y, self.STRIPE_W, self.STRIPE_H))
            y += self.STRIPE_H + self.GAP


# ──────────────────────────────────────────────
# СОСТОЯНИЕ ИГРЫ
# ──────────────────────────────────────────────

class RacerGame:
    """Главный контроллер игры."""

    ENEMY_BASE_SPEED  = 3.0   # Начальная скорость врагов
    SPAWN_ENEMY_EVERY = 90    # Интервал появления врагов (в кадрах)
    SPAWN_COIN_EVERY  = 60    # Интервал появления монет (в кадрах)

    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Гонщик – Практика 11")
        self.clock   = pygame.time.Clock()
        self.font    = pygame.font.SysFont("arial", 22, bold=True)
        self.big_font= pygame.font.SysFont("arial", 48, bold=True)
        self.reset()

    def reset(self):
        """Сброс / инициализация игровых переменных."""
        self.player       = PlayerCar()
        self.road         = Road()
        self.enemies      = []
        self.coins        = []
        self.score        = 0             # Общие очки за монеты
        self.coins_total  = 0             # Общее количество собранных монет
        self.enemy_speed  = self.ENEMY_BASE_SPEED
        self.frame        = 0             # Счетчик кадров для спавна
        self.running      = True
        self.game_over    = False
        # Порог для следующего ускорения
        self.next_speedup = COINS_PER_SPEEDUP

    # ── Главный цикл ───────────────────────────

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self._handle_events()
            if not self.game_over:
                self._update()
            self._draw()
        pygame.quit()
        sys.exit()

    # ── Обработка событий ──────────────────────

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset()               # Рестарт на клавишу R
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    # ── Логика обновления ──────────────────────

    def _update(self):
        self.frame += 1
        keys = pygame.key.get_pressed()

        # Обновление дороги
        self.road.update()

        # Обновление игрока
        self.player.update(keys)

        # Создание врага через интервалы
        if self.frame % self.SPAWN_ENEMY_EVERY == 0:
            self.enemies.append(EnemyCar(self.enemy_speed))

        # Создание монеты через интервалы
        if self.frame % self.SPAWN_COIN_EVERY == 0:
            self.coins.append(Coin(self.enemy_speed))

        # Обновление врагов и проверка столкновений
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
            elif self.player.rect.colliderect(enemy.rect):
                # Столкновение → Конец игры
                self.game_over = True

        # Обновление монет и сбор
        for coin in self.coins[:]:
            coin.update()
            if coin.is_off_screen():
                self.coins.remove(coin)
            elif self.player.rect.colliderect(coin.rect):
                # Сбор монеты: добавляем её ценность к счету
                self.score       += coin.value
                self.coins_total += 1
                self.coins.remove(coin)

                # Проверка: пора ли увеличивать скорость?
                # Зависит от КОЛИЧЕСТВА монет, а не от суммы очков
                if self.coins_total >= self.next_speedup:
                    self.enemy_speed  += SPEEDUP_AMOUNT
                    # Дорога тоже ускоряется для ощущения скорости
                    self.road.speed   += SPEEDUP_AMOUNT
                    # Скорость игрока растет чуть-чуть для баланса
                    self.player.speed += 0.3
                    self.next_speedup += COINS_PER_SPEEDUP

    # ── Отрисовка ──────────────────────────────

    def _draw(self):
        # Фон (трава)
        self.screen.fill(GREEN)

        # Дорога и разметка
        self.road.draw(self.screen)

        # Рисуем все монеты
        for coin in self.coins:
            coin.draw(self.screen)

        # Рисуем всех врагов
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Игрок поверх всего
        self.player.draw(self.screen)

        # ── Интерфейс (HUD) ──
        self._draw_hud()

        # ── Экран окончания игры ──
        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_hud(self):
        """Отрисовка счета, количества монет и скоростей."""
        # Полупрозрачный фон для интерфейса
        hud = pygame.Surface((230, 100), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 140))
        self.screen.blit(hud, (5, 5))

        # Текстовые данные
        coins_txt = self.font.render(f"Монеты: {self.coins_total}  →  {self.next_speedup}", True, SILVER)
        score_txt = self.font.render(f"Счет  : {self.score}", True, YELLOW)
        espd_txt  = self.font.render(f"Враги : {self.enemy_speed:.1f} пк/к", True, (255, 100, 100))
        pspd_txt  = self.font.render(f"Игрок : {self.player.speed:.1f} пк/к", True, (100, 200, 255))

        self.screen.blit(coins_txt, (10, 8))
        self.screen.blit(score_txt, (10, 30))
        self.screen.blit(espd_txt,  (10, 52))
        self.screen.blit(pspd_txt,  (10, 74))

        # Легенда типов монет (снизу справа)
        lx, ly = SCREEN_W - 150, SCREEN_H - 80
        for ct in COIN_TYPES:
            pygame.draw.circle(self.screen, ct["colour"], (lx + 10, ly + 8), 8)
            pygame.draw.circle(self.screen, BLACK,         (lx + 10, ly + 8), 8, 1)
            lbl = self.font.render(f"{ct['label']} +{ct['value']}", True, ct["colour"])
            self.screen.blit(lbl, (lx + 24, ly))
            ly += 24

    def _draw_game_over(self):
        """Затемнение экрана и надпись GAME OVER."""
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        go_txt   = self.big_font.render("ИГРА ОКОНЧЕНА", True, RED)
        sc_txt   = self.font.render(f"Финальный счет: {self.score}", True, YELLOW)
        rest_txt = self.font.render("Нажми  R  для рестарта  |  ESC для выхода", True, WHITE)

        self.screen.blit(go_txt,   go_txt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 50)))
        self.screen.blit(sc_txt,   sc_txt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 10)))
        self.screen.blit(rest_txt, rest_txt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 50)))


# ──────────────────────────────────────────────
# ТОЧКА ВХОДА
# ──────────────────────────────────────────────
if __name__ == "__main__":
    game = RacerGame()
    game.run()