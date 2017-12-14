import numpy as np
import time
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import random
from shapely import affinity
import matplotlib.pyplot as plt
from scipy import optimize

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

problems = []
with open('problems.rfp') as f:
    for line in f:
        furnitureList = []
        problem = line.replace(" ","").split("#")

        room_shape = problem[0].split(":")[1]
        furniture = problem[1].split(";")

        room = Room([tuple(np.float64(i) for i in el.strip('()').split(',')) for el in room_shape.split('),(')])

        for furnitureItem in furniture:
            parse_furniture = furnitureItem.strip().split(":")
            unit_cost = parse_furniture[0]
            shape = [tuple(np.float64(i) for i in el.strip('()').split(',')) for el in parse_furniture[1].split('),(')]
            furnitureItem = FurnitureItem(unit_cost, shape)
            furnitureList.append(furnitureItem)
        problems.append(Problem(room,furnitureList))

def random_points_within(poly, num_points):
    min_x, min_y, max_x, max_y = poly.bounds
    points = []
    while len(points) < num_points:
        random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
        if (random_point.within(poly)):
            points.append(random_point)
    return points



def insertRandomShape(room, shape):
    room_coordinates = list(zip(*room.exterior.xy))
    random_vertex = random.randint(0, len(room_coordinates) - 1)
    room_vertex = room_coordinates[random_vertex]
    shape_coordinates = list(zip(*shape.exterior.xy))

    room_coordinate_x = room_vertex[0]
    room_coordinate_y = room_vertex[1]

    def f(angle):
        return affinity.rotate(shape, angle, origin=(room_coordinate_x, room_coordinate_y)).difference(room).area

    for shape_coordinate_x, shape_coordinate_y in shape_coordinates:
        new_translated_shape = affinity.translate(shape, room_coordinate_x - shape_coordinate_x, room_coordinate_y - shape_coordinate_y)
        angle = np.float64(360) + optimize.minimize_scalar(f, bounds=(0,360), method='golden', options={'xtol': 1e-15}).x
        new_rotated_shape = affinity.rotate(new_translated_shape, angle, origin=(room_coordinate_x, room_coordinate_y))

        if (room.difference(new_rotated_shape).area == room.area - new_rotated_shape.area):
            new_updatable_room = Polygon()
            room_to_check = room.difference(new_rotated_shape)
            if (room_to_check.geom_type == 'MultiPolygon'):
                for poly in room_to_check:
                    new_updatable_room.union(poly)
            else:
                new_updatable_room = room_to_check

            if new_updatable_room.area > 0.00000000000000000000001:
                return (True, new_updatable_room, new_rotated_shape)
            else:
                continue
    return (False, room, shape)


def insertShape(room, shape, x, y):
    shape_coordinates = list(zip(*shape.exterior.xy))

    room_coordinate_x = x
    room_coordinate_y = y

    def f(angle):
        return affinity.rotate(shape, angle, origin=(room_coordinate_x, room_coordinate_y)).difference(room).area

    for shape_coordinate_x, shape_coordinate_y in shape_coordinates:
        new_translated_shape = affinity.translate(shape, room_coordinate_x - shape_coordinate_x, room_coordinate_y - shape_coordinate_y)
        angle = np.float64(360) + optimize.minimize_scalar(f, bounds=(0,360), method='golden', options={'xtol': 1e-15}).x
        new_rotated_shape = affinity.rotate(new_translated_shape, 0, origin=(room_coordinate_x, room_coordinate_y))

        if (room.difference(new_rotated_shape).area == room.area - new_rotated_shape.area):
            new_updatable_room = Polygon()
            room_to_check = room.difference(new_rotated_shape)
            if (room_to_check.geom_type == 'MultiPolygon'):
                for poly in room_to_check:
                    new_updatable_room.union(poly)
            else:
                new_updatable_room = room_to_check

            if new_updatable_room.area > 0.00000000000000000000001:
                return (True, new_updatable_room, new_rotated_shape)
            else:
                continue
    return (False, room, shape)

def algorithm(problem):
    updatable_room = problem.room.polygon
    shapes = problem.furniture
    updatable_room = updatable_room.difference(Polygon([(-129.88579350461248, 184.11594348582952), (-1.1023128184359925, 20.779434699969865), (19.314750779796498, 36.877369785741934), (-109.46872990638, 200.21387857160158)]))
    solution = []
    solution_shapes = []

    sorted_shapes = []
    for shape in shapes:
        sorted_shapes.append((shape, shape.total_cost))

    sorted_shapes = sorted(sorted_shapes, key = lambda x:x[1], reverse=True)
    '''
    for shape, d in sorted_shapes:
        for (x, y) in list(zip(*updatable_room.exterior.xy)):
            (isInserted, updatable_room, updated_shape) = insertShape(updatable_room, shape.polygon, x, y)
            if isInserted:
                x, y = updated_shape.exterior.xy
                solution_shapes.append(shape)
                solution.append(list(zip(*(x, y))))
                print(1 - updatable_room.area / problem.room.polygon.area)
                sorted_shapes.remove((shape, d))
                break
    '''
    for i in range(1):
        for shape, d in sorted_shapes:
            (tmpX, tmpY) = shape.polygon.exterior.xy
            (isInserted, updatable_room, updated_shape) = insertRandomShape(updatable_room, shape.polygon)
            if isInserted:
                x, y = updated_shape.exterior.xy
                solution_shapes.append(shape)
                solution.append(list(zip(*(x,y))))
                print(1 - updatable_room.area / problem.room.polygon.area)
                sorted_shapes.remove((shape, d))

    print("First a stecca finished")
    for i in range(20):
        for shape, d in sorted_shapes:
            x, y = shape.polygon.exterior.xy
            points = random_points_within(updatable_room, 1)[0]
            polygon = affinity.translate(shape.polygon, points.x, points.y)
            polygon = affinity.rotate(polygon, random.uniform(0, 0), origin="centroid")
            if updatable_room.contains(polygon):
                updatable_room = updatable_room.difference(polygon)
                x, y = polygon.exterior.xy
                solution_shapes.append(shape)
                solution.append(list(zip(*(x, y))))
                sorted_shapes.remove((shape, d))
                print(1 - updatable_room.area / problem.room.polygon.area)
    print("Area coverage: " + str(1 - (updatable_room.area / problem.room.polygon.area)))
    return (solution, solution_shapes)

def get_output(solution):
    output = ""
    for x in solution:
        output = output + str(x[:-1]).replace('[','').replace(']','') + "; "
    return output

def get_cost(solution_shapes):
    total_cost = 0
    for shape in solution_shapes:
        total_cost = total_cost + shape.total_cost
    return total_cost

i = 23
(solution, solution_shapes) = algorithm(problems[i-1])
print("Problem" + str(i))
print(get_output(solution))
print(get_cost(solution_shapes))


