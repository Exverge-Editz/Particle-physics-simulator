import pygame
from sys import exit
from pygame import Surface
from particles import *
from buttons import *
from forces import *
import math as maths

pygame.init()
#gets the information of the monitor so the window is the same size of the user's screen
info = pygame.display.Info()
screen_width, screen_height = int(info.current_w), int(info.current_h)
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Particle Physics simulator")
clock = pygame.time.Clock()

#the images for the particles
proton_img: Surface = pygame.image.load("proton.png").convert_alpha()
neutron_img: Surface = pygame.image.load("neutron.png").convert_alpha()
electron_img: Surface = pygame.image.load("electron.png").convert_alpha()
neutrino_img: Surface = pygame.image.load("neutrino.png").convert_alpha()

#the image for the exit button
exit_button_img: Surface = pygame.image.load("exit_button.png").convert_alpha()

#the image for the user note button
user_note_img: Surface = pygame.image.load("user_note.png").convert_alpha()

#the image for the help button
help_button_img: Surface = pygame.image.load("help_button.png").convert_alpha()

#image for the help menu
help_menu: Surface = pygame.image.load("help_menu.png").convert_alpha()
help_menu = pygame.transform.scale(help_menu,((screen_width* 0.95), (screen_height*1.3)))

help_button = Help_Button(125, 1.5, help_button_img)
exit_button = Exit_Button(0, 0, exit_button_img)
user_note_button = Notes_Button((screen_width - 100), 0, user_note_img)


#list of all the particles on the screen and there position so they don't disappear
particle_list = []

#the loop that opens the window and allows you to place particles
while True:
    #gets the mouse position for future use
    x, y = pygame.mouse.get_pos()

    #this is here so the screen refreshes so the particles move on the screen
    screen.fill((0,0,0))

    #puts the buttons on the screen
    if user_note_button.draw(screen):
        print("clicked")
    else:
        pass

    if exit_button.draw(screen):
        exit()
    else:
        pass

    help_button.draw(screen)
    if help_button.menu_visible:
        screen.blit(help_menu, (100, 100))
    else:
        pass

    #dictionary that allows for all the particle positions and their properties to be put into the forces
    physics_data = [{'x': particle.x, 'y': particle.y, 'charge': particle.charge, 'mass': particle.mass}
                    for particle, _ in particle_list]

    #how the forces are called in the main simulator
    em_force = Electromagnetic_force()
    strong_force_instance = strong_nuclear_force()

    em_forces = em_force.calculate_net_force(physics_data)
    strong_forces = strong_force_instance.calculate_net_force(physics_data)

    #set the max speed and the scale of the damping force
    MAX_SPEED = 25
    DAMPING = 0.20

    #how particles move on the screen by finding there velocities and accelerations
    #it then updates the position of the particle based of these

    for i, (particle, _) in enumerate(particle_list):

        fx, fy = (
            em_forces[i][0] + strong_forces[i][0],
            em_forces[i][1] + strong_forces[i][1]
        )

        #acceleration values for the particles
        if particle.mass != 0:
            ax = fx / particle.mass
            ay = fy / particle.mass
        else:
            ax = 1
            ay = 1

        #updates the velocity
        particle.vx += ax
        particle.vy += ay

        #applies the damping
        particle.vx *= DAMPING
        particle.vy *= DAMPING

        #caps the velocity
        speed = maths.hypot(particle.vx, particle.vy)
        if speed > MAX_SPEED:
            scale = MAX_SPEED / speed
            particle.vx *= scale
            particle.vy *= scale
        else:
            pass

        #updates the position of the particles
        particle.x += particle.vx
        particle.y += particle.vy

    #draws all the particles onto the screen by adding them to particle_list
    for particle, image in particle_list:
        screen.blit(image, (particle.x, particle.y))

    #the loop that handles the events of the game
    for event in pygame.event.get():
        #event that allows you to quit the game when you press the x button on the window bar
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        #allows the notes button to stay in the top right corner of the screen
        elif event.type == pygame.VIDEORESIZE:
            screen_width, screen_height = event.w, event.h
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
            button_x = screen_width - 100
            button_y = 0
            user_note_button = Notes_Button(button_x, button_y, user_note_img)
        #selection that allows you to place particles down
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                p = Baryon.proton(x, y)
                particle_list.append((p, proton_img))
            if event.key == pygame.K_e:
                e = Lepton.electron(x, y)
                particle_list.append((e, electron_img))
            if event.key == pygame.K_n:
                n = Baryon.neutron(x, y)
                particle_list.append((n, neutron_img))
            if event.key == pygame.K_v:
                v = Lepton.neutrino(x, y)
                particle_list.append((v, neutrino_img))

    #Updates the display at 60 frames per second
    pygame.display.update()
    clock.tick(60)
