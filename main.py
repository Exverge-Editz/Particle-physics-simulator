import pygame # type: ignore
from sys import exit
from pygame import Surface # type: ignore 
from particles import *
import user_notes
import Help_button_code
from forces import *
import math as maths
import time

pygame.init()
#gets the information of the monitor so the window is about the same size of the screen
info = pygame.display.Info()
screen_width, screen_height = int(info.current_w//1.13), int(info.current_h//1.13)
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Particle Physics simulator")
clock = pygame.time.Clock()

#the images for the particles
proton_img: Surface = pygame.image.load("proton.png").convert_alpha()
neutron_img: Surface = pygame.image.load("neutron.png").convert_alpha()
electron_img: Surface = pygame.image.load("electron.png").convert_alpha()

#the image for the user note button
user_note_img: Surface = pygame.image.load("user_note.png").convert_alpha()

#the image for the help button
help_button_img: Surface = pygame.image.load("help_button.png").convert_alpha()

#image for the help menu
help_menu: Surface = pygame.image.load("help_menu.png").convert_alpha()
help_menu = pygame.transform.scale(help_menu,(500, 500))

#the initial position of the user notes button
user_note_button = user_notes.Notes_button(screen_width - 10, 0, user_note_img)
help_button = Help_button_code.Help_button(0,0, help_button_img)


#list of all the particles on the screen and there position so they don't disappear
particle_list = []

#the loop that opens the window and allows you to place particles
while True:
    #gets the mouse position for future use
    x, y = pygame.mouse.get_pos()

    #this is here so the screen refreshes so the particles move on the screen
    screen.fill((0,0,0))

    #puts the user notes button on the screen
    if user_note_button.draw(screen):
        print("clicked")
    else:
        pass

    if help_button.draw(screen):
        screen.blit(help_menu, (100, 100))
        #print("help")
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
        ax = fx / particle.mass
        ay = fy / particle.mass

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
            button_x = screen_width - 10
            button_y = 0
            user_note_button = user_notes.Notes_button(button_x, button_y, user_note_img)
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

    #Updates the display at 60 frames per second
    pygame.display.update()
    clock.tick(60)
