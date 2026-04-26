import pygame
import datetime
import os

pygame.init()

W = 800
H = 800
center = pygame.math.Vector2(W // 2, H // 2)

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Mickey Clock")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")

image_clock = pygame.image.load(os.path.join(IMAGES_DIR, "clock.png")).convert_alpha()
image_clock = pygame.transform.scale(image_clock, (750, 600))

mickey = pygame.image.load(os.path.join(IMAGES_DIR, "mickey.png")).convert_alpha()
mickey = pygame.transform.scale(mickey, (400, 280))

hand_left = pygame.image.load(os.path.join(IMAGES_DIR, "left_hand.png")).convert_alpha()
hand_left = pygame.transform.scale(hand_left, (150, 190))

hand_right = pygame.image.load(os.path.join(IMAGES_DIR, "right_hand.png")).convert_alpha()
hand_right = pygame.transform.scale(hand_right, (150, 150))


def draw_hand(image, angle, pivot_pos):
    rect = image.get_rect()
    offset = pygame.math.Vector2(0, -rect.height // 6)

    rotated_image = pygame.transform.rotate(image, -angle)
    rotated_offset = offset.rotate(angle)

    rotated_rect = rotated_image.get_rect(center=pivot_pos + rotated_offset)
    screen.blit(rotated_image, rotated_rect)


font = pygame.font.SysFont("arial", 40)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    now = datetime.datetime.now()
    minute = now.minute
    second = now.second

    minute_angle = minute * 6 + second * 0.1
    second_angle = second * 6

    screen.fill((255, 255, 255))

    clock_rect = image_clock.get_rect(center=center)
    mickey_rect = mickey.get_rect(center=center)

    screen.blit(image_clock, clock_rect)
    screen.blit(mickey, mickey_rect)

    draw_hand(hand_right, minute_angle, center)
    draw_hand(hand_left, second_angle, center)

    time_text = font.render(now.strftime("%H:%M:%S"), True, (0, 0, 0))
    time_rect = time_text.get_rect(center=(W // 2, 50))
    screen.blit(time_text, time_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()