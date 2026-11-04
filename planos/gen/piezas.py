"""Geometría de cada pieza de la versión C y su dibujo.

Fuente: modelo3d.html (var P y la geometría de three.js) con el escalado
de la versión C (placas de 120 mm de fondo, cables a 100 mm,
bujes en X = ±58, Y = ±23.3) y la guía de láminas.
Ejes del plano: X sobre el manubrio, Y adelante-atrás, Z arriba.
"""
import math
from dibujo import View, Iso, rr_pts, circle_pts, f

PETG1 = "#e08a4a"   # piso 1 / base (color de impresión de referencia)
PETG_BASE = "#7d93a8"
PETG_P1 = "#3aa597"
PETG_P2 = "#e7914f"
STEEL = "#c4ccd2"
RUBBER = "#3a3f44"
G = 66  # separación entre vistas (px)


def masa_petg(vol_mm3, relleno):
    """Masa estimada: volumen x 1.27 g/cm3 x factor de relleno (igual que en modelo3d)."""
    return vol_mm3 / 1000 * 1.27 * relleno


def place(x, y, s, F, T=None, L=None, ml=48, mt=82, g=G):
    """Acomoda vistas en primer diedro: frontal arriba-izquierda, superior debajo,
    lateral a la derecha. Cada vista se da como (u0, u1, v0, v1) en mm.
    Devuelve los orígenes (ox, oy) de cada vista y la caja libre para el isométrico."""
    fu0, fu1, fv0, fv1 = F
    fx, fy = x + ml, y + mt
    of = (fx - fu0 * s, fy + fv1 * s)
    fb = fy + (fv1 - fv0) * s
    fr = fx + (fu1 - fu0) * s
    ot = ol = None
    tb = fb
    if T:
        tu0, tu1, tv0, tv1 = T
        ty = fb + g
        ot = (of[0], ty + tv1 * s)
        tb = ty + (tv1 - tv0) * s
    lr = fr
    if L:
        lu0, lu1, lv0, lv1 = L
        lx = fr + g
        ol = (lx - lu0 * s, of[1])
        lr = lx + (lu1 - lu0) * s
    return of, ot, ol, (fr, fb, lr, tb)


def vlabel(sh, view, u0, v0, txt, dy=34):
    x, y = view.P(u0, v0)
    sh.text(x, y + dy, txt.upper(), "vt")


# =====================================================================
# 1. Placa base
# =====================================================================
BUJ_X, BUJ_Y = 58, 23.3


def placa_base(sh, x, y, s, iso=True, isob=None, lat=True):
    sh.header(x, y + 18, "1", "Placa base", "Por imprimir · PETG",
              "Cant. 1 · relleno 60 %%, 6 perímetros · ≈ %.0f g" % masa_petg(132 * 120 * 8 - 6 * 16 * 3.14, 0.6))
    of, ot, ol, (fr, fb, lr, tb) = place(x, y, s, (-66, 66, 0, 8), (-66, 66, -60, 60), (-60, 60, 0, 8) if lat else None)
    F = View(sh, *of, s)
    F.rect(-66, 0, 66, 8)
    for u in (-BUJ_X, BUJ_X):
        for e in (-2.25, 2.25):
            F.line((u + e, 0), (u + e, 8), "h")
        F.cl((u, -3), (u, 11))
    for u in (-14, 14):
        F.poly([(u - 4.25, 8), (u - 2.25, 6), (u - 2.25, 0)], "h", False)
        F.poly([(u + 4.25, 8), (u + 2.25, 6), (u + 2.25, 0)], "h", False)
        F.cl((u, -3), (u, 11))
    F.dimv(0, 8, 66, 66, 78)
    vlabel(sh, F, -66, 0, "Vista frontal", 22)

    T = View(sh, *ot, s)
    T.poly(rr_pts(-66, -60, 66, 60, 5))
    for u in (-BUJ_X, BUJ_X):
        for v in (-BUJ_Y, BUJ_Y):
            T.circ(u, v, 4.5)
    for u in (-14, 14):
        T.circ(u, 0, 4.5)
        T.circ(u, 0, 8.5, "t", cm=False)
    T.slot((0, 14), (0, 17.3), 5.5)
    T.slot((0, -14), (0, -17.3), 5.5)
    T.dimh(-BUJ_X, BUJ_X, BUJ_Y, BUJ_Y, 72, "116")
    T.dimh(-66, 66, -60, -60, -74, "132")
    T.dimv(-BUJ_Y, BUJ_Y, -BUJ_X, -BUJ_X, -76, "46.6")
    T.dimv(-60, 60, 66, 66, 80, "120")
    T.dimh(-14, 14, 0, 0, -36, "28")
    T.lead(BUJ_X, BUJ_Y, 2.25, 135, 34, "4× Ø4.5 pasante · bujes")
    T.lead(14, 0, 4.25, 20, 60, "2× Ø4.5 avellanado Ø8.5 · bloque")
    T.lead(0, -17.3, 2.75, -40, 60, "2× ranura 5.5, Y de 14 a 17.3 · abrazadera")
    vlabel(sh, T, -66, -60, "Vista superior", 50)

    if lat:
      Lv = View(sh, *ol, s)
      Lv.rect(-60, 0, 60, 8)
      for v in (-BUJ_Y, BUJ_Y):
        for e in (-2.25, 2.25):
            Lv.line((-v + e, 0), (-v + e, 8), "h")
      Lv.dimh(-60, 60, 8, 8, 20, "120")
      vlabel(sh, Lv, -60, 0, "Vista lateral izq.", 22)

    if iso:
        m = Iso()
        holes = [(u, v, 4.5) for u in (-BUJ_X, BUJ_X) for v in (-BUJ_Y, BUJ_Y)] + [(-14, 0, 6), (14, 0, 6), (0, 15.6, 5.5), (0, -15.6, 5.5)]
        m.prism(rr_pts(-66, -60, 66, 60, 5), "z", 0, 8, PETG_BASE, holes)
        bx = isob or (fr + G, fb + 40, 330, tb - fb - 40)
        m.render(sh, *bx)


# =====================================================================
# 2. Bloque en V
# =====================================================================
def bloque_v(sh, x, y, s, iso=True, isob=None):
    prof = [(22, 0), (12, 0), (0, 12), (-12, 0), (-22, 0), (-22, 22), (22, 22)]
    area = 44 * 22 - 24 * 12 / 2
    sh.header(x, y + 18, "2", "Bloque en V", "Por imprimir · PETG",
              "Cant. 1 · relleno 80 %%, V hacia arriba, sin soportes · ≈ %.0f g" % masa_petg(area * 40, 0.8))
    of, ot, ol, (fr, fb, lr, tb) = place(x, y, s, (-20, 20, 0, 22), (-20, 20, -22, 22), (-22, 22, 0, 22), mt=100)
    F = View(sh, *of, s)
    F.rect(-20, 0, 20, 22)
    F.line((-20, 12), (20, 12), "h")
    for u in (-14, 14):
        F.line((u - 2.8, 22), (u - 2.8, 14), "h")
        F.line((u + 2.8, 22), (u + 2.8, 14), "h")
        F.line((u - 2.8, 14), (u + 2.8, 14), "h")
        F.cl((u, 11), (u, 25))
    F.dimh(-20, 20, 22, 22, 32, "40")
    F.dimv(0, 22, -20, -20, -30, "22")
    F.dimv(14, 22, 20, 20, 30, "8")
    vlabel(sh, F, -20, 0, "Vista frontal", 22)

    T = View(sh, *ot, s)
    T.rect(-20, -22, 20, 22)
    for u in (-14, 14):
        T.circ(u, 0, 5.6)
    T.slot((0, 14), (0, 17.3), 5.5)
    T.slot((0, -14), (0, -17.3), 5.5)
    T.line((-20, 0), (20, 0), "h")
    T.dimh(-14, 14, 0, 0, -32, "28")
    T.dimv(-22, 22, 20, 20, 32, "44")
    T.lead(14, 0, 2.8, 30, 24, "2× Ø5.6 × 8 · inserto M4")
    T.lead(0, -17.3, 2.75, -120, 26, "2× ranura 5.5")
    vlabel(sh, T, -20, -22, "Vista superior", 52)

    Lv = View(sh, *ol, s)
    Lv.poly([(-a, b) for a, b in prof])
    for v in (14, 17.3):
        Lv.line((-v + 2.75 * 0, 0), (-v, 22), "h")
        Lv.line((v, 0), (v, 22), "h")
    Lv.dimh(-12, 12, 0, 0, -10, "24")
    Lv.dimh(-22, 22, 22, 22, 32, "44")
    Lv.dimv(0, 12, 0, 0, -30, "12")
    Lv.note(0, 15, "90°", "middle", cls="dt")
    vlabel(sh, Lv, -22, 0, "Vista lateral (perfil)", 44)

    if iso:
        m = Iso()
        m.prism([(b, c) for b, c in prof], "x", -20, 20, PETG_BASE)
        bx = isob or (lr + 30, y + 40, 220, 200)
        m.render(sh, *bx, smax=4)


# =====================================================================
# 3. Abrazadera en U (ficha)
# =====================================================================
def abrazadera(sh, x, y, s):
    sh.header(x, y + 18, "3", "Abrazadera en U M5", "Por comprar",
              "Cant. 1 · acero zincado · 2 tuercas nyloc M5 y 2 arandelas")
    V = View(sh, x + 70 + 14 * s, y + 120 + 8 * s, s)
    R = 14
    arc = [(R * math.cos(math.pi + math.pi * i / 24), -33.7 + R * math.sin(math.pi + math.pi * i / 24)) for i in range(25)]
    path = [(-R, 8)] + arc + [(R, 8)]
    V.poly(path, "o", False)
    ro, ri = R + 2.5, R - 2.5
    V.poly([(-ro, 8)] + [(ro * math.cos(math.pi + math.pi * i / 24), -33.7 + ro * math.sin(math.pi + math.pi * i / 24)) for i in range(25)] + [(ro, 8)], "t", False)
    V.poly([(-ri, 8)] + [(ri * math.cos(math.pi + math.pi * i / 24), -33.7 + ri * math.sin(math.pi + math.pi * i / 24)) for i in range(25)] + [(ri, 8)], "t", False)
    V.circ(0, -33.7, 22.2, "ph", cm=True)
    for u in (-R, R):
        for k in range(8):
            V.line((u - 2.5, -4 + k * 1.5), (u + 2.5, -3.2 + k * 1.5), "t")
    V.dimh(-14, 14, 8, 8, 16, "28")
    V.dimv(-50.2, 8, 16.5, 16.5, 28, "≥ 58")
    V.note(0, -33.7, "Manubrio", "middle", dy=4, cls="nt")
    V.note(-30, -56, "Para tubo de 22 a 29 mm (7/8\" a 1⅛\")", "start", dy=12)
    V.lead(-16.5, -2, 0, 180, 18, "M5")
    vlabel(sh, V, -30, -56, "", 0)


# =====================================================================
# 4. Buje de neopreno
# =====================================================================
def buje(sh, x, y, s, iso=True, isob=None):
    sh.header(x, y + 18, "4", "Buje de neopreno", "Por comprar",
              "Cant. 4 · neopreno esponjoso, cortar de barra o tubo Ø16 × Ø5")
    of, ot, ol, (fr, fb, lr, tb) = place(x, y, s, (-8, 8, 0, 20), (-8, 8, -8, 8), None, mt=106)
    F = View(sh, *of, s)
    F.rect(-8, 0, 8, 20)
    F.line((-2.5, 0), (-2.5, 20), "h")
    F.line((2.5, 0), (2.5, 20), "h")
    F.cl((0, -3), (0, 23))
    F.dimh(-8, 8, 20, 20, 26, "Ø16")
    F.dimh(-2.5, 2.5, 0, 0, -5, "Ø5")
    F.dimv(0, 20, 8, 8, 18, "20")
    vlabel(sh, F, -8, 0, "Vista frontal", 58)
    T = View(sh, *ot, s)
    T.circ(0, 0, 16)
    T.circ(0, 0, 5, cm=False)
    vlabel(sh, T, -8, -8, "Vista superior", 26)
    if iso:
        m = Iso()
        m.cyl(0, 0, 0, 20, 16, RUBBER, hole=5)
        bx = isob or (fr + 50, y + 60, 160, 170)
        m.render(sh, *bx, smax=4)


# =====================================================================
# 5. Tornillo M4 x 50 + arandela + nyloc
# =====================================================================
def tornillo(sh, x, y, s):
    sh.header(x, y + 18, "5", "Tornillo M4 × 50 cabeza baja", "Por comprar",
              "Cant. 4 · con arandela Ø12 × 1 y tuerca nyloc M4 · inox A2")
    V = View(sh, x + 60, y + 110, s)
    # dibujado acostado: cabeza a la izquierda
    V.rect(-2.8, -3.5, 0, 3.5, "stl")
    V.rect(0, -2, 50, 2, "stl")
    for i in range(30):
        u = 20 + i * 1
        if u < 50:
            V.line((u, -2), (u + 0.7, 2), "t")
    V.dimh(0, 50, 2, 2, 9, "50")
    V.dimv(-3.5, 3.5, -2.8, -2.8, -8, "Ø7")
    V.dimh(-2.8, 0, -3.5, -3.5, -9, "2.8")
    V.note(53, -1.5, "M4", cls="dt")
    # arandela y nyloc
    V2 = View(sh, x + 60 + 64 * s, y + 110, s)
    V2.rect(0, -6, 1, 6, "stl")
    V2.rect(4, -3.5, 9, 3.5, "stl")
    V2.dimv(-6, 6, 1, 1, 4.5 - 2, "")
    V2.note(-1, -10, "Arandela Ø12 × 1", "start", dy=8)
    V2.note(4, -10, "Nyloc M4", "start", dy=24)


def montaje_buje(sh, x, y, s):
    """Corte del apilado de un buje: placa base, buje, caja, arandela y nyloc."""
    sh.text(x, y + 14, "CORTE DE MONTAJE DE UN BUJE (SIN CARGA)", "vt")
    V = View(sh, x + 120, y + 40 + 48 * s, s)
    V.rect(-30, -8, 30, 0, "sec")
    V.rect(-8, 0, 8, 20, "rub")
    V.rect(-30, 20, 30, 30, "sec")
    V.rect(-2, -10.8, 2, 37, "stl")
    V.rect(-3.5, -13.6, 3.5, -8, "stl")
    V.rect(-6, 33, 6, 34, "stl")
    V.rect(-3.5, 34, 3.5, 39, "stl")
    for v in (0, 20, 30, 33):
        pass
    V.dimv(0, 20, -30, -8, -40, "20")
    V.dimv(20, 30, -30, -30, -40, "10")
    V.dimv(-8, 0, -30, -30, -40, "8")
    V.dimv(30, 33, 6, 6, 18, "3 libre")
    V.note(32, -5, "Placa base (1)", dy=4)
    V.note(32, 9, "Buje (4)", dy=4)
    V.note(32, 24, "Caja de m₁ (6), Ø8", dy=4)
    V.note(32, 36, "Arandela + nyloc (5)", dy=4)
    V.note(-30, -16, "Los 3 mm libres son el tope de rebote.", dy=10)


# =====================================================================
# 6. Caja de m1 (con 2 postes de la guía)
# =====================================================================
CAJA_BAR = [(u, v) for u in (-27, 27) for v in (-50, 50)]


def caja(sh, x, y, s, iso=True, isob=None):
    vol = 132 * 120 * 10 - 97 * 39 * 6.6 + 2 * 14 * 8 * 40
    sh.header(x, y + 18, "6", "Caja de m₁ con postes de guía", "Por imprimir · PETG",
              "Cant. 1 · relleno 60 %% · lleva el lastre (7) en la cavidad · ≈ %.0f g" % masa_petg(vol, 0.6))
    of, ot, ol, (fr, fb, lr, tb) = place(x, y, s, (-66, 66, 0, 50), (-66, 66, -60, 60), None, mt=94)
    F = View(sh, *of, s)
    F.rect(-66, 0, 66, 10)
    F.poly([(-48.5, 10), (-48.5, 3.4), (48.5, 3.4), (48.5, 10)], "h", False)
    for u in (-22, 22):
        F.rect(u - 7, 10, u + 7, 50)
        for z in (28, 44):
            F.line((u - 7, z), (u + 7, z), "t")
    for u in (-BUJ_X, BUJ_X):
        F.line((u - 4, 0), (u - 4, 10), "h")
        F.line((u + 4, 0), (u + 4, 10), "h")
        F.cl((u, -3), (u, 13))
    F.dimv(0, 10, -66, -66, -78, "10")
    F.dimv(3.4, 10, 48.5, 48.5, 58, "6.6")
    F.dimv(10, 50, 29, 29, 40, "40")
    F.dimh(-29, -15, 50, 50, 58, "14")
    F.dimh(-22, 22, 50, 50, 30, "44")
    F.note(46, 36, "ranuras 0.8", "start", dy=4)
    F.note(46, 36, "de las láminas", "start", dy=20)
    F.dimv(10, 28, -29, -29, -40, "18")
    F.dimv(28, 44, -29, -29, -40, "16")
    vlabel(sh, F, -66, 0, "Vista frontal", 22)

    T = View(sh, *ot, s)
    T.poly(rr_pts(-66, -60, 66, 60, 5))
    T.rect(-48.5, -19.5, 48.5, 19.5)
    for u in (-BUJ_X, BUJ_X):
        for v in (-BUJ_Y, BUJ_Y):
            T.circ(u, v, 8)
    for u, v in CAJA_BAR:
        T.circ(u, v, 3.4)
    T.circ(0, 0, 4.5)
    for u in (-22, 22):
        T.rect(u - 7, 21, u + 7, 29, "of")
    T.dimh(-48.5, 48.5, -19.5, -19.5, -40, "97")
    T.dimv(-19.5, 19.5, -48.5, -48.5, -56, "39")
    T.dimh(-27, 27, -50, -50, -72, "54")
    T.dimh(-66, 66, -60, -60, -86, "132")
    T.dimv(-50, 50, 27, 27, 76, "100")
    T.dimv(-60, 60, 66, 66, 90, "120")
    T.dimv(21, 29, -29, -29, -40, "8")
    T.dimv(0, 25, 7, 7, 14, "25")
    T.lead(BUJ_X, BUJ_Y, 4, 120, 28, "4× Ø8 pasante")
    T.lead(27, 50, 1.7, 45, 26, "4× Ø3.4 · barras (9)")
    T.lead(0, 0, 2.25, -45, 34, "Ø4.5 · tope (8)")
    vlabel(sh, T, -66, -60, "Vista superior", 62)

    if iso:
        m = Iso()
        holes = [(u, v, 8) for u in (-BUJ_X, BUJ_X) for v in (-BUJ_Y, BUJ_Y)] + [(u, v, 3.4) for u, v in CAJA_BAR]
        m.prism(rr_pts(-66, -60, 66, 60, 5), "z", 0, 10, PETG_P1, holes + [(-48.5, -19.5, 48.5, 19.5)])
        for u in (-22, 22):
            m.box(u - 7, u + 7, 21, 29, 10, 50, PETG_P1)
        bx = isob or (fr + G, fb + 30, 330, tb - fb - 30)
        m.render(sh, *bx)


# =====================================================================
# 7. Lastre: solera de acero
# =====================================================================
def solera(sh, x, y, s, iso=True, isob=None):
    sh.header(x, y + 18, "7", "Lastre: solera 1½\" × ¼\"", "Por comprar",
              "Cant. 1 · acero 1018, cortar a 96 mm · ≈ 182 g · pegar con epóxico en la caja")
    of, ot, ol, (fr, fb, lr, tb) = place(x, y, s, (-48, 48, 0, 6.35), (-48, 48, -19.05, 19.05), None, mt=88)
    F = View(sh, *of, s)
    F.rect(-48, 0, 48, 6.35, "stl")
    F.line((-2.25, 0), (-2.25, 6.35), "h")
    F.line((2.25, 0), (2.25, 6.35), "h")
    F.dimh(-48, 48, 6.35, 6.35, 16, "96")
    F.dimv(0, 6.35, 48, 48, 58, "6.35")
    vlabel(sh, F, -48, 0, "Vista frontal", 22)
    T = View(sh, *ot, s)
    T.rect(-48, -19.05, 48, 19.05)
    T.circ(0, 0, 4.5)
    T.dimv(-19.05, 19.05, 48, 48, 58, "38.1")
    T.lead(0, 0, 2.25, 40, 30, "Ø4.5 al centro")
    vlabel(sh, T, -48, -19.05, "Vista superior", 22)
    if iso:
        m = Iso()
        m.box(-48, 48, -19.05, 19.05, 0, 6.35, STEEL, [(0, 0, 4.5)])
        bx = isob or (fr + G + 40, y + 40, 220, tb - y - 40)
        m.render(sh, *bx)


# =====================================================================
# 8. Tope central
# =====================================================================
def tope(sh, x, y, s, iso=True, isob=None):
    sh.header(x, y + 18, "8", "Tope central", "Por imprimir · PETG",
              "Cant. 1 · base PETG · disco de goma Ø16 × 12 (comprar) pegado arriba")
    of, ot, ol, (fr, fb, lr, tb) = place(x, y, s, (-8, 8, 0, 31), None, None, mt=96)
    F = View(sh, *of, s)
    F.rect(-8, 0, 8, 19)
    F.rect(-8, 19, 8, 31, "rub")
    F.rect(-2.8, 0, 2.8, 8, "h")
    F.cl((0, -3), (0, 34))
    F.dimv(0, 19, -8, -8, -16, "19")
    F.dimv(19, 31, -8, -8, -16, "12")
    F.dimh(-8, 8, 31, 31, 38, "Ø16")
    F.note(10, 4, "inserto M4", dy=4, cls="dt")
    F.note(10, 24, "Goma", dy=4, cls="dt")
    F.note(-8, -6, "Ø5.6 × 8 · deja 18 mm libres", dy=12)
    vlabel(sh, F, -8, 0, "Vista frontal", 44)
    if iso:
        m = Iso()
        m.cyl(0, 0, 0, 19, 16, PETG_P1)
        m.cyl(0, 0, 19, 31, 16, RUBBER)
        bx = isob or (fr + 160, y + 40, 130, 200)
        m.render(sh, *bx, smax=4)


# =====================================================================
# 9 y 11. Barras inferiores y superiores
# =====================================================================
def barra(sh, x, y, s, sup=False, iso=True, isob=None):
    L = 102 if sup else 114
    holes = [-45 + 18 * i for i in range(6)] if sup else [-54 + 18 * i for i in range(7)]
    mx = 36 if sup else 27
    num = "11" if sup else "9"
    nombre = "Barra superior" if sup else "Barra inferior"
    col = PETG_P2 if sup else PETG_P1
    sh.header(x, y + 18, num, nombre, "Por imprimir · PETG",
              "Cant. 2 · imprimir acostada · %d huecos Ø1.2 para el cable · ≈ %.0f g c/u"
              % (len(holes), masa_petg(10 * 10 * L, 0.95)))
    of, ot, ol, (fr, fb, lr, tb) = place(x, y, s, (-L / 2, L / 2, 0, 10), (-L / 2, L / 2, -5, 5), None, mt=108, g=100)
    F = View(sh, *of, s)
    F.rect(-L / 2, 0, L / 2, 10)
    for u in holes:
        F.circ(u, 5, 1.2, cm=False)
    for u in (-mx, mx):
        F.line((u - 1.7, 0), (u - 1.7, 10), "h")
        F.line((u + 1.7, 0), (u + 1.7, 10), "h")
        nut = (10, 7.5) if sup else (2.5, 0)
        F.rect(u - 2.85, nut[0] if not sup else 0, u + 2.85, nut[0] if sup else 2.5, "h") if False else None
        F.cl((u, -3), (u, 13))
    # tuerca M3 embebida: por arriba en la inferior, por abajo en la superior
    for u in (-mx, mx):
        if sup:
            F.rect(u - 2.85, 0, u + 2.85, 2.5, "h")
        else:
            F.rect(u - 2.85, 7.5, u + 2.85, 10, "h")
    F.dimh(-L / 2, L / 2, 10, 10, 22, f(L))
    F.dimh(holes[0], holes[1], 5, 5, -8, "18")
    F.dimh(-mx, mx, 0, 0, -18, f(2 * mx))
    F.dimv(0, 10, L / 2, L / 2, L / 2 + 10, "10")
    F.dimv(0, 5, -L / 2, -L / 2, -L / 2 - 8, "5")
    F.lead(holes[-1], 5, 0.6, 60, 22, "%d× Ø1.2 pasante" % len(holes))
    vlabel(sh, F, -L / 2, 0, "Vista frontal", 84)
    T = View(sh, *ot, s)
    T.rect(-L / 2, -5, L / 2, 5)
    for u in holes:
        T.line((u - 0.6, -5), (u - 0.6, 5), "h")
        T.line((u + 0.6, -5), (u + 0.6, 5), "h")
    for u in (-mx, mx):
        T.circ(u, 0, 3.4)
        if not sup:
            hexp = [(u + 3.18 * math.cos(math.radians(30 + 60 * k)), 3.18 * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
            T.poly(hexp, "t")
    T.lead(mx, 0, 1.7, -50, 26, "2× Ø3.4 + tuerca M3 %s" % ("abajo" if sup else "arriba"))
    vlabel(sh, T, -L / 2, -5, "Vista superior", 50)
    if iso:
        m = Iso()
        m.box(-L / 2, L / 2, -5, 5, 0, 10, col, [(u, 0, 3.4) for u in (-mx, mx)])
        for u in holes:
            m.cyl(u, 5, -5.05, -5.0, 1.4, "#2a2f33", axis="y")
        bx = isob or (lr + 40, y + 40, 260, 120)
        m.render(sh, *bx)


# =====================================================================
# 10. Cable
# =====================================================================
def cable(sh, x, y, s):
    sh.header(x, y + 18, "10", "Cable de acero 7×7, 1/32\"", "Por comprar",
              "Cant. 2 · inox 304, Ø0.8 · cortar 850 mm por cable · rematar con casquillo")
    V = View(sh, x + 60 + 54 * s, y + 96 + 44 * s, s)
    V.rect(-57, -5, 57, 5, "t")
    V.rect(-51, 34, 51, 44, "t")
    V.note(57, -5, "Barra inferior (9)", "end", dy=16)
    V.note(-51, 44, "Barra superior (11)", dy=-6)
    pts = []
    for i in range(0, 721):
        t = i / 720 * 6 * 2 * math.pi
        pts.append((-54 + t / (2 * math.pi) * 18, 19.5 - 19.5 * math.cos(t)))
    V.poly(pts, "o", False)
    V.dimv(0, 39, 57, 57, 66, "39")
    V.dimh(-54, -36, 0, 0, -12, "paso 18")
    V.note(0, 19.5, "6 vueltas", "middle", cls="dt")
    vlabel(sh, V, -57, -5, "Vista frontal (cable montado)", 40)
    V2 = View(sh, x + 60 + 54 * s * 2 + 120 + 20 * s, y + 96 + 44 * s, s)
    V2.circ(0, 19.5, 39, cm=True)
    V2.rect(-5, -5, 5, 5, "t")
    V2.rect(-5, 34, 5, 44, "t")
    V2.dimh(-19.5, 19.5, 19.5, 19.5, 52, "D = 39")
    vlabel(sh, V2, -19.5, -5, "Lateral", 40)


# =====================================================================
# 12. Placa superior (con 2 postes de guía)
# =====================================================================
SUP_BAR = [(u, v) for u in (-36, 36) for v in (-50, 50)]
SUP_ESC = [(u, v) for u in (-20, 20) for v in (-12, 12)]


def placa_sup(sh, x, y, s, iso=True, isob=None):
    vol = 106 * 120 * 5 - 2 * 20 * 40 * 5 + 2 * 14 * 8 * 29
    sh.header(x, y + 18, "12", "Placa superior con postes de guía", "Por imprimir · PETG",
              "Cant. 1 · relleno 60 %%, 4 perímetros · ≈ %.0f g" % masa_petg(vol, 0.6))
    of, ot, ol, (fr, fb, lr, tb) = place(x, y, s, (-53, 53, -29, 5), (-53, 53, -60, 60), (-60, 60, -29, 5), mt=90)
    F = View(sh, *of, s)
    F.rect(-53, 0, 53, 5)
    for u in (-22, 22):
        F.rect(u - 7, -29, u + 7, 0)
        for z in (-23, -7):
            F.line((u - 7, z), (u + 7, z), "t")
    F.dimv(0, 5, 53, 53, 62, "5")
    F.dimv(-29, 0, -29, -29, -40, "29")
    F.dimh(-53, 53, 5, 5, 14, "106")
    vlabel(sh, F, -53, -29, "Vista frontal", 22)
    T = View(sh, *ot, s)
    T.poly(rr_pts(-53, -60, 53, 60, 5))
    for k in (-1, 1):
        T.rect(k * 30, -20, k * 50, 20)
    for u, v in SUP_BAR:
        T.circ(u, v, 3.4)
    for u, v in SUP_ESC:
        T.circ(u, v, 4.5)
    for u in (-22, 22):
        T.rect(u - 7, -29, u + 7, -21, "h")
    T.dimh(-36, 36, 50, 50, 70, "72")
    T.dimh(-20, 20, 12, 12, 34, "40")
    T.dimv(-12, 12, 20, 20, 26, "24")
    T.dimv(-50, 50, -36, -36, -64, "100")
    T.dimv(-60, 60, 53, 53, 66, "120")
    vlabel(sh, T, -53, -60, "Vista superior", 46)

    Lv = View(sh, *ol, s)
    Lv.rect(-60, 0, 60, 5)
    Lv.rect(21, -29, 29, 0)
    for z in (-23, -7):
        Lv.rect(17, z - 0.4, 21, z + 0.4, "t")
    Lv.dimh(-60, 60, 5, 5, 14, "120")
    Lv.dimv(-23, 0, 29, 29, 38, "23")
    Lv.dimv(-7, 0, 29, 29, 48, "7")
    vlabel(sh, Lv, -60, -29, "Vista lateral izq.", 22)
    if iso:
        m = Iso()
        # placa con ventanas: armada como franjas
        holes = [(u, v, 3.4) for u, v in SUP_BAR] + [(u, v, 4.5) for u, v in SUP_ESC]
        m.box(-53, 53, 20, 60, 0, 5, PETG_P2, [h for h in holes if h[1] > 20])
        m.box(-53, 53, -60, -20, 0, 5, PETG_P2, [h for h in holes if h[1] < -20])
        m.box(-30, 30, -20, 20, 0, 5, PETG_P2, [h for h in holes if abs(h[1]) < 20])
        m.box(50, 53, -20, 20, 0, 5, PETG_P2)
        m.box(-53, -50, -20, 20, 0, 5, PETG_P2)
        for u in (-22, 22):
            m.box(u - 7, u + 7, -29, -21, -29, 0, PETG_P2)
        bx = isob or (fr + G, fb + 30, 330, tb - fb - 30)
        m.render(sh, *bx)


# =====================================================================
# 13. Lámina de fleje y detalle de la guía
# =====================================================================
def lamina(sh, x, y, s, iso=True, isob=None):
    sh.header(x, y + 18, "13", "Lámina de fleje", "Por comprar",
              "Cant. 4 · fleje de acero para resorte 0.6 mm, cortar 14 × 50 · se pega en las ranuras")
    of, ot, ol, (fr, fb, lr, tb) = place(x, y, s, (-25, 25, 0, 0.6), (-25, 25, -7, 7), None, mt=124, g=50)
    F = View(sh, *of, s)
    F.rect(-25, 0, 25, 0.6, "stl")
    F.dimh(-25, 25, 0.6, 0.6, 8, "50")
    F.dimv(0, 0.6, 25, 25, 31, "0.6")
    vlabel(sh, F, -25, 0, "Vista frontal", 22)
    T = View(sh, *ot, s)
    T.rect(-25, -7, 25, 7, "stl")
    for u in (-21, 21):
        T.line((u, -7), (u, 7), "h")
    T.dimv(-7, 7, 25, 25, 33, "14")
    T.dimh(-25, -21, -7, -7, -14, "4")
    T.note(0, -7, "4 mm de cada lado van dentro de la ranura", "middle", dy=40)
    vlabel(sh, T, -25, -7, "Vista superior", 56)


def guia_conjunto(sh, x, y, s):
    """Lateral de la guía montada: postes, láminas y alturas."""
    sh.text(x, y + 14, "GUÍA MONTADA · VISTA LATERAL (SIN CARGA)", "vt")
    V = View(sh, x + 70 + 60 * s, y + 60 + 80 * s, s)
    V.rect(-60, 20, 60, 30, "t")
    V.rect(-60, 79, 60, 84, "t")
    V.note(-60, 20, "Caja de m₁ (6)", dy=14)
    V.note(-60, 84, "Placa superior (12)", dy=-6)
    V.rect(21, 30, 29, 70)
    V.rect(-29, 50, -21, 79)
    for by, ty in ((48, 56), (64, 72)):
        V.line((25, by), (-25, ty), "o")
        V.line((25, by - 0.3), (-25, ty - 0.3), "o")
    V.dimv(30, 48, 29, 29, 40, "18")
    V.dimv(48, 64, 29, 29, 40, "16")
    V.dimv(72, 79, -29, -29, -40, "7")
    V.dimv(56, 72, -29, -29, -40, "16")
    V.dimh(-25, 25, 84, 84, 90, "50 entre postes")
    V.note(0, 40, "Láminas (13)", "middle", cls="dt")
    V.note(-60, 20, "Las láminas dejan subir y bajar el piso 2 y frenan el avance y la inclinación.", dy=34)
    V.note(-60, 20, "Solo en el piso 2: en ambos pisos pasaría la vibración horizontal al celular.", dy=50)


def ranura_detalle(sh, x, y, s):
    sh.text(x, y + 14, "DETALLE A · RANURA DEL POSTE (3:1)", "vt")
    V = View(sh, x + 40 + 8 * s, y + 70 + 24 * s, s)
    V.rect(-4, 0, 4, 24)
    V.rect(0, 11.6, 4, 12.4, "of")
    V.dimv(11.6, 12.4, 4, 4, 9, "0.8")
    V.dimh(0, 4, 24, 24, 28, "4")
    V.dimh(-4, 4, 0, 0, -4, "8")
    V.note(-4, 0, "Ranura de 14 de ancho:", dy=50, cls="nt")
    V.note(-4, 0, "toda la cara del poste.", dy=66, cls="nt")


# =====================================================================
# 14-17. Porta-celular
# =====================================================================
def escuadra(sh, x, y, s, iso=True, isob=None):
    t = math.radians(15)
    sh.header(x, y + 18, "14", "Escuadra de 15°", "Por imprimir · PETG",
              "Cant. 1 · relleno 60 % · imprimir de lado (sobre el perfil)")
    # lateral (Y-Z): pie horizontal y nervio inclinado 15° hacia atrás
    of, ot, ol, (fr, fb, lr, tb) = place(x, y, s, (-28, 28, 0, 78), None, (-34, 26, 0, 78), mt=88)
    F = View(sh, *of, s)
    F.rect(-28, 0, 28, 4)
    F.rect(-28, 4, 28, 76)
    for v in (19, 56):
        for u in (-18, 18):
            F.circ(u, v, 4.5)
    for u in (-24, 24):
        F.line((u - 1.5, 4), (u - 1.5, 60), "h")
        F.line((u + 1.5, 4), (u + 1.5, 60), "h")
    F.dimh(-28, 28, 76, 76, 84, "56")
    F.dimh(-18, 18, 56, 56, 68, "36")
    F.dimv(0, 4, 28, 28, 36, "4")
    F.dimv(19, 56, -18, -18, -36, "37")
    F.dimv(4, 19, -28, -28, -36, "15")
    F.lead(18, 19, 2.25, -30, 28, "4× Ø4.5 · respaldo (15)")
    vlabel(sh, F, -28, 0, "Vista frontal", 22)
    L = View(sh, *ol, s)
    # pie
    L.rect(-16, 0, 16, 4)
    # nervio inclinado: base en y=-4 (atrás), sube inclinándose hacia atrás (+u)
    def rot(a, b):
        return (a * math.cos(t) + b * math.sin(t), -a * math.sin(t) + b * math.cos(t))
    base = (8, 4)
    rib = [rot(0, 0), rot(-4, 0), rot(-4, 72), rot(0, 72)]
    rib = [(base[0] + p[0], base[1] + p[1]) for p in rib]
    L.poly(rib)
    gus = [rot(-4, 0), rot(-4, 56), rot(-4 - 18, 0)]
    gus = [(base[0] + p[0], base[1] + p[1]) for p in gus]
    L.poly([(max(-16, p[0]), p[1]) for p in gus], "t")
    for u in (-12, 12):
        L.line((u - 2.25, 0), (u - 2.25, 4), "h")
        L.line((u + 2.25, 0), (u + 2.25, 4), "h")
    L.dimh(-16, 16, 0, 0, -10, "32")
    L.note(base[0] - 9, 40, "15°", "end", cls="dt")
    L.cl((base[0], 4), (base[0], 76))
    L.dimv(4, rib[2][1], -16, -16, -28, f(rib[2][1] - 4))
    L.note(-16, 0, "Nervio 72 × 4", dy=34)
    vlabel(sh, L, -34, 0, "Vista lateral izq.", 52)
    if iso:
        m = Iso()
        m.box(-28, 28, -16, 16, 0, 4, PETG_P2, [(u, v, 4.5) for u in (-20, 20) for v in (-12, 12)])
        # nervio aproximado como prisma en (y, z) extruido en x
        prof = [(-p[0], p[1]) for p in rib]
        m.prism(prof, "x", -28, 28, PETG_P2)
        bx = isob or (lr + 20, y + 40, 200, 240)
        m.render(sh, *bx)


def respaldo(sh, x, y, s, iso=True, isob=None):
    sh.header(x, y + 18, "15", "Respaldo", "Por imprimir · PETG",
              "Cant. 1 · 84 × 120 × 4 · lleva 4 cojines de EVA (18) y la banda de silicón")
    of, ot, ol, (fr, fb, lr, tb) = place(x, y, s, (-42, 42, 0, 120), None, None, mt=86)
    F = View(sh, *of, s)
    F.poly(rr_pts(-42, 0, 42, 120, 4))
    F.slot((9, 70), (38, 70), 4.5)
    F.slot((-38, 70), (-9, 70), 4.5)
    for u in (-18, 18):
        F.circ(u, 15, 4.5)
        F.circ(u, 52, 4.5)
        F.circ(u, 8, 3.4)
    for u in (-24, 24):
        for v in (18, 102):
            F.rect(u - 8, v - 8, u + 8, v + 8, "ph")
    F.dimh(-42, 42, 120, 120, 128, "84")
    F.dimv(0, 120, -42, -42, -52, "120")
    F.dimv(0, 70, 42, 42, 50, "70")
    F.dimv(0, 52, 42, 42, 62, "52")
    F.dimh(9, 38, 70, 70, 80, "29")
    F.dimh(-18, 18, 15, 15, -14, "36")
    F.note(-42, 0, "4× Ø4.5: escuadra · 2× Ø3.4: repisa", dy=60)
    F.note(-42, 0, "2 ranuras 4.5: mordazas · espesor 4", dy=76)
    F.note(-42, 0, "Punteado: cojines EVA 16 × 16 × 4", dy=92)
    vlabel(sh, F, -42, 0, "Vista frontal", 44)
    if iso:
        m = Iso()
        m.prism(rr_pts(-42, 0, 42, 120, 4), "y", -2, 2, PETG_P2,
                [(u, v, 4.5) for u in (-18, 18) for v in (15, 52)])
        bx = isob or (lr + 40, y + 60, 200, 300)
        m.render(sh, *bx)


def repisa(sh, x, y, s, iso=True, isob=None):
    sh.header(x, y + 18, "16", "Repisa con hueco USB", "Por imprimir · PETG",
              "Cant. 1 · relleno 60 %")
    prof = [(0, 0), (22, 0), (22, 6), (19, 6), (19, 3), (3, 3), (3, 12), (0, 12)]
    of, ot, ol, (fr, fb, lr, tb) = place(x, y, s, (-25, 25, 0, 12), (-25, 25, 0, 22), (-22, 0, 0, 12), mt=100)
    F = View(sh, *of, s)
    F.rect(-25, 0, 25, 12)
    F.line((-25, 3), (25, 3), "t")
    F.line((-25, 6), (25, 6), "t")
    for u in (-18, 18):
        F.circ(u, 8, 3.4)
    F.dimh(-25, 25, 12, 12, 20, "50")
    F.dimh(-18, 18, 8, 8, -8, "36")
    vlabel(sh, F, -25, 0, "Vista frontal", 44)
    T = View(sh, *ot, s)
    T.rect(-25, 0, 25, 22)
    T.rect(-8, 7, 8, 15)
    T.line((-25, 3), (25, 3), "t")
    T.line((-25, 19), (25, 19), "t")
    T.dimh(-8, 8, 7, 7, -6, "16")
    T.dimv(7, 15, 8, 8, 32, "8")
    T.note(0, 11, "USB", "middle", dy=4, cls="dt")
    vlabel(sh, T, -25, 0, "Vista superior", 26)
    L = View(sh, *ol, s)
    L.poly([(-a, b) for a, b in prof])
    L.dimh(-22, 0, 0, 0, -8, "22")
    L.dimv(0, 12, 0, 0, 8, "12")
    L.dimv(0, 6, -22, -22, -30, "6")
    L.note(-11, 3, "esp. 3", "middle", dy=-6, cls="dt")
    vlabel(sh, L, -22, 0, "Perfil", 44)
    if iso:
        m = Iso()
        m.prism([(-a, b) for a, b in prof], "x", -25, 25, PETG_P2)
        bx = isob or (lr + 20, y + 40, 200, 160)
        m.render(sh, *bx)


def mordaza(sh, x, y, s, iso=True, isob=None):
    sh.header(x, y + 18, "17", "Mordaza con perilla M4", "Por imprimir · PETG",
              "Cant. 2 (una y su espejo) · se desliza en la ranura del respaldo")
    prof = [(-28, 0), (3, 0), (3, 25), (-6, 25), (-6, 22), (0, 22), (0, 3), (-28, 3)]
    of, ot, ol, (fr, fb, lr, tb) = place(x, y, s, (-28, 3, 0, 25), None, (-20, 20, 0, 25), mt=96)
    F = View(sh, *of, s)
    F.poly(prof)
    F.line((-18 - 2.25, 0), (-18 - 2.25, 3), "h")
    F.line((-18 + 2.25, 0), (-18 + 2.25, 3), "h")
    F.cl((-18, -3), (-18, 6))
    F.dimh(-28, 3, 0, 0, -10, "31")
    F.dimv(0, 25, 3, 3, 12, "25")
    F.dimh(-6, 0, 25, 25, 32, "6")
    F.dimv(0, 3, -28, -28, -34, "3")
    F.note(-18, 3, "Ø4.5 · perilla M4", "middle", dy=-14, cls="dt")
    vlabel(sh, F, -28, 0, "Planta (perfil)", 44)
    L = View(sh, *ol, s)
    L.rect(-20, 0, 20, 25)
    L.dimh(-20, 20, 25, 25, 32, "40")
    vlabel(sh, L, -20, 0, "Lateral", 44)
    if iso:
        m = Iso()
        m.prism(prof, "z", 0, 40, PETG_P2)
        bx = isob or (lr + 20, y + 40, 160, 160)
        m.render(sh, *bx)


def guia_iso(sh, bx):
    """Isométrico de la guía montada (sin las placas)."""
    m = Iso()
    for u in (-22, 22):
        m.box(u - 7, u + 7, 21, 29, 0, 40, PETG_P1)          # poste de la caja (z desde la cara de la caja)
        m.box(u - 7, u + 7, -29, -21, 20, 49, PETG_P2)       # poste de la placa superior
        for by, ty in ((18, 26), (34, 42)):
            prof = [(25, by - 0.3), (25, by + 0.3), (-25, ty + 0.3), (-25, ty - 0.3)]
            m.prism(prof, "x", u - 7, u + 7, STEEL)
    m.box(-40, 40, -40, 40, -3, 0, "#dfe4e8")
    m.render(sh, *bx, smax=3, label="ISOMÉTRICA DE LA GUÍA (SIN PLACAS)")


def barra_isos(sh, b1, b2):
    for sup, bx in ((False, b1), (True, b2)):
        L = 102 if sup else 114
        mx = 36 if sup else 27
        holes = [-45 + 18 * i for i in range(6)] if sup else [-54 + 18 * i for i in range(7)]
        m = Iso()
        m.box(-L / 2, L / 2, -5, 5, 0, 10, PETG_P2 if sup else PETG_P1, [(u, 0, 3.4) for u in (-mx, mx)])
        for u in holes:
            m.cyl(u, 5, -5.05, -5.0, 1.4, "#2a2f33", axis="y")
        m.render(sh, *bx, label="ISOMÉTRICA · BARRA %s" % ("SUPERIOR" if sup else "INFERIOR"))
