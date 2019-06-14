#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
   import contextlib
   with contextlib.redirect_stdout(None): # Import pygame without showing the "Hello from the pygame community" message (because it's boring)
      import pygame
      from pygame.locals import *
except ImportError:
   print ('Can\'t find module Pygame. Install it with "pip3 install pygame" (sudo permissions required)')
   exit()

import itertools
import time
import math
import imp
import os
import json

import Tiles
import Toolbox
import LevelChooser as lc
import Entities
from utilities import *
import Effects


def import_level_as_module(name):
   '''
   Import the level (as a module) for the given name
   Parameters:
      name (str) : The level name to load
   Returns:
      (module) : The level as a loaded module
      
   Note: The imp module used in this function seems to be deprecated.
   '''
   
   levelPath = 'Levels/'+name
   find = imp.find_module(levelPath)
   loaded = imp.load_module(levelPath,*find)
   return loaded

class Music: # Needed to convert to OGG because of a crash when filetype was WAV (maybe file was too large to be loaded?)
   Theme = 'Zardow Theme.ogg'
   Space = 'Zardow Space Theme.ogg'

   environment = {'earth':Theme,'space':Space}
   all = [Theme, Space]

class Zardow(object):
   '''
   Main class of the game
   '''
   def __init__(self,levelName = None):
      '''
      Constructor of the main game class.
      If a level name is specified, won't show the menu and start immediatly on this level.
      Parameters:
         levelName (str) : A level name to start immediatly
      '''

      self.window_size = 1000 # Keep 800 for 800x800 px
      self.window_title = "Zardow"
      self.bgcolor = (0,255,255) # blue

      self.running = True # Is mainloop looping
      self.key_repeat_time = 1 # Default: 1
      self.tile_side_size = int(self.window_size/20) # 40 for a 800px window sized
      
      Entities.Entity.image_side = self.tile_side_size
      Toolbox.Toolbox.tile_side_size = self.tile_side_size

      self.update_frequency = 20 # times per second (= fps / = Hz)

      self.mouse_position = (0,0) # Will be updated in the mainloop

      self.is_choosing_level = False # Is the user in the level chooser
      self.init_window()

      self.load_sounds(['breakingBox','gravity','lose','putTile','teleport','antimatter','enough antimatter','spring','rocket','hover'])

      self.playing_music_name = None

      #Build the map
      if levelName:
         self.is_menu = False # True if user is in the menu, False if the user is playing
         self.load_level(levelName)
      else:
         self.is_menu = True
         self.load_level('MENU')




   def load_level(self,levelName):
      '''
      Load the level named as the parameter levelName, build new dimension, set Zardow's position,...
      Use self.load_level(self.level_name) to restart the current level.
      Parameters:
         levelName (str) : The name of the level to play
      '''
      
      self.level_path = levelName
      level = import_level_as_module('%s'%levelName)

      self.mapsize = (20,20) # Always 20*20
      self.background_image = level.background
      self.play_music(Music.environment[level.music])
      dimensionNum = level.dimension

      self.toolbox = Toolbox.Toolbox(level.inventory, 0 )

      self.dimension = []
      #list(map(lambda a: list(map(getTileInstance,a)),dimensionNum))
      for x,row in enumerate(dimensionNum):
         subDim = []
         for y,tileId in enumerate(row):
            tile = Tiles.identifiers[tileId](size = (self.tile_side_size,self.tile_side_size), coords=(x, y))
            subDim.append(tile)

         self.dimension.append(subDim)

      self.level_surface = pygame.Surface((self.window_size, self.window_size))

      self.level_message = level.message
      self.needed_antimatter = level.antimatter
      level_image = load_image('Ressources/Backgrounds/'+level.background)
      width = int(self.window_size * (level_image.get_width()/800))
      self.level_image = pygame.transform.scale(level_image, (width, self.window_size))
      

      self.collected_antimatter = 0

      # Sprite managment
      self.effects = []
      self.need_build_map = True


      # Entities managment
      self.zardow_entity = Entities.Zardow()
      self.zardow_entity.position = level.position
      self.zardow_entity.direction = level.direction

      self.rocket_entity = Entities.Rocket()
      self.rocket_entity.position = level.rocketPosition

      self.entities = [self.zardow_entity, self.rocket_entity] # Create entities array containing every entities instances actually in the game, default containing just the main character and the rocket

      if hasattr(level, 'entities'):
         self.entities.extend(level.entities)
         self.moving_boxes = list(filter(lambda e: isinstance(e, Entities.MovingBox), self.entities))
         
      else:
         self.moving_boxes = []

      self.level_won = False
      self.pause = False

      self.anti_gravity = False

   def load_sounds(self, sounds):
      '''
      Preload sounds and effects for the game to play them quicker when needed.
      When loaded, each sound is placed in the self.loaded_sounds list.
      Parameters:
         sounds ( list of str ) : The name of all sound files (without the .flac extension!) to load.
      '''
      self.loaded_sounds = {}
      for sound_name in sounds:
         sound_path = 'Ressources/Sounds/%s.ogg'%sound_name
         try:
            son = pygame.mixer.Sound(sound_path)
            self.loaded_sounds.update({sound_name: son})
         except Exception as e:
             print ('Error "{e}" while loading or playing the music {sound}'.format(e = e, sound = sound_name))

   def play_sound(self,sound_name, volume = 0.5, override = True):
      '''
      Play a sound that has been proviously loaded with self.load_sounds([name])
      Parameters:
         sound_name (str) : The name of the sound (without .flac extension!) that we want to play
         volume (float) : The volume, as a system volume ratio. Note that music i playing with a 0.5 volume.
         override (bool) : If True, ound will play and stop every other playing sounds (except music).
      '''
      son = self.loaded_sounds[sound_name]#pygame.mixer.Sound(sound_path)
      son.set_volume(volume)
      try:
         # Decide what channel
         channel = 0
         while self.sound_channels[channel].get_busy():
            channel += 1
            if channel >= len(self.sound_channels):
               channel = None
               break
               
         if channel == None and override:
            channel = 0
            
         if channel != None:
            self.sound_channels[channel].play(son)
            
      except Exception as e:
         print ('Error "{e}" while loading or playing the music {sound}'.format(e = e, sound = sound_name))
         

   def play_music(self, music_name):
      '''
      Will play a music it this music is not already playing
      Parameters:
         music_name (str) : The name of the music file
      '''
      if self.playing_music_name != music_name:
         self.playing_music_name = music_name
         try:
            pygame.mixer.music.load("Ressources/Musics/"+music_name)
            pygame.mixer.music.queue("Ressources/Musics/"+music_name)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
         except Exception as e:
            print ('Error "{e}" while loading or playing the music {music}'.format(e = e, music = music_name))



   def init_window(self):
      '''
      Init and display a window
      '''
      global ressources
      #pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
      pygame.init()

      try:
         pygame.mixer.init()
      except:
         print ('No audio output detected')

      self.surface = pygame.display.set_mode((self.window_size, self.window_size))
      pygame.display.set_caption(self.window_title)

      #self.surface.fill(self.bgcolor)

      pygame.key.set_repeat(self.key_repeat_time, self.key_repeat_time)

      self.sound_channels = (pygame.mixer.Channel(2), pygame.mixer.Channel(3)) # Allocate two channels = two simultaneous sounds 

      # Set cursor image
      #self.cursor_image = pygame.image.load('Ressources/Hud/cursor.png').convert_alpha()
      #pygame.mouse.set_visible(False)

      self.level_chooser = lc.LevelChooser(self.window_size, [])

      self.just_clicked = False

      #self.refresh_display()
      
   def reset_game(self):
      self.is_menu = True
      

   def update(self):
      '''
      The update fonction represents one refresh of the game behaviour.
      It is called by the self.clock Pygame clock, at a frequency "self.update_frequency" defined in __init__.
      Globally, this function is responsible of entities' movement and behaviours, of visual effects updates, of detecting if the current level is won or should be restarted, and call refresh_display()
      '''

      # Entities
      for entity in self.entities:
         x = entity.position[0]
         y = entity.position[1]


         if entity.direction == Entities.Direction.RIGHT:
            around_function = math.ceil
            around_opposite_function = math.floor
         elif entity.direction == Entities.Direction.LEFT:
            around_function = math.floor
            around_opposite_function = math.ceil
         else:
            around_function = int
            around_opposite_function = int

         next_position_x = around_function(x + (entity.velocity * entity.direction))
         next_position_y = int(y+0.1)

         if next_position_x >= 20 or next_position_x < 0 or next_position_y >= 20 or next_position_y < 0: # If entity is out of the map: kill it
            self.kill_entity(entity)
            continue

         next_block = self.dimension[next_position_x][next_position_y]
         current_block = self.dimension[int(x+0.5)][int(y)]
         previous_block = self.dimension[int(x-0.5)][int(y)]


         is_blocked_by_moving_box = False
         for b in self.moving_boxes:
            if b.position[0] == next_position_x and b.position[1] == next_position_y:
               is_blocked_by_moving_box = True

         if next_block.traversable and not is_blocked_by_moving_box:
            entity.velocity = entity.speed
            entity.position = (x + (entity.velocity * entity.direction), int(y)) # Int because we always want entity to be at a determined level
         else:
            entity.velocity = 0

         #print ('Pos', entity.position,'| Current', current_block,'| Prev',previous_block,'| Next', next_block,'| Intra',entity.position_in_block) # Debug

         if current_block.is_type(Tiles.SpringLeft) and entity.direction == Entities.Direction.RIGHT and entity.position_in_block >= 0.5: # If entity is on a right-facing spring
            entity.direction = Entities.Direction.LEFT
            self.dimension[next_position_x][int(y)] = next_block.become(Tiles.SpringLeftPressed)
            self.need_build_map = True

         if current_block.is_type(Tiles.SpringRight) and entity.direction == Entities.Direction.LEFT and entity.position_in_block <= 0.5: # If entity is on a left-facing spring
            entity.direction = Entities.Direction.RIGHT
            self.dimension[next_position_x][int(y)] = next_block.become(Tiles.SpringRightPressed)
            self.need_build_map = True

         if current_block.is_type(Tiles.SpringRightPressed) and entity.direction == Entities.Direction.RIGHT: # If entity leaves a left-facing spring
            self.dimension[int(x+0.5)][int(y)] = current_block.become(Tiles.SpringRight)
            self.need_build_map = True
            self.play_sound('spring')

         if current_block.is_type(Tiles.SpringLeftPressed) and entity.direction == Entities.Direction.LEFT: # If entity leaves a left-facing spring
            self.dimension[int(x+0.5)][int(y)] = current_block.become(Tiles.SpringLeft)
            self.need_build_map = True
            self.play_sound('spring')

         if current_block.is_one_types(Tiles.PortalBlue, Tiles.PortalRed, Tiles.PortalGreen) and entity.travelable_in_portals and not entity.just_travelled_in_portal: # Enter a portal
            entity.just_travelled_in_portal = True # To avoid being reteleported immediatly when go out of the portal
            type_of_portal = type(current_block)

            portals_positions = searchTypeInMatrix(type_of_portal, self.dimension) # Search for portal with same color in the dimension
            for portal in portals_positions:
               if portal != current_block.coords:
                  entity.position = portal
                  exit_portal = self.dimension[portal[0]][portal[1]]
                  if entity.start_y: # If entity is falling (because of gravity) while it is teleported: change it's start_y value to take account of delta between Y of the two portals
                     entity.start_y += (exit_portal.coords[1] - current_block.coords[1])
                     
                  if exit_portal.is_type(Tiles.PortalBlue): # Get textures for Portal color
                     textures = Effects.getTexturesFromDirectory('Ressources/Particles/BluePortal')
                  elif exit_portal.is_type(Tiles.PortalRed):
                     textures = Effects.getTexturesFromDirectory('Ressources/Particles/RedPortal')
                  if exit_portal.is_type(Tiles.PortalGreen):
                     textures = Effects.getTexturesFromDirectory('Ressources/Particles/GreenPortal')
                     
                  effectOut = Effects.UniformEffect(exit_portal.position, textures, quantity = 5, radius_max = 3, age_max = 14, textures_alternating_mode = Effects.TextureAlternatingMode.TIMED)
                  self.effects.append(effectOut) # Add particles to exit portal
                  
                  effectIn = Effects.UniformEffect(current_block.position, textures, quantity = 5, radius_max = 3, age_max = 14, textures_alternating_mode = Effects.TextureAlternatingMode.TIMED)
                  self.effects.append(effectIn) # Add particles to enter portal

                  self.play_sound('teleport')
                  break





         if not current_block.is_one_types(Tiles.PortalBlue, Tiles.PortalRed, Tiles.PortalGreen): # Exits the portal
            entity.just_travelled_in_portal = False

         if current_block.is_type(Tiles.Antimatter) and entity == self.zardow_entity: # Collect antimatter (only for Zardow)
            self.collected_antimatter += 1
            current_block = current_block.become(Tiles.Air)
            self.dimension[int(x+0.5)][int(y)] = self.dimension[int(self.zardow_entity.position[0])][int(self.zardow_entity.position[1])].become(Tiles.Air)
            if self.collected_antimatter == self.needed_antimatter:
               self.play_sound('enough antimatter')
            else:
               self.play_sound('antimatter')
            self.need_build_map = True

         if current_block.is_one_types(Tiles.Spikes, Tiles.SpikesDown): # If entity is on spikes: die
            self.kill_entity(entity)
            continue

         if current_block.is_type(Tiles.Ladder): # If entity is on ladders
            entity.position = (entity.position[0], entity.position[1] + 1)

         if current_block.is_one_types(Tiles.ButtonUp, Tiles.ButtonDown) and not entity.just_pressed_button: # If entity is on antigravity button
            self.anti_gravity = not self.anti_gravity
            entity.just_pressed_button = True
            for e in self.entities:
                e.falling_time = 0
            self.play_sound('gravity')

         if not current_block.is_one_types(Tiles.ButtonUp, Tiles.ButtonDown): # If entity is not on antigravity button anymore
            entity.just_pressed_button = False





         # Gravity
         if entity.subject_gravity: # Is entity is subject to gravity

            if not self.anti_gravity: # Normal gravity

               y = entity.position[1]
               y_to_test = math.ceil(y)-1

               if y_to_test < 0 or y_to_test >= 20: # If entity vertically out of map: kill it
                  self.kill_entity(entity)
                  continue

               bloc_to_test = self.dimension[math.floor(x+0.5)][y_to_test]

               is_blocked_by_moving_box = False
               for box in self.moving_boxes:
                  if box.position[0] == math.floor(x+0.5) and box.position[1] == y_to_test:
                     is_blocked_by_moving_box = True


               if bloc_to_test.traversable and not bloc_to_test.is_type(Tiles.Ladder) and not current_block.is_one_types(Tiles.SpringLeft, Tiles.SpringLeftPressed, Tiles.SpringRight, Tiles.SpringRightPressed) and not is_blocked_by_moving_box:
                  if not entity.start_y:
                     entity.start_y = y
                     
                  yGravity = entity.start_y - (0.5 * 19 * ((entity.falling_time/self.update_frequency) ** 2)) # y(t) = 1/2 gt^2 + y0 (here, g is 19)
                  entity.position = (entity.position[0], yGravity)
                  entity.falling_time += 1
               else:
                  entity.falling_time = 0
                  entity.start_y = 0

            else: # Anti gravity

               y = entity.position[1]
               y_to_test = math.floor(y)+1

               if y_to_test < 0 or y_to_test >= 20: # If entity vertically out of map: kill it
                  self.kill_entity(entity)
                  continue

               bloc_to_test = self.dimension[math.floor(x+0.5)][y_to_test]

               is_blocked_by_moving_box = False
               for box in self.moving_boxes:
                  if box.position[0] == math.floor(x+0.5) and box.position[1] == y_to_test:
                     is_blocked_by_moving_box = True


               if bloc_to_test.traversable and not bloc_to_test.is_type(Tiles.Ladder) and not current_block.is_one_types(Tiles.SpringLeft, Tiles.SpringLeftPressed, Tiles.SpringRight, Tiles.SpringRightPressed) and not is_blocked_by_moving_box:
                  if not entity.start_y:
                     entity.start_y = y
                     
                  yGravity = min(y_to_test+0.1, entity.start_y + (0.5 * 19 * ((entity.falling_time/self.update_frequency) ** 2)))# y(t) = 1/2 gt^2 + y0
                  entity.position = (entity.position[0], yGravity)
                  entity.falling_time += 1
               else:
                  entity.falling_time = 0
                  entity.start_y = 0


         entity.update(instance=self) # Entity specific behaviour update


      ### End entities behaviour
      
         

      ### Presenting effects and particles

      for effect in self.effects:
         effect.present()

      ### End effects presenting
      
      

      ### Zardow behaviour


      if ((int(self.zardow_entity.position[0]) == int(self.rocket_entity.position[0])) and
            (int(self.zardow_entity.position[1]) == int(self.rocket_entity.position[1])) and
            (self.zardow_entity in self.entities)): # If Zardow on the rocket
            
         if self.collected_antimatter == self.needed_antimatter: # Enough antimatter and : win
            self.rocket_entity.zardow_is_in = True
            self.entities.remove(self.zardow_entity)
            self.play_sound('rocket')
            self.level_won = True
         else:
            self.kill_entity(self.zardow_entity)


      if self.zardow_entity.dead or self.rocket_entity.dead: # If any Zardow or the rocket (normally not happening) die
         self.load_level(self.level_path)
         
      ### Zardow behaviour
         

      self.refresh_display()




   def kill_entity(self, entity):
      '''
      Kill an entity.
      Invoke entity.kill but prepare the game to make it more efficient, and to check if the killed entity is Zardow (then play the "you lose" sound).
      Parameters:
         entity (Entities.Entity) : The entity to kill, to remove of the game
      '''
      entity.kill()
      if entity == self.zardow_entity:
         self.play_sound('lose')
      self.entities.remove(entity)

      if entity in self.moving_boxes:
         self.moving_boxes.remove(entity)



   def refresh_display(self):
      '''
      This function if responsible of the display refreshing.
      First, we will refresh the tilemap. This step may take some time, so we only do it if self.need_build_map is True, only if the tilemap NEEDS to be redrawn.
      Then, we draw entities, visual effects, toolbox and GUIs depending on the status of the game (in game, in menu, paused, win)
      /!\ If selecting level, this function don't be called, but show_level_chooser will.
      '''
      
      
   
      #self.surface.fill((255, 255, 255))
      pygame.display.update()

      # Rebuild map if needed

      if self.need_build_map or True:
         self.level_surface.blit(self.level_image,(0, 0))

         for x,subdim in enumerate(self.dimension):
            for y,bloc in reversedEnumerate(subdim):
               bloc.position = (x * self.tile_side_size, y * self.tile_side_size)
               rect = bloc.position + bloc.rect
               self.level_surface.blit(bloc.image, rect)

         self.need_build_map = False

         # Display a message if there is a message
         if len(self.level_message) > 0:
            font_baloo48 = pygame.font.Font('./Ressources/Fonts/Baloo.ttf', 48)
            message_line_1 = font_baloo48.render(self.level_message[0], True, (255, 255, 255))
            message_line_1_rect = message_line_1.get_rect(center = (self.level_surface.get_width() / 2, self.level_surface.get_height() / 4))
            self.level_surface.blit(message_line_1, message_line_1_rect)

         if len(self.level_message) > 1:
            message_line_2 = font_baloo48.render(self.level_message[1], True, (255, 255, 255))
            message_line_2_rect = message_line_2.get_rect(center = (self.level_surface.get_width() / 2, self.level_surface.get_height() / 4 + 48))
            self.level_surface.blit(message_line_2, message_line_2_rect)
            
         # Display the amount of antimatter (if needed)
         if self.needed_antimatter:
            font_baloo32 = pygame.font.Font('./Ressources/Fonts/Baloo.ttf', 32)
            text = font_baloo32.render('{collected}/{total}'.format(collected = self.collected_antimatter, total = self.needed_antimatter), True, (255, 255, 255))
            self.level_surface.blit(text, (self.window_size - 3 * (32 + 32) - 24 - text.get_width() , 29))
            
            antimatterImage = load_image('./Ressources/Hud/antimatter.png',(32, 32))
            self.level_surface.blit(antimatterImage, (self.window_size - 4 * (32 + 32) - text.get_width(), 35))



      self.surface.blit(self.level_surface, self.surface.get_rect())


      # Draw entities

      for entity in self.entities:
         image = entity.get_image(self.anti_gravity)
         w = image.get_width()
         h = image.get_height()
         x, y = entity.position
         anchor_point = (entity.anchor_point[0] * Entities.Entity.image_side, entity.anchor_point[1] * Entities.Entity.image_side)
         position = (x * self.tile_side_size - anchor_point[0], (len(self.dimension) - y - 1) * self.tile_side_size - anchor_point[1]) # Position in-window to display the entity at
         rect = position + (w, h)
         self.surface.blit(image, rect)

         #pygame.draw.circle(self.surface, (255,0,0) , (int(position[0]),int(position[1])), 5) # For debugging


      # Draw toolbox

      if self.toolbox.items:
         self.toolbox.draw(self.surface)

      # Draw particles

      for effect in self.effects:
         effect.show(self.surface)
         

      # GUIs

      # If Menu level; place title and buttons
      if self.is_menu:
         title_image = load_image('Ressources/Hud/menuTitleWithoutZardow.png',(515,144))
         width = 10 * self.tile_side_size
         height = int(width * (322 / 2272))
         title_image = pygame.transform.scale(title_image, (width, height))
         
         title_image = self.surface.blit(title_image,(
            5 * self.tile_side_size,
            2 * self.tile_side_size
         ))


         button_width = 256
         button_height = 64

         self.play_button_rect =  pygame.Rect((self.level_surface.get_width() / 2) - (button_width / 2), 3/8*self.window_size, button_width, button_height)

         if self.play_button_rect.collidepoint(self.mouse_position):
            play_button_image = load_image('Ressources/Hud/playButtonHover.png',(button_width,button_height))
         else:
            play_button_image = load_image('Ressources/Hud/playButton.png',(button_width,button_height))
         self.surface.blit(play_button_image,self.play_button_rect)


      if self.level_won: # Refresh while "You Win" screen
         image = pygame.Surface((self.surface.get_width(),self.surface.get_height()))
         image.set_alpha(128)
         image.fill((0,0,0))
         self.surface.blit(image,(0,0))

         won_title_image = load_image('Ressources/Hud/wonTitle.png',(629,150))
         self.surface.blit(won_title_image,(
            (self.level_surface.get_width() / 2) - (won_title_image.get_width() / 2)-12,
            self.level_surface.get_height()/4
         ))

         button_width = 256
         button_height = 64

         self.next_button_rect =  pygame.Rect((self.level_surface.get_width() / 2) - (button_width / 2), self.window_size/2, button_width, button_height)

         if self.next_button_rect.collidepoint(self.mouse_position):
            next_button_image = load_image('Ressources/Hud/nextButtonHover.png',(button_width,button_height))
         else:
            next_button_image = load_image('Ressources/Hud/nextButton.png',(button_width,button_height))
         self.surface.blit(next_button_image,self.next_button_rect)
         
      if self.pause: # Refresh while in pause
         image = pygame.Surface((self.surface.get_width(),self.surface.get_height()))
         image.set_alpha(128)
         image.fill((0,0,0))
         self.surface.blit(image,(0,0))

         pause_title_image = load_image('Ressources/Hud/pauseTitle.png',(629,150))
         self.surface.blit(pause_title_image,(
            (self.level_surface.get_width() / 2) - (pause_title_image.get_width() / 2)-12,
            self.level_surface.get_height()/4
         ))

         button_width = 256
         button_height = 64

         self.resume_button_rect =  pygame.Rect((self.level_surface.get_width() / 2) - (button_width / 2), self.window_size/2, button_width, button_height)

         if self.resume_button_rect.collidepoint(self.mouse_position):
            resume_button_image = load_image('Ressources/Hud/resumeButtonHover.png',(button_width,button_height))
         else:
            resume_button_image = load_image('Ressources/Hud/resumeButton.png',(button_width,button_height))
         self.surface.blit(resume_button_image,self.resume_button_rect)


      # In-game buttons

      retryButtonImage = load_image('Ressources/Hud/retry.png',(32,38))
      self.retry_button_rect = pygame.Rect(self.window_size - 32 - 32 , 32, retryButtonImage.get_width(), retryButtonImage.get_height() )
      if (not self.is_menu) and (not self.level_won):
         # Draw retry button
         self.surface.blit(retryButtonImage,self.retry_button_rect)
         
      pauseButtonImage = load_image('Ressources/Hud/pauseButton.png',(32,38))
      self.pause_button_rect = pygame.Rect(self.window_size - 2 * (32 + 32), 32, pauseButtonImage.get_width(), pauseButtonImage.get_height() )
      if (not self.is_menu) and (not self.level_won):
         # Draw retry button
         self.surface.blit(pauseButtonImage,self.pause_button_rect)

      menuButtonImage = load_image('Ressources/Hud/menuButton.png',(32,38))
      self.menu_button_rect = pygame.Rect(self.window_size - 3 * (32 + 32), 32, menuButtonImage.get_width(), menuButtonImage.get_height() )
      if (not self.is_menu) and (not self.level_won):
         # Draw retry button
         self.surface.blit(menuButtonImage,self.menu_button_rect)



      # Update the display
      pygame.display.flip() # At the end of refresh_display

   def show_level_chooser(self):
      '''
      "Hook" of refresh_display but if user is choosing a level in the level selector.
      This doesn't appears on refresh_display because refresh_display is called every update and this will be called every occurence of the mainloop (since level choosing is not very ressources heavy and need to be fluid)
      '''
      self.level_chooser.draw(self.surface)
      pygame.display.flip()


   def mainloop(self):
      '''
      The mainloop function will make the game running.
      It contains a while loop that will keep the window open, deal with received events, and call self.update if needed.
      
      '''
      global sound_channel
      #pygame.display.flip()

      time_elapsed_since_last_update = 0
      self.clock = pygame.time.Clock()

      pause = False # For debugging



      while self.running:
         self.mouse_position = pygame.mouse.get_pos()
         
         ## BEGIN EVENTS DEALING
         
         for event in pygame.event.get():
            if event.type == pygame.QUIT: # Quit event (sent by red-cross-button)
               print ('Quit event')
               self.running = False
               pygame.quit()
               break


            elif event.type == pygame.KEYDOWN: # Key press

               keys_down = pygame.key.get_pressed()
               if self.is_choosing_level:
                  if keys_down[K_UP]:
                     self.level_chooser.move(-1)
                  elif keys_down[K_DOWN]:
                     self.level_chooser.move(1)

               else:
                  if keys_down[pygame.K_SPACE]: # If SPACE key is pressed:
                     boxes = searchTypeInMatrix(Tiles.Box, self.dimension)
                     play_sound = False
                     for box_to_break_position in boxes: # Search for every boxes in the level
                        play_sound = True
                        box = self.dimension[box_to_break_position[0]][box_to_break_position[1]].become(Tiles.Air)
                        self.dimension[box_to_break_position[0]][box_to_break_position[1]] =  box# Replace the box by a broken box

                        textures = Effects.getTexturesFromDirectory('Ressources/Particles/Breaking Box')
                        position_pixels = (box_to_break_position[0] * self.tile_side_size, (self.mapsize[1] - box_to_break_position[1]) * self.tile_side_size)
                        particle = Effects.GravityEffect(position_pixels, textures, 10,50)
                        self.effects.append(particle)

                        self.need_build_map = True # Need to refresh the map
                        
                     if play_sound:
                        self.play_sound('breakingBox')

                  elif keys_down [pygame.K_r] and not self.is_menu: # If user press R key, restart level
                      self.load_level(self.level_path)
                     
                  elif keys_down [pygame.K_ESCAPE] and not self.is_menu:
                     self.pause = not self.pause

                  else:
                     #pause = True # For debugging
                     pass


            elif event.type == pygame.KEYUP: # For debugging
               pause = False

            elif event.type == pygame.MOUSEBUTTONDOWN: # Mouse wheel: when on level selector, scroll up or down
                if self.is_choosing_level:
                    if event.button == 4: # Mouse wheel scrolling down
                        self.level_chooser.move(-2)
                    elif event.button == 5: # Mouse wheel scrolling up
                        self.level_chooser.move(2)
         ## END EVENTS DEALING
         
         ## BEGIN MOUSE CLICKING

         if self.running:
            mouse_click = bool(sum(pygame.mouse.get_pressed())) # True if a mouse button is pressed, False otherwise.
         else: # User has closed the window, to avoid crashing because of a uninitialized window
            mouse_click = False

         if mouse_click: # Mouse press
            self.just_clicked = True
         else:
            if self.just_clicked:
               x_click, y_click = self.mouse_position

               if self.is_menu: # Clicked when on menu
                  if self.play_button_rect.collidepoint(self.mouse_position):
                     self.play_sound('hover')
                     self.is_menu = False
                     self.is_choosing_level = True
                     with open('LevelPack.json','r') as levelPackJson:
                        levels = json.loads(levelPackJson.read())['Levels']

                     self.level_chooser.items = levels
                     #self.load_level('1')

               elif self.level_won: # Clicked on "You win" screen
                  if self.next_button_rect.collidepoint(self.mouse_position): # Next level button
                     self.play_sound('hover')

                     with open('LevelPack.json','r') as levelPackJson:
                        levels = json.loads(levelPackJson.read())['Levels']

                     for index,level in enumerate(levels):
                        if level['path'] == self.level_path:
                           next_level = levels[index+1]
                           if 'animation' in next_level: # Next "level" is an animatio
                              path = next_level['path']
                              images_name = next_level['images']
                              images = map(lambda img_name: os.path.join(path, img_name), images_name)
                              if 'music' in next_level:
                                 self.play_music(next_level['music'])
                              animation = Effects.Animation(list(images), self.window_size, image_duration = 2, repeat = False, completion = self.reset_game, hide_cursor = True)
                              self.effects.append(animation)
                              self.level_won = False
                              self.pause = False
                           else: # Next level is a basic level
                              self.load_level(levels[index+1]['path'])
                              break

               elif self.is_choosing_level: # Clicked on the level selector
                  selected_level_index = self.level_chooser.select(self.mouse_position)
                  if selected_level_index != None:

                    with open('LevelPack.json','r') as levelPackJson:
                        levels = json.loads(levelPackJson.read())['Levels']

                    level = levels[selected_level_index]
                    self.is_choosing_level = False
                    self.load_level(level['path'])
               
               elif self.pause: # Clicked while level in pause
                  if self.resume_button_rect.collidepoint(self.mouse_position):
                     self.pause = False
                     self.refresh_display()

               else: # Clicked while playing.
                  if self.toolbox.rect.collidepoint(self.mouse_position): # Clicked in inventory
                     self.toolbox.selectByClick(self.mouse_position)

                  elif self.retry_button_rect.collidepoint(self.mouse_position): # Pressed Retry button
                     self.load_level(self.level_path)
                     
                  elif self.pause_button_rect.collidepoint(self.mouse_position): # Pressed Pause button
                     self.pause = True

                  elif self.menu_button_rect.collidepoint(self.mouse_position): # Pressed Menu button
                     self.is_menu = True
                     self.load_level('MENU')
                     self.play_music(Music.environment['earth'])

                  else: # Clicked anywhere else on the window
                     # Determine the ingame-coordinates for the click position
                     x = int(x_click / self.tile_side_size)
                     y = len(self.dimension) - int(y_click / self.tile_side_size) - 1

                     if self.dimension[x][y].is_type(Tiles.TileTarget) and not (x == int(self.zardow_entity.position[0]) and y == int(self.zardow_entity.position[1])): # If clicked tile is a target tile
                        self.dimension[x][y] = self.toolbox.selected_item(size = (self.tile_side_size,self.tile_side_size), coords = (x, y)) # Replace the target tile by the selected tile
                        self.toolbox.items[self.toolbox.selected_slot] = None # After having placed the tile, we remove it from the toolbox
                        self.toolbox.sort()
                        self.need_build_map = True # After replacing the tile, we need to refresh the display of the map
                        self.play_sound('putTile')



               self.just_clicked = False

            ## END MOUSE CLICKING
            
         ## BEGIN UPDATES AND DISPLAY REFRESHING

         if self.is_choosing_level: # If user is in the game selector, call show_level_chooser to refresh display and don't call self.update (see show_level_chooser for more detail)
            self.show_level_chooser()
         else:
            if self.running:
               # Update function that will be called on each fps

               dt = self.clock.tick()
               time_elapsed_since_last_update += dt
               
               if time_elapsed_since_last_update >= (1000/self.update_frequency):
                  if not self.pause:
                     self.update()
                  else:
                     self.refresh_display()
                  time_elapsed_since_last_update = 0
                  
            elif not self.running:
                exit()
   
         ## END UPDATES AND DISPLAY REFRESHING

if __name__ == '__main__':
   jeu = Zardow() # Init variables
   jeu.mainloop() # Run game
    



