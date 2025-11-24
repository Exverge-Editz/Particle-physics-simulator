import pygame

class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        raise NotImplementedError("Subclasses should implement this method.")

class Exit_Button(Button):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def draw(self, surface):
        action = False
        LEFT_MOUSE_BUTTON: int = 0
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[LEFT_MOUSE_BUTTON] and not self.clicked:
                self.clicked = True
                action = True
        if not pygame.mouse.get_pressed()[LEFT_MOUSE_BUTTON]:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action

class Help_Button(Button):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.menu_visible = False

    def draw(self, surface):
        action = False
        LEFT_MOUSE_BUTTON: int = 0
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[LEFT_MOUSE_BUTTON] and not self.clicked:
                self.clicked = True
                self.menu_visible = not self.menu_visible
                action = True
        if not pygame.mouse.get_pressed()[LEFT_MOUSE_BUTTON]:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action

class Notes_Button(Button):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.menu_visible = False

    def draw(self, surface):
        action = False
        LEFT_MOUSE_BUTTON: int = 0
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[LEFT_MOUSE_BUTTON] and not self.clicked:
                self.clicked = True
                self.menu_visible = not self.menu_visible
                action = True
        if not pygame.mouse.get_pressed()[LEFT_MOUSE_BUTTON]:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action