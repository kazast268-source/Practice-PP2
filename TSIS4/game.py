import pygame
import random
from config import *
from db import get_or_create_player, save_result, get_personal_best

# --- Вспомогательные классы и функции ---

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

def get_random_point(snake_body, obstacles, extra_points=None):
    """Генерирует точку, которая не занята змейкой, стенами или другими объектами."""
    if extra_points is None: extra_points = []
    while True:
        p = Point(random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1))
        if p not in snake_body and p not in obstacles and p not in extra_points:
            return p

class Snake:
    def __init__(self, color):
        self.body = [Point(10, 10), Point(9, 10), Point(8, 10)]
        self.direction = (1, 0)
        self.color = color
        self.score = 0
        self.level = 1
        self.shield = False

    def move(self):
        head = self.body[0]
        new_head = Point(head.x + self.direction[0], head.y + self.direction[1])
        self.body.insert(0, new_head)
        self.body.pop()

    def grow(self):
        self.body.append(Point(self.body[-1].x, self.body[-1].y))

    def shrink(self):
        """Уменьшает змейку на 2 сегмента (эффект яда)."""
        for _ in range(2):
            if len(self.body) > 1:
                self.body.pop()
        return len(self.body) <= 1  # Возвращает True, если змейка стала слишком короткой (смерть)

# --- Основная функция игры ---

def run_game(screen, username, settings):
    # Инициализация данных игрока из БД
    player_id = get_or_create_player(username)
    personal_best = get_personal_best(player_id)
    
    snake = Snake(tuple(settings["snake_color"]))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Verdana", 20)

    # Объекты на поле
    obstacles = []
    food = get_random_point(snake.body, obstacles)
    poison = get_random_point(snake.body, obstacles, [food])
    
    # Power-up система
    powerup_pos = None
    powerup_type = None
    powerup_spawn_time = 0
    active_effect = None
    effect_end_time = 0

    running = True
    while running:
        now = pygame.time.get_ticks()

        # 1. Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != (0, 1): snake.direction = (0, -1)
                if event.key == pygame.K_DOWN and snake.direction != (0, -1): snake.direction = (0, 1)
                if event.key == pygame.K_LEFT and snake.direction != (1, 0): snake.direction = (-1, 0)
                if event.key == pygame.K_RIGHT and snake.direction != (-1, 0): snake.direction = (1, 0)

        # 2. Логика скорости (зависит от уровня и бонусов)
        current_fps = BASE_FPS + (snake.level * FPS_STEP)
        if active_effect == "speed": current_fps += 7
        elif active_effect == "slow": current_fps = max(4, current_fps - 5)
        
        if now > effect_end_time: active_effect = None

        # 3. Движение
        snake.move()
        head = snake.body[0]

        # 4. Проверка столкновений (Стены, хвост, препятствия)
        collision = (head.x < 0 or head.x >= GRID_W or 
                     head.y < 0 or head.y >= GRID_H or 
                     head in snake.body[1:] or 
                     head in obstacles)

        if collision:
            if snake.shield:
                snake.shield = False  # Щит спасает один раз
                # Возвращаем змейку в центр, чтобы не застрять в стене
                head.x, head.y = GRID_W // 2, GRID_H // 2
            else:
                save_result(player_id, snake.score, snake.level)
                return "game_over", {"score": snake.score, "level": snake.level, "best": max(snake.score, personal_best)}

        # 5. Взаимодействие с едой
        if head == food:
            snake.score += 10
            snake.grow()
            # Повышение уровня каждые 40 очков
            new_level = (snake.score // 40) + 1
            if new_level > snake.level:
                snake.level = new_level
                if snake.level >= 3: # Добавляем новые препятствия
                    obstacles.append(get_random_point(snake.body, obstacles, [food, poison]))
            
            food = get_random_point(snake.body, obstacles, [poison])

        # 6. Взаимодействие с ядом
        if head == poison:
            if snake.shrink(): # Если стала слишком короткой
                save_result(player_id, snake.score, snake.level)
                return "game_over", {"score": snake.score, "level": snake.level, "best": max(snake.score, personal_best)}
            poison = get_random_point(snake.body, obstacles, [food])

        # 7. Логика бонусов (Power-ups)
        # Спавн бонуса раз в некоторое время, если его нет на поле
        if not powerup_pos and now % 7000 < 100:
            powerup_pos = get_random_point(snake.body, obstacles, [food, poison])
            powerup_type = random.choice(["speed", "slow", "shield"])
            powerup_spawn_time = now

        if powerup_pos:
            # Исчезает через 8 секунд
            if now - powerup_spawn_time > POWERUP_LIFETIME:
                powerup_pos = None
            elif head == powerup_pos:
                if powerup_type == "shield":
                    snake.shield = True
                else:
                    active_effect = powerup_type
                    effect_end_time = now + POWERUP_DURATION
                powerup_pos = None

        # 8. Отрисовка
        screen.fill(BLACK)
        
        if settings.get("grid", True):
            for x in range(0, WIDTH, CELL): pygame.draw.line(screen, DARK_GRAY, (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, CELL): pygame.draw.line(screen, DARK_GRAY, (0, y), (WIDTH, y))

        # Препятствия
        for obs in obstacles:
            pygame.draw.rect(screen, GRAY, (obs.x * CELL, obs.y * CELL, CELL, CELL))

        # Еда и Яд
        pygame.draw.rect(screen, RED, (food.x * CELL, food.y * CELL, CELL, CELL))
        pygame.draw.rect(screen, DARK_RED, (poison.x * CELL, poison.y * CELL, CELL, CELL))

        # Змейка
        for i, part in enumerate(snake.body):
            color = WHITE if i == 0 else snake.color
            pygame.draw.rect(screen, color, (part.x * CELL, part.y * CELL, CELL - 1, CELL - 1))

        # Бонус
        if powerup_pos:
            p_color = BLUE if powerup_type == "speed" else PURPLE if powerup_type == "slow" else ORANGE
            pygame.draw.circle(screen, p_color, (powerup_pos.x * CELL + CELL//2, powerup_pos.y * CELL + CELL//2), CELL//3)

        # Интерфейс (HUD)
        score_txt = font.render(f"Score: {snake.score}  Lvl: {snake.level}", True, WHITE)
        screen.blit(score_txt, (10, 10))
        if snake.shield:
            pygame.draw.circle(screen, ORANGE, (WIDTH - 20, 20), 10)

        pygame.display.flip()
        clock.tick(current_fps)