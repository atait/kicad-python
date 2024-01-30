# pcbnew_easy.py
import math
import cmath

from kicad import pcbnew_bare as pcbnew

print('pcbnew_easy is not supported in KiCad >= 5.99\nUse the universal interface with "from kicad import pcbnew"')

# helper functions
def _from_mm(val):
    """Convert mm to internal units"""
    return pcbnew.FromMM(float(val))

def _point_mm(x, y):
    """Convert coordinate in mm to internal coordinate"""
    return pcbnew.wxPointMM(float(x), float(y))

def _size_mm(x, y):
    """Convert size in mm to internal size"""
    return pcbnew.wxSizeMM(float(x), float(y))

def rotate(coord, angle):
    """Rotate coordinate around (0, 0)"""
    coord = (coord[0]+coord[1]*1j) * cmath.exp(math.radians(angle)*1j)
    return (coord.real, coord.imag)

# dicts for converting layer name to id, used by _get_layer
layer_dict = {pcbnew.BOARD_GetStandardLayerName(n):n for n in range(pcbnew.PCB_LAYER_ID_COUNT)}
layer_names = {s:n for n, s in layer_dict.items()}

def _get_layer(s):
    """Get layer id from layer name

    If it is already an int just return it.
    """
    return layer_dict[s]

def _to_LayerSet(layers):
    """Create LayerSet used for defining pad layers"""
    bitset = 0
    for l in layers:
        bitset |= 1 << _get_layer(l)
    hexset = '{0:013x}'.format(bitset)
    lset = pcbnew.LSET()
    lset.ParseHex(hexset, len(hexset))
    return lset

def _from_LayerSet(layerset):
    mask = [c for c in layerset.FmtBin() if c in ('0','1')]
    mask.reverse()
    ids = [i for i, c in enumerate(mask) if c == '1']
    return tuple(layer_names[i] for i in ids)



class Module(object):
    def __init__(self, module):
        """Convenience wrapper for pcbnew Module"""
        self._module = module

    @property
    def position(self):
        return pcbnew.ToMM(self._module.GetPosition())
    @position.setter
    def position(self, position):
        self._module.SetPosition(_point_mm(position[0], position[1]))

    @property
    def reference(self):
        return self._module.GetReference()
    @reference.setter
    def reference(self, value):
        self._module.SetReference(value)

    @property
    def value(self):
        return self._module.GetValue()
    @value.setter
    def value(self, value):
        self._module.SetValue(value)

    @property
    def pads(self):
        p = self._module.Pads().begin()
        while not p == None:
            yield Pad(p)
            p = p.Next()

    def flip(self, center=None):
        if center==None:
            center = self.position
        self._module.Flip(_point_mm(center[0], center[1]))

    def add_line(self, start, end, layer='F.SilkS', width=0.15):
        """Create a graphic line on the module"""
        a = pcbnew.EDGE_MODULE(self._module)
        a.SetShape(pcbnew.S_SEGMENT)
        a.SetStart(_point_mm(start[0], start[1]))
        a.SetEnd(_point_mm(end[0], end[1]))
        a.SetLayer(_get_layer(layer))
        a.SetWidth(_from_mm(width))
        a.SetLocalCoord()
        self._module.Add(a)
        return a

    def add_polyline(self, coords, layer='F.SilkS', width=0.15):
        """Create a graphic polyline on the module"""
        for n in range(len(coords)-1):
            self.add_line(coords[n], coords[n+1], layer=layer, width=width)

    def add_circle(self, center, radius, layer='F.SilkS', width=0.15):
        """Create a graphic circle on the module"""
        a = pcbnew.EDGE_MODULE(self._module)
        a.SetShape(pcbnew.S_CIRCLE)
        a.SetCenter(_point_mm(center[0], center[1]))
        start_coord = _point_mm(center[0], center[1]+radius)
        a.SetArcStart(start_coord)
        a.SetLayer(_get_layer(layer))
        a.SetWidth(_from_mm(width))
        a.SetLocalCoord()
        self._module.Add(a)
        return a

    def add_arc(self, center, radius, start_angle, stop_angle, layer='F.SilkS', width=0.15):
        """Create a graphic arc on the module"""
        start_coord = radius * cmath.exp(math.radians(start_angle-90)*1j)
        start_coord = _point_mm(start_coord.real, start_coord.imag)
        angle = stop_angle - start_angle
        a = pcbnew.EDGE_MODULE(self._module)
        a.SetShape(pcbnew.S_ARC)
        a.SetCenter(_point_mm(center[0], center[1]))
        a.SetArcStart(start_coord)
        a.SetAngle(angle*10)
        a.SetLayer(_get_layer(layer))
        a.SetWidth(_from_mm(width))
        a.SetLocalCoord()
        self._module.Add(a)
        return a

    def add_pad(self, position, size, name='', pad_type='standard', shape='circle',
                drill=1.0, layers=None):
        """Create a pad on the module

        Args:
            position: pad position in mm
            size: pad size in mm, value if shape == 'circle', tuple otherwise
            name: pad name/number
            pad_type: One of 'standard', 'smd', 'conn', 'hole_not_plated'
            shape: One of 'circle', 'rect', 'oval', 'trapezoid'
            drill: drill size in mm, single value for round hole, or tuple for oblong hole.
            layers: None for default, or a list of layer definitions (for example: ['F.Cu', 'F.Mask'])
        """
        pad = Pad(pcbnew.D_PAD(self._module))

        pad.type = pad_type
        pad.shape = shape
        pad.size = size
        pad.name = name
        pad.position = position
        pad.layers = layers

        self._module.Add(pad._pad)
        return pad

    def save(self, library_path):
        """Save footprint in given library

        library_path should end with .pretty
        """
        self._module.SetFPID(pcbnew.FPID(self._module.GetReference()))

        io = pcbnew.PCB_IO()

        try:
            io.FootprintLibCreate(library_path)
        except IOError:
            pass # we try to create, but may be it exists already

        io.FootprintSave(library_path, self._module)

class Pad(object):
    """Convenience wrapper for pcbnew Pad"""
    _pad_types = {'standard':pcbnew.PAD_STANDARD,
                  'smd':pcbnew.PAD_SMD,
                  'conn':pcbnew.PAD_CONN,
                  'hole_not_plated':pcbnew.PAD_HOLE_NOT_PLATED}
    _pad_types_id = {s:n for n, s in _pad_types.items()}
    _shapes = {'circle':pcbnew.PAD_CIRCLE,
               'rect':pcbnew.PAD_RECT,
               'oval':pcbnew.PAD_OVAL,
               'trapezoid':pcbnew.PAD_TRAPEZOID}
    _shapes_id = {s:n for n, s in _shapes.items()}

    def __init__(self, pad):
        self._pad = pad

    @property
    def position(self):
        return pcbnew.ToMM(self._pad.GetPosition())
    @position.setter
    def position(self, position):
        self._pad.SetPosition(_point_mm(position[0], position[1]))
        self._pad.SetLocalCoord()

    @property
    def name(self):
        return self._pad.GetPadName()
    @name.setter
    def name(self, value):
        self._pad.SetPadName(value)

    @property
    def type(self):
        return self._pad_types_id[self._pad.GetAttribute()]
    @type.setter
    def type(self, value):
        self._pad.SetAttribute(self._pad_types[value])

    @property
    def shape(self):
        return self._shapes_id[self._pad.GetShape()]
    @shape.setter
    def shape(self, value):
        self._pad.SetShape(self._shapes[value])

    @property
    def size(self):
        if self.shape == 'circle':
            return pcbnew.ToMM(self._pad.GetSize())[0]
        else:
            return pcbnew.ToMM(self._pad.GetSize())
    @size.setter
    def size(self, size):
        if self.shape == 'circle':
            self._pad.SetSize(_size_mm(size, size))
        else:
            self._pad.SetSize(_size_mm(size[0], size[1]))

    @property
    def orientation(self):
        return self._pad.GetOrientation()/10.0
    @orientation.setter
    def orientation(self, value):
        self._pad.SetOrientation(value*10)

    @property
    def layers(self):
        return _from_LayerSet(self._pad.GetLayerSet())
    @layers.setter
    def layers(self, value):
        if value == None: # if None set default layers
            default_masks = {'standard':self._pad.StandardMask(),
                             'smd':self._pad.SMDMask(),
                             'conn':self._pad.ConnSMDMask(),
                             'hole_not_plated':self._pad.UnplatedHoleMask()}
            self._pad.SetLayerSet(default_masks[self.type])
        else:
            self._pad.SetLayerSet(_to_LayerSet(value))

    @property
    def drill(self):
        if self.type in ('standard', 'hole_not_plated'):
            if self._pad.GetDrillShape() == pcbnew.PAD_DRILL_OBLONG:
                return pcbnew.ToMM(self._pad.GetDrillSize())
            else:
                return pcbnew.ToMM(self._pad.GetDrillSize())[0]
        else:
            return None
    @drill.setter
    def drill(self, drill):
        if self.type in ('standard', 'hole_not_plated'):
            if hasattr(drill, '__getitem__'):
                self._pad.SetDrillShape(pcbnew.PAD_DRILL_OBLONG)
                self._pad.SetDrillSize(_size_mm(drill[0], drill[1]))
            else:
                self._pad.SetDrillSize(_size_mm(drill, drill))
        else:
            pass

def get_board():
    """Get the current board"""
    return Board(pcbnew.GetBoard())


# Usage example and test
def test():
    """Make an example board

    Run in the pcbnew scripting console:
      import pcbnew_easy
      pcbnew_easy.test()
    """
    # get current board
    pcb = get_board()

    # create test module
    m = pcb.create_module('test')
    m.add_arc(center=(0, 0), radius=8, start_angle=-90, stop_angle=90, width=0.2)
    m.add_line(start=(-8, 0), end=(8, 0), width=0.2)
    m.add_pad(position=(-4, -3), size=2, drill=1)
    m.add_pad(position=(4, -3), size=2, drill=1, layers=['B.Cu', 'F.Cu'])
    for n, x in enumerate([-1, -.5, 0, .5, 1]):
        m.add_pad(position=(x, -4), size=(0.25, 1.2), name=n, pad_type='smd', shape='rect')

    # move module to right location
    m.position = (30, 30)

    # add test track with via
    track1 = [(30, 26), (30, 50), (60, 80)]
    track2 = [(60, 80), (80, 80)]
    pcb.add_track(track1, layer='F.Cu', width=0.25)
    pcb.add_track_via(track1[-1])
    pcb.add_track(track2, layer='B.Cu')

    # add board edge
    ul = (20, 20)
    pcb_size = (100, 80)
    edge = [ul,
            (ul[0], ul[1]+pcb_size[1]),
            (ul[0]+pcb_size[0], ul[1]+pcb_size[1]),
            (ul[0]+pcb_size[0], ul[1]),
            ul]
    pcb.add_polyline(edge, layer='Edge.Cuts')

    print('List all pads of all modules')
    for module in pcb.modules:
        print(module.reference)
        for pad in m.pads:
            print('  {0.name}: {0.shape}'.format(pad))
