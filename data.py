from enum import Enum, unique

from utils import Struct


@unique
class Rating(Enum):
    WATCHED = -1
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6
    R7 = 7
    R8 = 8
    R9 = 9
    R10 = 10

class ItemInfo(Struct):
    title = None
    year = None
    rating = None
    folders = None
