import pygame


class Events:
    def __init__(self, event_quit, mouse_down, mouse_up, mouse_pos):
        self.quit = event_quit
        self.mouse_down = mouse_down
        self.mouse_up = mouse_up
        self.mouse_pos = mouse_pos

    @classmethod
    def update(cls):
        event_quit = False
        mouse_down = False
        mouse_up = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                event_quit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_up = True
        mouse_pos = pygame.mouse.get_pos()

        return cls(event_quit, mouse_down, mouse_up, mouse_pos)
