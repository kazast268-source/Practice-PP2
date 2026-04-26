import pygame

pygame.init()

W = 800
H = 480
R = 25

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Moving Ball")

circle_x = W // 2
circle_y = H // 2

clock = pygame.time.Clock()


running = True
while running:
    screen.fill('white')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and circle_y - 20 - R >= 0:
                circle_y -= 20
            elif event.key == pygame.K_DOWN and circle_y + 20 + R <= H:
                circle_y += 20
            elif event.key == pygame.K_LEFT and circle_x - 20 - R >= 0:
                circle_x -= 20
            elif event.key == pygame.K_RIGHT and circle_x + 20 + R <= W:
                circle_x += 20

    pygame.draw.circle(screen, (255, 0, 0), (circle_x, circle_y), R)

    pygame.display.flip()
    clock.tick()

pygame.quit()