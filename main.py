import pygame
from pygame import Surface, KMOD_CTRL, K_DELETE, K_BACKSPACE
from particles import *
from buttons import *
from forces import *
import math as maths

pygame.init()

# -----------------------------------------------------------------------------
# Display & window initialization
# -----------------------------------------------------------------------------
# This section sets up the display/window and timing primitives.
#
# Details:
#   - pygame.display.Info():
#       Queries the current display/monitor properties (width/height in pixels).
#   - pygame.display.set_mode((w, h), pygame.RESIZABLE):
#       Creates a resizable window so the UI can adapt to user-driven changes.
#   - pygame.display.set_caption():
#       Sets the window title.
#   - clock:
#       Used to cap the frame rate for consistent timing and reduced CPU usage.
# -----------------------------------------------------------------------------
info = pygame.display.Info()
screen_width, screen_height = int(info.current_w), int(info.current_h)
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Particle Physics simulator")
clock = pygame.time.Clock()

# -----------------------------------------------------------------------------
# Utility: crop_transparency(image) -> Surface
# -----------------------------------------------------------------------------
# Purpose:
#   Trim fully transparent borders from sprites so rendering/interaction uses a
#   tight bounding box.
#
# Details:
#   - get_bounding_rect():
#       Returns a Rect that bounds all pixels with alpha > 0.
#   - subsurface(rect).copy():
#       Cuts the image down to that rectangle and returns an independent Surface
#       copy, so later operations don’t reference the original larger surface.
# -----------------------------------------------------------------------------
def crop_transparency(image: pygame.Surface) -> pygame.Surface:
    rect = image.get_bounding_rect()  # Finds non-transparent area
    return image.subsurface(rect).copy()

# -----------------------------------------------------------------------------
# Asset loading (images) & scaling
# -----------------------------------------------------------------------------
# Steps:
#   1) Load -> convert_alpha() to preserve per-pixel alpha.
#   2) crop_transparency() to reduce draw footprint and improve precision.
#   3) Scale menu overlays relative to window size for an initial layout fit.
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# UI layout constants
# -----------------------------------------------------------------------------
# These constants define anchor positions for buttons and menus.
#
# Notes:
#   - The notes button is initially anchored to the right edge (screen_width - 100)
#     and will be repositioned to the right edge if the screen is resized
# -----------------------------------------------------------------------------
X_POS_HELP_BUTTON = 125
Y_POS_HELP_BUTTON = 0

X_POS_EXIT_BUTTON = 0
Y_POS_EXIT_BUTTON = 0

X_POS_NOTE_BUTTON = screen_width - 100
Y_POS_NOTE_BUTTON = 0

# -----------------------------------------------------------------------------
# Menu placement constants
# -----------------------------------------------------------------------------
# Top-left anchors for overlays.
# -----------------------------------------------------------------------------
X_POS_HELP_MENU = 100
Y_POS_HELP_MENU = 100

X_POS_NOTE_MENU = 100
Y_POS_NOTE_MENU = 100

# -----------------------------------------------------------------------------
# UI controls: instantiate buttons
# -----------------------------------------------------------------------------
# Each button class manages its own drawing and state (e.g., menu_visible).
# -----------------------------------------------------------------------------
help_button = Help_Button(X_POS_HELP_BUTTON, Y_POS_HELP_BUTTON, help_button_img)
exit_button = Exit_Button(X_POS_EXIT_BUTTON, Y_POS_EXIT_BUTTON, exit_button_img)
user_note_button = Notes_Button(X_POS_NOTE_BUTTON, Y_POS_NOTE_BUTTON, user_note_img)

# -----------------------------------------------------------------------------
# Simulation state containers
# -----------------------------------------------------------------------------
#   - particle_list:
#       A list of (particle_object, sprite_surface) used for update and render.
#   - running:
#       Main loop control flag.
# -----------------------------------------------------------------------------
particle_list = []

running = True

# -----------------------------------------------------------------------------
# Main loop: input → update → render → events → present
# -----------------------------------------------------------------------------
# Order each frame:
#   1) Sample continuous input (mouse position).
#   2) Clear the screen and draw particles (world).
#   3) Draw UI (buttons/menus).
#   4) Build physics input, compute forces, integrate motion.
#   5) Process event queue (window/keyboard).
#   6) Present frame & cap FPS.
# -----------------------------------------------------------------------------
while running:

    # -----------------------------------------------------------------------------
    # Input sampling (continuous state)
    # -----------------------------------------------------------------------------
    # Reads current cursor position and offsets slightly so sprite placement
    # aligns closer to the cursor tip.
    # -----------------------------------------------------------------------------
    x_pos, y_pos = pygame.mouse.get_pos()

    x_pos -= 5
    y_pos -= 5

    # -----------------------------------------------------------------------------
    # Frame clear
    # -----------------------------------------------------------------------------
    # Fill backbuffer before drawing everything for this frame.
    # -----------------------------------------------------------------------------
    screen.fill((0,0,0))

    # -----------------------------------------------------------------------------
    # World rendering: particles
    # -----------------------------------------------------------------------------
    # Draw every (particle, image) at the particle's (x, y) position.
    # -----------------------------------------------------------------------------
    for particle, image in particle_list:
        screen.blit(image, (particle.x, particle.y))

    # -----------------------------------------------------------------------------
    # UI overlays & buttons
    # -----------------------------------------------------------------------------
    # Notes overlay (currently under construction).
    # -----------------------------------------------------------------------------

    # Exit button: .draw() can return True when clicked to request termination.
    if exit_button.draw(screen):
        running = False
    else:
        pass

    # Help overlay when visible.
    if help_button.menu_visible:
        screen.blit(help_menu, (X_POS_HELP_MENU, Y_POS_HELP_MENU))
    else:
        pass

    if user_note_button.menu_visible:
        screen.blit(under_construction, (X_POS_HELP_MENU, Y_POS_HELP_MENU))
    else:
        pass

    # Draw static buttons each frame (hover/click visuals may be internal).
    exit_button.draw(screen)
    user_note_button.draw(screen)
    help_button.draw(screen)

    # -----------------------------------------------------------------------------
    # Physics input build
    # -----------------------------------------------------------------------------
    # Converts particles into a simple, immutable structure that force modules
    # can consume safely.
    #
    # Each entry:
    #   { 'x': float, 'y': float, 'charge': float, 'mass': float }
    # -----------------------------------------------------------------------------
    physics_data = [{'x': particle.x, 'y': particle.y, 'charge': particle.charge, 'mass': particle.mass}
                    for particle, _ in particle_list]

    #------------------------------------------------------------------------------
    # Force evaluation
    # -----------------------------------------------------------------------------
    # Instantiates force models and computes net forces per particle for this frame.
    #
    # Notes:
    #   - em_forces[i] and strong_forces[i] correspond to particle_list[i].
    # -----------------------------------------------------------------------------
    em_force = Electromagnetic_force()
    strong_force_instance = strong_nuclear_force()

    em_forces = em_force.calculate_net_force(physics_data)
    strong_forces = strong_force_instance.calculate_net_force(physics_data)

    # -----------------------------------------------------------------------------
    # Integration parameters
    # -----------------------------------------------------------------------------
    #   - MAX_SPEED:
    #       Hard cap on velocity magnitude to prevent numeric explosions/tunneling.
    #   - DAMPING:
    #       Simple multiplicative damping factor (0 < DAMPING < 1) for stability.
    # -----------------------------------------------------------------------------
    MAX_SPEED = 25
    DAMPING = 0.20

    # -----------------------------------------------------------------------------
    # Motion integration: accelerate → damp → cap → advance
    # -----------------------------------------------------------------------------
    # Combines forces, computes acceleration (a = F / m), and updates velocity/position.
    #
    # Edge case:
    #   - For mass == 0, use a small fallback (ax=ay=1) to avoid division by zero.
    # -----------------------------------------------------------------------------
    for i, (particle, _) in enumerate(particle_list):

        fx, fy = (
            em_forces[i][0] + strong_forces[i][0],
            em_forces[i][1] + strong_forces[i][1]
        )

        # Acceleration from net force
        if particle.mass != 0:
            ax = fx / particle.mass
            ay = fy / particle.mass
        else:
            ax = 1
            ay = 1

        # Velocity update
        particle.vx += ax
        particle.vy += ay

        # Damping
        particle.vx *= DAMPING
        particle.vy *= DAMPING

        # Speed cap
        speed = maths.hypot(particle.vx, particle.vy)
        if speed > MAX_SPEED:
            scale = MAX_SPEED / speed
            particle.vx *= scale
            particle.vy *= scale
        else:
            pass

        # Position update
        particle.x += particle.vx
        particle.y += particle.vy

    # -----------------------------------------------------------------------------
    # Event processing: window, input, keyboard-driven particle placement
    # -----------------------------------------------------------------------------
    for event in pygame.event.get():
        # Window close (X button).
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # Resize handling
        #   - Recreate the display surface with the new size.
        #   - Re-anchor the notes button at the top-right (screen_width - 100, 0).

        elif event.type == pygame.VIDEORESIZE:
            screen_width, screen_height = event.w, event.h
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
            button_x = screen_width - 100
            button_y = 0
            user_note_button = Notes_Button(button_x, button_y, user_note_img)

        # -----------------------------------------------------------------------------
        # key_actions: maps keyboard keys to the action for creating a particle
        # -----------------------------------------------------------------------------
        # This dictionary is a lookup table where:
        #   - The KEY (e.g., pygame.K_p) identifies which keyboard key was pressed.
        #   - The VALUE is a 2-item tuple: (constructor, image)
        #       * constructor: a callable (function/classmethod) that returns a new
        #         particle when called with (x_pos, y_pos).
        #       * image: the pygame.Surface sprite used to render that particle.
        # -----------------------------------------------------------------------------
        key_actions = {
            pygame.K_p: (Baryon.proton, proton_img),
            pygame.K_e: (Lepton.electron, electron_img),
            pygame.K_n: (Baryon.neutron, neutron_img),
            pygame.K_v: (Lepton.neutrino, neutrino_img),
        }

        # -----------------------------------------------------------------------------
        # Keyboard input handling (KEYDOWN):
        # -----------------------------------------------------------------------------
        # This section responds to key presses and performs three types of actions:
        #   1) Backspace: remove the most recently placed particle (if any exist).
        #   2) Ctrl + Delete: clear ALL particles.
        #   3) Single-key particle placement via the key_actions dictionary.
        #
        # Details:
        #   - mods = pygame.key.get_mods():
        #       Retrieves the current modifier keys (Ctrl, Shift, Alt) as a bitmask.
        #       We use this to detect key combinations like Ctrl + Delete.
        #
        #   - Backspace behavior:
        #       If the user presses Backspace and there is at least one particle
        #       (len(particle_list) >= 1), we pop the last entry to "undo" the most
        #       recent placement.
        #
        #   - Ctrl + Delete behavior:
        #       If Ctrl is held (mods & pygame.KMOD_CTRL) AND the Delete key is pressed,
        #       we call particle_list.clear() to remove all particles at once.
        #
        #   - Dictionary-based particle placement:
        #       If the pressed key exists in key_actions:
        #           * Unpack (constructor, image) from the mapping.
        #           * Create the particle at the current cursor (x_pos, y_pos).
        #           * Append (particle, image) to particle_list for update & rendering.
        #
        # Notes:
        #   - The order of checks matters:
        #       * We handle "special" keys (Backspace, Ctrl+Delete) first.
        #       * Then we fall back to normal single-key actions defined in key_actions.
        #   - key_actions is defined elsewhere and maps keys like pygame.K_p to a
        #     (constructor, image) pair. This keeps the event logic clean and scalable.
        # -----------------------------------------------------------------------------
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            if event.key == K_BACKSPACE and len(particle_list) >= 1:
                particle_list.pop()
            if mods & pygame.KMOD_CTRL and event.key == pygame.K_DELETE:
                particle_list.clear()
            elif event.key in key_actions:
                constructor, image = key_actions[event.key]
                particle = constructor(x_pos, y_pos)
                particle_list.append((particle, image))

    # -----------------------------------------------------------------------------
    # Frame present & pacing
    # -----------------------------------------------------------------------------
    #   - pygame.display.update(): swaps the backbuffer to the screen.
    #   - clock.tick(60): caps the frame rate at ~60 FPS for consistent timing.
    # -----------------------------------------------------------------------------
    pygame.display.update()
    clock.tick(60)