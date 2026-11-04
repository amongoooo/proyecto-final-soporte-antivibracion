"""Hoja de conjunto de la versión C: vistas armadas, alturas y lista de piezas."""
import math
from dibujo import View, rr_pts, f, esc, INK

PHONE_H, PHONE_W, PHONE_T = 170, 84, 11  # Galaxy S26 Ultra con funda (referencia)
TILT = math.radians(15)

BOM = [
    ("1", "Placa base 132 × 120 × 8", "1", "Por imprimir", "PETG", "2"),
    ("2", "Bloque en V 40 × 44 × 22", "1", "Por imprimir", "PETG", "2"),
    ("3", "Abrazadera en U M5 + nyloc", "1", "Por comprar", "Acero zincado", "3"),
    ("4", "Buje Ø16 × Ø5 × 20", "4", "Por comprar", "Neopreno esponjoso", "3"),
    ("5", "Tornillo M4 × 50 + arandela + nyloc", "4", "Por comprar", "Inox A2", "3"),
    ("6", "Caja de m₁ con 2 postes", "1", "Por imprimir", "PETG", "4"),
    ("7", "Lastre: solera 1½\" × ¼\" × 96", "1", "Por comprar", "Acero 1018", "4"),
    ("8", "Tope central Ø16 + goma", "1", "Por imprimir", "PETG + hule", "4"),
    ("9", "Barra inferior 10 × 10 × 114", "2", "Por imprimir", "PETG", "5"),
    ("10", "Cable 7×7 1/32\", 850 mm", "2", "Por comprar", "Inox 304", "5"),
    ("11", "Barra superior 10 × 10 × 102", "2", "Por imprimir", "PETG", "5"),
    ("12", "Placa superior con 2 postes", "1", "Por imprimir", "PETG", "7"),
    ("13", "Lámina de fleje 14 × 50 × 0.6", "4", "Por comprar", "Acero resorte", "6"),
    ("14", "Escuadra de 15°", "1", "Por imprimir", "PETG", "7"),
    ("15", "Respaldo 84 × 120 × 4", "1", "Por imprimir", "PETG", "7"),
    ("16", "Repisa con hueco USB", "1", "Por imprimir", "PETG", "7"),
    ("17", "Mordaza con perilla M4", "2", "Por imprimir", "PETG + M4", "7"),
    ("18", "Cojín 16 × 16 × 4 y banda", "4 + 1", "Por comprar", "EVA / silicón", "7"),
    ("19", "Cordón de seguridad Ø1.5", "1", "Por comprar", "Poliéster", "1"),
    ("20", "Tornillería M3 × 10 (8), M4 × 12 (8)", "—", "Por comprar", "Inox A2", "—"),
]


def tabla(sh, x, y):
    cols = [(0, "#"), (30, "PIEZA"), (252, "CANT."), (294, "FABRICACIÓN"), (402, "MATERIAL"), (524, "HOJA")]
    w, rh = 556, 22
    sh.add('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="#eef1f4" stroke="%s" stroke-width="1.2"/>' % (x, y, w, rh, INK))
    for cx, t in cols:
        sh.text(x + cx + 6, y + 15, t, "tb")
    for i, r in enumerate(BOM):
        yy = y + rh * (i + 1)
        sh.add('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="#fff" stroke="%s" stroke-width="0.6"/>' % (x, yy, w, rh, INK))
        for (cx, _), v in zip(cols, r):
            if v in ("Por imprimir", "Por comprar"):
                c = "#d4691f" if v == "Por imprimir" else "#2a6fb0"
                sh.add('<text x="%.1f" y="%.1f" style="font-size:12px;font-weight:700;fill:%s">%s</text>' % (x + cx + 6, yy + 15.5, c, v.upper()))
            else:
                sh.text(x + cx + 6, yy + 15.5, v, "nt")
    for cx, _ in cols[1:]:
        sh.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.6"/>' % (x + cx, y, x + cx, y + rh * (len(BOM) + 1), INK))


def helix_front(V, z0, z1):
    pts = []
    for i in range(721):
        t = i / 720 * 12 * math.pi
        pts.append((-54 + t / (2 * math.pi) * 18, z0 + (z1 - z0) / 2 * (1 - math.cos(t))))
    V.poly(pts, "t", False)


def frontal(sh, ox, oy, s):
    V = View(sh, ox, oy, s)
    # manubrio, abrazadera y bloque
    V.circ(0, -33.7, 22.2, "ph")
    V.rect(-20, -30, 20, -8)
    V.rect(-66, -8, 66, 0)
    for u in (-58, 58):
        V.rect(u - 8, 0, u + 8, 20, "rub")
    V.rect(-66, 20, 66, 30)
    for u in (-22, 22):
        V.rect(u - 7, 30, u + 7, 70, "t")
        V.rect(u - 7, 50, u + 7, 79, "t")
    V.rect(-57, 30, 57, 40)
    V.rect(-51, 69, 51, 79)
    helix_front(V, 35, 74)
    V.rect(-8, 30, 8, 49)
    V.rect(-8, 49, 8, 61, "rub")
    V.rect(-53, 79, 53, 84)
    V.rect(-28, 84, 28, 88)
    hp = 98 + 120 * math.cos(TILT)
    V.rect(-42, 98, 42, hp)
    V.rect(-PHONE_W / 2, 98 + 3 * math.cos(TILT), PHONE_W / 2, 98 + (3 + PHONE_H) * math.cos(TILT), "ph")
    V.rect(-25, 98, 25, 98 + 12 * math.cos(TILT), "t")
    V.dimh(-66, 66, -8, -8, -66, "132")
    V.dimh(-58, 58, 0, 0, -54, "116")
    return V


def lateral(sh, ox, oy, s):
    """Vista lateral izquierda: u = -Y."""
    V = View(sh, ox, oy, s)
    V.circ(0, -33.7, 22.2, "ph")
    V.poly([(22, -30), (12, -30), (0, -18), (-12, -30), (-22, -30), (-22, -8), (22, -8)])
    V.rect(-60, -8, 60, 0)
    for v in (-23.3, 23.3):
        V.rect(v - 8, 0, v + 8, 20, "rub")
    V.rect(-60, 20, 60, 30)
    V.rect(-29, 30, -21, 70)       # poste de la caja (Y = +25 -> u = -25)
    V.rect(21, 50, 29, 79)         # poste de la placa superior (Y = -25)
    for by, ty in ((48, 56), (64, 72)):
        V.line((-25, by), (25, ty))
    for v in (-50, 50):
        V.rect(v - 5, 30, v + 5, 40)
        V.rect(v - 5, 69, v + 5, 79)
        V.circ(v, 54.5, 39, "t", cm=False)
    V.rect(-8, 30, 8, 49)
    V.rect(-8, 49, 8, 61, "rub")
    V.rect(-60, 79, 60, 84)
    V.rect(-16, 84, 16, 88)

    def P(yl, zl):
        # punto del porta-celular: (y local hacia arriba, z local hacia el frente)
        Y = 13.3 + yl * math.sin(-TILT) * -1 * -1 if False else None
        z = 98 + yl * math.cos(TILT) - zl * math.sin(-TILT)
        yy = 13.3 + yl * math.sin(-TILT) + zl * math.cos(TILT)
        return (-yy, z)
    V.poly([P(0, -4), P(120, -4), P(120, 0), P(0, 0)])
    V.poly([P(-14, -8), P(60, -8), P(60, -4), P(-14, -4)], "t")
    V.poly([P(0, 0), P(0, 22), P(6, 22), P(6, 19), P(3, 19), P(3, 0)], "t")
    V.poly([P(3, 4), P(3 + PHONE_H, 4), P(3 + PHONE_H, 4 + PHONE_T), P(3, 4 + PHONE_T)], "ph")
    # alturas
    xs = 78
    for a, b in ((0, 20), (20, 30), (30, 79), (79, 84), (84, 98)):
        V.dimv(a, b, 60, 60, xs, f(b - a))
    V.dimv(0, 98, 60, 60, xs + 18, "98")
    V.note(P(120, 0)[0] + 4, P(120, 0)[1], "15°", dy=10, cls="dt")
    return V


def iso_conjunto(sh, bx):
    from dibujo import Iso
    from piezas import PETG_BASE, PETG_P1, PETG_P2, STEEL, RUBBER
    m = Iso()
    m.box(-20, 20, -22, 22, -30, -8, PETG_BASE)
    m.prism(rr_pts(-66, -60, 66, 60, 5), "z", -8, 0, PETG_BASE)
    for u in (-58, 58):
        for v in (-23.3, 23.3):
            m.cyl(u, v, 0, 20, 16, RUBBER)
    m.prism(rr_pts(-66, -60, 66, 60, 5), "z", 20, 30, PETG_P1)
    for v in (-50, 50):
        m.box(-57, 57, v - 5, v + 5, 30, 40, PETG_P1)
        m.box(-51, 51, v - 5, v + 5, 69, 79, PETG_P2)
    for u in (-22, 22):
        m.box(u - 7, u + 7, 21, 29, 30, 70, PETG_P1)
        m.box(u - 7, u + 7, -29, -21, 50, 79, PETG_P2)
    m.cyl(0, 0, 30, 49, 16, PETG_P1)
    m.cyl(0, 0, 49, 61, 16, RUBBER)
    m.prism(rr_pts(-53, -60, 53, 60, 5), "z", 79, 84, PETG_P2)
    m.box(-28, 28, -16, 16, 84, 88, PETG_P2)

    def P(yl, zl):
        z = 98 + yl * math.cos(TILT) + zl * math.sin(TILT)
        yy = 13.3 - yl * math.sin(TILT) + zl * math.cos(TILT)
        return (yy, z)
    m.prism([P(0, -4), P(0, 0), P(120, 0), P(120, -4)], "x", -42, 42, PETG_P2)
    m.prism([P(3, 4), P(3, 4 + PHONE_T), P(3 + PHONE_H, 4 + PHONE_T), P(3 + PHONE_H, 4)], "x", -PHONE_W / 2, PHONE_W / 2, "#2a3036")
    m.render(sh, *bx, smax=2, label="ISOMÉTRICA DEL CONJUNTO (SIN CABLES NI GUÍA)")
