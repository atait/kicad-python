import os
import pytest
from lytest import contained_pcbnewBoard, difftest_it
from lytest.utest_buds import get_src_dir
from kigadgets.zone import Zone, Keepout, RuleArea
from kigadgets.board import Board


def test_wrap():
    src_file = os.path.join(get_src_dir(), 'zone_mutate.kicad_pcb')
    pcb = Board.load(src_file)
    zz = list(pcb.zones)[0]
    for zone in pcb.zones:
        if zone.name == 'Z1':
            break
    zz = zone.native_obj

    ww = RuleArea.wrap(zz)
    xx = Keepout.wrap(zz)
    yy = Zone.wrap(zz)
    assert type(ww) is type(xx)
    assert type(xx) is type(yy)


def test_keepout_allowance():
    src_file = os.path.join(get_src_dir(), 'zone_mutate.kicad_pcb')
    pcb = Board.load(src_file)
    ko = list(pcb.keepouts)[0]

    ko.allow.tracks = True
    assert ko.allow.tracks and ko.allow['tracks']
    ko.allow['tracks'] = False
    assert not ko.allow.tracks and not ko.allow['tracks']


def test_fillpoly_geohash():
    src_file = os.path.join(get_src_dir(), 'zone_mutate.kicad_pcb')
    pcb = Board.load(src_file)
    pcb.fill_zones()
    original = pcb.copy()
    zz = list(pcb.zones)[0]

    zz.clearance /= 2
    pcb.fill_zones()
    assert pcb.geohash() != original.geohash()
    zz.clearance *= 2
    pcb.fill_zones()
    assert pcb.geohash() == original.geohash()


@contained_pcbnewBoard
def zone_create(pcb):
    zz = Zone([(1, 2), (3, 4), (-5, 4), (1, 2)], layers=['F.Cu', 'B.Cu'], board=pcb)
    pcb.add(zz)
    pcb.fill_zones()

@pytest.mark.skip(reason='__init__ not supported. It needs a way to turn coords into Outline')
def test_zone_create(): difftest_it(zone_create)()


@contained_pcbnewBoard
def zone_mutate(pcb):
    for zz in pcb.zones:
        if zz.name == 'Zoutside':
            outer_zone = zz
        elif zz.name == 'Zinside':
            inner_zone = zz
    ko = list(pcb.keepouts)[0]

    assert outer_zone.net_name == 'GND'
    assert inner_zone.net_name == '/NET1'
    assert ko.layers == ['F.Cu']

    # Make changes
    # ko.layers = ['F.Cu', 'B.Cu']
    # pcb.add(ko.to_polygon(layer='User.1'))
    # for poly in outer_zone.get_fill_polygons():
    #     poly.layer = 'User.2' if poly.layer == 'F.Cu' else 'User.3'
    #     pcb.add(poly)
    # for poly in inner_zone.get_fill_polygons():
    #     poly.layer = 'User.4' if poly.layer == 'F.Cu' else 'User.5'
    #     pcb.add(poly)
    # assert inner_zone.filled_area > 0
    inner_zone.priority = 0

    pcb.fill_zones()

    # assert inner_zone.filled_area == 0

def test_zone_mutate(): difftest_it(zone_mutate)()
