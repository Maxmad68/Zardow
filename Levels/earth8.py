
from Tiles import *
from Entities import *

dimension = [[3, 10, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[3, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[3, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[3, 19, 25, 25, 25, 25, 25, 25, 25, 25, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[3, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 11, 0, 0, 0, 0, 0, 0, 0, 10, 10],
[3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10],
[3, 11, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10],
[3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10],
[3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10],
[3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 10, 10, 10, 10, 10, 10, 10, 10, 3],
[3, 19, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
[3, 3, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
[3, 3, 10, 3, 0, 0, 0, 0, 10, 10, 10, 3, 10, 10, 10, 3, 10, 10, 10, 10],
[3, 3, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
[3, 3, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]]

position = (3, 1)
rocketPosition = (13, 10)
antimatter = 3

direction = Direction.RIGHT
inventory = [SpringRight, SpringLeft, Ladder]

background = 'earth.png'
music = 'earth'

message = ['']
