# SPDX-License-Identifier: AGPL-3.0-or-later
import sys
import manifold3d as m3
from make_bottom import load, save

# One-piece adapter: top of a one-piece source (above the groove ceiling) fused to a bottom part without pins.
#   usage: make_onepiece.py v1/onepiece_4.5.stl BOTTOM.stl OUT.stl
# Groove ceiling of the source sits at z=-2 (v5..v7); bottom part is in print coords (flange 0..2, core 2..2.7).
SRC, BOTTOM, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
Z_CUT, Z_CORE = -2.0, 2.7
box = lambda z0, z1: m3.Manifold.cube((200, 200, z1 - z0), center=True).translate((0, 0, (z0 + z1) / 2))

top = load(SRC) ^ box(Z_CUT, 20)
# keep 0.01 above the core so it overlaps the top part (pin stubs end up inside solid material)
bottom = (load(BOTTOM) ^ box(-1, Z_CORE + 0.01)).translate((0, 0, Z_CUT - Z_CORE))
part = top + bottom
save(part.translate((0, 0, -part.bounding_box()[2])), OUT, 'one-piece adapter (flange face on z=0)')
