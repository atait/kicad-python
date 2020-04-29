# -*- coding: utf-8 -*-
#
# This script will re-annotate board companents according to their x,y
# positions and back-annotate those changes to schematic files.
#
# Make sure you have backups of all your files!
#
# You should run the script from inside pcbnew script console. After
# running script, re-open your schematic files, update the netlist
# file and import net list changes to pcbnew. This should update some
# net names, but shouldn't change any component footprints.
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

from kicad.pcbnew.board import Board
from kicad.pcbnew.layer import Layer
import re
import glob
import os
import codecs

b = Board.from_editor()

mods = list(b.modules)

def sortkeys(mod):
    if mod.layer == Layer.Front:
        return (mod.layer, mod.y, mod.x)
    else: # Layer.Back
        # Components in the back are sorted from right to
        # left according to their canvas position. When you flip the
        # board at your hand, they will be sorted 'left to right'.
        return (mod.layer, mod.y, -mod.x)

mods = sorted(mods, key=sortkeys)

ref_counter = {} # dictionary of reference names
changes = [] # a list of tuples

for mod in mods:
    prev_ref = mod.reference
    m = re.match('^((?:[a-zA-Z_\d]+[a-zA-Z_])|(?:[a-zA-Z_]+))(\d+)$', prev_ref)

    if m:
        name, number = m.groups()  # for ex: R16 -> name:'R' , number: '16'
    else:
        print("Skipping: %s." % prev_ref)
        continue

    if name in ref_counter:
        next_ref = name + str(ref_counter[name]+1)
        ref_counter[name] += 1
    else:
        next_ref = name + str(1)
        ref_counter[name] = 1

    if next_ref == prev_ref:
        continue

    print('Re-naming %s -> %s' % (prev_ref, next_ref))

    mod.reference = next_ref
    changes.append((prev_ref, next_ref))

if changes:
    b.save()
    print("PCB annotated.")

    # PCB annotation completed, now back-annotate schematics

    # prepare replacer
    changes = dict(changes)

    def replacer(match):
        ref = match.group(2)
        if ref in changes:
            return match.group(1) + changes[ref]
        else:
            # not changed
            return match.group(0)

    # regex for changing component references
    regx = re.compile(r'^(L \S+ |F 0 "|AR Path="[/\w]+" Ref=")(\w+)', re.MULTILINE)

    # get a list of schematic files by globbing
    directory = os.path.dirname(b.filename)
    sch_files = glob.glob(directory + '/*.sch')

    for sch_file in sch_files:
        print("Updating %s..." % sch_file)
        # read file
        s = codecs.open(sch_file, mode='r+', encoding='utf-8').read()

        # make changes
        s = regx.sub(replacer, s)

        # update file contents
        codecs.open(sch_file, mode='w', encoding='utf-8').write(s)
else:
    print("No changes were made! This is normal if your components were already named in correct order.")
