import pygame
import random
import sys
import json
import os

# ──────────────────────────────────────────────
# КОНСТАНТЫ
# ──────────────────────────────────────────────
SCREEN_W, SCREEN_H = 480, 750
FPS = 60
ROAD_LEFT, ROAD_RIGHT = 80, 400

WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (50, 50, 50)
RED, YELLOW, BLUE = (220, 50, 50), (255, 215, 0), (30, 120, 255)
GREEN, PURPLE, CYAN = (50, 200, 80), (160, 32, 240), (0, 255, 255)
BRONZE, SILVER, GOLD = (205, 127, 50), (192, 192, 192), (255, 215, 0)
DARK_GRAY = (30, 30, 30)

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

# ──────────────────────────────────────────────
# ГРАФИКА СПРАЙТОВ
# ──────────────────────────────────────────────

def draw_car_sprite(color, is_player=False):
    surf = pygame.Surface((40, 70), pygame.SRCALPHA)
    for x, y in [(2, 10), (33, 10), (2, 50), (33, 50)]:
        pygame.draw.rect(surf, (20, 20, 20), (x, y, 5, 12), border_radius=2)
    pygame.draw.rect(surf, color, (5, 5, 30, 60), border_radius=8)
    pygame.draw.rect(surf, (100, 150, 255), (8, 20, 24, 15), border_radius=4)
    f_col = CYAN if is_player else WHITE
    pygame.draw.rect(surf, f_col, (7, 5, 8, 4), border_radius=2)
    pygame.draw.rect(surf, f_col, (25, 5, 8, 4), border_radius=2)
    return surf

def draw_coin_sprite(color):
    surf = pygame.Surface((26, 26), pygame.SRCALPHA)
    pygame.draw.circle(surf, (40, 40, 40), (13, 13), 12)
    pygame.draw.circle(surf, color, (13, 13), 10)
    pygame.draw.circle(surf, WHITE, (9, 9), 3)
    return surf

def draw_powerup_sprite(p_type):
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    if p_type == 'nitro': 
        pygame.draw.polygon(surf, YELLOW, [(15, 2), (28, 28), (15, 20), (2, 28)])
    elif p_type == 'shield': 
        pygame.draw.circle(surf, CYAN, (15, 15), 13, 2)
        pygame.draw.rect(surf, CYAN, (11, 11, 8, 8))
    else: # repair
        pygame.draw.rect(surf, GREEN, (13, 5, 4, 20))
        pygame.draw.rect(surf, GREEN, (5, 13, 20, 4))
    return surf

# ──────────────────────────────────────────────
# КЛАССЫ ОБЪЕКТОВ
# ──────────────────────────────────────────────

class Player(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()
        self.color = color
        self.image = draw_car_sprite(self.color, True)
        self.rect = self.image.get_rect(center=(SCREEN_W//2, SCREEN_H-120))
        self.nitro_timer = 0
        self.shield_active = False

    def update(self, keys):
        spd = 12 if self.nitro_timer > 0 else 7
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > ROAD_LEFT:
            self.rect.x -= spd
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < ROAD_RIGHT:
            self.rect.x += spd
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 100:
            self.rect.y -= 4
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < SCREEN_H - 20:
            self.rect.y += 4

        if self.nitro_timer > 0: self.nitro_timer -= 1
        self.image = draw_car_sprite(self.color, True)
        if self.shield_active:
            pygame.draw.circle(self.image, CYAN, (20, 35), 36, 2)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = draw_car_sprite(random.choice([RED, PURPLE, (255, 120, 0)]))
        self.rect = self.image.get_rect(midbottom=(random.randint(ROAD_LEFT+25, ROAD_RIGHT-25), -50))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H: self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        r = random.random()
        if r < 0.7: self.val, col = 1, BRONZE
        elif r < 0.9: self.val, col = 5, SILVER
        else: self.val, col = 10, GOLD
        self.image = draw_coin_sprite(col)
        self.rect = self.image.get_rect(center=(random.randint(ROAD_LEFT+20, ROAD_RIGHT-20), -30))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H: self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.type = random.choice(['nitro', 'shield', 'repair'])
        self.image = draw_powerup_sprite(self.type)
        self.rect = self.image.get_rect(center=(random.randint(ROAD_LEFT+20, ROAD_RIGHT-20), -50))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H: self.kill()

# ──────────────────────────────────────────────
# ОСНОВНОЙ ДВИЖОК
# ──────────────────────────────────────────────

class RacerGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Racer Pro: TSIS 3")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 18, bold=True)
        self.big_font = pygame.font.SysFont("Verdana", 36, bold=True)
        self.load_settings()
        self.load_leaderboard()
        self.player_name = ""
        self.state = "MENU"

    def load_settings(self):
        self.settings = {"color": "BLUE", "sound": True, "diff": 1}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f: self.settings.update(json.load(f))
            except: pass

    def load_leaderboard(self):
        self.leaderboard = []
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, "r") as f: self.leaderboard = json.load(f)
            except: pass

    def save_all(self):
        with open(SETTINGS_FILE, "w") as f: json.dump(self.settings, f, indent=4)
        with open(LEADERBOARD_FILE, "w") as f: json.dump(self.leaderboard, f, indent=4)

    def draw_text(self, text, pos, color=WHITE, center=True, font=None):
        f = font if font else self.font
        surf = f.render(text, True, color)
        rect = surf.get_rect(center=pos) if center else surf.get_rect(topleft=pos)
        self.screen.blit(surf, rect)

    def play_game(self):
        color_map = {"BLUE": BLUE, "GREEN": GREEN, "PURPLE": PURPLE}
        player = Player(color_map.get(self.settings["color"], BLUE))
        enemies, coins, powerups = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
        
        coin_total, coin_step, next_level = 0, 0, 10
        distance, road_speed, frame = 0, 5 + self.settings["diff"], 0

        while self.state == "GAME":
            self.screen.fill((30, 100, 30)) 
            pygame.draw.rect(self.screen, GRAY, (ROAD_LEFT, 0, ROAD_RIGHT-ROAD_LEFT, SCREEN_H))
            
            for y in range(-100, SCREEN_H, 100):
                pygame.draw.rect(self.screen, WHITE, (SCREEN_W//2-4, (y + frame*road_speed)%SCREEN_H, 8, 50))
            
            frame += 1; distance += 1
            if frame % 70 == 0: enemies.add(Enemy(road_speed + random.randint(1, 3)))
            if frame % 110 == 0: coins.add(Coin(road_speed))
            if frame % 500 == 0: powerups.add(PowerUp(road_speed))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            keys = pygame.key.get_pressed()
            player.update(keys)
            enemies.update(); coins.update(); powerups.update()

            # Коллизии
            if pygame.sprite.spritecollide(player, enemies, not player.shield_active):
                if player.shield_active:
                    player.shield_active = False
                    pygame.sprite.spritecollide(player, enemies, True)
                else: self.state = "GAMEOVER"

            for c in pygame.sprite.spritecollide(player, coins, True):
                coin_total += c.val
                coin_step += c.val
                if coin_step >= next_level:
                    road_speed += 0.8
                    coin_step = 0

            for p in pygame.sprite.spritecollide(player, powerups, True):
                if p.type == 'nitro': player.nitro_timer = 200
                elif p.type == 'shield': player.shield_active = True
                elif p.type == 'repair': coin_total += 15

            # Отрисовка
            coins.draw(self.screen); powerups.draw(self.screen); enemies.draw(self.screen)
            self.screen.blit(player.image, player.rect)
            
            # HUD
            pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_W, 55))
            self.draw_text(f"ID: {self.player_name}", (10, 5), WHITE, False)
            self.draw_text(f"SCORE: {distance//10}", (SCREEN_W//2, 15), CYAN)
            self.draw_text(f"COINS: {coin_total}", (SCREEN_W-10, 5), YELLOW, False)
            
            # Прогресс бар
            pygame.draw.rect(self.screen, DARK_GRAY, (SCREEN_W-110, 32, 100, 10))
            prog = min(100, (coin_step / next_level) * 100)
            pygame.draw.rect(self.screen, YELLOW, (SCREEN_W-110, 32, prog, 10))

            pygame.display.flip()
            self.clock.tick(FPS)

        self.leaderboard.append({"name": self.player_name, "score": distance//10 + coin_total})
        self.leaderboard = sorted(self.leaderboard, key=lambda x: x['score'], reverse=True)[:10]
        self.save_all()

    def name_input(self):
        while self.state == "NAME":
            self.screen.fill(BLACK)
            self.draw_text("IDENTIFY YOURSELF:", (SCREEN_W//2, 300), YELLOW)
            self.draw_text(self.player_name + "_", (SCREEN_W//2, 360), WHITE, font=self.big_font)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN and self.player_name: self.state = "GAME"
                    elif e.key == pygame.K_BACKSPACE: self.player_name = self.player_name[:-1]
                    elif len(self.player_name) < 10: self.player_name += e.unicode

    def run(self):
        while True:
            if self.state == "MENU":
                self.screen.fill(GRAY)
                self.draw_text("RACER ADVANCED", (SCREEN_W//2, 200), YELLOW, font=self.big_font)
                self.draw_text("1. PLAY", (SCREEN_W//2, 350))
                self.draw_text("2. SETTINGS", (SCREEN_W//2, 410))
                self.draw_text("3. LEADERBOARD", (SCREEN_W//2, 470))
                pygame.display.flip()
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_1: self.state = "NAME"
                        if e.key == pygame.K_2: self.state = "SET"
                        if e.key == pygame.K_3: self.state = "LEADS"
            elif self.state == "NAME": self.name_input()
            elif self.state == "GAME": self.play_game()
            elif self.state == "GAMEOVER":
                self.screen.fill(RED)
                self.draw_text("WASTED", (SCREEN_W//2, 350), WHITE, font=self.big_font)
                self.draw_text("SPACE TO MENU", (SCREEN_W//2, 450), BLACK)
                pygame.display.flip()
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE: self.state = "MENU"
            elif self.state == "SET":
                self.screen.fill(GRAY)
                self.draw_text("GARAGE", (SCREEN_W//2, 100), WHITE, font=self.big_font)
                self.draw_text(f"COLOR: {self.settings['color']} (C)", (SCREEN_W//2, 300))
                self.draw_text("ESC TO BACK", (SCREEN_W//2, 500), YELLOW)
                pygame.display.flip()
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_c:
                            opts = ["BLUE", "GREEN", "PURPLE"]
                            self.settings["color"] = opts[(opts.index(self.settings["color"])+1)%3]
                        if e.key == pygame.K_ESCAPE: self.save_all(); self.state = "MENU"
            elif self.state == "LEADS":
                self.screen.fill(BLACK)
                self.draw_text("HALL OF FAME", (SCREEN_W//2, 100), YELLOW, font=self.big_font)
                for i, entry in enumerate(self.leaderboard[:10]):
                    self.draw_text(f"{i+1}. {entry['name']} - {entry['score']}", (SCREEN_W//2, 200 + i*35))
                pygame.display.flip()
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: self.state = "MENU"

if __name__ == "__main__":
    RacerGame().run()