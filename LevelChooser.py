#!/usr/bin/python3
# -*- coding: utf-8 -*-

##################################################
################################################## LEVELCHOOSER.PY
##################################################

import pygame
from pygame.locals import *

from utilities import *


class LevelChooser(pygame.Surface):
    '''
    LevelChooser is the part of the game that will allow the player to choose a level in a beautiful scrollable menu.
    There is only one LevelChooser instance for any Zardow instance.
    '''
    def __init__(self, size, items=[]):
        self.rect = pygame.Rect(0, 0, size, size)
        pygame.Surface.__init__(self,size = (size, size))
        self.scroll_y = 0

        self.items = items

        background = load_image('Ressources/Backgrounds/earth.png')
        width = int(size * (background.get_width()/800))
        self.background = pygame.transform.scale(background, (width, size))
        self.button_image = load_image('Ressources/Hud/choiceButton.png', (500, 60))

        self.font_baloo32 = pygame.font.Font('Ressources/Fonts/Baloo.ttf', 32)

        self.rects = []

        self.scrolling_speed = 10 # scrolling_y delta

    def move(self, direction):
        '''
        Called when the player scoll the menu up or down.
        Parameters:
            direction (int) : Positive number if scroll up (go down), negative number if scroll down (go up)
        '''
        number_of_levels = len(list(filter(lambda d: 'animation' not in d, self.items)))
        self.scroll_y += direction * self.scrolling_speed
        self.scroll_y = max(0, self.scroll_y)
        self.scroll_y = min((number_of_levels-7)*(self.get_height() / 7) + 64, self.scroll_y)

    def draw(self, surface):
        '''
        Render the level selector and show it on the specified surface.
        '''
        self.blit(self.background, (0, 0))
        self.rects = []

        texty = (40 - self.scroll_y)
        text = self.font_baloo32.render('Choose a level:', True, (255, 255, 255))
        text_rect = text.get_rect( center=(self.get_width() / 2, texty) )
        self.blit(text, text_rect)

        for index,item in enumerate(self.items):
            if 'animation' not in item:
                button_image = load_image('Ressources/Menu/%s.png'%item['environment'], (500, 60))

                x = self.get_width() / 2 - button_image.get_width() / 2
                y = 64 + (32 - self.scroll_y) + (index * (self.get_height() / 7))


                self.blit(button_image, (x, y))

                text = self.font_baloo32.render(item['name'], True, (255, 255, 255))
                text_rect = text.get_rect( center=(self.get_width() / 2,(y + (button_image.get_height() / 2) )))
                self.blit(text, text_rect)

                rect = pygame.Rect(x, y, button_image.get_width(), button_image.get_height())
                self.rects.append((rect, index))

        surface.blit(self,(0,0))

    def select(self, position):
        '''
        Called when user click on the level selector.
        It the clicked position ties in a level button, then returns the index of the level in the self.items list.
        Parameters:
            position ( tuple(x, y) ) : The position of the mouse when clicked
        Returns:
            int : The index of the level
        '''
        x, y = position
        #if x > (self.get_width() / 2 - self.button_image.get_width() / 2) and (x < self.get_width() / 2 + self.button_image.get_width() / 2):
        for rect, item in self.rects:
            if rect.collidepoint(position):
                return item
