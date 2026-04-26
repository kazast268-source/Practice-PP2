import pygame
import sys
import math

# ──────────────────────────────────────────────
# КОНСТАНТЫ
# ──────────────────────────────────────────────
SCREEN_W  = 900
SCREEN_H  = 650
TOOLBAR_W = 160   # ширина левой панели инструментов
CANVAS_X  = TOOLBAR_W
CANVAS_W  = SCREEN_W - TOOLBAR_W
CANVAS_H  = SCREEN_H

# Цвета (R, G, B)
WHITE       = (255, 255, 255)
BLACK       = (0,   0,   0)
BG_TOOLBAR  = (40,  42,  54)   # темный фон панели инструментов
BG_CANVAS   = (255, 255, 255)  # белый холст
HIGHLIGHT   = (80, 140, 255)   # цвет выделения активного инструмента
TEXT_COLOUR = (220, 220, 220)
GRID_COLOUR = (230, 230, 230)

# Палитра доступных цветов для рисования
PALETTE = [
    (0,   0,   0),       # Черный
    (220, 40,  40),      # Красный
    (30,  120, 255),     # Синий
    (50,  200, 80),      # Зеленый
    (255, 220, 0),       # Желтый
    (255, 140, 0),       # Оранжевый
    (180, 60,  200),     # Фиолетовый
    (0,   200, 200),     # Циан
    (255, 105, 180),     # Розовый
    (139, 90,  43),      # Коричневый
    (128, 128, 128),     # Серый
    (255, 255, 255),     # Белый (ластик)
]

# Варианты размеров кисти (в пикселях)
BRUSH_SIZES = [2, 4, 8, 16]

# ID инструментов
TOOL_PENCIL      = "pencil"
TOOL_LINE        = "line"
TOOL_RECT        = "rect"
TOOL_SQUARE      = "square"
TOOL_CIRCLE      = "circle"
TOOL_RTRIANGLE   = "right_tri"
TOOL_EQTRIANGLE  = "eq_tri"
TOOL_RHOMBUS     = "rhombus"
TOOL_FILL        = "fill"
TOOL_ERASER      = "eraser"

# Отображаемые названия инструментов на кнопках
TOOL_LABELS = {
    TOOL_PENCIL:    "✏ Карандаш",
    TOOL_LINE:      "╱ Линия",
    TOOL_RECT:      "▭ Прямоуг.",
    TOOL_SQUARE:    "■ Квадрат",
    TOOL_CIRCLE:    "○ Круг",
    TOOL_RTRIANGLE: "◺ Пр. Треуг.",
    TOOL_EQTRIANGLE:"△ Равн. Треуг.",
    TOOL_RHOMBUS:   "◇ Ромб",
    TOOL_FILL:      "🪣 Заливка",
    TOOL_ERASER:    "⬜ Ластик",
}

# Порядок отображения инструментов в панели
TOOL_ORDER = [
    TOOL_PENCIL, TOOL_LINE,
    TOOL_RECT, TOOL_SQUARE,
    TOOL_CIRCLE,
    TOOL_RTRIANGLE, TOOL_EQTRIANGLE,
    TOOL_RHOMBUS,
    TOOL_FILL, TOOL_ERASER,
]

# ──────────────────────────────────────────────
# ВСПОМОГАТЕЛЬНАЯ ГЕОМЕТРИЯ
# ──────────────────────────────────────────────

def points_for_right_triangle(x1, y1, x2, y2):
    """Строит прямоугольный треугольник."""
    return [(x1, y1), (x1, y2), (x2, y2)]


def points_for_equilateral_triangle(x1, y1, x2, y2):
    """Строит равносторонний треугольник."""
    bx1 = min(x1, x2)
    bx2 = max(x1, x2)
    by  = max(y1, y2)
    cx  = (bx1 + bx2) / 2
    side = bx2 - bx1
    height = side * math.sqrt(3) / 2
    ay  = by - height
    return [(cx, ay), (bx1, by), (bx2, by)]


def points_for_rhombus(x1, y1, x2, y2):
    """Строит ромб по границам области."""
    lx = min(x1, x2); rx = max(x1, x2)
    ty = min(y1, y2); by = max(y1, y2)
    cx = (lx + rx) / 2
    cy = (ty + by) / 2
    return [(cx, ty), (rx, cy), (cx, by), (lx, cy)]


def flood_fill(surface, pos, fill_colour):
    """Итеративная заливка области."""
    target_colour = surface.get_at(pos)[:3]
    if target_colour == fill_colour:
        return

    width, height = surface.get_size()
    stack = [pos]
    visited = set()

    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        if surface.get_at((x, y))[:3] != target_colour:
            continue

        surface.set_at((x, y), fill_colour)
        visited.add((x, y))
        stack += [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]


# ──────────────────────────────────────────────
# КОМПОНЕНТ ИНТЕРФЕЙСА (ПАНЕЛЬ)
# ──────────────────────────────────────────────

class Toolbar:
    """Отрисовка панели инструментов, палитры и размеров."""

    BTN_H    = 34
    BTN_PAD  = 4
    SEC_GAP  = 10

    def __init__(self, font, small_font):
        self.font       = font
        self.small_font = small_font

        self.tool_rects = {}
        y = 10
        for tool in TOOL_ORDER:
            r = pygame.Rect(6, y, TOOLBAR_W - 12, self.BTN_H)
            self.tool_rects[tool] = r
            y += self.BTN_H + self.BTN_PAD

        self.tool_section_bottom = y + self.SEC_GAP

        self.palette_rects = []
        px, py = 8, self.tool_section_bottom + 24
        SWATCH = 28
        for i, col in enumerate(PALETTE):
            col_idx = i % 4
            row_idx = i // 4
            r = pygame.Rect(px + col_idx * (SWATCH + 4), py + row_idx * (SWATCH + 4), SWATCH, SWATCH)
            self.palette_rects.append((r, col))

        self.palette_bottom = py + (len(PALETTE) // 4 + 1) * (SWATCH + 4) + self.SEC_GAP

        self.size_rects = []
        sx, sy = 10, self.palette_bottom + 24
        for i, sz in enumerate(BRUSH_SIZES):
            r = pygame.Rect(sx + i * 34, sy, 30, 30)
            self.size_rects.append((r, sz))

        self.clear_rect = pygame.Rect(10, sy + 44, TOOLBAR_W - 20, 32)

    def draw(self, surface, active_tool, active_colour, active_size):
        pygame.draw.rect(surface, BG_TOOLBAR, (0, 0, TOOLBAR_W, SCREEN_H))
        pygame.draw.line(surface, HIGHLIGHT, (TOOLBAR_W - 1, 0), (TOOLBAR_W - 1, SCREEN_H), 2)

        # ── Заголовок ──
        title = self.small_font.render("ИНСТРУМЕНТЫ", True, TEXT_COLOUR)
        surface.blit(title, (TOOLBAR_W // 2 - title.get_width() // 2, 2))

        # ── Кнопки инструментов ──
        for tool, rect in self.tool_rects.items():
            colour = HIGHLIGHT if tool == active_tool else (60, 63, 78)
            pygame.draw.rect(surface, colour, rect, border_radius=5)
            txt = self.small_font.render(TOOL_LABELS[tool], True, WHITE)
            surface.blit(txt, txt.get_rect(center=rect.center))

        # ── Заголовок палитры ──
        ph = self.small_font.render("ЦВЕТ", True, TEXT_COLOUR)
        surface.blit(ph, (TOOLBAR_W // 2 - ph.get_width() // 2, self.tool_section_bottom + 6))

        # ── Ячейки палитры ──
        for rect, col in self.palette_rects:
            pygame.draw.rect(surface, col, rect, border_radius=4)
            if col == active_colour:
                pygame.draw.rect(surface, WHITE, rect, 3, border_radius=4)
            else:
                pygame.draw.rect(surface, (100, 100, 100), rect, 1, border_radius=4)

        # ── Заголовок размера ──
        sh = self.small_font.render("РАЗМЕР", True, TEXT_COLOUR)
        surface.blit(sh, (TOOLBAR_W // 2 - sh.get_width() // 2, self.palette_bottom + 6))

        # ── Кнопки выбора размера ──
        for rect, sz in self.size_rects:
            col = HIGHLIGHT if sz == active_size else (60, 63, 78)
            pygame.draw.rect(surface, col, rect, border_radius=4)
            pygame.draw.circle(surface, WHITE, rect.center, min(sz // 2, 10))

        # ── Кнопка очистки ──
        pygame.draw.rect(surface, (180, 50, 50), self.clear_rect, border_radius=6)
        ct = self.small_font.render("🗑 Очистить", True, WHITE)
        surface.blit(ct, ct.get_rect(center=self.clear_rect.center))

    def handle_click(self, pos, active_tool, active_colour, active_size):
        new_tool   = active_tool
        new_colour = active_colour
        new_size   = active_size
        clear      = False

        for tool, rect in self.tool_rects.items():
            if rect.collidepoint(pos):
                new_tool = tool

        for rect, col in self.palette_rects:
            if rect.collidepoint(pos):
                new_colour = col

        for rect, sz in self.size_rects:
            if rect.collidepoint(pos):
                new_size = sz

        if self.clear_rect.collidepoint(pos):
            clear = True

        return new_tool, new_colour, new_size, clear


# ──────────────────────────────────────────────
# ОСНОВНОЕ ПРИЛОЖЕНИЕ
# ──────────────────────────────────────────────

class PaintApp:
    def __init__(self):
        pygame.init()
        self.screen     = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Рисовалка – Практика 11")
        self.clock      = pygame.time.Clock()
        self.font       = pygame.font.SysFont("arial", 18, bold=True)
        self.small_font = pygame.font.SysFont("arial", 13)

        self.canvas     = pygame.Surface((CANVAS_W, CANVAS_H))
        self.canvas.fill(BG_CANVAS)

        self.toolbar    = Toolbar(self.font, self.small_font)

        self.active_tool   = TOOL_PENCIL
        self.active_colour = BLACK
        self.active_size   = 4

        self.drawing       = False
        self.start_pos     = None
        self.last_pos      = None
        self.running       = True

    def to_canvas(self, pos):
        return (pos[0] - CANVAS_X, pos[1])

    def on_canvas(self, pos):
        return pos[0] >= CANVAS_X

    def run(self):
        while self.running:
            self.clock.tick(60)
            self._handle_events()
            self._draw()
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_DELETE:
                    self.canvas.fill(BG_CANVAS)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if not self.on_canvas(pos):
                    self.active_tool, self.active_colour, self.active_size, clear = \
                        self.toolbar.handle_click(pos, self.active_tool,
                                                  self.active_colour, self.active_size)
                    if clear:
                        self.canvas.fill(BG_CANVAS)
                else:
                    cp = self.to_canvas(pos)
                    self.drawing   = True
                    self.start_pos = cp
                    self.last_pos  = cp

                    if self.active_tool == TOOL_FILL:
                        flood_fill(self.canvas, cp, self.active_colour)
                        self.drawing = False
                    elif self.active_tool in (TOOL_PENCIL, TOOL_ERASER):
                        colour = WHITE if self.active_tool == TOOL_ERASER else self.active_colour
                        pygame.draw.circle(self.canvas, colour, cp, self.active_size // 2)

            elif event.type == pygame.MOUSEMOTION and self.drawing:
                pos = event.pos
                if self.on_canvas(pos):
                    cp = self.to_canvas(pos)
                    if self.active_tool in (TOOL_PENCIL, TOOL_ERASER):
                        colour = WHITE if self.active_tool == TOOL_ERASER else self.active_colour
                        pygame.draw.line(self.canvas, colour, self.last_pos, cp, self.active_size)
                        self.last_pos = cp

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.drawing and self.on_canvas(event.pos):
                    cp = self.to_canvas(event.pos)
                    self._commit_shape(self.start_pos, cp)
                self.drawing   = False
                self.start_pos = None

    def _commit_shape(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        col  = self.active_colour
        w    = self.active_size
        tool = self.active_tool

        if tool == TOOL_LINE:
            pygame.draw.line(self.canvas, col, p1, p2, w)
        elif tool == TOOL_RECT:
            rx = min(x1, x2); ry = min(y1, y2)
            rw = abs(x2 - x1); rh = abs(y2 - y1)
            pygame.draw.rect(self.canvas, col, (rx, ry, rw, rh), w)
        elif tool == TOOL_SQUARE:
            side = min(abs(x2 - x1), abs(y2 - y1))
            sx   = x1 if x2 >= x1 else x1 - side
            sy   = y1 if y2 >= y1 else y1 - side
            pygame.draw.rect(self.canvas, col, (sx, sy, side, side), w)
        elif tool == TOOL_CIRCLE:
            cx   = (x1 + x2) // 2; cy = (y1 + y2) // 2
            rad  = int(math.hypot(x2 - x1, y2 - y1) / 2)
            pygame.draw.circle(self.canvas, col, (cx, cy), rad, w)
        elif tool == TOOL_RTRIANGLE:
            pts = points_for_right_triangle(x1, y1, x2, y2)
            pts_int = [(int(px), int(py)) for px, py in pts]
            pygame.draw.polygon(self.canvas, col, pts_int, w)
        elif tool == TOOL_EQTRIANGLE:
            pts = points_for_equilateral_triangle(x1, y1, x2, y2)
            pts_int = [(int(px), int(py)) for px, py in pts]
            pygame.draw.polygon(self.canvas, col, pts_int, w)
        elif tool == TOOL_RHOMBUS:
            pts = points_for_rhombus(x1, y1, x2, y2)
            pts_int = [(int(px), int(py)) for px, py in pts]
            pygame.draw.polygon(self.canvas, col, pts_int, w)

    def _draw_preview(self, surface, p1, p2):
        def sc(pt): return (pt[0] + CANVAS_X, pt[1])
        x1, y1 = p1
        x2, y2 = p2
        w   = self.active_size
        tool = self.active_tool

        if tool == TOOL_LINE:
            pygame.draw.line(surface, self.active_colour, sc(p1), sc(p2), w)
        elif tool == TOOL_RECT:
            rx = min(x1, x2) + CANVAS_X; ry = min(y1, y2)
            rw = abs(x2 - x1); rh = abs(y2 - y1)
            pygame.draw.rect(surface, self.active_colour, (rx, ry, rw, rh), w)
        elif tool == TOOL_SQUARE:
            side = min(abs(x2 - x1), abs(y2 - y1))
            sx   = (x1 if x2 >= x1 else x1 - side) + CANVAS_X
            sy   = y1 if y2 >= y1 else y1 - side
            pygame.draw.rect(surface, self.active_colour, (sx, sy, side, side), w)
        elif tool == TOOL_CIRCLE:
            cx = (x1 + x2) // 2 + CANVAS_X; cy = (y1 + y2) // 2
            rad = max(1, int(math.hypot(x2 - x1, y2 - y1) / 2))
            pygame.draw.circle(surface, self.active_colour, (cx, cy), rad, w)
        elif tool == TOOL_RTRIANGLE:
            pts = points_for_right_triangle(x1, y1, x2, y2)
            pts_sc = [(int(px) + CANVAS_X, int(py)) for px, py in pts]
            pygame.draw.polygon(surface, self.active_colour, pts_sc, w)
        elif tool == TOOL_EQTRIANGLE:
            pts = points_for_equilateral_triangle(x1, y1, x2, y2)
            pts_sc = [(int(px) + CANVAS_X, int(py)) for px, py in pts]
            pygame.draw.polygon(surface, self.active_colour, pts_sc, w)
        elif tool == TOOL_RHOMBUS:
            pts = points_for_rhombus(x1, y1, x2, y2)
            pts_sc = [(int(px) + CANVAS_X, int(py)) for px, py in pts]
            pygame.draw.polygon(surface, self.active_colour, pts_sc, w)

    def _draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.canvas, (CANVAS_X, 0))

        if self.drawing and self.start_pos and self.active_tool not in (
                TOOL_PENCIL, TOOL_ERASER, TOOL_FILL):
            mouse_canvas = self.to_canvas(pygame.mouse.get_pos())
            self._draw_preview(self.screen, self.start_pos, mouse_canvas)

        self.toolbar.draw(self.screen, self.active_tool, self.active_colour, self.active_size)

        # Строка состояния
        mx, my  = pygame.mouse.get_pos()
        cx, cy  = self.to_canvas((mx, my))
        tool_lbl = TOOL_LABELS.get(self.active_tool, "")
        status   = self.small_font.render(
            f"{tool_lbl}  ({cx},{cy})  разм:{self.active_size}", True, TEXT_COLOUR)
        pygame.draw.rect(self.screen, (25, 25, 35), (0, SCREEN_H - 18, TOOLBAR_W, 18))
        self.screen.blit(status, (4, SCREEN_H - 16))

        pygame.display.flip()

if __name__ == "__main__":
    app = PaintApp()
    app.run()