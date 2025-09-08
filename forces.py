import pygame
import math
from pygame import Vector2

class Electromagnetic_force:
    def __init__(self, COLOUMBS_CONSTANT=50):
        self.COLOUMBS_CONSTANT = COLOUMBS_CONSTANT

    def calculate_force(self, p1, p2):
        r_vec = pygame.math.Vector2(p2['x'], p2['y']) - pygame.math.Vector2(p1['x'], p1['y'])
        distance = r_vec.length()
        if distance < 1:
            return (0, 0)
        force_magnitude = -(self.COLOUMBS_CONSTANT * p1['charge']* p2['charge']) / (distance ** 2)
        force_direction = r_vec.normalize()
        force = force_magnitude * force_direction
        return (force.x, force.y)

    def calculate_net_force(self, particle):
        forces = []
        for i, p1 in enumerate(particle):
            net_force = pygame.math.Vector2(0, 0)
            for j, p2 in enumerate(particle):
                if i != j and p1['charge'] !=0 and p2['charge'] != 0 :
                    fx, fy = self.calculate_force(p1, p2)
                    net_force += pygame.math.Vector2(fx, fy)
            forces.append((net_force.x, net_force.y))
        return forces

class strong_nuclear_force:
    def __init__(self, H_BAR=1e10, E=3, COUPLING_CONSTANT=25, SPEED_OF_LIGHT=3000, MASS_CHARGED_PION=2.4e-28):
        self.H_BAR = H_BAR
        self.E = E
        self.COUPLING_CONSTANT = COUPLING_CONSTANT
        self.SPEED_OF_LIGHT = SPEED_OF_LIGHT
        self.MASS_CHARGED_PION = MASS_CHARGED_PION

    def calculate_force(self, p1, p2):
        r_vec = pygame.math.Vector2(p2['x'], p2['y']) - pygame.math.Vector2(p1['x'], p1['y'])
        distance = r_vec.length()
        if distance < 1:
            return (0, 0)
        inverse_range =self.MASS_CHARGED_PION*self.SPEED_OF_LIGHT/self.H_BAR
        force_magnitude = self.COUPLING_CONSTANT*((self.E**-(inverse_range*distance))/distance**1.75)
        force_direction = r_vec.normalize()
        force = force_magnitude * force_direction
        return (force.x, force.y)

    def calculate_net_force(self, particle):
        forces = []
        for i, p1 in enumerate(particle):
            net_force = pygame.math.Vector2(0, 0)
            for j, p2 in enumerate(particle):
                if i != j and p1['mass'] != 0.05 and p2['mass'] != 0.05 :
                    fx, fy = self.calculate_force(p1, p2)
                    net_force += pygame.math.Vector2(fx, fy)
            forces.append((net_force.x, net_force.y))
        return forces
