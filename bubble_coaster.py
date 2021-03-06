# The MIT License (MIT)
# Copyright (c) 2016 Will Holland

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
  
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
  
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This script was written to generate an svg for a drinks coaster with a bubble
# design. It randomly places bubbles of random sizes within the coaster circle.
# I noticed while observing bubbles in foam that there tend to be large bubbles
# and the gaps between them are filled with smaller bubbles so this script has
# the concept of small_bubbles and large_bubbles. These are generated according
# to the normal distribution and the parameters can be tweaked separately

from math import cos
from math import log
from math import pi
from math import sin
from math import sqrt
from random import random
import sys

from numbers import Number

class Mm:
    def __mul__(self, other):
        if isinstance(other,Number):
            return "%smm" % other
        raise TypeError("Tried to apply mm to a non-number")

    def __rmul__(self, other):
        return self.__mul__(other)

mm = Mm()

if sys.version_info >= (3, 0):
    # if python 3.x
    from configparser import RawConfigParser
else:
    # if python 2.x
    from ConfigParser import RawConfigParser

def help(_exit=0):
    sys.stdout.write("usage: git [-h] [-c <config file path>] [<output file path>]\n")
    sys.exit(_exit)

def distance(a,b):
    ''' return the euclidean distance between points a and b in 2D space '''
    return sqrt( (a[0] - b[0])**2 + (a[1] - b[1])**2 )

def boxmuller(mu,sigma):
    ''' A transformation which transforms from a two-dimensional continuous
        uniform distribution to a two-dimensional bivariate normal distribution
    '''
    u = random()
    v = random()

    z1 = sqrt(-2 * log(u)) * sin(2 * pi * v)
    z2 = sqrt(-2 * log(u)) * cos(2 * pi * v)

    x1 = mu + z1 * sigma
    x2 = mu + z2 * sigma

    return x2

def add_circle(radius,center,stroke='black',fill='none'):
    ''' add a circle to Drawing '''
    stroke_width = 1
    outfile.write('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (center[0],center[1],radius,fill,stroke,stroke_width))
    outfile.write('\n')

class BubbleContainer:
    ''' Contains bubbles '''
    def __init__(self):
        self.container = list()

    def __iter__(self):
        for b in self.container:
            yield b

    def __len__(self):
        return len(self.container)

    def new_bubble(self,bubble_dict):
        x = 2*coaster_radius*random()
        y = 2*coaster_radius*random()
        r = 0
        m = bubble_dict["mean"]
        s = bubble_dict["deviation"]
        stroke = bubble_dict["stroke"]
        fill = bubble_dict["fill"]
        if max_bubble_size == -1:
            while r < min_bubble_size:
                r = boxmuller(m,s)
        else:
            while r < min_bubble_size or max_bubble_size < r:
                r = boxmuller(m,s)
        bubble = Bubble(r,x,y,stroke,fill)
        if bubble.in_valid_place():
            self.container.append(bubble)

bubble_container = BubbleContainer()

class Bubble:
    ''' A bubble is a circle with radius and center (x,y) all in mm '''
    def __init__(self,radius,x,y,stroke='black',fill='none'):
        self.radius = radius
        self.x = x
        self.y = y
        self.stroke = stroke
        self.fill = fill
        self.center = (x,y)

    def add(self):
        ''' add this to the svg'''
        add_circle(
                   self.radius*mm,
                   (self.x*mm,self.y*mm),
                   self.stroke,
                   self.fill
            )

    def in_coaster(self):
        ''' True if this is completely within the coaster and clear of the
            boarder described in config '''
        dist = distance(self.center, coaster_center)
        if (dist + self.radius + coaster_boarder) > coaster_radius:
            return False
        return True

    def too_close(self,bubble):
        ''' True if this is too close to another bubble, ie overlapping or
            within min_bubble_gap of it '''
        dist = distance(self.center,bubble.center)
        if dist < self.radius + bubble.radius + min_bubble_gap:
            return True
        return False

    def in_valid_place(self):
        ''' True if this has valid x,y coordinates and radius '''
        if not self.in_coaster():
            return False
        for B in bubble_container:
            if self.too_close(B):
                return False
        return True

def main():
    ''' Create a coaster and fill it with bubbles '''
    import time
    sys.stdout.write("Creating coaster ... ")
    sys.stdout.flush()
    add_circle(
               radius = coaster_radius*mm,
               center = (coaster_radius*mm,coaster_radius*mm)
        )
    sys.stdout.write("done\n")
    timeout_at = time.time() + timeout
    sys.stdout.write("Placing large bubbles ... ")
    sys.stdout.flush()
    if timeout == -1:
        while True:
            bubble_container.new_bubble(large_bubble)
            if max_large_bubbles != -1:
                if len(bubble_container) >= max_large_bubbles:
                    break
    else:
        while time.time() < timeout_at:
            bubble_container.new_bubble(large_bubble)
            if max_large_bubbles != -1:
                if len(bubble_container) >= max_large_bubbles:
                    break
    timeout_at = time.time() + timeout
    num_large_bubbles = len(bubble_container)
    sys.stdout.write("placed %s large bubbles\n" % num_large_bubbles)
    sys.stdout.write("Filling gaps with small bubbles ... ")
    sys.stdout.flush()
    if timeout == -1:
        while True:
            bubble_container.new_bubble(small_bubble)
            if max_small_bubbles != -1:
                if len(bubble_container) >= max_small_bubbles:
                    break
    else:
        while time.time() < timeout_at:
            bubble_container.new_bubble(small_bubble)
            if max_small_bubbles != -1:
                if len(bubble_container) >= max_small_bubbles:
                    break
    num_small_bubbles = len(bubble_container) - num_large_bubbles
    sys.stdout.write("placed %s small bubbles\n" % num_small_bubbles)
    sys.stdout.write("Drawing ... ")
    sys.stdout.flush()
    for b in bubble_container:
        b.add()
    sys.stdout.write("done\n")
        
    sys.stdout.write("Saving ... ")
    sys.stdout.flush()
    sys.stdout.write("done\n")

if __name__ == '__main__':
    import os
    import getopt

    optlist, args = getopt.getopt(sys.argv[1:], 'hc:')

    arg_dict = {}
    for opt in optlist:
        arg_dict[opt[0]] = opt[1]

    if ('-h','') in optlist:
        help(0)

    if len(args) > 1:
        sys.stdout.write("Too many arguments provided\n")
        help(1)
    elif len(args) < 1:
        filename = "out.svg"
        counter = 0
        while os.path.exists(filename):
            counter += 1
            filename = "out_%s.svg" % counter
    else:
        filename = args[0]
        if os.path.exists(filename):
            sys.stdout.write("File %s exists\n" % filename)
            sys.exit(1)

    cfgfile = arg_dict.get('-c',"default.cfg")

    outfile = open(filename,"w")
    svg_version=1.1

    config = RawConfigParser()
    config.read(cfgfile)

    coaster_radius = config.getfloat('Coaster', 'radius')
    coaster_boarder = config.getfloat('Coaster', 'boarder')
    min_bubble_gap = config.getfloat('Bubbles', 'min_gap')
    small_bubble_stroke = config.get('Bubbles', 'small_bubble.stroke')
    small_bubble_fill = config.get('Bubbles', 'small_bubble.fill')
    small_bubble = {
        "mean" : config.getfloat('Bubbles', 'small_bubble.mean'),
        "deviation" : config.getfloat('Bubbles', 'small_bubble.deviation'),
        "stroke" : small_bubble_stroke,
        "fill" : small_bubble_fill
    }
    large_bubble_stroke = config.get('Bubbles', 'large_bubble.stroke')
    large_bubble_fill = config.get('Bubbles', 'large_bubble.fill')
    large_bubble = {
        "mean" : config.getfloat('Bubbles', 'large_bubble.mean'),
        "deviation" : config.getfloat('Bubbles', 'large_bubble.deviation'),
        "stroke" : large_bubble_stroke,
        "fill" : large_bubble_fill
    }
    min_bubble_size = config.getfloat('Bubbles', 'min_size')
    max_bubble_size = config.getfloat('Bubbles', 'max_size')
    max_large_bubbles = config.getfloat('Bubbles', 'max_large_bubbles')
    max_small_bubbles = config.getfloat('Bubbles', 'max_small_bubbles')
    timeout = config.getint('Bubbles', 'timeout')
    coaster_center = (coaster_radius, coaster_radius)
    drawing_size = (2*coaster_radius*mm,2*coaster_radius*mm)

    outfile.write('<?xml version="1.0"?>')
    outfile.write('<svg width="%s" height="%s" version="%s">\n' % (drawing_size[0], drawing_size[1],svg_version))

    main()

    outfile.write('</svg>\n')
    outfile.close()
    sys.stdout.write("File written to %s\n" % filename)
    os.system("xdg-open %s &" % filename)
