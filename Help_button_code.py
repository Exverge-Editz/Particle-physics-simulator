import pygame

class Help_button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.menu_visible = False  #visibilty flag

    def draw(self, surface):
        action = False
        LEFT_MOUSE_BUTTON = 0
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[LEFT_MOUSE_BUTTON] == True and not self.clicked:
                self.clicked = True
                self.menu_visible = not self.menu_visible  #Toggle visibility
                action = True

        if pygame.mouse.get_pressed()[LEFT_MOUSE_BUTTON] == False:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action
