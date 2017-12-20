from shapely.geometry.polygon import LinearRing, Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely.ops import cascaded_union
import matplotlib.colors as colors
from shapely.geometry import Point
from itertools import chain
import numpy as np
import matplotlib.pyplot as plt
from shapely import affinity
import random

def draw_room(room):
    x, y = room.exterior.xy
    plt.fill(x, y, '#7f8c8d', alpha=1)

def draw_shape(shape):
    x, y = shape.exterior.xy
    #ax.fill(x, y, '#7f8c8d', alpha=1)
    plt.fill(x, y, '#c0392b', alpha=0.5)


def draw_furniture(item, intensity, unit_cost, color):
    x, y = item.exterior.xy
    (minx, miny, maxx, maxy) = item.bounds
    plt.fill(x, y, color, alpha=intensity)
    plt.text(maxx, maxy, str(unit_cost) , fontsize=8, color='black')

def draw_remaining_furniture(room, furniture_list, color):
    plotted_items = []
    plotted_items.append(room)
    total_area = 0
    max_cost = 0
    min_cost = 0
    for item in furniture_list:
        if int(item.unit_cost) > max_cost:
            max_cost = int(item.unit_cost)
        if int(item.unit_cost) < min_cost:
            min_cost = int(item.unit_cost)

        total_area = total_area + item.polygon.area
    plotted_shape = room
    margin = np.sqrt(total_area)*2
    for item in furniture_list:
        item_poly = item.polygon

        rand_point = Point([random.uniform(-margin, margin), random.uniform(-margin, margin)])
        shape_to_plot = affinity.translate(item_poly, rand_point.x, rand_point.y)

        while(plotted_shape.intersects(shape_to_plot) or plotted_shape.contains(shape_to_plot)):
            rand_point = Point([random.uniform(-margin, margin), random.uniform(-margin, margin)])
            shape_to_plot = affinity.translate(item_poly, rand_point.x, rand_point.y)

        draw_furniture(shape_to_plot, (int(item.unit_cost)-min_cost)/(max_cost-min_cost)*0.8+0.2,item.unit_cost, color)
        plotted_items.append(shape_to_plot)
        plotted_shape = cascaded_union(plotted_items)

#draw_scattered(problems[2].room.polygon, problems[2].furniture, color)
#plt.axis('equal')
#plt.show()