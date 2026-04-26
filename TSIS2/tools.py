import pygame
import math

# ───────────── DRAW SHAPES ─────────────
def draw_shape(surface, color, start, end, shape_type, width):
    """Draw shapes based on drag (start -> end)."""
    x1, y1 = start
    x2, y2 = end

    rect = pygame.Rect(min(x1, x2), min(y1, y2),
                       abs(x2 - x1), abs(y2 - y1))

    if shape_type == 'rect':
        pygame.draw.rect(surface, color, rect, width)

    elif shape_type == 'square':
        side = max(rect.width, rect.height)
        square_rect = pygame.Rect(
            x1 if x1 < x2 else x1 - side,
            y1 if y1 < y2 else y1 - side,
            side, side
        )
        pygame.draw.rect(surface, color, square_rect, width)

    elif shape_type == 'circle':
        radius = max(rect.width, rect.height) // 2
        center = (rect.x + rect.width // 2, rect.y + rect.height // 2)
        if radius > 0:
            pygame.draw.circle(surface, color, center, radius, width)

    elif shape_type == 'right_tri':
        points = [(x1, y1), (x1, y2), (x2, y2)]
        if len(set(points)) > 2:
            pygame.draw.polygon(surface, color, points, width)

    elif shape_type == 'eq_tri':
        side = abs(x2 - x1)
        height = int(side * math.sqrt(3) / 2)
        direction = 1 if y2 >= y1 else -1

        points = [
            (x1, y1 + direction * height),
            (x1 + side // 2, y1),
            (x1 + side, y1 + direction * height)
        ]
        if len(set(points)) > 2:
            pygame.draw.polygon(surface, color, points, width)

    elif shape_type == 'rhombus':
        mid_x = (x1 + x2) // 2
        mid_y = (y1 + y2) // 2

        points = [
            (mid_x, y1),
            (x2, mid_y),
            (mid_x, y2),
            (x1, mid_y)
        ]
        if len(set(points)) > 2:
            pygame.draw.polygon(surface, color, points, width)


# ───────────── FLOOD FILL (FIXED) ─────────────
def flood_fill(surface, start_pos, new_color):
    """
    Flood fill using get_at() and set_at() (TSIS requirement).
    """
    width, height = surface.get_size()

    target_color = surface.get_at(start_pos)

    # If same color — do nothing
    if target_color == new_color:
        return

    stack = [start_pos]

    while stack:
        x, y = stack.pop()

        # Bounds check
        if x < 0 or y < 0 or x >= width or y >= height:
            continue

        # Only fill same-colored pixels
        if surface.get_at((x, y)) != target_color:
            continue

        # Fill pixel
        surface.set_at((x, y), new_color)

        # Add neighbors
        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))