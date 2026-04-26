import pygame
import os

pygame.init()
pygame.mixer.init()

W = 800
H = 480

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Music Player")

clock = pygame.time.Clock()

base = os.path.dirname(__file__)
music_dir = os.path.join(base, "music")
playlist = [i for i in os.listdir(music_dir) if i.endswith(".mp3")]
current = 0

pygame.mixer.music.load(os.path.join(music_dir, playlist[current]))

font = pygame.font.SysFont("Verdana", 20)

playing = False
paused = False

running = True
while running:
    screen.fill('black')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # PLAY / PAUSE
            if event.key == pygame.K_p:
                if not playing:
                    pygame.mixer.music.play()
                    playing = True
                    paused = False
                elif paused:
                    pygame.mixer.music.unpause()
                    paused = False
                else:
                    pygame.mixer.music.pause()
                    paused = True

            # STOP
            elif event.key == pygame.K_s:
                pygame.mixer.music.stop()
                playing = False

            # NEXT
            elif event.key == pygame.K_n:
                current = (current + 1) % len(playlist)
                pygame.mixer.music.load(os.path.join(music_dir, playlist[current]))
                pygame.mixer.music.play()
                playing = True
                paused = False

            # BACK
            elif event.key == pygame.K_b:
                current = (current - 1) % len(playlist)
                pygame.mixer.music.load(os.path.join(music_dir, playlist[current]))
                pygame.mixer.music.play()
                playing = True
                paused = False

            # QUIT
            elif event.key == pygame.K_q:
                running = False

    track_text = "Track: " + playlist[current]

    if playing:
        status = "Paused" if paused else "Playing"
    else:
        status = "Stopped"

    screen.blit(font.render(track_text, True, 'white'), (20, 100))
    screen.blit(font.render("Status: " + status, True, 'white'), (20, 130))
    screen.blit(font.render("P-play/pause S-stop N-next B-back Q-quit", True, "white"), (20, 170))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()