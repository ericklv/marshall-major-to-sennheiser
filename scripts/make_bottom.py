# SPDX-License-Identifier: AGPL-3.0-or-later
import sys, numpy as np
import manifold3d as m3

# Rebuild the bottom part (B) with a new groove depth, keeping flange, bore, core height and pins.
#   usage: make_bottom.py v1/m3_bottom.stl OUT.stl DEPTH
# Print orientation: flange 0..2, core 2..2.7 (groove height 0.7), pins above.
# Groove depth = how far the groove goes in from the lower flange edge (v1/m3_bottom.stl: 3.0 mm).
Z_FLANGE, Z_CORE = 2.0, 2.7
SEG = 128
DT = np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])

def load(p):
    d = open(p, 'rb').read()
    n = int.from_bytes(d[80:84], 'little')
    t = np.frombuffer(d, DT, count=n, offset=84)['v']
    uq, inv = np.unique(t.reshape(-1, 3), axis=0, return_inverse=True)
    return m3.Manifold(m3.Mesh(vert_properties=uq.astype(np.float32), tri_verts=inv.reshape(-1, 3).astype(np.uint32)))

def save(man, p, label):
    mesh = man.to_mesh()
    P = np.asarray(mesh.vert_properties)[:, :3].astype(np.float64)[np.asarray(mesh.tri_verts)]
    nn = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    nn /= np.maximum(np.linalg.norm(nn, axis=1), 1e-30)[:, None]
    out = np.zeros(len(P), DT); out['v'] = P; out['n'] = nn
    with open(p, 'wb') as f:
        f.write(label.encode()[:80].ljust(80, b' ')); f.write(np.uint32(len(P)).tobytes()); f.write(out.tobytes())
    print(f"wrote {p}: {len(P)} tris, volume {man.volume():.1f} mm3, genus {man.genus()}, status {man.status()}")

if __name__ == '__main__':
    SRC, OUT, DEPTH = sys.argv[1], sys.argv[2], float(sys.argv[3])
    src = load(SRC)
    box = lambda z0, z1: m3.Manifold.cube((200, 200, z1 - z0), center=True).translate((0, 0, (z0 + z1) / 2))

    flange_sec = src.slice(Z_FLANGE / 2)
    # offset only the outer outline inward, then cut the original bore back out
    outer = m3.CrossSection([max(flange_sec.to_polygons(), key=lambda p: m3.CrossSection([p]).area())])
    bore = outer - flange_sec
    core_sec = outer.offset(-DEPTH, m3.JoinType.Round, circular_segments=SEG) - bore
    core = m3.Manifold.extrude(core_sec, Z_CORE - Z_FLANGE + 0.01).translate((0, 0, Z_FLANGE - 0.01))

    # pins keep a 0.01 overlap with the core, clipped to the new core outline (no leftover sheet of the old core)
    pins = (src ^ box(Z_CORE - 0.01, 10)) ^ m3.Manifold.extrude(core_sec, 20).translate((0, 0, Z_CORE - 1))
    B = (src ^ box(-1, Z_FLANGE)) + core + pins
    save(B, OUT, f'm3 bottom, groove depth {DEPTH} mm')
