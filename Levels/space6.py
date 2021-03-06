
from Tiles import *
from Entities import *

dimension = [[28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28],
[28, 28, 28, 0, 0, 0, 0, 28, 16, 0, 0, 0, 28, 0, 0, 0, 28, 28, 28, 28],
[28, 28, 28, 20, 0, 0, 0, 28, 0, 0, 0, 0, 28, 0, 0, 0, 28, 28, 28, 28],
[28, 28, 28, 0, 0, 0, 0, 28, 11, 0, 0, 0, 28, 28, 28, 12, 28, 28, 28, 28],
[28, 28, 28, 19, 0, 0, 0, 28, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 28, 28],
[28, 28, 28, 28, 0, 0, 0, 28, 0, 0, 0, 0, 19, 0, 0, 0, 28, 28, 28, 28],
[28, 28, 28, 28, 0, 0, 19, 28, 26, 0, 0, 0, 0, 0, 0, 19, 28, 28, 28, 28],
[28, 28, 28, 28, 0, 0, 0, 28, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 28, 28],
[28, 28, 28, 16, 0, 0, 0, 28, 0, 0, 0, 0, 0, 0, 0, 11, 28, 28, 28, 28],
[28, 28, 28, 0, 0, 0, 0, 28, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 28, 28],
[28, 0, 19, 0, 0, 0, 0, 28, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 28, 28],
[28, 0, 28, 0, 0, 0, 0, 28, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 28, 28],
[28, 26, 19, 0, 0, 0, 0, 28, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 28, 28],
[28, 28, 28, 0, 0, 0, 0, 28, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 28, 28],
[28, 28, 28, 11, 0, 0, 0, 28, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 28, 28],
[28, 28, 28, 0, 0, 0, 0, 28, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 28, 28],
[28, 28, 28, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 28, 28],
[28, 28, 28, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 28, 28, 28, 28],
[28, 28, 28, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 28, 28, 28, 28],
[28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28]]

position = (1, 3)
rocketPosition = (1, 13)
antimatter = 3

direction = Direction.RIGHT
inventory = [Box, ButtonUp, ButtonDown, ButtonDown, PortalBlue, Box]

background = 'space.png'
music = 'space'

message = ['']
