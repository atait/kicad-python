'''
    This script will put all your components on an arc path. You can
    define the parameters of the arc in the script (see below). All
    components will be modified but making it select desired components
    shouldn't be hard.
'''

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
