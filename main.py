import pygame
from pygame import Surface, KMOD_CTRL, K_DELETE
from particles import *
from buttons import *
from forces import *
import math as maths

pygame.init()

#gets the information of the monitor so the window is the same size of the user's screen.
info = pygame.display.Info()
screen_width, screen_height = int(info.current_w), int(info.current_h)
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Particle Physics simulator")
clock = pygame.time.Clock()

#function that crops the transparent part of the image
#by finding pixels with an alpha level of 0 and removing them which is done by the .get_bounding_rect() function
#it then creates a copy of that new rect using the .copy() function which is what the simulator uses
def crop_transparency(image: pygame.Surface) -> pygame.Surface:
    rect = image.get_bounding_rect()  # Finds non-transparent area
    return image.subsurface(rect).copy()

#loads and crops images
proton_img = crop_transparency(pygame.image.load("proton.png").convert_alpha())
neutron_img = crop_transparency(pygame.image.load("neutron.png").convert_alpha())
electron_img = crop_transparency(pygame.image.load("electron.png").convert_alpha())
neutrino_img = crop_transparency(pygame.image.load("neutrino.png").convert_alpha())

exit_button_img = crop_transparency(pygame.image.load("exit_button.png").convert_alpha())
user_note_img = crop_transparency(pygame.image.load("user_note.png").convert_alpha())
help_button_img = crop_transparency(pygame.image.load("help_button.png").convert_alpha())

help_menu = crop_transparency(pygame.image.load("help_menu.png").convert_alpha())
help_menu = pygame.transform.scale(help_menu, ((screen_width * 0.50), (screen_height * 0.75)))

under_construction = crop_transparency(pygame.image.load("under construction.png").convert_alpha())
under_construction = pygame.transform.scale(under_construction, ((screen_width * 0.70), (screen_height * 0.75)))

#positions for the button variables.
X_POS_HELP_BUTTON = 125
Y_POS_HELP_BUTTON = 0

X_POS_EXIT_BUTTON = 0
Y_POS_EXIT_BUTTON = 0

X_POS_NOTE_BUTTON = screen_width - 100
Y_POS_NOTE_BUTTON = 0

#position for menus.
X_POS_HELP_MENU = 100
Y_POS_HELP_MENU = 100

X_POS_NOTE_MENU = 100
Y_POS_NOTE_MENU = 100

#initialising the buttons.
help_button = Help_Button(X_POS_HELP_BUTTON, Y_POS_HELP_BUTTON, help_button_img)
exit_button = Exit_Button(X_POS_EXIT_BUTTON, Y_POS_EXIT_BUTTON, exit_button_img)
user_note_button = Notes_Button(X_POS_NOTE_BUTTON, Y_POS_NOTE_BUTTON, user_note_img)

#list of all the particles on the screen and there position so they don't disappear.
particle_list = []

#flag to tell if the programme is running
running = True

#the loop that opens the window and allows you to place particles.
while running:
    #gets the mouse position for future use.
    x_pos, y_pos = pygame.mouse.get_pos()

    x_pos -= 5
    y_pos -= 5

    #this is here so the screen refreshes so the particles move on the screen.
    screen.fill((0,0,0))

    #draws all the particles onto the screen by adding them to particle_list.
    for particle, image in particle_list:
        screen.blit(image, (particle.x, particle.y))

    #how the buttons get put onto the screen.
    if user_note_button.menu_visible:
        screen.blit(under_construction, (X_POS_NOTE_MENU, Y_POS_NOTE_MENU))
    else:
        pass

    if exit_button.draw(screen):
        running = False
    else:
        pass

    if help_button.menu_visible:
        screen.blit(help_menu, (X_POS_HELP_MENU, Y_POS_HELP_MENU))
    else:
        pass

    exit_button.draw(screen)
    user_note_button.draw(screen)
    help_button.draw(screen)

    #creates a dictionary for each particle by looping through the particle list
    physics_data = [{'x': particle.x, 'y': particle.y, 'charge': particle.charge, 'mass': particle.mass}
                    for particle, _ in particle_list]

    #how the forces are called in the main simulator.
    em_force = Electromagnetic_force()
    strong_force_instance = strong_nuclear_force()

    em_forces = em_force.calculate_net_force(physics_data)
    strong_forces = strong_force_instance.calculate_net_force(physics_data)

    #set the max speed and the scale of the damping force.
    MAX_SPEED = 25
    DAMPING = 0.20

    #how particles move on the screen by finding there velocities and accelerations.
    #it then updates the position of the particle based of these.

    for i, (particle, _) in enumerate(particle_list):

        fx, fy = (
            em_forces[i][0] + strong_forces[i][0],
            em_forces[i][1] + strong_forces[i][1]
        )

        #acceleration values for the particles.
        if particle.mass != 0:
            ax = fx / particle.mass
            ay = fy / particle.mass
        else:
            ax = 1
            ay = 1

        #updates the velocity.
        particle.vx += ax
        particle.vy += ay

        #applies the damping.
        particle.vx *= DAMPING
        particle.vy *= DAMPING

        #caps the velocity.
        speed = maths.hypot(particle.vx, particle.vy)
        if speed > MAX_SPEED:
            scale = MAX_SPEED / speed
            particle.vx *= scale
            particle.vy *= scale
        else:
            pass

        #updates the position of the particles.
        particle.x += particle.vx
        particle.y += particle.vy

    #the loop that handles the events of the game.
    for event in pygame.event.get():
        #event that allows you to quit the game when you press the x button on the window bar.
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        #allows the notes button to stay in the top right corner of the screen.
        elif event.type == pygame.VIDEORESIZE:
            screen_width, screen_height = event.w, event.h
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
            button_x = screen_width - 100
            button_y = 0
            user_note_button = Notes_Button(button_x, button_y, user_note_img)
        #selection that allows you to place particles down.
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                p = Baryon.proton(x_pos, y_pos)
                particle_list.append((p, proton_img))
            if event.key == pygame.K_e:
                e = Lepton.electron(x_pos, y_pos)
                particle_list.append((e, electron_img))
            if event.key == pygame.K_n:
                n = Baryon.neutron(x_pos, y_pos)
                particle_list.append((n, neutron_img))
            if event.key == pygame.K_v:
                v = Lepton.neutrino(x_pos, y_pos)
                particle_list.append((v, neutrino_img))
            if event.key == pygame.K_BACKSPACE:
                if len(particle_list) >= 1:
                    particle_list.pop()
            if event.key == K_DELETE:
                #returns the current modifier key
                mods = pygame.key.get_mods()
                #cheaks if control is being held
                if mods & pygame.KMOD_CTRL:
                    particle_list.clear()
    #Updates the display at 60 frames per second.
    pygame.display.update()
    clock.tick(60)