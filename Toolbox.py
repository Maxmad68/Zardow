#!/usr/bin/python3
# -*- coding: utf-8 -*-

##################################################
################################################## TOOLBOX.PY
##################################################

import pygame

class Toolbox(pygame.Surface):
    tile_side_size = None
    '''
    Represents the toolbox of the game.
    It can contains up to 10 items.
    '''
    
    def __init__(self, items=[], selected=0):
        
        width = (10 * Toolbox.tile_side_size) + (11 * 8)
        height = Toolbox.tile_side_size + (2 * 16)
        self.rect = pygame.Rect(10, 10, width, height)
        
        pygame.Surface.__init__(self, size=(self.rect[2], self.rect[3]))
        
        self.items = items
        if self.items:
            self.selected_slot = selected
            self.selected_item = self.items[self.selected_slot]
        else:
            self.selected_slot = None
            self.selected_item = None
        
    def selectByClick(self, pos):
        '''
        Set the selected slot and the selected item according to the mouse position when a click was detected by the main game
        Parameters:
            pos ( tuple(x, y) ) : The position of the mouse click
        '''
        x = pos[0]
        
        slot = int((x - 8) / (Toolbox.tile_side_size + 8))
        self.selected_slot = min(9,slot)
        
        if self.selected_slot > len(self.items)-1:
            self.selected_slot = len(self.items)-1
        
        self.selected_item = self.items[self.selected_slot]
        
    def draw(self, surface):
        '''
        Draw the toolbox and its items on the specified surface
        '''
        self.fill((204,255,255))
        
        if self.items and (self.selected_slot != None):
            pygame.draw.rect(self, (220,220,220), (8 + (Toolbox.tile_side_size + 8) * self.selected_slot - 4, 8, Toolbox.tile_side_size + (4 * 2), Toolbox.tile_side_size + 16))
        
        
        for index,item in enumerate(self.items): 
            instance = item(size = (Toolbox.tile_side_size, Toolbox.tile_side_size))
        
            x = 8 + (Toolbox.tile_side_size + 8) * index
            y = (self.get_height()/2) - (instance.height /2)
        
            self.blit(instance.get_describing_image((Toolbox.tile_side_size, Toolbox.tile_side_size)), (x, y, instance.width, instance.height))
        
        surface.blit(self, (self.rect[0],self.rect[1]))
        
    def sort(self):
        '''
        Avoid having empty slots between items in the toolbox. It aligns every items on the left. 
        '''
        while None in self.items:
            self.items.remove(None)
        
        #self.selected_slot = 0
        
        if self.selected_slot > len(self.items)-1:
            self.selected_slot = len(self.items)-1
            
        if self.selected_slot<0:
            self.selected_item = None
        else:
            self.selected_item = self.items[self.selected_slot]