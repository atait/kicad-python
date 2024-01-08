from kicad import pcbnew_bare as pcbnew

import kicad
from kicad.pcbnew import drawing
from kicad.pcbnew import module
from kicad.pcbnew.track import Track
from kicad.pcbnew.via import Via
from kicad.pcbnew.drawing import Drawing
from kicad.pcbnew.zone import Zone
from kicad import units, SWIGtype, instanceof


class _ModuleList(object):
    """Internal class to represent `Board.modules`"""
    def __init__(self, board):
        self._board = board

    def __getitem__(self, key):
        found = self._board._obj.FindFootprintByReference(key)
        if found:
            return module.Module.wrap(found)
        else:
            raise KeyError("No module with reference: %s" % key)

    def __iter__(self):
        # Note: this behavior is inconsistent with python manuals
        # suggestion. Manual suggests that a mapping should iterate
        # over keys ('reference' in our case). See:
        # https://docs.python.org/2.7/reference/datamodel.html?emulating-container-types#object.__iter__
        # But in my opinion `_ModuleList` is a list then mapping.
        for m in self._board._obj.GetFootprints():
            yield module.Module.wrap(m)

    def __len__(self):
        return len(self._board._obj.GetFootprints())

class Board(object):
    def __init__(self, wrap=None):
        """Board object"""
        if wrap:
            self._obj = wrap
        else:
            self._obj = pcbnew.BOARD()

        self._modulelist = _ModuleList(self)
        self._removed_elements = []

    @property
    def native_obj(self):
        return self._obj

    @staticmethod
    def wrap(instance):
        """Wraps a C++/old api BOARD object, and returns a Board."""
        return Board(wrap=instance)

    def add(self, obj):
        """Adds an object to the Board.

        Tracks, Drawings, Modules, etc...
        """
        self._obj.Add(obj.native_obj)
        return obj

    @property
    def modules(self):
        """Provides an iterator over the board Module objects."""
        return self._modulelist

    def moduleByRef(self, ref):
        """Returns the module that has the reference `ref`. Returns `None` if
        there is no such module."""
        found = self._obj.FindFootprintByReference(ref)
        if found:
            return module.Module.wrap(found)

    @property
    def footprints(self):
        """Alias footprint to module"""
        return self.modules

    def footprintByRef(self, ref):
        """Alias footprint to module"""
        return self.moduleByRef(ref)

    @property
    def vias(self):
        """An iterator over via objects"""
        for t in self._obj.GetTracks():
            if type(t) == SWIGtype.Via:
                yield Via.wrap(t)
            else:
                continue

    @property
    def tracks(self):
        """An iterator over track objects"""
        for t in self._obj.GetTracks():
            if type(t) == SWIGtype.Track:
                yield Track.wrap(t)
            else:
                continue

    @property
    def zones(self):
        """ An iterator over zone objects
            Implementation note: The iterator breaks if zones are removed during the iteration,
            so it is put in a list first, then yielded from that list.
            This issue was not seen with the other iterators
        """
        builder = list()
        for t in self._obj.Zones():
            if type(t) == SWIGtype.Zone:
                builder.append(Zone.wrap(t))
            else:
                continue
        for tt in builder:
            yield tt

    @property
    def drawings(self):
        all_drawings = []
        for drawing in self._obj.GetDrawings():
            if instanceof(drawing, (SWIGtype.Shape, SWIGtype.Text)):
                yield Drawing.wrap(drawing)

    @property
    def items(self):
        ''' Everything on the board '''
        for item in self.modules:
            yield item
        for item in self.vias:
            yield item
        for item in self.tracks:
            yield item
        for item in self.zones:
            yield item
        for item in self.drawings:
            yield item

    @staticmethod
    def from_editor():
        """Provides the board object from the editor."""
        return Board.wrap(pcbnew.GetBoard())

    @staticmethod
    def load(filename):
        """Loads a board file."""
        return Board.wrap(pcbnew.LoadBoard(filename))

    def save(self, filename=None):
        """Save the board to a file.

        filename should have .kicad_pcb extention.
        """
        if filename is None:
            filename = self._obj.GetFileName()
        self._obj.Save(filename)

    def copy(self):
        return Board(wrap=self._obj.Clone())

    # TODO: add setter for Board.filename
    @property
    def filename(self):
        """Name of the board file."""
        return self._obj.GetFileName()

    def add_module(self, ref, pos=(0, 0)):
        """Create new module on the board"""
        return module.Module(ref, pos, board=self)

    @property
    def default_width(self, width=None):
        b = self._obj
        return (
            float(b.GetDesignSettings().GetCurrentTrackWidth()) /
            units.DEFAULT_UNIT_IUS)

    def add_track_segment(self, start, end, layer='F.Cu', width=None):
        """Create a track segment."""

        track = Track(width or self.default_width,
                      start, end, layer, board=self)
        self._obj.Add(track.native_obj)
        return track

    def get_layer_id(self, name):
        lid = self._obj.GetLayerID(name)
        if lid == -1:
            # Try to recover from silkscreen rename
            if name == 'F.SilkS':
                lid = self._obj.GetLayerID('F.Silkscreen')
            elif name == 'F.Silkscreen':
                lid = self._obj.GetLayerID('F.SilkS')
            elif name == 'B.SilkS':
                lid = self._obj.GetLayerID('B.Silkscreen')
            elif name == 'B.Silkscreen':
                lid = self._obj.GetLayerID('B.Silkscreen')
        if lid == -1:
            raise ValueError('Layer {} not found in this board'.format(name))
        return lid

    def get_layer_name(self, layer_id):
        return self._obj.GetLayerName(layer_id)

    def add_track(self, coords, layer='F.Cu', width=None):
        """Create a track polyline.

        Create track segments from each coordinate to the next.
        """
        for n in range(len(coords) - 1):
            self.add_track_segment(coords[n], coords[n + 1],
                                   layer=layer, width=width)

    @property
    def default_via_size(self):
        return (float(self._obj.GetDesignSettings().GetCurrentViaSize()) /
                units.DEFAULT_UNIT_IUS)

    @property
    def default_via_drill(self):
        via_drill = self._obj.GetDesignSettings().GetCurrentViaDrill()
        if via_drill > 0:
            return (float(via_drill) / units.DEFAULT_UNIT_IUS)
        else:
            return 0.2

    def add_via(self, coord, layer_pair=('B.Cu', 'F.Cu'), size=None,
                drill=None):
        """Create a via on the board.

        :param coord: Position of the via.
        :param layer_pair: Tuple of the connected layers (for example
                           ('B.Cu', 'F.Cu')).
        :param size: size of via in mm, or None for current selection.
        :param drill: size of drill in mm, or None for current selection.
        :returns: the created Via
        """
        return self.add(
            Via(coord, layer_pair, size or self.default_via_size,
                drill or self.default_via_drill, board=self))

    def add_line(self, start, end, layer='F.SilkS', width=0.15):
        """Create a graphic line on the board"""
        return self.add(
            drawing.Segment(start, end, layer, width, board=self))

    def add_polyline(self, coords, layer='F.SilkS', width=0.15):
        """Create a graphic polyline on the board"""
        for n in range(len(coords) - 1):
            self.add_line(coords[n], coords[n + 1], layer=layer, width=width)

    def add_circle(self, center, radius, layer='F.SilkS', width=0.15):
        """Create a graphic circle on the board"""
        return self.add(
            drawing.Circle(center, radius, layer, width, board=self))

    def add_arc(self, center, radius, start_angle, stop_angle,
                layer='F.SilkS', width=0.15):
        """Create a graphic arc on the board"""
        return self.add(
            drawing.Arc(center, radius, start_angle, stop_angle,
                        layer, width, board=self))

    def add_text(self, position, text, layer='F.SilkS', size=1.0, thickness=0.15):
        return self.add(
            drawing.TextPCB(position, text, layer, size, thickness, board=self))

    def remove(self, element, permanent=False):
        ''' Makes it so Ctrl-Z works.
            Keeps a reference to the element in the python pcb object,
            so it persists for the life of that object
        '''
        if not permanent:
            self._removed_elements.append(element)
        self._obj.Remove(element._obj)

    def restore_removed(self):
        if hasattr(self, '_removed_elements'):
            for element in self._removed_elements:
                self._obj.Add(element._obj)
        self._removed_elements = []

    def deselect_all(self):
        self._obj.ClearSelected()

    @property
    def selected_items(self):
        ''' This useful for duck typing in the interactive terminal
            Suppose you want to set some drill radii. Iterating everything would cause attribute errors,
            so it is easier to just select the vias you want, then use this method for convenience.
            To get one item that you selected, use
                xx = next(pcb.selected_items)
        '''
        for item in self.items:
            try:
                if item.is_selected:
                    yield item
            except AttributeError:
                continue

    def fill_zones(self, zone_to_fill=None):
        ''' zone_to_fill=None fills all zones in this board '''
        filler = pcbnew.ZONE_FILLER(self._obj)
        filler.Fill(self._obj.Zones())
