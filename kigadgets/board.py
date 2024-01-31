import logging
import tempfile
from typing import Iterable, Optional, Union

from Pyro5.api import expose

from kigadgets import SWIGtype, instanceof
from kigadgets import pcbnew_bare as pcbnew
from kigadgets import units
from kigadgets.drawing import Arc, Circle, Segment, TextPCB, wrap_drawing
from kigadgets.module import Footprint
from kigadgets.track import Track
from kigadgets.util import register_return, register_yielded
from kigadgets.via import Via
from kigadgets.zone import Zone

log = logging.getLogger(__name__)


COPPER_TYPES = Union[Footprint, Track, Via, Zone]
DRAWING_TYPES = Union[Arc, Circle, Segment, TextPCB]

@expose
class FootprintList(object):
    """Internal class to represent `Board.footprints`"""
    def __init__(self, board):
        self._board = board

    def __getitem__(self, key):
        found = self._board._obj.FindFootprintByReference(key)
        if found:
            return Footprint.wrap(found)
        else:
            raise KeyError("No footprint with reference: %s" % key)

    def __iter__(self):
        # Note: this behavior is inconsistent with python manuals
        # suggestion. Manual suggests that a mapping should iterate
        # over keys ('reference' in our case). See:
        # https://docs.python.org/2.7/reference/datamodel.html?emulating-container-types#object.__iter__
        # But in my opinion `_FootprintList` is a list then mapping.
        for m in self._board._obj.GetFootprints():
            yield Footprint.wrap(m)

    def __len__(self):
        return len(self._board._obj.GetFootprints())


@expose
class Board(object):
    def __init__(self, wrap=None):
        """Board object"""
        log.debug("Creating board from: %s", wrap)
        if wrap:
            self._obj = wrap
        else:
            self._obj = pcbnew.BOARD()
        log.debug("Board object created: %s", self._obj)

        self._fplist = FootprintList(self)
        self._removed_elements = []

    @property
    def native_obj(self) -> "pcbnew.BOARD":
        return self._obj

    @classmethod
    @register_return
    def wrap(cls, instance: "pcbnew.BOARD") -> "Board":
        """Wraps a C++/old api `BOARD` object, and returns a `Board`."""
        return Board(wrap=instance)

    @register_return
    def add(self, obj: COPPER_TYPES) -> COPPER_TYPES:
        """Adds an object to the Board.

        Tracks, Drawings, Modules, etc...
        """
        self._obj.Add(obj.native_obj)
        return obj

    @property
    @register_return
    def footprints(self) -> Iterable[Footprint]:
        """Provides an iterator over the board Footprint objects."""
        return self._fplist

    @register_return
    def footprint_by_ref(self, ref) -> Optional[Footprint]:
        """Returns the footprint that has the reference `ref`. Returns `None` if
        there is no such footprint."""
        found = self._obj.FindFootprintByReference(ref)
        if found:
            return Footprint.wrap(found)

    @property
    @register_return
    def modules(self) -> Iterable[Footprint]:
        """Alias footprint to module"""
        return self.footprints

    @register_return
    def module_by_ref(self, ref) -> Optional[Footprint]:
        """Alias footprint to module"""
        return self.footprintByRef(ref)

    @property
    @register_yielded
    def vias(self) -> Iterable[Via]:
        """An iterator over via objects"""
        for t in self._obj.GetTracks():
            if type(t) == SWIGtype.Via:
                yield Via.wrap(t)
            else:
                continue

    @property
    @register_yielded
    def tracks(self) -> Iterable[Track]:
        """An iterator over track objects"""
        for t in self._obj.GetTracks():
            if type(t) == SWIGtype.Track:
                yield Track.wrap(t)
            else:
                continue

    @property
    @register_yielded
    def zones(self) -> Iterable[Zone]:
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
    @register_yielded
    def drawings(self) -> Iterable[DRAWING_TYPES]:
        all_drawings = []
        for drawing in self._obj.GetDrawings():
            yield wrap_drawing(drawing)

    @property
    @register_yielded
    def items(self) -> Iterable[Union[COPPER_TYPES, DRAWING_TYPES]]:
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

    @classmethod
    @register_return
    def from_editor(cls):
        """Provides the board object from the editor."""
        return Board.wrap(pcbnew.GetBoard())

    @classmethod
    @register_return
    def load(cls, filename):
        """Loads a board file."""
        return Board.wrap(pcbnew.LoadBoard(filename))

    def save(self, filename=None):
        """Save the board to a file.

        filename should have .kicad_pcb extention.
        """
        if filename is None:
            filename = self._obj.GetFileName()
        self._obj.Save(filename)

    @register_return
    def copy(self):
        native = self._obj.Clone()
        if native is None:  # Clone not implemented in v7
            # Fallback to save/load
            with tempfile.NamedTemporaryFile(suffix='.kicad_pcb') as tfile:
                self.save(tfile.name)
                return Board.load(tfile.name)

    # TODO: add setter for Board.filename. For now, use brd.save(filename)
    @property
    def filename(self) -> str:
        """Name of the board file."""
        log.debug("repr(Board:self._obj): %s", self._obj)
        return self._obj.GetFileName()

    def geohash(self) -> int:
        ''' Geometric hash '''
        item_hashes = []
        for item in self.items:
            try:
                item_hashes.append(item.geohash())
            except AttributeError:
                continue
        item_hashes.sort()
        return hash(tuple(item_hashes))

    @register_return
    def add_footprint(self, ref, pos=(0, 0)) -> Footprint:
        """Create new module on the board"""
        return Footprint(ref, pos, board=self)

    @register_return
    def add_module(self, ref, pos=(0, 0)) -> Footprint:
        """Same as add_footprint"""
        return Footprint(ref, pos, board=self)

    @property
    def default_width(self, width=None) -> float:
        b = self._obj
        return (
            float(b.GetDesignSettings().GetCurrentTrackWidth()) /
            units.DEFAULT_UNIT_IUS)

    @register_return
    def add_track_segment(self, start, end, layer='F.Cu', width=None) -> Track:
        """Create a track segment."""
        track = Track(start, end, layer,
                      width or self.default_width, board=self)
        self._obj.Add(track.native_obj)
        return track

    def get_layer_id(self, name) -> int:
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

    def get_layer_name(self, layer_id) -> str:
        return self._obj.GetLayerName(layer_id)

    @register_return
    def add_track(self, coords, layer='F.Cu', width=None) -> Track:
        """Create a track polyline.

        Create track segments from each coordinate to the next.
        """
        for n in range(len(coords) - 1):
            self.add_track_segment(coords[n], coords[n + 1],
                                   layer=layer, width=width)

    @property
    def default_via_size(self) -> float:
        return (float(self._obj.GetDesignSettings().GetCurrentViaSize()) /
                units.DEFAULT_UNIT_IUS)

    @property
    def default_via_drill(self) -> float:
        via_drill = self._obj.GetDesignSettings().GetCurrentViaDrill()
        if via_drill > 0:
            return (float(via_drill) / units.DEFAULT_UNIT_IUS)
        else:
            return 0.2

    @register_return
    def add_via(self, coord, size=None, drill=None, layer_pair=None) -> Via:
        """Create a via on the board.

        :param coord: Position of the via.
        :param layer_pair: Tuple of the connected layers (for example
                           ('B.Cu', 'F.Cu')).
        :param size: size of via in mm, or None for current selection.
        :param drill: size of drill in mm, or None for current selection.
        :returns: the created Via
        """
        return self.add(
            Via(coord, size or self.default_via_size,
                drill or self.default_via_drill, layer_pair, board=self))

    @register_return
    def add_line(self, start, end, layer='F.SilkS', width=0.15) -> Segment:
        """Create a graphic line on the board"""
        return self.add(
            Segment(start, end, layer, width, board=self))

    def add_polyline(self, coords, layer='F.SilkS', width=0.15):
        """Create a graphic polyline on the board"""
        for n in range(len(coords) - 1):
            self.add_line(coords[n], coords[n + 1], layer=layer, width=width)

    @register_return
    def add_circle(self, center, radius, layer='F.SilkS', width=0.15) -> Circle:
        """Create a graphic circle on the board"""
        return self.add(
            Circle(center, radius, layer, width, board=self))

    @register_return
    def add_arc(self, center, radius, start_angle, stop_angle,
                layer='F.SilkS', width=0.15) -> Arc:
        """Create a graphic arc on the board"""
        return self.add(
            Arc(center, radius, start_angle, stop_angle,
                        layer, width, board=self))

    @register_return
    def add_text(self, position, text, layer='F.SilkS', size=1.0, thickness=0.15) -> TextPCB:
        return self.add(
            TextPCB(position, text, layer, size, thickness, board=self))

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
    @register_yielded
    def selected_items(self) -> Iterable[Union[COPPER_TYPES, DRAWING_TYPES]]:
        ''' This useful for duck typing in the interactive terminal
            Suppose you want to set some drill radii. Iterating everything would cause attribute errors,
            so it is easier to just select the vias you want, then use this method for convenience.

            To get one item that you selected, use

            >>> xx = next(pcb.selected_items)
        '''
        for item in self.items:
            try:
                if item.is_selected:
                    yield item
            except AttributeError:
                continue

    def fill_zones(self):
        ''' fills all zones in this board '''
        filler = pcbnew.ZONE_FILLER(self._obj)
        filler.Fill(self._obj.Zones())
