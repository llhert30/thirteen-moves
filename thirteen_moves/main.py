from events import Events
from game import Game
import pygame


LIGHT_GRAY = (240, 240, 240)


def main():
    pygame.init()
    screen = pygame.display.set_mode([600, 800])
    pygame.display.set_caption("Thirteen Moves")

    game = Game.new(50, 150, x_center=300)

    running = True
    while running:
        events = Events.update()

        if events.quit:
            running = False

        screen.fill(LIGHT_GRAY)
        game.update(events, screen)
        game.display(screen, events)
        pygame.display.flip()


if __name__ == "__main__":
    main()
