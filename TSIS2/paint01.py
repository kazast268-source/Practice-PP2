import pygame
import sys
import math
import datetime

# --- КОНСТАНТЫ ЭКРАНА ---
SCREEN_W = 1000
SCREEN_H = 700
TOOLBAR_W = 180
CANVAS_X = TOOLBAR_W
CANVAS_W = SCREEN_W - TOOLBAR_W
CANVAS_H = SCREEN_H

# --- ЦВЕТОВАЯ ПАЛИТРА ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_TOOLBAR = (33, 33, 33)
BG_CANVAS = (255, 255, 255)
HIGHLIGHT = (0, 120, 215)

PALETTE = [
    (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0),
    (0, 0, 255), (255, 255, 0), (255, 165, 0), (128, 0, 128),
    (0, 255, 255), (255, 0, 255), (165, 42, 42), (128, 128, 128)
]

# --- СПИСОК ИНСТРУМЕНТОВ ---
TOOL_PENCIL = "pencil"
TOOL_LINE = "line"
TOOL_RECT = "rect"
TOOL_SQUARE = "square"
TOOL_CIRCLE = "circle"
TOOL_RTRIANGLE = "right_tri"
TOOL_EQTRIANGLE = "eq_tri"
TOOL_RHOMBUS = "rhombus"
TOOL_FILL = "fill"
TOOL_TEXT = "text"
TOOL_ERASER = "eraser"


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ГЕОМЕТРИИ ---
def get_rtri_pts(p1, p2):
    return [p1, (p1[0], p2[1]), p2]


def get_eqtri_pts(p1, p2):
    bx1, bx2 = min(p1[0], p2[0]), max(p1[0], p2[0])
    by = max(p1[1], p2[1])
    side = bx2 - bx1
    return [((bx1 + bx2) // 2, by - int(side * 0.866)), (bx1, by), (bx2, by)]


def get_rhombus_pts(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return [((x1 + x2) // 2, y1), (x2, (y1 + y2) // 2), ((x1 + x2) // 2, y2), (x1, (y1 + y2) // 2)]


def flood_fill(surface, pos, fill_color):
    target_color = surface.get_at(pos)
    if target_color == fill_color:
        return
    pixels = [pos]
    visited = set()
    w, h = surface.get_size()
    while pixels:
        x, y = pixels.pop()
        if (x, y) in visited or x < 0 or x >= w or y < 0 or y >= h:
            continue
        if surface.get_at((x, y)) != target_color:
            continue
        surface.set_at((x, y), fill_color)
        visited.add((x, y))
        pixels.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])


# --- ОСНОВНОЕ ПРИЛОЖЕНИЕ ---
class PaintApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Pygame Paint TSIS 2 - Premium Edition")
        self.clock = pygame.time.Clock()
        
        # Шрифты
        self.font = pygame.font.SysFont("Arial", 16)
        self.text_font = pygame.font.SysFont("Verdana", 24)
        
        # Холст
        self.canvas = pygame.Surface((CANVAS_W, CANVAS_H))
        self.canvas.fill(BG_CANVAS)
        
        # Начальное состояние
        self.active_tool = TOOL_PENCIL
        self.active_color = BLACK
        self.brush_size = 5
        self.drawing = False
        self.start_pos = None
        self.last_pos = None
        self.text_active = False
        self.text_input = ""
        self.text_pos = None

    def save_canvas(self):
        fn = f"drawing_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pygame.image.save(self.canvas, fn)

    def draw_shape(self, surface, tool, p1, p2, color, size, offset_x=0):
        """Универсальная отрисовка фигур."""
        x1, y1 = p1[0] + offset_x, p1[1]
        x2, y2 = p2[0] + offset_x, p2[1]
        w, h = x2 - x1, y2 - y1

        if tool == TOOL_LINE:
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), size)
        elif tool == TOOL_RECT:
            pygame.draw.rect(surface, color, (min(x1, x2), min(y1, y2), abs(w), abs(h)), size)
        elif tool == TOOL_SQUARE:
            side = min(abs(w), abs(h))
            pygame.draw.rect(surface, color, (x1 if x2 > x1 else x1 - side, y1 if y2 > y1 else y1 - side, side, side), size)
        elif tool == TOOL_CIRCLE:
            pygame.draw.circle(surface, color, ((x1 + x2) // 2, (y1 + y2) // 2), int(math.hypot(w, h) / 2), size)
        elif tool == TOOL_RTRIANGLE:
            pygame.draw.polygon(surface, color, get_rtri_pts((x1, y1), (x2, y2)), size)
        elif tool == TOOL_EQTRIANGLE:
            pygame.draw.polygon(surface, color, get_eqtri_pts((x1, y1), (x2, y2)), size)
        elif tool == TOOL_RHOMBUS:
            pygame.draw.polygon(surface, color, get_rhombus_pts((x1, y1), (x2, y2)), size)

    def draw_ui(self):
        # Панель инструментов
        pygame.draw.rect(self.screen, BG_TOOLBAR, (0, 0, TOOLBAR_W, SCREEN_H))
        
        tools = [
            TOOL_PENCIL, TOOL_LINE, TOOL_RECT, TOOL_SQUARE, TOOL_CIRCLE,
            TOOL_RTRIANGLE, TOOL_EQTRIANGLE, TOOL_RHOMBUS, TOOL_FILL, TOOL_TEXT, TOOL_ERASER
        ]
        
        for i, t in enumerate(tools):
            rect = pygame.Rect(10, 10 + i * 33, 160, 28)
            color = HIGHLIGHT if self.active_tool == t else (60, 60, 60)
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            label = self.font.render(t.capitalize(), True, WHITE)
            self.screen.blit(label, (20, 15 + i * 33))

        # Палитра цветов
        for i, col in enumerate(PALETTE):
            r, c = divmod(i, 4)
            rect = pygame.Rect(10 + c * 42, 405 + r * 42, 35, 35)
            pygame.draw.rect(self.screen, col, rect)
            border_color = HIGHLIGHT if self.active_color == col else WHITE
            pygame.draw.rect(self.screen, border_color, rect, 3 if self.active_color == col else 1)

        # Выбор размера кисти
        for i, s in enumerate([2, 5, 10]):
            rect = pygame.Rect(10 + i * 55, 525, 50, 30)
            color = HIGHLIGHT if self.brush_size == s else (100, 100, 100)
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            size_label = self.font.render(str(s), True, WHITE)
            self.screen.blit(size_label, (rect.centerx - 5, rect.centery - 8))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if self.text_active:
                    if event.key == pygame.K_RETURN:
                        txt_surface = self.text_font.render(self.text_input, True, self.active_color)
                        self.canvas.blit(txt_surface, self.text_pos)
                        self.text_active = False
                    elif event.key == pygame.K_ESCAPE:
                        self.text_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.text_input = self.text_input[:-1]
                    else:
                        self.text_input += event.unicode
                else:
                    if event.key == pygame.K_1:
                        self.brush_size = 2
                    elif event.key == pygame.K_2:
                        self.brush_size = 5
                    elif event.key == pygame.K_3:
                        self.brush_size = 10
                    elif event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        self.save_canvas()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if mx < TOOLBAR_W:
                    # Логика клика по тулбару
                    if 10 < my < 380:
                        tool_list = [
                            TOOL_PENCIL, TOOL_LINE, TOOL_RECT, TOOL_SQUARE, TOOL_CIRCLE,
                            TOOL_RTRIANGLE, TOOL_EQTRIANGLE, TOOL_RHOMBUS, TOOL_FILL, TOOL_TEXT, TOOL_ERASER
                        ]
                        self.active_tool = tool_list[(my - 10) // 33]
                    elif 405 < my < 490:
                        idx = ((my - 405) // 42) * 4 + (mx - 10) // 42
                        if idx < len(PALETTE):
                            self.active_color = PALETTE[idx]
                    elif 525 < my < 555:
                        self.brush_size = [2, 5, 10][(mx - 10) // 55]
                else:
                    # Клик по холсту
                    cp = (mx - CANVAS_X, my)
                    if self.active_tool == TOOL_TEXT:
                        self.text_active, self.text_input, self.text_pos = True, "", cp
                    elif self.active_tool == TOOL_FILL:
                        flood_fill(self.canvas, cp, self.active_color)
                    else:
                        self.drawing = True
                        self.start_pos = self.last_pos = cp

            if event.type == pygame.MOUSEMOTION and self.drawing:
                cp = (event.pos[0] - CANVAS_X, event.pos[1])
                if self.active_tool == TOOL_PENCIL:
                    pygame.draw.line(self.canvas, self.active_color, self.last_pos, cp, self.brush_size)
                    self.last_pos = cp
                elif self.active_tool == TOOL_ERASER:
                    pygame.draw.circle(self.canvas, WHITE, cp, self.brush_size * 2)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.drawing:
                    cp = (event.pos[0] - CANVAS_X, event.pos[1])
                    if self.active_tool not in [TOOL_PENCIL, TOOL_ERASER]:
                        self.draw_shape(self.canvas, self.active_tool, self.start_pos, cp, self.active_color, self.brush_size)
                    self.drawing = False

    def run(self):
        while True:
            self.handle_events()
            self.screen.fill(BLACK)
            self.screen.blit(self.canvas, (CANVAS_X, 0))

            # Реальное время (Live Preview)
            if self.drawing and self.active_tool not in [TOOL_PENCIL, TOOL_ERASER]:
                m_x, m_y = pygame.mouse.get_pos()
                m_pos = (m_x - CANVAS_X, m_y)
                self.draw_shape(
                    self.screen, self.active_tool, self.start_pos, 
                    m_pos, self.active_color, self.brush_size, offset_x=CANVAS_X
                )

            # Отрисовка вводимого текста
            if self.text_active:
                ts = self.text_font.render(self.text_input + "|", True, self.active_color)
                self.screen.blit(ts, (self.text_pos[0] + CANVAS_X, self.text_pos[1]))

            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    PaintApp().run()