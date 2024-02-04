''' Mousebites using the Eco1 layer.
    An example of an action plugin simplified by kigadgets (<200 lines)
    Note: this gives plated vias; NPTH are preferred
    - You can place NPTH Footprints instead of Vias
'''
import os
import sys
from kigadgets.board import Board
from kigadgets.drawing import Segment, Arc, Polygon, Rectangle
from kigadgets.via import Via
from kigadgets import Point, notify
from pcbnew import Refresh
from mousebite_kigadget import objview


def fracture_polygons(board):
    cutters = [dwg for dwg in board.drawings if isinstance(dwg, Segment) and dwg.layer == opts.slay]
    cuttees = [dwg for dwg in board.drawings if isinstance(dwg, Polygon) and dwg.layer == 'Edge.Cuts']
    for poly in cuttees:
        for cut in cutters:
            is_crossing = poly.contains(cut.start) ^ poly.contains(cut.end)
            if is_crossing:
                poly.to_segments(replace=True)
                break


def get_segments(board):
    ''' Called multiple times because we are changing the segments
        every time we manifest a new mousebite
    '''
    eco_dwgs = [dwg for dwg in board.drawings if isinstance(dwg, Segment) and dwg.layer == opts.slay]
    edge_dwgs = [dwg for dwg in board.drawings if isinstance(dwg, Segment) and dwg.layer == 'Edge.Cuts']
    is_vert = lambda seg: seg.start.x == seg.end.x
    is_horz = lambda seg: seg.start.y == seg.end.y
    eco_vert = [eco for eco in eco_dwgs if is_vert(eco)]
    eco_horz = [eco for eco in eco_dwgs if is_horz(eco)]
    edge_vert = [edge for edge in edge_dwgs if is_vert(edge)]
    edge_horz = [edge for edge in edge_dwgs if is_horz(edge)]
    return eco_vert, eco_horz, edge_vert, edge_horz


def intersect_perp(vert, horz, either=True):
    x = vert.start.x
    y = horz.start.y
    if either and intersect_perp(horz, vert, either=False):
        return True
    if (horz.start.x < x) ^ (horz.end.x > x):
        return False
    if (vert.start.y < y) ^ (vert.end.y > y):
        return False
    return True


def get_bite_pair(eco_segments, edge_segments):
    for eco in eco_segments:
        matches = []
        for ed in edge_segments:
            if intersect_perp(eco, ed):
                matches.append(ed)
        if len(matches) == 2:
            return (eco, matches[0], matches[1])
        elif len(matches) == 0:
            pass
        else:
            eco.select()
            _ = [match.select() for match in matches]
            if len(matches) == 1:
                matches[0].select()
            raise ValueError(
                f'Got {len(matches)} of intersecting Edge.Cuts segments.\n'
                'It must be exactly 2. See the selected {} segment.'.format(opts.slay)
            )
    return None


def sort_box(og_box, ix=0):
    ''' Sorts a 2x2 list of Points
        The first index is north/south with ascending y
        The second index is west/east with ascending x
    '''
    og_box[0].sort(key=lambda pt: pt[ix])
    og_box[1].sort(key=lambda pt: pt[ix])
    og_box.sort(key=lambda ln: ln[0][1-ix])


def do_drawing(board, eco, h1, h2, horizontal=False):
    # XY indexing
    ix = 1 if horizontal else 0
    iy = 1 - ix
    if horizontal:
        latlon_point = lambda lat, lon: Point(lon, lat)
    else:
        latlon_point = lambda lat, lon: Point(lat, lon)

    for ln in [eco, h1, h2]:
        board.remove(ln, permanent=False)

    # Key anchor points oriented by latitude/longitude instead of X/Y
    box_corner = [[h1.start, h1.end], [h2.start, h2.end]]
    sort_box(box_corner, ix)
    longitudes = [h.start[iy] for h in (h1, h2)]  # y if vertical, x if not
    latitudes = [eco.start[ix] + sgn * opts.tab_width/2 for sgn in [-1, 1]]
    box_bridge = [[latlon_point(lat, lon) for lat in latitudes] for lon in longitudes]
    sort_box(box_bridge, ix)

    # Place the fillets, bridge, and snipped original edge
    dwg_kws = dict(width=h1.width, layer='Edge.Cuts', board=board)
    for iwe in range(2):
        for ins in range(2):
            sgn_we = (-1) ** iwe
            sgn_ns = (-1) ** ins
            # fillet
            dr = latlon_point(-sgn_we * opts.fillet, sgn_ns * opts.fillet)
            center = box_bridge[ins][iwe] + dr
            angle = 90 * (ins - iwe * sgn_ns)
            if horizontal and ins == iwe:
                angle += 180
            arc = Arc(center, opts.fillet, angle, angle + 90, **dwg_kws)
            board.add(arc)
            # replacement clipped edge
            outward_end = arc.start if (ins == iwe ^ horizontal) else arc.end
            inward_end = arc.end if (ins == iwe ^ horizontal) else arc.start
            board.add(Segment(outward_end, box_corner[ins][iwe], **dwg_kws))
            # bridge
            if ins == 0:
                prev_end = inward_end
            else:
                board.add(Segment(prev_end, inward_end, **dwg_kws))
    # Vias
    lat0 = eco.start[ix]
    nvias = (opts.tab_width + 2 * opts.fillet) / opts.pitch
    niter = nvias / 2
    niter = int(-1 * niter // 1 * -1)  # ceil function
    longitudes = [box_corner[0][0][iy] - opts.inset, box_corner[1][0][iy] + opts.inset]
    for lon in longitudes:
        for ivia in range(-niter+1, niter):
            point = latlon_point(lat0 + ivia * opts.pitch, lon)
            board.add(Via(
                point,
                layer_pair=['B.Cu', 'F.Cu'],
                size=.1, drill=opts.drill,
                board=board)
            )


opts = objview(
    slay = 'User.Eco1',
    tab_width = 3,  # mm
    pitch = 1.3,
    fillet = 1,
    drill = .8,
    inset = 0.25,
)


def main(pcb, dialog_opts=None):
    if dialog_opts is not None:
        opts.update(dialog_opts)

    fracture_polygons(pcb)

    for _ in range(1000):
        eco_vert, _, _, edge_horz = get_segments(pcb)
        lines = get_bite_pair(eco_vert, edge_horz)
        if lines is None: break
        do_drawing(pcb, *lines, horizontal=False)

    for _ in range(1000):
        _, eco_horz, edge_vert, _ = get_segments(pcb)
        lines = get_bite_pair(eco_horz, edge_vert)
        if lines is None: break
        do_drawing(pcb, *lines, horizontal=True)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Mousebite script based on kigadgets. You are looking at the CLI. An action plugin is also available'
    )
    parser.add_argument('-s', '--slay', type=str, default='User.Eco1', help='Layer with segments that cut across board edges')
    parser.add_argument('input', type=str, help='Input pcb (.kicad_pcb)')
    args = parser.parse_args()
    # parser.add_argument('kicad_config_path', type=str)
    # parser.add_argument('-n', '--dry-run', action='store_true')

    pcb = Board.load(args.input)
    newname = os.path.splitext(pcb.filename)[0] + '-proc.kicad_pcb'
    opts.slay = args.slay
    main(pcb)
    pcb.save(newname)
