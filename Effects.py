#!/usr/bin/python3
# -*- coding: utf-8 -*-

##################################################
################################################## EFFECTS.PY
##################################################

import pygame
import random
import math
import os

from utilities import *

class TextureAlternatingMode:
    RANDOMLY = 0 # Textures spawn with a random texture from the list
    TIMED = 1 # Texture will spawn with the first texture of the list and textures will evolve.

def getTexturesFromDirectory(path):
    '''
    Get a list of every textures of a path.
    Parameters:
        path (string) : The path to the folder containing the textures
   
    Returns:
        [str, ...] : The list contaning paths of all the textures
    '''
    
    relative_path = os.path.relpath(path)
    content = os.listdir(path)
    joiner = lambda item: os.path.join(relative_path, item)
    filtered = lambda item: not item.startswith('.')
    textures = list(map(joiner, filter(filtered, content)))
    return textures    

class UniformEffect(object):
    '''
    A Uniform effect is an effect in which particles will follow a straight trajectory before disappearing.
    
    '''
    def __init__(self, coords, textures, quantity = 10, radius_max = 10, age_max = 10, textures_alternating_mode = TextureAlternatingMode.RANDOMLY):
        self.textures = textures
        self.quantity = quantity
        self.radius_max = radius_max
        self.age_max = age_max
        self.textures_alternating_mode = textures_alternating_mode
        
        self.particles = []
        
        self.loaded_textures = list(map(load_image, self.textures))          
        
        for _ in range(self.quantity):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(1, self.radius_max)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            if self.textures_alternating_mode == TextureAlternatingMode.RANDOMLY:
                texture = random.choice(self.textures)
            else:
                texture = self.textures[0]
            
            particle = UniformParticle(texture)
            particle.radius_max = self.radius_max
            particle.start_coordinates = coords
            particle.speed = (x, y)
            
            self.particles.append(particle)
            
    def present(self): 
        '''
        Make particles evolve
        '''
        for particle in self.particles:
            particle.age += 1
            
            if particle.age >= self.age_max:
                self.particles.remove(particle)
                break
            
            if self.textures_alternating_mode == TextureAlternatingMode.TIMED:
                particle.image = self.loaded_textures[particle.age]
            
            particle.update()
            
            
            
    def show(self, surface):
        '''
        Show the particles on a surface
        Parameters:
            surface (pygame.surface.Surface) : The surface on which show the particles
        '''
        for particle in self.particles:
            particle.show(surface)
            

class UniformParticle(pygame.sprite.Sprite):
    '''
    A UniformParticle will be shown by a UniformEffect.
    A UniformParticle will move on a straight line before disappearing.
    '''
    def __init__(self, texture):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(texture)
        self.x = self.y = 0
        
        self.age = 0
        
    def update(self):
        start_x, start_y = self.start_coordinates
        self.x = start_x + self.speed[0] * self.age
        self.y = start_y + self.speed[1] * self.age
        
        
    def show(self, surface):
        surface.blit(self.image, (self.x, self.y))
        
        
        
# Gravity effects        
        
        
        
        
class GravityEffect(object):
    '''
    A GravityEffect is an effect in which particles will fall to the ground.
    '''
    def __init__(self, coords, textures, quantity = 10, age_max = 10):
        self.textures = textures
        self.quantity = quantity
        self.age_max = age_max
        #self.acceleration = acceleration
        #self.speed = speed
        
        self.particles = []
        
        for _ in range(self.quantity):
            angle = 0 - random.uniform(0,math.pi)
            x = 5
            y = 5
            
            start_x, start_y = coords
            delta_start_x = 0
            delta_start_y = 0
            
            texture = random.choice(self.textures)
            
            particle = GravityParticle(texture)
            particle.start_coordinates = (start_x + delta_start_x, start_y + delta_start_y)
            particle.angle = angle
            particle.speed = (x, y)
            
            self.particles.append(particle)
            
    def present(self): 
        '''
        Make particles evolve
        '''
        for particle in self.particles:
            particle.age += 1
            particle.update()
            
            if particle.age >= self.age_max:
                self.particles.remove(particle)
            
            
    def show(self, surface):
        '''
        Show the particles on a surface
        Parameters:
            surface (pygame.surface.Surface) : The surface on which show the particles
        '''
        for particle in self.particles:
            particle.show(surface)
            

class GravityParticle(pygame.sprite.Sprite):
    '''
    A GravityParticle is shown by a GravityEffect
    A GravityParticle will fall to the ground.
    '''
    def __init__(self, texture):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(texture)
        self.x = self.y = 0
        
        self.age = 0
        
    def update(self):
        start_x, start_y = self.start_coordinates
        self.x = math.cos(self.angle) * self.speed[0] * self.age + start_x
        self.y = (self.age ** 2) + math.sin(self.angle) * self.speed[1] * self.age + start_y
            
        
    def show(self, surface):
        surface.blit(self.image, (self.x, self.y))
        
        
        
class Animation(pygame.sprite.Sprite):
    '''
    An Animation is a visual effect the purpose of which is to show sequence of images on the full window.
    It has no "particle" associated class
    '''
    def __init__(self, images, size, image_duration = 5, repeat = False, completion = None, hide_cursor = False):
        self.images = images
        self.loaded_textures = list(map(lambda i: load_image(i, (size, size)), self.images))
        
        self.texture = self.loaded_textures[0]
        self.image_duration = image_duration
        self.repeat = repeat
        self.completion = completion
        self.hide_cursor = hide_cursor
        
        self.age = 0
        self.image_index = 0
        
        
    
    def present(self):
        self.age += 1
        if self.age%self.image_duration == 0:
            if (self.image_index + 1) < len(self.images):
                self.image_index += 1
                if self.hide_cursor:
                    pygame.mouse.set_visible(False)
            else:
                if self.hide_cursor:
                    pygame.mouse.set_visible(True)
                self.completion.__call__()
            
        self.texture = self.loaded_textures[self.image_index]
        
    def show(self, surface):
        surface.blit(self.texture, (0, 0))
