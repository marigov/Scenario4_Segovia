from shapely.geometry.polygon import LinearRing, Polygon
import numpy as np

class Room():
    def __init__(self, shape):
        self.shape = shape
        self.polygon = Polygon(np.array(shape, dtype=np.float64))

class FurnitureItem():
    def __init__(self, unitcost, shape):
        self.shape = shape
        self.unit_cost = unitcost
        self.polygon = Polygon(np.array(shape, dtype=np.float64))
        self.total_cost = np.float64((np.float64(self.unit_cost) * self.polygon.area))
        self.sorting = (self.polygon, self.polygon.area)

class Problem():
    def __init__(self, room, furniture):
        self.room = room
        self.furniture = furniture
