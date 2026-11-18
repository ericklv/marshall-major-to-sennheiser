# SPDX-License-Identifier: AGPL-3.0-or-later
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch

# Half cross-section on the long axis (print orientation, flange on bed) comparing groove variants.
#   usage: sketch_groove_risk.py OUT.png {en|es}
OUT, LANG = sys.argv[1], sys.argv[2]
R_FL_LOW, R_FL_UP, T_FL = 45.0, 46.0, 2.0
CHAMF_SLOPE = (46.0 - 31.46) / 3.5          # radial mm lost per mm of height on the outer chamfer
UP_STRAIGHT = 2.15                          # straight part of the upper flange before the chamfer
X0, X1 = 34.0, 53.0

TXT = {
    'en': dict(
        cases=('Printed prototype (v1/onepiece_4.5.stl)', 'v1 two-part (v1/m3_bottom.stl)',
               'v2 one-piece (v2/onepiece_4.5.stl)', 'v2 two-part (v2/m3_bottom_d7.stl)'),
        sep='.', seam='glued joint A/B', no_ovh='no overhangs: each part prints without supports',
        ovh='overhang (red) of {} mm when printing:', ovh_big='7 mm supports inside a 0.7 slot: almost impossible to remove',
        ovh_mid='needs supports inside the groove', ovh_small='usually prints without supports',
        pad='earpad', grip_low='lower flange grip', grip_up='upper flange grip', width='width {}', pull='pull',
        title='groove {} wide × {} deep', xlabel='radius from centre, long axis (mm)  ← centre',
        suptitle='7 mm deep groove: lip grip and print risk',
        foot=('Schematic section on the long axis, lower flange on the bed. The earpad lip is schematic, not measured.\n'
              'With a 7 deep groove the lip is held 7 mm below and 8 mm above (was 3 and 4), but the earpad lip must be at least 7 mm long.\n'
              'In one piece, the groove ceiling becomes an 8 mm overhang inside a 0.7 slot: supports cannot be cleaned out. The two-part version has no overhangs.')),
    'es': dict(
        cases=('Prototipo impreso (v1/onepiece_4.5.stl)', 'v1 dos piezas (v1/m3_bottom.stl)',
               'v2 una pieza (v2/onepiece_4.5.stl)', 'v2 dos piezas (v2/m3_bottom_d7.stl)'),
        sep=',', seam='unión pegada A/B', no_ovh='sin voladizos: cada pieza se imprime sin soportes',
        ovh='voladizo (rojo) de {} mm al imprimir:', ovh_big='soportes de 7 mm dentro de una ranura de 0,7: casi imposibles de sacar',
        ovh_mid='necesita soportes dentro de la muesca', ovh_small='suele imprimirse sin soportes',
        pad='almohadilla', grip_low='agarre brida inferior', grip_up='agarre brida superior', width='ancho {}', pull='tirón',
        title='muesca {} de ancho × {} de fondo', xlabel='radio desde el centro, eje largo (mm)  ← centro',
        suptitle='Muesca de 7 mm de fondo: agarre del labio y riesgo al imprimir',
        foot=('Corte esquemático por el eje largo, con la brida inferior en la cama. El labio de la almohadilla es un esquema, no está medido.\n'
              'Con 7 de fondo el labio queda atrapado 7 mm por debajo y 8 mm por arriba (antes 3 y 4), pero el labio de la almohadilla tiene que medir al menos 7 mm.\n'
              'En una pieza, el techo de la muesca pasa a ser un voladizo de 8 mm dentro de una ranura de 0,7: los soportes no se pueden limpiar. En dos piezas no hay voladizos.')),
}[LANG]

CASES = list(zip(TXT['cases'], (1.0, 0.7, 0.7, 0.7), (42.0, 42.0, 38.0, 38.0), ('one', 'split', 'one', 'split')))
fmt = lambda v: f'{v:.1f}'.replace('.', TXT['sep'])
C_PART, C_LIP, C_OVH, C_TXT = '#c9ccd3', '#4a6fa5', '#d9534f', '#222'

def profile(width, core):
    z_g0, z_g1 = T_FL, T_FL + width
    z_c = z_g1 + UP_STRAIGHT
    top = z_c + (R_FL_UP - X0) / CHAMF_SLOPE
    return [(X0, 0), (R_FL_LOW, 0), (R_FL_LOW, z_g0), (core, z_g0), (core, z_g1),
            (R_FL_UP, z_g1), (R_FL_UP, z_c), (X0, top)], z_g0, z_g1

fig, axes = plt.subplots(2, 2, figsize=(13, 9.5))
for ax, (title, width, core, kind) in zip(axes.flat, CASES):
    pts, z0, z1 = profile(width, core)
    ax.add_patch(Polygon(pts, closed=True, fc=C_PART, ec='#555', lw=1.2))
    if kind == 'split':
        ax.plot([X0, core], [z1, z1], ls='--', color='#555', lw=1)
        ax.text(X0 + 0.3, z1 + 0.15, TXT['seam'], fontsize=8, color='#555')
        ax.text(X0 + 0.3, 8.4, TXT['no_ovh'], fontsize=8, color='#2e7d32',
                va='top', bbox=dict(fc='white', ec='none', alpha=0.85, pad=1.5))
    else:
        ax.add_patch(Rectangle((core, z1 - 0.05), R_FL_UP - core, 0.18, fc=C_OVH, ec='none', alpha=0.8))
        ovh = R_FL_UP - core
        note = TXT['ovh_big'] if ovh > 5 else TXT['ovh_mid'] if ovh > 2 else TXT['ovh_small']
        ax.text(X0 + 0.3, 8.4, TXT['ovh'].format(fmt(ovh)) + '\n' + note, fontsize=8, color=C_OVH,
                va='top', bbox=dict(fc='white', ec='none', alpha=0.85, pad=1.5))
    # earpad lip, schematic: fills the groove to its bottom, then turns down into the cushion
    lip = [(core, z0), (50.0, z0), (50.0, -2.5), (51.0, -2.5), (51.0, z1), (core, z1)]
    ax.add_patch(Polygon(lip, closed=True, fc=C_LIP, ec='none', alpha=0.55))
    ax.text(50.3, -2.3, TXT['pad'], fontsize=8, color=C_LIP, rotation=90, va='bottom')
    for r_fl, y, lab in ((R_FL_LOW, -0.45, TXT['grip_low']), (R_FL_UP, z1 + UP_STRAIGHT + 0.5, TXT['grip_up'])):
        ax.add_patch(FancyArrowPatch((core, y), (r_fl, y), arrowstyle='<->', mutation_scale=9, color=C_TXT, lw=1))
        ax.text((core + r_fl) / 2, y + (0.2 if y > 0 else -0.55), f'{lab}: {fmt(r_fl - core)}', fontsize=8.5, ha='center', color=C_TXT)
    ax.annotate(TXT['width'].format(fmt(width)), xy=(core + 0.3, (z0 + z1) / 2), xytext=(X0 + 0.5, (z0 + z1) / 2 - 1.6),
                fontsize=8.5, arrowprops=dict(arrowstyle='->', lw=0.8))
    ax.add_patch(FancyArrowPatch((52.3, z0 + 0.3), (52.3, -2.2), arrowstyle='->', mutation_scale=12, color='#888', lw=1.2))
    ax.text(52.5, -1.2, TXT['pull'], fontsize=8, color='#888', rotation=90)
    ax.set_title(title + '\n' + TXT['title'].format(fmt(width), fmt(R_FL_LOW - core)), fontsize=10, loc='left')
    ax.set_xlim(X0, X1); ax.set_ylim(-3.3, 9.2); ax.set_aspect('equal')
    ax.set_xlabel(TXT['xlabel'], fontsize=8); ax.set_ylabel('z (mm)', fontsize=8)
    ax.tick_params(labelsize=7); ax.grid(alpha=0.25)

fig.suptitle(TXT['suptitle'], fontsize=12.5, y=0.995)
fig.text(0.5, 0.005, TXT['foot'], ha='center', va='bottom', fontsize=8.5, color=C_TXT)
fig.tight_layout(rect=(0, 0.06, 1, 0.98))
fig.subplots_adjust(hspace=0.42)
fig.savefig(OUT, dpi=160)
print('wrote', OUT)
