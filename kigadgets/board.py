from kigadgets import pcbnew_bare as pcbnew
from kigadgets import units, SWIGtype, instanceof, SWIG_version
import tempfile
import os

from kigadgets.drawing import wrap_drawing, Segment, Circle, Arc, TextPCB
from kigadgets.module import Footprint
from kigadgets.track import Track
from kigadgets.via import Via
from kigadgets.zone import Zone, Keepout, RuleArea


class Board(object):
    def __init__(self, wrap=None):
        """Board object"""
        if wrap:
            self._obj = wrap
        else:
            self._obj = pcbnew.BOARD()
        self._removed_elements = []

    @property
    def native_obj(self):
        return self._obj

    @staticmethod
    def wrap(instance):
        """Wraps a C++/old api `BOARD` object, and returns a `Board`."""
        return Board(wrap=instance)

    def add(self, obj):
        """Adds an object to the Board.

        Tracks, Drawings, Modules, etc...
        """
        self._obj.Add(obj.native_obj)
        return obj

    @property
    def footprints(self):
        """Provides a list of the board Footprint objects."""
        return [Footprint.wrap(fp) for fp in self._obj.GetFootprints()]

    def footprint_by_ref(self, ref):
        """Returns the footprint that has the reference `ref`. Returns `None` if
        there is no such footprint."""
        found = self._obj.FindFootprintByReference(ref)
        if found:
            return Footprint.wrap(found)

    @property
    def modules(self):
        """Alias footprint to module"""
        return self.footprints

    def module_by_ref(self, ref):
        """Alias footprint to module"""
        return self.footprint_by_ref(ref)

    @property
    def vias(self):
        """A list of via objects"""
        return [Via.wrap(t) for t in self._obj.GetTracks() if instanceof(t, SWIGtype.Via)]

    @property
    def tracks(self):
        """A list of track objects"""
        return [Track.wrap(t) for t in self._obj.GetTracks() if instanceof(t, SWIGtype.Track)]

    @property
    def rule_areas(self):
        """A list of both zone and keepout objects"""
        return [RuleArea.wrap(t) for t in self._obj.Zones() if instanceof(t, SWIGtype.Zone)]

    @property
    def zones(self):
        return [area for area in self.rule_areas if not area.is_keepout]

    @property
    def keepouts(self):
        return [area for area in self.rule_areas if area.is_keepout]

    @property
    def drawings(self):
        """List of drawings, including all shapes and text"""
        return [wrap_drawing(dwg) for dwg in self._obj.GetDrawings()]

    @property
    def items(self):
        """Everything on the board"""
        return self.modules + self.vias + self.tracks + self.drawings + self.rule_areas

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
        The filename should have .kicad_pcb extention, but it is not enforced.
        If filename=None, the board's GetFileName value is used.
        """
        if filename is None:
            filename = self._obj.GetFileName()
        self._obj.Save(filename)

    def copy(self):
        if SWIG_version <= 6:
            native = self._obj.Clone()
            return Board.wrap(native)
        else:
            # Fallback to save/load
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_pcbfile = os.path.join(temp_dir, "kigadgets_copying.kicad_pcb")
                self.save(temp_pcbfile)
                return Board.load(temp_pcbfile)

    # TODO: add setter for Board.filename. For now, use brd.save(filename)
    @property
    def filename(self):
        """Name of the board file."""
        return self._obj.GetFileName()

    def geohash(self):
        """Geometric hash"""
        item_hashes = []
        for item in self.items:
            try:
                item_hashes.append(item.geohash())
            except AttributeError:
                continue
        item_hashes.sort()
        res = hash(tuple(item_hashes))
        if res == 0:
            print("You won a bitcoin!")
        return res

    def add_footprint(self, ref, pos=(0, 0)):
        """Create new module on the board"""
        return Footprint(ref, pos, board=self)

    def add_module(self, ref, pos=(0, 0)):
        """Same as add_footprint"""
        return self.add_footprint(ref, pos, board=self)

    @property
    def default_width(self, width=None):
        pcb_settings = self._obj.GetDesignSettings()
        width_ius = float(pcb_settings.GetCurrentTrackWidth())
        width_mm = width_ius / units.DEFAULT_UNIT_IUS
        return width_mm

    def add_track_segment(self, start, end, layer="F.Cu", width=None):
        """Create a track segment."""
        track = Track(start, end, layer, width or self.default_width, board=self)
        self._obj.Add(track.native_obj)
        return track

    def get_layer_id(self, name):
        lid = self._obj.GetLayerID(name)
        if lid == -1:
            # Try to recover from silkscreen rename
            if name == "F.SilkS":
                lid = self._obj.GetLayerID("F.Silkscreen")
            elif name == "F.Silkscreen":
                lid = self._obj.GetLayerID("F.SilkS")
            elif name == "B.SilkS":
                lid = self._obj.GetLayerID("B.Silkscreen")
            elif name == "B.Silkscreen":
                lid = self._obj.GetLayerID("B.Silkscreen")
        if lid == -1:
            raise ValueError(f"Layer {name} not found in this board")
        return lid

    def get_layer_name(self, layer_id):
        return self._obj.GetLayerName(layer_id)

    def add_track(self, coords, layer="F.Cu", width=None):
        """Create a track polyline.

        Create track segments from each coordinate to the next.
        """
        for n in range(len(coords) - 1):
            self.add_track_segment(coords[n], coords[n + 1], layer=layer, width=width)

    @property
    def default_via_size(self):
        pcb_settings = self._obj.GetDesignSettings()
        size_ius = float(pcb_settings.GetCurrentViaSize())
        size_mm = size_ius / units.DEFAULT_UNIT_IUS
        return size_mm

    @property
    def default_via_drill(self):
        via_drill = self._obj.GetDesignSettings().GetCurrentViaDrill()
        if via_drill > 0:
            return float(via_drill) / units.DEFAULT_UNIT_IUS
        else:
            return 0.2

    def add_via(self, coord, size=None, drill=None, layer_pair=None):
        """Create a via on the board.

        :param coord: Position of the via.
        :param layer_pair: Tuple of the connected layers (for example
                           ('B.Cu', 'F.Cu')).
        :param size: size of via in mm, or None for current selection.
        :param drill: size of drill in mm, or None for current selection.
        :returns: the created Via
        """
        return self.add(
            Via(
                coord,
                size or self.default_via_size,
                drill or self.default_via_drill,
                layer_pair,
                board=self,
            )
        )

    def add_line(self, start, end, layer="F.SilkS", width=0.15):
        """Create a graphic line on the board"""
        return self.add(Segment(start, end, layer, width, board=self))

    def add_polyline(self, coords, layer="F.SilkS", width=0.15):
        """Create a graphic polyline on the board"""
        for n in range(len(coords) - 1):
            self.add_line(coords[n], coords[n + 1], layer=layer, width=width)

    def add_circle(self, center, radius, layer="F.SilkS", width=0.15):
        """Create a graphic circle on the board"""
        return self.add(Circle(center, radius, layer, width, board=self))

    def add_arc(self, center, radius, start_angle, stop_angle, layer="F.SilkS", width=0.15):
        """Create a graphic arc on the board"""
        return self.add(Arc(center, radius, start_angle, stop_angle, layer, width, board=self))

    def add_text(self, position, text, layer="F.SilkS", size=1.0, thickness=0.15):
        return self.add(TextPCB(position, text, layer, size, thickness, board=self))

    def remove(self, element, permanent=False):
        """Makes it so Ctrl-Z works.
        Keeps a reference to the element in the python pcb object,
        so it persists for the life of that object
        """
        if not permanent:
            self._removed_elements.append(element)
        self._obj.Remove(element._obj)

    def restore_removed(self):
        for element in self._removed_elements:
            self._obj.Add(element._obj)
        self._removed_elements = []

    def deselect_all(self):
        self._obj.ClearSelected()

    @property
    def selected_items(self):
        """This useful for duck typing in the interactive terminal
        Suppose you want to set some drill radii. Iterating everything would cause attribute errors,
        so it is easier to just select the vias you want, then use this method for convenience.

        To get one item that you selected, use

        >>> xx = pcb.selected_items[0]
        """
        selected = []
        for item in self.items:
            try:
                if item.is_selected:
                    selected.append(item)
            except AttributeError:
                continue
        return selected

    def fill_zones(self):
        """fills all zones in this board"""
        filler = pcbnew.ZONE_FILLER(self._obj)
        filler.Fill(self._obj.Zones())
