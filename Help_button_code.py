import pygame #type: ignore

class Help_button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False #states if the button has been clicked

    def draw(self, surface):
        action = False
        LEFT_MOUSE_BUTTON = 0

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            #allows you to click the button
            if pygame.mouse.get_pressed()[LEFT_MOUSE_BUTTON] == True and self.clicked == False:
                self.clicked = True
                action = True
        #if pygame.mouse.get_pressed()[LEFT_MOUSE_BUTTON] == False : #button hasn't been clicked
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action