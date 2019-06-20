#!/usr/bin/python3
# -*- coding: utf-8 -*-

##################################################
################################################## UTILITIES.PY
##################################################
import pygame

global alreadyImportedImages
alreadyImportedImages = {}

def load_image(path, size = None, force_import = False):
	'''
	Load an image in pygame and put it in the dict alreadyImportedImages.
	To avoid lags, if image was already loaded, take it from the dict alreadyImportedImages.
	Parameters:
		- path (str) : The path of the image to load
		- size (tuple(Int, Int)) : The size of the image
			Default: None = take the default size fo the image
		- force_import (bool) : If True, will load the image from file even if it has already been loaded earlier.
	Returns:
		- pygame.image : The instance of the loaded image
	'''
	global alreadyImportedImages
	
	if path in alreadyImportedImages.keys() and not force_import:
		image = alreadyImportedImages[path]
		#print (path,'already loaded')
	else:
		image = pygame.image.load(path).convert_alpha()
		alreadyImportedImages[path] = image
		
	if size:	
		image = pygame.transform.scale(image, size)
	
	return image
		
def reversedEnumerate(list):
	'''
	Like a enumerate function, but reversing index.
	Parameters:
		list (array) : the list to enumerate
	Returns:
		[ (index, item), ... ]
	'''
	return zip(range(len(list)-1, -1, -1), list)

def searchTypeInMatrix(item_instance, matrix):
	'''
	Search for every items whose the parent type is the indicated type item_instance in the matrix named matrix.
	Parameters:
		item_instance (type) : the type to search
	Returns:
		[ (x, y), ...] : The list of coordinates of corresponding items 
	'''
	for x,row in enumerate(matrix):
		for y,item in enumerate(row):
			if isinstance(item, item_instance):
				yield (x,y)
				
def around(x, nearest):
	'''
	Around the number (int or float) x to the nearest n*(parameter nearest).
	Exemple: around(14, 10) -> 10
				around(16, 10) -> 20
	Parameters:
		x (int | float) : The number to around
		nearest (int | float) : The nearest number to around x
	Returns:
		int | float : The nearest n*(parameter nearest) of x
	'''
	return round(x/float(nearest))*nearest