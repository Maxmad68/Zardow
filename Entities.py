#!/usr/bin/python3
# -*- coding: utf-8 -*-

##################################################
################################################## ENTITIES.PY
##################################################

from utilities import *
#import pygame
import os
import Tiles
import Effects

class Direction:
    RIGHT = 1
    LEFT = -1
    FACE = 0

    @staticmethod
    def reverse(direction):
        if direction == Direction.RIGHT:
            return Direction.LEFT
        elif direction == Direction.LEFT:
            return Direction.RIGHT


class Entity(object):
    image_side = 50
    def __init__(self, *args,**kwargs):
        self.direction = Direction.RIGHT
        self.speed = 0.1 # Bloc per frame ( this * fps = velocity in bloc/sec )
        self.velocity = self.speed # CURRENT velocity
        # Speed is the ability of the character to move.
        # Velocity is the CURRENT speed of the character.
        # For example, the speed can be 0.1 bpf, but the velocity is 0. This means the character normaly walks with a speed of 0.1 bpf but is now stationary.

        self.travelable_in_portals = True

        self.face_image = ''
        self.walk_cycle_images = []
        self.ressources_name = 'Entity'
        self.scale = (1, 1)
        self.alternate_image = None

        self.subject_gravity = True
        self.falling_time = 0 # For gravity calculation
        self.start_y = 0 # For gravity calculation

        self.dead = False

        self.just_travelled_in_portal = False
        self.just_pressed_button = False

        self.position = (0, 0)
        self.anchor_point = (0, 0)

    def import_ressources(self):
        '''
        Import images
        '''
        real_size = (self.size[0] * Entity.image_side, self.size[1] * Entity.image_side)
        self.walk_cycle_images_instances_left = list(map(lambda path: load_image(os.path.join('Ressources', self.ressources_name, 'Left', path), real_size), self.walk_cycle_images))
        self.walk_cycle_images_instances_right = list(map(lambda path: load_image(os.path.join('Ressources', self.ressources_name, 'Right', path), real_size), self.walk_cycle_images))
        self.face_image_instance = load_image(os.path.join('Ressources', self.ressources_name, self.face_image), real_size)
        if self.alternate_image:
            self.alternate_image_instance = load_image(os.path.join('Ressources',self.ressources_name, self.alternate_image), real_size)


    def get_image(self, antigravity = False):
        '''
        Return the current image that should be displayed
        Parameters:
            antigravity = False (bool) : If True, image will be vertically reversed
        Returns:
            pygame.surface.Surface : The image of the entity that should be displayed
        '''
        image = self.face_image_instance
        if antigravity: # If gravity is reversed: flip image vertically
            image = pygame.transform.flip(image, False, True)
        return image

    def position_in_block_getter(self):
        '''
        Getter of the self.position_in_block property.
        Returns:
            float : The horizontal position between two tiles
        '''
        return (self.position[0]%1)
        
    position_in_block = property(position_in_block_getter)


    def update(self, instance = None):
        '''
        Executed on each update of the game
        Useful to implement non default behaviours for an entity
        Parameters:
            instance (Zardow) : The instance of the main game. Useful to retrieve arguments of to act directly on the game behaviour.
        '''
        pass

    def kill(self):
        '''
        Change parameters to make the entity dead
        '''
        self.dead = True
        self.size = (0,0)
        self.velocity = 0
        self.subject_gravity = False

    


class Zardow(Entity):
    '''
    The default entity which represents the main character of the game
    It has a 9 images walk cycle and is subject to gravity.
    '''
    def __init__(self, image_size = 40, *args,**kwargs):
        Entity.__init__(self,*args,**kwargs)

        self.travelable_in_portals = True
        self.direction = Direction.RIGHT
        self.speed = 0.1
        self.subject_gravity = True

        self.ressources_name = 'Entity/Zardow'
        self.size = (1,1)

        self.walk_cycle_images = ['Face.png','1.png','2.png','3.png','4.png','5.png','6.png','7.png','8.png','9.png']
        self.face_image = 'Face.png'

        self.import_ressources()
        
    def get_image(self, antigravity = False):
        '''
        Overriding Entity.get_image
        
        Return the good image of the walk cycle depending of the horizontal position inside the current tile (position_in_block)
        
        Parameters: see Entity.get_image
        Returns: see Entity.get_image
        '''
        if self.velocity > 0: # Moving

            if self.direction == Direction.LEFT: #elif?
                walking_cycle_offset = int(self.position_in_block / (1 / float(len(self.walk_cycle_images_instances_left)-1)))+1
                walking_cycle_offset = walking_cycle_offset % len(self.walk_cycle_images_instances_right)
                image = self.walk_cycle_images_instances_left[walking_cycle_offset]

            elif self.direction == Direction.RIGHT:
                walking_cycle_offset = int(self.position_in_block / (1 / float(len(self.walk_cycle_images_instances_right)-1)))+1
                walking_cycle_offset = walking_cycle_offset % len(self.walk_cycle_images_instances_right)
                image = self.walk_cycle_images_instances_right[walking_cycle_offset]

        else: # Stopped

            if self.direction == Direction.LEFT:
                image = self.walk_cycle_images_instances_left[0]

            elif self.direction == Direction.RIGHT:
                image = self.walk_cycle_images_instances_right[0]

        if antigravity: # If gravity is reversed: flip image vertically
            image = pygame.transform.flip(image, False, True)

        return image


class Rocket(Entity):
    '''
    The rocket is the goal of the main character.
    It has globally no behaviour, except when the main character reach it, then the rocket takes-off with showing fire particles.
    It has only one image and is not subject to gravity
    '''
    def __init__(self, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)

        self.travelable_in_portals = False
        self.direction = Direction.LEFT
        self.speed = 0
        self.subject_gravity = False

        self.walk_cycle_images = []
        self.ressources_name = 'Entity/Rocket'
        self.size = (1, 2)
        self.anchor_point = (0, 1)

        self.zardow_is_in = False

        self.face_image = 'Standing.png'
        self.alternate_image = 'WithZardow.png'

        self.import_ressources()

    def get_image(self, antigravity = False):
        '''
        Overriding Entity.get_image
        
        Return a rocket with Zardow inside image if Zardow reached the Rocket, the normal image otherwise.
        
        Parameters: see Entity.get_image
        Returns: see Entity.get_image
        '''

        if self.zardow_is_in:
            return self.alternate_image_instance
        else:
            return self.face_image_instance

    def update(self, instance):
        '''
        Overriding Entity.update
        
        Rocket specific behaviour:
            If Zardow is in the rocket, make it take-off (increase vertical position by 0.1 every fps)
        
        Parameters: see Entity.update
        Returns: see Entity.update
        '''
        if self.zardow_is_in:
            self.position = (self.position[0] + 0.1, self.position[1] + 1)
            
            smoke_textures = Effects.getTexturesFromDirectory('Ressources/Particles/SmokeAndFire')
            smoke_effect = Effects.UniformEffect(((self.position[0] + 0.3) * instance.tile_side_size, (instance.mapsize[1] - self.position[1]) * instance.tile_side_size), smoke_textures, quantity = 2, radius_max = 3, age_max = 3, textures_alternating_mode = Effects.TextureAlternatingMode.RANDOMLY)
            instance.effects.append(smoke_effect)
                        
            if max(self.position) > 19: # If rocket out of the map
                self.position = (18, 18)
                self.size = (0, 0) # Invisible
                self.import_ressources()
                self.zardow_is_in = False # End animation


class MovingBox(Entity):
    '''
    A Moving box act like a non-traversable tile, making entities stop and not able to cross them.
    It has only one image and is subject to gravity
    '''
    def __init__(self, *args, **kwargs):
        Entity.__init__(self, *args, **kwargs)
                
        #self.image_side = 40
                
        self.travelable_in_portals = True
        self.direction = Direction.FACE
        self.speed = 0
        self.subject_gravity = True

        self.walk_cycle_images = []
        self.ressources_name = 'Entity/MovingBox'
        self.size = (1, 1)

        self.face_image = 'Face.png'

        self.import_ressources()

    def get_image(self, antigravity = False):
        '''
        Overriding Entity.get_image
        
        Return always the same image for it not to be vertically flip(ped?) when gravity is reversed (very ugly)
        
        Parameters: see Entity.get_image
        Returns: see Entity.get_image
        '''
        return self.face_image_instance
