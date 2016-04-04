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

from math import sqrt
from numpy.random import normal
from random import random
from svgwrite import mm
import ConfigParser
import sys

import svgwrite

def distance(a,b):
    ''' return the euclidean distance between points a and b in 2D space '''
    return sqrt( (a[0] - b[0])**2 + (a[1] - b[1])**2 )

def add_circle(dwg,radius,center,fill='none'):
    ''' add a circle to Drawing '''
    circle1 = dwg.circle(
                         center = center,
                         r = radius,
                         fill = fill,
                         stroke = 'black',
                         stroke_width = 1,
        )
    dwg.add(circle1)

class BubbleContainer:
    ''' Contains bubbles '''
    def __init__(self):
        self.container = list()

    def __iter__(self):
        for b in self.container:
            yield b

    def __len__(self):
        return len(self.container)

    def new_bubble(self,dwg,bubble_size_dict):
        # TODO x, y don't need to be int
        x = 2*coaster_radius*random()
        y = 2*coaster_radius*random()
        r = 0
        m = bubble_size_dict["mean"]
        s = bubble_size_dict["deviation"]
        while r < min_bubble_size or m - s < r < m + s:
            r = normal(m,s)
        bubble = Bubble(r,x,y)
        if bubble.in_valid_place():
            self.container.append(bubble)

bubble_container = BubbleContainer()

class Bubble:
    ''' A bubble is a circle with radius and center (x,y) all in mm '''
    def __init__(self,radius,x,y):
        self.radius = radius
        self.x = x
        self.y = y
        self.center = (x,y)

    def add(self,dwg):
        ''' add this to the Drawing dwg'''
        add_circle(dwg,self.radius*mm,(self.x*mm,self.y*mm))

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
    dwg = svgwrite.Drawing(filename, drawing_size)
    print "Creating coaster ... ",
    sys.stdout.flush()
    add_circle(dwg,
               radius = coaster_radius*mm,
               center = (coaster_radius*mm,coaster_radius*mm)
        )
    print "done"
    timeout_at = time.time() + timeout
    print "Placing large bubbles ... ",
    sys.stdout.flush()
    while len(bubble_container) < max_large_bubbles and time.time() < timeout_at:
        bubble_container.new_bubble(dwg,large_bubble)
    timeout_at = time.time() + timeout
    print "done"
    print "Filling gaps with small bubbles ... ",
    sys.stdout.flush()
    while time.time() < timeout_at:
        bubble_container.new_bubble(dwg,small_bubble)
    print "done"
    print "Drawing ... ",
    sys.stdout.flush()
    for b in bubble_container:
        b.add(dwg)
    print "done"
        
    print "Saving ... ",
    sys.stdout.flush()
    dwg.save()
    print "done"

if __name__ == '__main__':
    import os
    try:
        filename = sys.argv[1]
    except:
        filename = "out.svg"
    if os.path.exists(filename):
        print "File %s exists" % filename
        sys.exit(1)

    try:
        cfgfile = sys.argv[2]
    except:
        cfgfile = "default.cfg"

    config = ConfigParser.RawConfigParser()
    config.read(cfgfile)

    coaster_radius = config.getfloat('Coaster', 'radius')
    coaster_boarder = config.getfloat('Coaster', 'boarder')
    min_bubble_gap = config.getfloat('Bubbles', 'min_gap')
    small_bubble = {
        "mean" : config.getfloat('Bubbles', 'small_bubble.mean'),
        "deviation" : config.getfloat('Bubbles', 'small_bubble.deviation')
    }
    large_bubble = {
        "mean" : config.getfloat('Bubbles', 'large_bubble.mean'),
        "deviation" : config.getfloat('Bubbles', 'large_bubble.deviation')
    }
    min_bubble_size = config.getfloat('Bubbles', 'min_size')
    max_large_bubbles = config.getfloat('Bubbles', 'max_large_bubbles')
    timeout = config.getint('Bubbles', 'timeout')
    coaster_center = (coaster_radius, coaster_radius)
    drawing_size = (2*coaster_radius*mm,2*coaster_radius*mm)

    main()
    print "File written to %s" % filename
    os.system("xdg-open %s &" % filename)
