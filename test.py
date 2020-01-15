import pygame

pygame.init()

screen =  pygame.display.set_mode((400, 400))

degree = 0
dir = pygame.Vector2(0,1)
while True:
    screen.fill((40, 40, 40))

    surf = pygame.Surface((100, 50))
    surf.fill((255, 255, 255))
    surf.set_colorkey((255, 0, 0))
    where = 200, 200

    blittedRect = screen.blit(surf, where)
    oldCenter = blittedRect.center
    rotatedSurf = pygame.transform.rotate(surf, degree)
    dir.rotate_ip(degree)
    rotRect = rotatedSurf.get_rect()
    rotRect.center = oldCenter
    screen.blit(rotatedSurf, rotRect)
    pygame.draw.line(screen, 234, [200, 200], [200, 200] + dir.rotate(degree) * 100)

    degree += 5
    if degree > 360:
        degree = 0

    pygame.display.flip()

    pygame.time.wait(100)