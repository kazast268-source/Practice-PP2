import pygame
import sys
import random
from config import *
from db import init_db, get_top_scores
from game import run_game

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS4: Snake Database Edition")

# Шрифты
font_main = pygame.font.SysFont("Verdana", 24)
font_big = pygame.font.SysFont("Verdana", 48, bold=True)
font_small = pygame.font.SysFont("Verdana", 18)

class Button:
    def __init__(self, x, y, w, h, text, color=GRAY):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=5)
        txt_img = font_main.render(self.text, True, WHITE)
        surface.blit(txt_img, txt_img.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

def draw_text(text, font, color, y_pos):
    img = font.render(text, True, color)
    screen.blit(img, img.get_rect(center=(WIDTH // 2, y_pos)))

def ask_username():
    """Экран ввода имени пользователя."""
    username = ""
    while True:
        screen.fill(BLACK)
        draw_text("ENTER YOUR NAME", font_main, GREEN, 200)
        
        # Поле ввода
        input_rect = pygame.Rect(WIDTH//2 - 150, 250, 300, 50)
        pygame.draw.rect(screen, DARK_GRAY, input_rect, border_radius=5)
        draw_text(username + "|", font_main, YELLOW, 275)
        
        draw_text("Press ENTER to Start", font_small, WHITE, 350)
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username: return username
                elif event.key == pygame.K_BACKSPACE: username = username[:-1]
                elif len(username) < 15: username += event.unicode

def main_menu():
    btn_play = Button(200, 200, 200, 50, "PLAY", GREEN)
    btn_leader = Button(200, 270, 200, 50, "LEADERBOARD")
    btn_settings = Button(200, 340, 200, 50, "SETTINGS")
    btn_quit = Button(200, 410, 200, 50, "QUIT", RED)

    while True:
        screen.fill(BLACK)
        draw_text("SNAKE TSIS4", font_big, WHITE, 100)
        
        for b in [btn_play, btn_leader, btn_settings, btn_quit]: b.draw(screen)
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or btn_quit.is_clicked(event): return "quit"
            if btn_play.is_clicked(event): return "play"
            if btn_leader.is_clicked(event): return "leaderboard"
            if btn_settings.is_clicked(event): return "settings"

def leaderboard_screen():
    scores = get_top_scores()
    btn_back = Button(200, 520, 200, 40, "BACK")
    
    while True:
        screen.fill(BLACK)
        draw_text("TOP 10 PLAYERS", font_main, YELLOW, 50)
        
        y = 120
        for i, (name, score, lvl, date) in enumerate(scores):
            txt = f"{i+1}. {name:10} | {score:4} pts | Lvl {lvl}"
            draw_text(txt, font_small, WHITE, y)
            y += 35
            
        btn_back.draw(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if btn_back.is_clicked(event): return "menu"

def settings_screen():
    current = load_settings()
    btn_grid = Button(150, 200, 300, 50, f"GRID: {'ON' if current['grid'] else 'OFF'}")
    btn_color = Button(150, 270, 300, 50, "CHANGE COLOR")
    btn_back = Button(200, 400, 200, 50, "SAVE & BACK", GREEN)

    while True:
        screen.fill(BLACK)
        draw_text("SETTINGS", font_main, BLUE, 100)
        
        # Предпросмотр цвета змейки
        pygame.draw.rect(screen, current['snake_color'], (WIDTH//2 - 25, 330, 50, 50))
        
        for b in [btn_grid, btn_color, btn_back]: b.draw(screen)
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if btn_grid.is_clicked(event):
                current['grid'] = not current['grid']
                btn_grid.text = f"GRID: {'ON' if current['grid'] else 'OFF'}"
            if btn_color.is_clicked(event):
                current['snake_color'] = [random.randint(50, 255) for _ in range(3)]
            if btn_back.is_clicked(event):
                save_settings(current)
                return "menu"

def game_over_screen(res):
    btn_retry = Button(100, 400, 180, 50, "RETRY", GREEN)
    btn_menu = Button(320, 400, 180, 50, "MENU")

    while True:
        screen.fill(BLACK)
        draw_text("GAME OVER", font_big, RED, 150)
        draw_text(f"SCORE: {res['score']}", font_main, WHITE, 230)
        draw_text(f"LEVEL: {res['level']}", font_main, WHITE, 270)
        draw_text(f"PERSONAL BEST: {res['best']}", font_main, YELLOW, 320)
        
        btn_retry.draw(screen)
        btn_menu.draw(screen)
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if btn_retry.is_clicked(event): return "retry"
            if btn_menu.is_clicked(event): return "menu"

def main():
    # Инициализируем БД при запуске
    try:
        init_db()
    except Exception as e:
        print(f"Database error: {e}")

    while True:
        state = main_menu()
        
        if state == "quit": break
        elif state == "leaderboard": leaderboard_screen()
        elif state == "settings": settings_screen()
        elif state == "play":
            user = ask_username()
            if not user: continue
            
            # Игровой цикл (retry/menu)
            while True:
                game_state, result = run_game(screen, user, load_settings())
                if game_state == "quit": 
                    pygame.quit()
                    sys.exit()
                
                after_action = game_over_screen(result)
                if after_action == "retry": continue
                break

    pygame.quit()

if __name__ == "__main__":
    main()