import pygame
import datetime
from tools import draw_shape, flood_fill

# Initialize Pygame & Fonts
pygame.init()
pygame.font.init()

# Constants
WIDTH, HEIGHT = 1000, 700
FPS = 120

# Colors
COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
}

# Setup Display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Extended Paint App - TSIS 2")

# Main Canvas (Where permanent drawings go)
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(COLORS['white'])

# Font setup
font = pygame.font.SysFont('Arial', 24)
ui_font = pygame.font.SysFont('Arial', 16)

def draw_ui(current_tool, current_color, current_size):
    """Draws a simple top bar with current settings."""
    ui_rect = pygame.Rect(0, 0, WIDTH, 30)
    pygame.draw.rect(screen, (200, 200, 200), ui_rect)
    pygame.draw.line(screen, (100, 100, 100), (0, 30), (WIDTH, 30), 2)
    
    status_text = f"Tool: {current_tool.upper()} | Color: {current_color} | Size (1,2,3): {current_size}px"
    controls_text = "Press 'T' for Text | 'F' for Fill | 'S' to Save | Keys 1-3 for Size"
    
    status_surf = ui_font.render(status_text, True, COLORS['black'])
    controls_surf = ui_font.render(controls_text, True, COLORS['black'])
    
    screen.blit(status_surf, (10, 5))
    screen.blit(controls_surf, (WIDTH - controls_surf.get_width() - 10, 5))

def main():
    clock = pygame.time.Clock()
    
    # State Variables
    current_tool = 'pencil'
    current_color = 'black'
    current_color_rgb = COLORS[current_color]
    sizes = {pygame.K_1: 2, pygame.K_2: 5, pygame.K_3: 10} # Small, Medium, Large
    current_size = 5
    
    drawing = False
    last_pos = None
    start_pos = None
    
    # Text Tool Variables
    typing_mode = False
    text_input = ""
    text_pos = (0, 0)
    
    running = True
    while running:
        # 1. Base Rendering: Draw the persistent canvas
        screen.blit(canvas, (0, 0))
        
        # 2. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # --- KEYBOARD EVENTS ---
            if event.type == pygame.KEYDOWN:
                # Text Tool Logic
                if typing_mode:
                    if event.key == pygame.K_RETURN:
                        # Commit text to canvas
                        txt_surf = font.render(text_input, True, current_color_rgb)
                        canvas.blit(txt_surf, text_pos)
                        typing_mode = False
                        text_input = ""
                    elif event.key == pygame.K_ESCAPE:
                        # Cancel text
                        typing_mode = False
                        text_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]
                    else:
                        text_input += event.unicode
                    continue # Skip other key checks while typing

                # Ctrl + S to Save
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"canvas_{timestamp}.png"
                    pygame.image.save(canvas, filename)
                    print(f"Saved canvas to {filename}")
                
                # Brush Sizes
                if event.key in sizes:
                    current_size = sizes[event.key]
                
                # Tool Selection Shortcuts
                if event.key == pygame.K_p: current_tool = 'pencil'
                elif event.key == pygame.K_l: current_tool = 'line'
                elif event.key == pygame.K_r: current_tool = 'rect'
                elif event.key == pygame.K_c: current_tool = 'circle'
                elif event.key == pygame.K_q: current_tool = 'square'
                elif event.key == pygame.K_t: current_tool = 'text'
                elif event.key == pygame.K_f: current_tool = 'fill'
                elif event.key == pygame.K_e: current_tool = 'eraser'
                
                # Shapes shortcuts (Optional, extending practice 11)
                elif event.key == pygame.K_7: current_tool = 'right_tri'
                elif event.key == pygame.K_8: current_tool = 'eq_tri'
                elif event.key == pygame.K_9: current_tool = 'rhombus'

                # Color Shortcuts
                if event.key == pygame.K_z: current_color_rgb, current_color = COLORS['black'], 'black'
                if event.key == pygame.K_x: current_color_rgb, current_color = COLORS['red'], 'red'
                if event.key == pygame.K_v: current_color_rgb, current_color = COLORS['green'], 'green'
                if event.key == pygame.K_b: current_color_rgb, current_color = COLORS['blue'], 'blue'

            # --- MOUSE EVENTS ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    if event.pos[1] < 30: continue # Ignore clicks in the UI bar
                    
                    if current_tool == 'text':
                        typing_mode = True
                        text_pos = event.pos
                        text_input = ""
                    elif current_tool == 'fill':
                        flood_fill(canvas, event.pos, current_color_rgb)
                    else:
                        drawing = True
                        start_pos = event.pos
                        last_pos = event.pos
                        
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    drawing = False
                    # Commit shapes and lines to the canvas on release
                    if current_tool == 'line':
                        pygame.draw.line(canvas, current_color_rgb, start_pos, event.pos, current_size)
                    elif current_tool in ['rect', 'circle', 'square', 'right_tri', 'eq_tri', 'rhombus']:
                        draw_shape(canvas, current_color_rgb, start_pos, event.pos, current_tool, current_size)

            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    if current_tool == 'pencil':
                        # Draw continuously onto the permanent canvas
                        pygame.draw.line(canvas, current_color_rgb, last_pos, event.pos, current_size)
                        last_pos = event.pos
                    elif current_tool == 'eraser':
                        # Eraser draws white continuously
                        pygame.draw.line(canvas, COLORS['white'], last_pos, event.pos, current_size)
                        last_pos = event.pos

        # 3. Live Preview Rendering (Drawn on screen, NOT canvas)
        if drawing and current_tool not in ['pencil', 'eraser', 'fill', 'text']:
            mouse_pos = pygame.mouse.get_pos()
            if current_tool == 'line':
                pygame.draw.line(screen, current_color_rgb, start_pos, mouse_pos, current_size)
            else:
                draw_shape(screen, current_color_rgb, start_pos, mouse_pos, current_tool, current_size)

        # 4. Text Tool Live Preview
        if typing_mode:
            txt_surf = font.render(text_input + "|", True, current_color_rgb)
            screen.blit(txt_surf, text_pos)
            
            # Highlight border to show typing mode is active
            pygame.draw.rect(screen, COLORS['red'], (text_pos[0]-5, text_pos[1]-5, txt_surf.get_width()+10, txt_surf.get_height()+10), 1)

        # 5. UI Overlay
        draw_ui(current_tool, current_color, current_size)

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()