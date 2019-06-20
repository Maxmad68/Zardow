#!/usr/bin/python3
# -*- coding: utf-8 -*-

##################################################
################################################## TILES.PY
##################################################

import pygame, os
from utilities import *

class Tile(pygame.sprite.Sprite):
    def __init__(self,img,*args,**kwargs):
        '''
        A Tile is an item of the Tilemap.
        '''

        size = kwargs.get('size',None)
        if size:
            kwargs.pop('size')
            
        coords = kwargs.get('coords',None)
        if coords:
            kwargs.pop('coords')

        pygame.sprite.Sprite.__init__(self,*args,**kwargs)
        self.__dict__.update(kwargs)
        
        self.coords = coords

        if img:
            self.image = load_image(img,size)

            self.width = self.image.get_width()
            self.height = self.image.get_height()

            self.rect = (self.width, self.height)
        else:
            self.image = pygame.Surface((0,0))

            self.width = 0
            self.height = 0

            self.rect = (0, 0)

        self.describing_image = None # Image as they will be shown in toolbox / level editor

        self.traversable = False
        self.portalId = None

    def __repr__(self):
        '''
        Moslty used for debug:
            print (ladders_tile_instance) -> <Tile 25>
        '''
        return '<Tile %i>'%(list(identifiers.keys())[list(identifiers.values()).index(type(self))])

    def is_type(self, blocType):
        '''
        Check if the tile is instance of a type of tiles.
        Parameters:
            - self
            - blocType (subclass of Tile) : the type of tile to check if self is an instance
        Returns:
            bool : True if the tile is of this instance, False otherwise.
        '''
        return isinstance(self, blocType)

    def is_one_types(self, *blocTypes):
        '''
        Similar as is_type but it can test if the tile is instance of one of the specified tile subclasses.
        Parameters:
            - self
            - *blocTypes ([subclass of Tile])
        Returns:
            bool : True if the tile is instance of at least one of the specified tile subclass. False otherwise.
        '''
        for blocType in blocTypes:
            if isinstance(self, blocType):
                return True
        return False

    def become(self, tileType):
        '''
        Returns instance of another tile but with same parameters as this one.
        Mostly used to make tiles of the tilemap become other tiles
        '''
        
        return tileType(size = self.rect)
        
    def copy(self, *args, **kwargs):
        '''
        Create an instance of a similar tile
        '''
        return type(self).__init__(*args,**kwargs)
        
    def get_describing_image(self, size):
        '''
        Returns the image that should be used to describe the tile (in toolbox or in level editor).
        If to describing tile is set, returns the basic image.
        Parameters:
            size ( tuple(x, y) ) : The size of the image
        Returns:
            pygame.surface.Surface : The image
        '''
        if self.describing_image:
            return load_image(self.describing_image,size)
        else:
            return self.image
            

## Begin tiles definitions

class Air(Tile):
    '''
    Air tile if the default one.
    It is traversable by entities
    '''
    def __init__(self,*args,**kwargs):
        Tile.__init__(self,None,*args,**kwargs)
        self.traversable = True

class GrassTile(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/grass.png',*args,**kwargs)

class GrassLeft(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/grassLeft.png',*args,**kwargs)

class GrassMiddle(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/grassMid.png',*args,**kwargs)

class GrassUp(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/grassUp.png',*args,**kwargs)

class GrassRight(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/grassRight.png',*args,**kwargs)

class GrassHalfTile(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/grassHalf.png',*args,**kwargs)

class GrassHalfLeft(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/grassHalfLeft.png',*args,**kwargs)

class GrassHalfMiddle(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/grassHalfMid.png',*args,**kwargs)

class GrassHalfRight(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/grassHalfRight.png',*args,**kwargs)

class Antimatter(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/antimatter.png',*args,**kwargs)
        self.traversable = True


class PortalBlue(Tile):
    def __init__(self,target=None,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/portalBlue.gif',*args,**kwargs)
        self.traversable = True

class PortalGreen(Tile):
    def __init__(self,target=None,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/portalGreen.gif',*args,**kwargs)
        self.traversable = True

class PortalRed(Tile):
    def __init__(self,target=None,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/portalRed.gif',*args,**kwargs)
        self.traversable = True
        

class DirtTile(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/dirt.png',*args,**kwargs)

class SpringLeft(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/springLeft.png',*args,**kwargs)
        self.traversable = True

class SpringRight(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/springRight.png',*args,**kwargs)
        self.traversable = True

class SpringLeftPressed(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/springLeftPressed.png',*args,**kwargs)
        self.traversable = True

class SpringRightPressed(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/springRightPressed.png',*args,**kwargs)
        self.traversable = True
        
class TileTarget(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/target.png',*args,**kwargs)
        self.traversable = True

class Box(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/box.png',*args,**kwargs)
        self.traversable = False

class BrokenBox(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/brokenBox.png',*args,**kwargs)
        self.traversable = True
        
class InvisibleBloc(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, None,*args,**kwargs)
        self.traversable = False
        self.describing_image = 'Ressources/Tiles/invisible.png'
        
class Bricks(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/bricks.png',*args,**kwargs)
        self.traversable = False
        
class Spikes(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/spikes.png',*args,**kwargs)
        self.traversable = True
        
class Ladder(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/ladder.png',*args,**kwargs)
        self.traversable = True
    
class ButtonUp(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/buttonUp.png',*args,**kwargs)
        self.traversable = True
        
class ButtonDown(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/buttonDown.png',*args,**kwargs)
        self.traversable = True
        
class Metal(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/metal.png',*args,**kwargs)
        self.traversable = False

class SpikesDown(Tile):
    def __init__(self,*args,**kwargs):
        Tile.__init__(self, 'Ressources/Tiles/spikesDown.png',*args,**kwargs)
        self.traversable = False



# Link every tiles type to a numeric identifier in order to simplify tilemap storing in different level files

identifiers = {
    0: Air,
    1: GrassTile,
    2: GrassLeft,
    3: GrassMiddle,
    4: GrassRight,
    5: GrassUp,
    6: GrassHalfTile,
    7: GrassHalfLeft,
    8: GrassHalfMiddle,
    9: GrassHalfRight,
    10: DirtTile,
    11: Antimatter,
    12: PortalBlue,
    13: PortalGreen,
    14: PortalRed,
    15: SpringLeft,
    16: SpringRight,
    17: SpringLeftPressed,
    18: SpringRightPressed,
    19: TileTarget,
    20: Box,
    21: BrokenBox,
    22: InvisibleBloc,
    23: Bricks,
    24: Spikes,
    25: Ladder,
    26: ButtonUp,
    27: ButtonDown,
    28: Metal,
    29: SpikesDown,
}


if __name__ == '__main__':
    print ('\nSyntax: OK')