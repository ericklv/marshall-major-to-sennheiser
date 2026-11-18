# SPDX-License-Identifier: AGPL-3.0-or-later
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from make_bottom import load

# Vertical section through the pins (45°) of a two-part adapter: assembled and exploded, from the real STLs.
#   usage: sketch_section.py TOP.stl BOTTOM.stl OUT.png {en|es} TITLE
TOP, BOTTOM, OUT, LANG, TITLE = sys.argv[1:6]
Z_CORE, GAP = 2.7, 3.0                       # bottom core top (print coords), exploded gap
ANG = 45.0

TXT = {
    'en': dict(asm='Assembled', exp='Exploded (print orientation of each part)', top='top part A (Major III side)',
               bot='bottom part B (earpad flange)', groove='groove', pin='pin Ø3.0 into hole Ø3.3',
               xlabel='distance from centre along the 45° pin axis (mm)', note='Section through the pins. Both parts print without supports.'),
    'es': dict(asm='Ensamblado', exp='Despiece (cada pieza en su orientación de impresión)', top='pieza superior A (lado Major III)',
               bot='pieza inferior B (brida de la almohadilla)', groove='muesca', pin='pin Ø3,0 en agujero Ø3,3',
               xlabel='distancia al centro sobre el eje de los pines a 45° (mm)', note='Corte por los pines. Las dos piezas se imprimen sin soportes.'),
}[LANG]
C_A, C_B = '#4a7fc1', '#e8913a'

def vsection(man):
    # plane through the Z axis at ANG -> XY plane (x = radial distance, y = height)
    polys = man.rotate((0, 0, -ANG)).rotate((-90, 0, 0)).slice(0.0).to_polygons()
    return [np.asarray(p) for p in polys if len(p) > 2]

def draw(ax, polys, col, dz=0.0):
    verts, codes = [], []
    for p in polys:
        q = p + [0, dz]
        verts += list(q) + [q[0]]; codes += [Path.MOVETO] + [Path.LINETO] * (len(q) - 1) + [Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), fc=col, ec='#222', lw=0.8, alpha=0.9))

A = load(TOP).translate((0, 0, Z_CORE))      # A bed face sits on B's core top
B = load(BOTTOM)
sA, sB = vsection(A), vsection(B)
xmax = max(np.abs(p[:, 0]).max() for p in sA + sB) + 3

fig, axes = plt.subplots(2, 1, figsize=(13, 6.2))
for ax, dz, sub in ((axes[0], 0.0, TXT['asm']), (axes[1], GAP, TXT['exp'])):
    draw(ax, sB, C_B); draw(ax, sA, C_A, dz)
    ax.set_xlim(-xmax, xmax); ax.set_ylim(-1, 10 + dz); ax.set_aspect('equal')
    ax.set_title(sub, fontsize=11, loc='left'); ax.grid(alpha=0.25); ax.tick_params(labelsize=7)
    ax.set_xlabel(TXT['xlabel'], fontsize=8); ax.set_ylabel('z (mm)', fontsize=8)

# labels on the assembled view, right side
ax = axes[0]
r_fl = max(p[:, 0].max() for p in sB)
ax.annotate(TXT['groove'], xy=(r_fl - 0.5, Z_CORE - 0.35), xytext=(r_fl + 0.5, -0.6), fontsize=9,
            arrowprops=dict(arrowstyle='->', lw=0.8))
ax.annotate(TXT['pin'], xy=(29.0, Z_CORE + 0.8), xytext=(6, 7), fontsize=9, arrowprops=dict(arrowstyle='->', lw=0.8))
axes[1].text(0, 7.5 + GAP, TXT['top'], color=C_A, fontsize=10, ha='center')
axes[1].text(0, 1.0, TXT['bot'], color=C_B, fontsize=10, ha='center')

fig.suptitle(TITLE, fontsize=12.5)
fig.text(0.5, 0.01, TXT['note'], ha='center', fontsize=9)
fig.tight_layout(rect=(0, 0.03, 1, 0.97))
fig.savefig(OUT, dpi=160)
print('wrote', OUT)
