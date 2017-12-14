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

        if (room.difference(new_rotated_shape).area < (room.area - new_rotated_shape.area) + 5) or (room.difference(new_rotated_shape).area > (room.area - new_rotated_shape.area) - 5):
            new_updatable_room = Polygon()
            room_to_check = room.difference(new_rotated_shape)
            if (room_to_check.geom_type == 'MultiPolygon'):
                for poly in room_to_check:
                    new_updatable_room.union(poly)
            else:
                new_updatable_room = room_to_check

            if new_updatable_room.area > 0.00000000000000000000001:
                # plt.plot(updatedRoom, updatedRoomY, color='#6699cc', alpha=0.7, linewidth=3, solid_capstyle='round',
                #          zorder=2)
                # plt.plot(x, y, color='#e50000', alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)
                # display.display(plt.gcf())
                # display.display(plt.clf())
                # display.clear_output(wait=True)
                # time.sleep(0.0001)
                # plt.show()
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

    solution = []
    solution_shapes = []

    sorted_shapes = []
    for shape in shapes:
        sorted_shapes.append((shape, shape.total_cost))

    sorted_shapes = sorted(sorted_shapes, key = lambda x:x[1], reverse=True)

    # for shape, d in sorted_shapes:
    #     x, y = shape.polygon.exterior.xy
    #     if shape.polygon.area == 48.00000000000001:
    #         print("Entrati")
    #         (isInserted, updatable_room, updated_shape) = insertRandomShape(updatable_room, shape.polygon)
    #         while not isInserted:
    #             (isInserted, updatable_room, updated_shape) = insertRandomShape(updatable_room, shape.polygon)
    #             if isInserted:
    #                 x, y = updated_shape.exterior.xy
    #                 solution_shapes.append(shape)
    #                 solution.append(list(zip(*(x,y))))
    #                 print(1 - updatable_room.area / problem.room.polygon.area)
    #                 sorted_shapes.remove((shape, d))
    #                 print(shape.polygon.exterior.xy)
    #                 print("Inserito quadrato")
    #                 break

    for i in range(2):
        for shape, d in sorted_shapes:
            (isInserted, updatable_room, updated_shape) = insertRandomShape(updatable_room, shape.polygon)
            if isInserted:
                x, y = updated_shape.exterior.xy
                solution_shapes.append(shape)
                solution.append(list(zip(*(x,y))))
                print(1 - updatable_room.area / problem.room.polygon.area)
                sorted_shapes.remove((shape, d))
                newPlot(updatable_room, updated_shape)

    print("First a stecca finished")

    # for i in range(20):
    #     for shape, d in sorted_shapes:
    #         if (shape.polygon.area == 12.5):
    #             x, y = shape.polygon.exterior.xy
    #             points = random_points_within(updatable_room, 1)[0]
    #             polygon = affinity.translate(shape.polygon, points.x, points.y)
    #             polygon = affinity.rotate(polygon, random.uniform(0, 180), origin="centroid")
    #             while not updatable_room.contains(polygon):
    #                 x, y = shape.polygon.exterior.xy
    #                 points = random_points_within(updatable_room, 1)[0]
    #                 polygon = affinity.translate(shape.polygon, points.x, points.y)
    #                 polygon = affinity.rotate(polygon, random.uniform(0, 180), origin="centroid")
    #             updatable_room = updatable_room.difference(polygon)
    #             x, y = polygon.exterior.xy
    #             solution_shapes.append(shape)
    #             solution.append(list(zip(*(x, y))))
    #             sorted_shapes.remove((shape, d))
    #             print(1 - updatable_room.area / problem.room.polygon.area)

    # for i in range(10):
    #     for shape, d in sorted_shapes:
    #         x, y = shape.polygon.exterior.xy
    #         points = random_points_within(updatable_room, 1)[0]
    #         polygon = affinity.translate(shape.polygon, points.x, points.y)
    #         polygon = affinity.rotate(polygon, random.uniform(0, 180), origin="centroid")
    #         if updatable_room.contains(polygon):
    #             updatable_room = updatable_room.difference(polygon)
    #             x, y = polygon.exterior.xy
    #             solution_shapes.append(shape)
    #             solution.append(list(zip(*(x, y))))
    #             sorted_shapes.remove((shape, d))
    #             print(1 - updatable_room.area / problem.room.polygon.area)

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

# i = 3
# (solution, solution_shapes) = algorithm(problems[i-1])
# while (get_cost(solution_shapes) < 200):
#     (solution, solution_shapes) = algorithm(problems[i - 1])
#     print("Problem" + str(i))
#     print("Solution" + get_output(solution))
#     print("Cost: " + str(get_cost(solution_shapes)))
#     print("\n")
#
# print("CI SIAMO -----------")
# print("Problem" + str(i))
# print(get_output(solution))
# print(get_cost(solution_shapes))


# poly = Polygon([(62.231807006994536, -9.859117437386894), (34.64972834903697, -5.03947669286642), (33.96120824267689, -8.979773644003235), (61.543286900634456, -13.799414388523708)])
# newPlot(problems[21].room.polygon, Polygon([(21.89146917959829, 3.280789106099032), (21.547209126418256, 1.3106406305306413), (7.756169797439478, 3.7204610027908798), (8.100429850619511, 5.690609478359271)]) )

def get_output(solution):
    output = ""
    for x in solution:
        output = output + str(x[:-1]).replace('[', '').replace(']', '') + "; "
    return output

# def plot(poly):
#     x,y = poly.exterior.xy
#     plt.plot(x, y, color='#6699cc', alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)
#     plt.show()
#
# plot(Polygon([(6.0, 0.0), (10.0, 0.0), (10.0, 10.0), (6.0, 10.0) (0.0, 0.0), (6.0, 0.0), (0.0, 10.0)]))


def insertShape(room, shape, x, y):
    shape_coordinates = list(zip(*shape.exterior.xy))

    room_coordinate_x = x
    room_coordinate_y = y

    updatable_room = room


    for shape_coordinate_x, shape_coordinate_y in shape_coordinates:
        new_translated_shape = affinity.translate(shape, room_coordinate_x - shape_coordinate_x, room_coordinate_y - shape_coordinate_y)

        def f(angle):
            return room.hausdorff_distance(affinity.rotate(new_translated_shape, angle, origin=(room_coordinate_x, room_coordinate_y)))
            #return np.float64(affinity.rotate(new_translated_shape, angle, origin=(room_coordinate_x, room_coordinate_y)).difference(room).area)

        optimization = optimize.minimize_scalar(f, bounds=(0,360), method='bounded',tol=0.0000000000001, options={'xatol': np.float64(0.00000011)})
        angle = optimization.x
        print(optimization)
        print(angle)
        new_rotated_shape = affinity.rotate(new_translated_shape, angle, origin=(room_coordinate_x, room_coordinate_y))
        newPlot(room, new_rotated_shape)
        # print(list(zip(*(new_rotated_shape.exterior.xy))))

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


(isInserted, room, shape) = insertShape(problems[19].room.polygon, Polygon([(0.0, 0.0), (52.72459822826777, -18.87105565854075), (55.08348018558537, -12.280480880007264), (2.3588819573175894, 6.590574778533473)]) , -10.13089306020976, 122.81028053791992)
# (isInserted, room, shape) = insertRandomShape(problems[19].room.polygon, Polygon([(0.0, 0.0), (52.72459822826777, -18.87105565854075), (55.08348018558537, -12.280480880007264), (2.3588819573175894, 6.590574778533473)]))

# newPlot(room, shape)
# while not isInserted:
#     (isInserted, room, shape) = insertShape(problems[22].room.polygon, Polygon(
#         [(0.0, 0.0), (52.72459822826777, -18.87105565854075), (55.08348018558537, -12.280480880007264),
#          (2.3588819573175894, 6.590574778533473)]), -10.13089306020976, 122.81028053791992)
#
#     print(isInserted)