import numpy as np
import time
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import random
from shapely import affinity
import matplotlib.pyplot as plt
from scipy import optimize
from viewer import *
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

def newPlot(room, poly):
    x, y = poly.exterior.xy
    x2, y2 = room.exterior.xy
    plt.plot(x, y, color='#6699cc', alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)
    plt.plot(x2, y2, color='#ff0000', alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)
    plt.show()
    time.sleep(3)

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

def random_points_within(poly, num_points):
    min_x, min_y, max_x, max_y = poly.bounds
    points = []
    while len(points) < num_points:
        random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
        if (random_point.within(poly)):
            points.append(random_point)
    return points


def algorithm(problem):
    room_polygon = problem.room.polygon
    updatable_room = room_polygon
    shapes = problem.furniture
    solution_translated_shapes = []

    solution = []
    solution_shapes = []

    sorted_shapes = []
    for shape in shapes:
        sorted_shapes.append((shape, shape.total_cost))

    sorted_shapes = sorted(sorted_shapes, key = lambda x:x[1], reverse=True)

    for i in range(1):
        for shape, d in sorted_shapes:
            (isInserted, updatable_room, updated_shape) = insertRandomShape(updatable_room, shape.polygon)
            if isInserted:
                x, y = updated_shape.exterior.xy
                solution_shapes.append(shape)
                solution.append(list(zip(*(x,y))))
                solution_translated_shapes.append(updated_shape)
                print(1 - updatable_room.area / problem.room.polygon.area)
                sorted_shapes.remove((shape, d))

    for i in range(10):
        for shape, d in sorted_shapes:
            points = random_points_within(updatable_room, 1)[0]
            polygon = affinity.translate(shape.polygon, points.x, points.y)
            polygon = affinity.rotate(polygon, random.uniform(0, 180), origin="centroid")
            if updatable_room.contains(polygon):
                updatable_room = updatable_room.difference(polygon)
                x, y = polygon.exterior.xy
                solution_shapes.append(shape)
                solution.append(list(zip(*(x, y))))
                solution_translated_shapes.append(polygon)
                sorted_shapes.remove((shape, d))
                print(1 - updatable_room.area / problem.room.polygon.area)

    print("Area coverage: " + str(1 - (updatable_room.area / problem.room.polygon.area)))
    return (solution, solution_shapes, solution_translated_shapes)

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

i = 30
(solution, solution_shapes, solution_translated_shapes) = algorithm(problems[i-1])
print("Problem" + str(i))
print("Solution" + get_output(solution))
print("Cost: " + str(get_cost(solution_shapes)))

min_cost = 0
max_cost = 0

for item in solution_shapes:
    if int(item.unit_cost) > max_cost:
        max_cost = int(item.unit_cost)
    if int(item.unit_cost) < min_cost:
        min_cost = int(item.unit_cost)

draw_room(problems[i-1].room.polygon)

for item, polygon in list(zip(solution_shapes, solution_translated_shapes)):
    draw_furniture(polygon, (int(item.unit_cost)-min_cost)/(max_cost-min_cost)*0.8+0.2, item.unit_cost, "#1abc9c")

remaining_furniture = list(set(problems[i-1].furniture)-set(solution_shapes))
print(len(remaining_furniture), len(problems[i-1].furniture ))
draw_remaining_furniture(problems[i-1].room.polygon, remaining_furniture, "#d35400")
plt.axis('equal')
plt.show()