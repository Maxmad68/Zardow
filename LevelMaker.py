#coding: utf-8

import pygame
from pygame.locals import *

import time
import math
import os
import string
import imp


import Tiles
import Toolbox
import Entities
from utilities import *

import main


def import_level(name):
	levelPath = 'Levels/'+name
	find = imp.find_module(levelPath)
	loaded = imp.load_module(levelPath,*find)
	return loaded

class InputBox:

	def __init__(self, x, y, w, h, text=''):
		self.rect = pygame.Rect(x, y, w, h)
		self.color = (255,255,255)
		self.text = text
		self.font = pygame.font.Font('./Ressources/Fonts/Baloo.ttf', 64)
		self.txt_surface = self.font.render(text, True, self.color)
		self.active = False
		self.action = None

	def handle_event(self, event):
		if self.active:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					if self.action:
						self.action(self.text)
				elif event.key == pygame.K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					character = event.unicode
					if character in (string.ascii_letters + string.digits):
						self.text += event.unicode
				# Re-render the text.
				self.txt_surface = self.font.render(self.text, True, self.color)

	def update(self):
		# Resize the box if the text is too long.
		width = max(200, self.txt_surface.get_width()+10)
		self.rect.w = width

	def draw(self, screen):
		# Blit the text.
		screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
		# Blit the rect.
		pygame.draw.rect(screen, self.color, self.rect, 2)

class LevelMaker(object):
	def __init__(self,loadLevel=None):


		self.is_typing_level_name = False

		self.window_size = (1600,1000)
		self.window_title = "Zardow Level Maker"
		self.bgcolor = (0,255,255) # blue

		self.running = True
		self.key_repeat_time = 1 # Default: 1
		self.tile_side_size = 40 # Default: 40

		self.update_frequency = 20 # times per second (= fps / = Hz)

		self.mouse_position = (0,0) # Will be updated in the mainloop
		
		Toolbox.Toolbox.tile_side_size = self.tile_side_size

		#Build the map

		self.mapsize = (20,20)
		self.background_image = 'earth.png'
		self.dimension = []
		for x in range(self.mapsize[0]):
			subDim = [3]
			for y in range(self.mapsize[1]-1):
				subDim.append(0)
			self.dimension.append(subDim)


		self.selectedId = 1

		self.zardow_position = (1,1)
		self.rocket_position = (10,1)
		self.zardow_orientation = 'right'
		self.antimatter_number = 0

		self.level = None
		if loadLevel:
			self.level = import_level(loadLevel)
			self.zardow_position = self.level.position
			self.rocket_position = self.level.rocketPosition
			self.zardow_orientation = {-1:'left',0:'face',1:'right'}[self.level.direction]
			self.antimatter_number = self.level.antimatter
			self.dimension = self.level.dimension
			
		self.init_window()

		self.level_image = load_image('Ressources/Backgrounds/'+self.background_image)



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
			print ('Aucune sortie audio')

		self.surface = pygame.display.set_mode(self.window_size)
		pygame.display.set_caption(self.window_title)

		self.surface.fill(self.bgcolor)

		pygame.key.set_repeat(self.key_repeat_time, self.key_repeat_time)

		self.font_baloo48 = pygame.font.Font('./Ressources/Fonts/Baloo.ttf', 48)
		self.font_baloo32 = pygame.font.Font('./Ressources/Fonts/Baloo.ttf', 32)
		self.font_baloo24 = pygame.font.Font('./Ressources/Fonts/Baloo.ttf', 24)
		self.font_baloo16 = pygame.font.Font('./Ressources/Fonts/Baloo.ttf', 16)

		#self.sound_channel = pygame.mixer.Channel(5)

		self.toolbox = Toolbox.Toolbox()
		if self.level:
			self.toolbox.items = self.level.inventory

		self.input_box = InputBox(self.surface.get_width() / 2 - 400, self.surface.get_height() / 2 - 100, 800, 100)
		self.input_box.action = self.save_level

		self.refresh_display()


	def refresh_display(self):
		self.surface.fill(self.bgcolor) # Reset display

		# Dimension


		for x,subdim in enumerate(self.dimension):
			for y,blocId in reversedEnumerate(subdim):
				bloc = Tiles.identifiers[blocId](size = (self.tile_side_size, self.tile_side_size))
				bloc.position = (x * self.tile_side_size, y * self.tile_side_size)
				rect = bloc.position + bloc.rect
				image = bloc.get_describing_image((self.tile_side_size, self.tile_side_size))
				self.surface.blit(image, rect)

		# Item Chooser
		pygame.draw.rect(self.surface,(204,255,255),(800,0,800,800))

		columnSelected = self.selectedId % 7
		rowSelected = int(self.selectedId / 7)
		xSelected = 800 + 65 + columnSelected * (self.tile_side_size + 65) - 16
		ySelected = 65 + rowSelected * (self.tile_side_size + 65) - 16

		pygame.draw.rect(self.surface,(220,220,220),(xSelected,ySelected,self.tile_side_size + 32,self.tile_side_size + 32))

		for index,item in Tiles.identifiers.items():
			instance = item(size = (self.tile_side_size, self.tile_side_size))
			index_x = index % 7
			index_y = int(index / 7)
			x = 800 + 65 + index_x * (self.tile_side_size + 65)
			y = 65 + index_y * (self.tile_side_size + 65)
			instance.position = (x, y)
			rect = instance.position + (self.tile_side_size,self.tile_side_size)
			image = instance.get_describing_image((self.tile_side_size, self.tile_side_size))
			self.surface.blit(image, rect)


		# Properties
		pygame.draw.rect(self.surface,(100,100,100),(0,800,1600,2))
		pygame.draw.rect(self.surface,(220,220,220),(0,801,1600,200))

		# Zardow Character
		zardowImage = load_image('Ressources/Entity/Zardow/%s/Face.png'%(self.zardow_orientation.title()),(40,40))
		self.surface.blit(zardowImage, (self.zardow_position[0] * self.tile_side_size, (19-self.zardow_position[1]) * self.tile_side_size))

		# Rocket
		rocketImage = load_image('Ressources/Entity/Rocket/Standing.png',(40,80))
		self.surface.blit(rocketImage, (self.rocket_position[0] * self.tile_side_size, (18-self.rocket_position[1]) * self.tile_side_size))

		# Zardow buttons
		self.zardow_left_button_rect = pygame.Rect(50,900,50,50)
		pygame.draw.rect(self.surface,(251,120,253),self.zardow_left_button_rect)

		self.zardow_right_button_rect = pygame.Rect(154,900,50,50)
		pygame.draw.rect(self.surface,(251,120,253),self.zardow_right_button_rect)

		self.zardow_up_button_rect = pygame.Rect(102,873,50,50)
		pygame.draw.rect(self.surface,(251,120,253),self.zardow_up_button_rect)

		self.zardow_down_button_rect = pygame.Rect(102,925,50,50)
		pygame.draw.rect(self.surface,(251,120,253),self.zardow_down_button_rect)

		zardowImageLeft = load_image('Ressources/Entity/Zardow/Left/Face.png',(50,50))
		self.zardow_facing_left_button_rect = pygame.Rect(75,810,50,50)
		self.surface.blit(zardowImageLeft,self.zardow_facing_left_button_rect)

		zardowImageRight = load_image('Ressources/Entity/Zardow/Right/Face.png',(50,50))
		self.zardow_facing_right_button_rect = pygame.Rect(127,810,50,50)
		self.surface.blit(zardowImageRight,self.zardow_facing_right_button_rect)



		# Rocket buttons
		self.rocket_left_button_rect = pygame.Rect(250,900,50,50)
		pygame.draw.rect(self.surface,(32,157,215),self.rocket_left_button_rect)

		self.rocket_right_button_rect = pygame.Rect(354,900,50,50)
		pygame.draw.rect(self.surface,(32,157,215),self.rocket_right_button_rect)

		self.rocket_up_button_rect = pygame.Rect(302,873,50,50)
		pygame.draw.rect(self.surface,(32,157,215),self.rocket_up_button_rect)

		self.rocket_down_button_rect = pygame.Rect(302,925,50,50)
		pygame.draw.rect(self.surface,(32,157,215),self.rocket_down_button_rect)

		rocketImage = load_image('Ressources/Entity/Rocket/Standing.png',(20,40))
		self.surface.blit(rocketImage, (317, 820))


		# Antimatter buttons
		self.antimatter_less_button_rect = pygame.Rect(550,875,50,50)
		pygame.draw.rect(self.surface,(146,146,146),self.antimatter_less_button_rect)

		self.antimatter_more_button_rect = pygame.Rect(704,875,50,50)
		pygame.draw.rect(self.surface,(146,146,146),self.antimatter_more_button_rect)

		antimatterImage = load_image('Ressources/Tiles/antimatter.png',(50,50))
		self.surface.blit(antimatterImage, (650, 875))

		antimatter_text = self.font_baloo32.render(str(self.antimatter_number), True, (255,255,255))
		antimatter_text_rect = antimatter_text.get_rect(center=(625, 900))
		self.surface.blit(antimatter_text, antimatter_text_rect)


		# Save button
		save_button = self.font_baloo48.render('Save', True, (255,255,255))
		self.save_button_rect = save_button.get_rect(center=(1500, 850))
		self.surface.blit(save_button, self.save_button_rect)

		# Play button
		play_button = self.font_baloo32.render('Play', True, (255,255,255))
		self.play_button_rect = play_button.get_rect(center=(1500, 950))
		self.surface.blit(play_button, self.play_button_rect)


		# Toolbox
		self.toolbox.draw(self.surface)

		# Saving
		if self.is_typing_level_name:
			rect = (self.surface.get_width() / 2 - 500, self.surface.get_height() / 2 - 150, 1000, 200)
			pygame.draw.rect(self.surface,(220,220,220),rect)

			self.input_box.active = True
			self.input_box.draw(self.surface)



		# Update the display
		pygame.display.flip() # At the end of refresh_display


	def mainloop(self):
		#pygame.display.flip()

		time_elapsed_since_last_action = 0
		self.clock = pygame.time.Clock()

		pause = False # For debugging

		just_clicked = False

		while self.running:
			self.mouse_position = pygame.mouse.get_pos()
			for event in pygame.event.get():


				if event.type == pygame.QUIT: # Quit event (sent by red-cross-button)
					print ('Quit event')
					self.running = False
					break

				if self.is_typing_level_name:
					self.input_box.handle_event(event)
					self.refresh_display()


			mouse_click = bool(sum(pygame.mouse.get_pressed()))
			if mouse_click: # Mouse press
				mouse_position = pygame.mouse.get_pos()
				x, y = mouse_position

				if y < 800:

					if self.toolbox.rect.collidepoint(mouse_position):
						if self.selectedId:
							self.toolbox.items.append(Tiles.identifiers[self.selectedId])
							self.toolbox.selected_slot = None
						else:
							self.toolbox.items = self.toolbox.items[:-1]
							self.toolbox.selected_slot = None

					elif x < 800:
						xC = int(x / self.tile_side_size)
						yC = self.mapsize[1] - int(y / self.tile_side_size) -1
						self.dimension[xC][yC] = self.selectedId

					else:
						column = int((x - 800 - 65) / (self.tile_side_size + 65))
						row = int((y - 65) / (self.tile_side_size + 65))
						self.selectedId = row * 7 + column

				else:
					just_clicked = True
			else:
				if just_clicked:
					if self.zardow_left_button_rect.collidepoint(mouse_position):
						self.zardow_position = (self.zardow_position[0]-1,self.zardow_position[1])
					elif self.zardow_right_button_rect.collidepoint(mouse_position):
						self.zardow_position = (self.zardow_position[0]+1,self.zardow_position[1])
					elif self.zardow_up_button_rect.collidepoint(mouse_position):
						self.zardow_position = (self.zardow_position[0],self.zardow_position[1]+1)
					elif self.zardow_down_button_rect.collidepoint(mouse_position):
						self.zardow_position = (self.zardow_position[0],self.zardow_position[1]-1)

					if self.zardow_facing_left_button_rect.collidepoint(mouse_position):
						self.zardow_orientation = 'left'
					elif self.zardow_facing_right_button_rect.collidepoint(mouse_position):
						self.zardow_orientation = 'right'

					if self.rocket_left_button_rect.collidepoint(mouse_position):
						self.rocket_position = (self.rocket_position[0]-1,self.rocket_position[1])
					elif self.rocket_right_button_rect.collidepoint(mouse_position):
						self.rocket_position = (self.rocket_position[0]+1,self.rocket_position[1])
					elif self.rocket_up_button_rect.collidepoint(mouse_position):
						self.rocket_position = (self.rocket_position[0],self.rocket_position[1]+1)
					elif self.rocket_down_button_rect.collidepoint(mouse_position):
						self.rocket_position = (self.rocket_position[0],self.rocket_position[1]-1)

					if self.antimatter_more_button_rect.collidepoint(mouse_position):
						self.antimatter_number += 1
					elif self.antimatter_less_button_rect.collidepoint(mouse_position):
						self.antimatter_number -=1

					if self.save_button_rect.collidepoint(mouse_position):
						self.ask_for_saving_level()

					if self.play_button_rect.collidepoint(mouse_position):
						self.save_level('tmp')
						#runpy.run_path('LevelMaker_tester.py')
					just_clicked = False

			self.refresh_display()

	def ask_for_saving_level(self):
		self.is_typing_level_name = True

	def save_level(self,name):
		self.is_typing_level_name = False
		self.input_box.active = False
		self.refresh_display()

		toolbox_content = ', '.join(map(lambda c:c.__name__,self.toolbox.items))

		path = 'Levels/%s.py'%name

		content = '''
from Tiles import *
from Entities import *

dimension = {dimension}

position = {position}
rocketPosition = {rocketPosition}
antimatter = {antimatter}

direction = Direction.{orientation}
mapsize = (20,15)
inventory = [{toolbox}]

background = 'earth.png'
music = 'earth'

message = ['']
'''.format(
	dimension = self.dimension.__repr__().replace('], [','],\n[',20),
	position = self.zardow_position.__repr__(),
	rocketPosition = self.rocket_position.__repr__(),
	antimatter = self.antimatter_number,
	orientation = self.zardow_orientation.upper(),
	toolbox = toolbox_content
	)

		with open(path,'w') as file_:
			file_.write(content)

		print ('Level saved at:', path)


jeu = LevelMaker('earth9')
jeu.mainloop()