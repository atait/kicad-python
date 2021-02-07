# -*- coding: utf-8 -*-
#
# This script will put all your components on an arc path. You can
# define the parameters of the arc in the script (see below). All
# components will be modified but making it select desired components
# shouldn't be hard.
#
# Copyright © 2015 Hasan Yavuz Özderya
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

from math import cos, sin, radians, pi
from kicad.pcbnew.board import Board

# PARAMETERS
center = (100, 100)
radius = 40
start = 0 # degrees
end = radians(-180) # degreees

#
b = Board.from_editor()

# get a list of components to put on arc
comps = []

for m in b.modules:
    # MAYBE FILTER COMPONENTS HERE
    comps.append(m)

# put components on arc
angle = end-start
step = angle/float(len(comps)-1)

for i, comp in enumerate(comps):
    angle_i = start + step*i
    comp.x = center[0] + radius * cos(angle_i)
    comp.y = center[0] + radius * sin(angle_i)
    comp.rotation = pi/2.-angle_i

print("Done")
