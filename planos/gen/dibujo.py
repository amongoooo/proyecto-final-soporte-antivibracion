"""Herramientas para dibujar hojas de plano en SVG, estilo hoja de SolidWorks.

Hoja de 1200 x 900 px que representa 400 x 300 mm: 3 px = 1 mm, así que
s = 3 es escala 1:1, s = 1.5 es 1:2 y s = 6 es 2:1.
"""
import math

W, H = 1200, 900
PX_MM = 3.0
FONT = "'Century Gothic','Segoe UI',Arial,sans-serif"
INK = "#15191d"
DIM = "#1f2d3a"
FECHA = "04/11/2026"


def f(v):
    """Número con punto decimal solo si hace falta."""
    if abs(v - round(v)) < 1e-6:
        return str(int(round(v)))
    return ("%.1f" % v).rstrip("0").rstrip(".")


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def escala_txt(s):
    r = s / PX_MM
    if r >= 1:
        return "%s:1" % f(r)
    return "1:%s" % f(1 / r)


STYLE = """
.o{fill:none;stroke:%(ink)s;stroke-width:1.7;stroke-linejoin:round;stroke-linecap:round}
.of{fill:#ffffff;stroke:%(ink)s;stroke-width:1.7;stroke-linejoin:round}
.t{fill:none;stroke:%(ink)s;stroke-width:1}
.h{fill:none;stroke:%(ink)s;stroke-width:0.9;stroke-dasharray:5 3}
.c{fill:none;stroke:#6b7480;stroke-width:0.7;stroke-dasharray:14 3 2 3}
.ph{fill:none;stroke:#7b8590;stroke-width:1;stroke-dasharray:7 4}
.d{fill:none;stroke:%(dim)s;stroke-width:0.8}
.x{fill:none;stroke:%(dim)s;stroke-width:0.6}
.sec{fill:url(#rayado);stroke:%(ink)s;stroke-width:1.5}
.rub{fill:#3a3f44;stroke:%(ink)s;stroke-width:1.3}
.stl{fill:#c9d0d6;stroke:%(ink)s;stroke-width:1.3}
text{font-family:%(font)s;fill:%(ink)s}
.dt{font-size:12.5px;fill:%(dim)s}
.nt{font-size:11.5px;fill:#36414c}
.vt{font-size:12px;font-weight:700;letter-spacing:.4px;fill:#36414c}
.hd{font-size:17px;font-weight:700}
.sb{font-size:12px;fill:#36414c}
.tb{font-size:10px;fill:#5b6672;letter-spacing:.5px}
.tv{font-size:14px;font-weight:700}
.tvs{font-size:12px;font-weight:600}
""" % {"ink": INK, "dim": DIM, "font": FONT}

DEFS = """<defs>
<marker id="fl" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" markerHeight="9" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0,1.6 L10,5 L0,8.4 z" fill="%s"/></marker>
<pattern id="rayado" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="#fff"/><line x1="0" y1="0" x2="0" y2="6" stroke="#15191d" stroke-width="0.8"/></pattern>
</defs>""" % DIM


class Sheet:
    def __init__(self, titulo, hoja, total, escala, material="", fab="", cant="", masa="", notas=None):
        self.titulo, self.hoja, self.total, self.escala = titulo, hoja, total, escala
        self.material, self.fab, self.cant, self.masa = material, fab, cant, masa
        self.notas = notas or []
        self.el = []

    def add(self, s):
        self.el.append(s)

    def text(self, x, y, t, cls="nt", anchor="start", extra=""):
        self.add('<text x="%.1f" y="%.1f" class="%s" text-anchor="%s" %s>%s</text>' % (x, y, cls, anchor, extra, esc(t)))

    def badge(self, x, y, fab):
        col = {"IMPRESA": "#d4691f", "COMPRAR": "#2a6fb0", "PROPUESTA": "#b38a12", "REFERENCIA": "#6b7480"}
        key = fab.split()[0].upper()
        c = col.get(key, "#6b7480")
        w = 14 + 8.0 * len(fab)
        self.add('<rect x="%.1f" y="%.1f" width="%.1f" height="19" rx="9.5" fill="%s"/>' % (x, y - 14, w, c))
        self.add('<text x="%.1f" y="%.1f" style="font-size:11px;font-weight:700;fill:#fff;letter-spacing:.6px" text-anchor="middle">%s</text>' % (x + w / 2, y, esc(fab.upper())))
        return w

    def header(self, x, y, num, nombre, fab, info, maxc=None):
        """Título de la pieza; debajo, la etiqueta (impresa / comprar) y los datos."""
        self.text(x, y, "%s  %s" % (num, nombre), "hd")
        bw = self.badge(x, y + 21, fab)
        if not info:
            return
        maxc = maxc or min(64, int((W - 40 - x) / 6.4))
        parts = info.split(" · ")
        lines, cur = [], ""
        for p in parts:
            cand = (cur + " · " + p) if cur else p
            lim = maxc - (len(fab) + 2 if not lines else 0)
            if len(cand) > lim and cur:
                lines.append(cur)
                cur = p
            else:
                cur = cand
        lines.append(cur)
        self.text(x + bw + 8, y + 21, lines[0], "sb")
        for i, l in enumerate(lines[1:]):
            self.text(x, y + 38 + 16 * i, l, "sb")

    # ---------- marco y rotulación ----------
    def frame(self):
        m = 14
        a = ['<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H)]
        a.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="%s" stroke-width="2"/>' % (m, m, W - 2 * m, H - 2 * m, INK))
        # marcas de zona como en la hoja de SolidWorks
        for i in range(1, 8):
            x = m + i * (W - 2 * m) / 8
            a.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1"/>' % (x, m, x, m + 7, INK))
            a.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1"/>' % (x, H - m, x, H - m - 7, INK))
        for i in range(1, 6):
            y = m + i * (H - 2 * m) / 6
            a.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>' % (m, y, m + 7, y, INK))
            a.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>' % (W - m, y, W - m - 7, y, INK))
        return "\n".join(a)

    def title_block(self):
        x0, y0, x1, y1 = 620, 762, W - 14, H - 14
        a = []
        L = lambda xa, ya, xb, yb: a.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>' % (xa, ya, xb, yb, INK))
        a.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#fff" stroke="%s" stroke-width="2"/>' % (x0, y0, x1 - x0, y1 - y0, INK))
        r1, r2 = y0 + 42, y0 + 78
        L(x0, r1, x1, r1)
        L(x0, r2, x1, r2)
        c1, c2, c3 = x0 + 200, x0 + 340, x0 + 440
        L(c2, y0, c2, y1)
        L(c3, y0, c3, y1)
        L(c1, r1, c1, r2)

        def cell(x, y, lab, val, cls="tvs"):
            a.append('<text x="%.1f" y="%.1f" class="tb">%s</text>' % (x + 6, y + 12, esc(lab)))
            a.append('<text x="%.1f" y="%.1f" class="%s">%s</text>' % (x + 6, y + 29, cls, esc(val)))
        cell(x0, y0, "NOMBRE", self.titulo, "tv")
        cell(c2, y0, "VERSIÓN", "C · cables a 100")
        cell(c3, y0, "HOJA", "%s de %s" % (self.hoja, self.total), "tv")
        cell(x0, r1, "MATERIAL", self.material or "Ver cada pieza")
        cell(c1, r1, "FABRICACIÓN", self.fab or "Ver cada pieza")
        cell(c2, r1, "CANT.", self.cant or "—")
        cell(c3, r1, "ESCALA", self.escala)
        a.append('<text x="%.1f" y="%.1f" class="tb">EQUIPO CAMARADAS · ING. MECATRÓNICA</text>' % (x0 + 6, r2 + 14))
        a.append('<text x="%.1f" y="%.1f" class="tvs">Soporte antivibración · Vibraciones Mecánicas</text>' % (x0 + 6, r2 + 34))
        cell(c2, r2, "MASA", self.masa or "—")
        cell(c3, r2, "FECHA", FECHA)
        # símbolo de primer diedro dentro de la celda de escala
        sx, sy = x1 - 30, r1 + 17
        a.append('<g stroke="%s" stroke-width="1.1" fill="none"><path d="M%.1f %.1f l11 -5.5 v11 z"/><circle cx="%.1f" cy="%.1f" r="5.5"/><circle cx="%.1f" cy="%.1f" r="2.4"/></g>' % (INK, sx - 20, sy, sx + 8, sy, sx + 8, sy))
        a.append('<text x="%.1f" y="%.1f" class="tb" text-anchor="middle" style="font-size:8.5px">1er DIEDRO</text>' % (sx - 3, sy + 17))
        return "\n".join(a)

    def svg(self):
        out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
        out.append("<title>%s</title>" % esc(self.titulo))
        out.append("<style>%s</style>" % STYLE)
        out.append(DEFS)
        out.append(self.frame())
        out.extend(self.el)
        if self.notas:
            y = 780
            self.notas_y = y
            out.append('<text x="30" y="%d" class="vt">NOTAS</text>' % y)
            for i, n in enumerate(self.notas):
                out.append('<text x="30" y="%d" class="nt">%d. %s</text>' % (y + 18 + 16 * i, i + 1, esc(n)))
        out.append(self.title_block())
        out.append("</svg>")
        return "\n".join(out)


class View:
    """Vista ortogonal. Coordenadas en mm con v hacia arriba.

    (ox, oy) es el punto de la hoja donde cae el origen (0, 0) de la vista.
    """

    def __init__(self, sh, ox, oy, s, nombre=None, bbox=None):
        self.sh, self.ox, self.oy, self.s = sh, ox, oy, s
        if nombre and bbox:
            u0, v0, u1, v1 = bbox
            x, y = self.P(u0, v0)
            sh.text(x, y + 30, nombre.upper(), "vt")

    def P(self, u, v):
        return self.ox + u * self.s, self.oy - v * self.s

    def pts(self, pts):
        return " ".join("%.2f,%.2f" % self.P(u, v) for u, v in pts)

    def poly(self, pts, cls="o", close=True):
        tag = "polygon" if close else "polyline"
        self.sh.add('<%s points="%s" class="%s"/>' % (tag, self.pts(pts), cls))

    def line(self, a, b, cls="o"):
        (x1, y1), (x2, y2) = self.P(*a), self.P(*b)
        self.sh.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" class="%s"/>' % (x1, y1, x2, y2, cls))

    def rect(self, u0, v0, u1, v1, cls="o", r=0):
        x0, y0 = self.P(min(u0, u1), max(v0, v1))
        w, h = abs(u1 - u0) * self.s, abs(v1 - v0) * self.s
        self.sh.add('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" class="%s"/>' % (x0, y0, w, h, r * self.s, cls))

    def circ(self, cu, cv, d, cls="o", cm=True):
        x, y = self.P(cu, cv)
        self.sh.add('<circle cx="%.2f" cy="%.2f" r="%.2f" class="%s"/>' % (x, y, d / 2 * self.s, cls))
        if cm:
            e = d / 2 + max(1.5, 6 / self.s)
            self.line((cu - e, cv), (cu + e, cv), "c")
            self.line((cu, cv - e), (cu, cv + e), "c")

    def slot(self, a, b, w, cls="o", cm=True):
        """Ranura redondeada entre los centros a y b."""
        (x1, y1), (x2, y2) = self.P(*a), self.P(*b)
        r = w / 2 * self.s
        ang = math.atan2(y2 - y1, x2 - x1)
        nx, ny = -math.sin(ang) * r, math.cos(ang) * r
        d = "M%.2f %.2f L%.2f %.2f A%.2f %.2f 0 0 0 %.2f %.2f L%.2f %.2f A%.2f %.2f 0 0 0 %.2f %.2f Z" % (
            x1 + nx, y1 + ny, x2 + nx, y2 + ny, r, r, x2 - nx, y2 - ny, x1 - nx, y1 - ny, r, r, x1 + nx, y1 + ny)
        self.sh.add('<path d="%s" class="%s"/>' % (d, cls))
        if cm:
            e = w / 2 + max(1.5, 6 / self.s)
            if abs(a[0] - b[0]) < 1e-6:
                self.line((a[0], min(a[1], b[1]) - e), (a[0], max(a[1], b[1]) + e), "c")
                for p in (a, b):
                    self.line((p[0] - e, p[1]), (p[0] + e, p[1]), "c")
            else:
                self.line((min(a[0], b[0]) - e, a[1]), (max(a[0], b[0]) + e, a[1]), "c")
                for p in (a, b):
                    self.line((p[0], p[1] - e), (p[0], p[1] + e), "c")

    def cl(self, a, b):
        self.line(a, b, "c")

    def _arrowline(self, a, b):
        (x1, y1), (x2, y2) = self.P(*a), self.P(*b)
        self.sh.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" class="d" marker-start="url(#fl)" marker-end="url(#fl)"/>' % (x1, y1, x2, y2))

    def dimh(self, u1, u2, vb1, vb2, vd, txt=None, tside=1):
        """Cota horizontal entre u1 y u2; extensiones desde vb1 / vb2 hasta vd."""
        g = 2 / self.s
        ov = 3 / self.s * (1 if vd > max(vb1, vb2) else -1)
        for u, vb in ((u1, vb1), (u2, vb2)):
            sgn = 1 if vd > vb else -1
            self.line((u, vb + sgn * g), (u, vd + ov), "x")
        self._arrowline((u1, vd), (u2, vd))
        t = txt if txt is not None else f(abs(u2 - u1))
        x, y = self.P((u1 + u2) / 2, vd)
        self.sh.text(x, y - 4, t, "dt", "middle")

    def dimv(self, v1, v2, ub1, ub2, ud, txt=None):
        g = 2 / self.s
        ov = 3 / self.s * (1 if ud > max(ub1, ub2) else -1)
        for v, ub in ((v1, ub1), (v2, ub2)):
            sgn = 1 if ud > ub else -1
            self.line((ub + sgn * g, v), (ud + ov, v), "x")
        self._arrowline((ud, v1), (ud, v2))
        t = txt if txt is not None else f(abs(v2 - v1))
        x, y = self.P(ud, (v1 + v2) / 2)
        self.sh.add('<text x="%.1f" y="%.1f" class="dt" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">%s</text>' % (x - 4, y, x - 4, y, esc(t)))

    def lead(self, cu, cv, r, ang, length, txt, side=None):
        """Llamada con flecha: apunta al borde de un círculo de radio r (mm) en ángulo ang (grados)."""
        a = math.radians(ang)
        tip = (cu + r * math.cos(a), cv + r * math.sin(a))
        x0, y0 = self.P(*tip)
        x1 = x0 + math.cos(a) * length
        y1 = y0 - math.sin(a) * length
        right = math.cos(a) >= 0 if side is None else side > 0
        tw = 6.9 * len(txt) + 6
        x2 = x1 + (tw if right else -tw)
        self.sh.add('<polyline points="%.2f,%.2f %.2f,%.2f %.2f,%.2f" class="d" marker-start="url(#fl)"/>' % (x0, y0, x1, y1, x2, y1))
        self.sh.text((x1 + 3) if right else (x1 - 3), y1 - 4, txt, "dt", "start" if right else "end")

    def note(self, u, v, txt, anchor="start", dy=0, cls="nt"):
        x, y = self.P(u, v)
        self.sh.text(x, y + dy, txt, cls, anchor)


def rr_pts(u0, v0, u1, v1, r, n=6):
    """Puntos de un rectángulo con esquinas redondeadas."""
    pts = []
    cs = [(u1 - r, v1 - r, 0), (u0 + r, v1 - r, 90), (u0 + r, v0 + r, 180), (u1 - r, v0 + r, 270)]
    for cu, cv, a0 in cs:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
    return pts


def circle_pts(cu, cv, d, n=32):
    return [(cu + d / 2 * math.cos(2 * math.pi * i / n), cv + d / 2 * math.sin(2 * math.pi * i / n)) for i in range(n)]


# ---------------- Isométrico sombreado ----------------
def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _shade(c, k):
    r, g, b = _hex(c)
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(x * k))) for x in (r, g, b))


C30 = math.cos(math.radians(30))
LIGHT = (0.35, 0.55, 1.0)
_ln = math.sqrt(sum(x * x for x in LIGHT))
LIGHT = tuple(x / _ln for x in LIGHT)


class Iso:
    """Modelo hecho de prismas. Ejes: X (manubrio), Y (adelante), Z arriba.
    La cámara mira desde (+X, -Y, +Z)."""

    def __init__(self):
        self.faces = []  # (pts3d, normal, color, smooth, decals, clave de la pieza)
        self.n = 0

    @staticmethod
    def _map(axis, p, q, a):
        if axis == "z":
            return (p, q, a)
        if axis == "x":
            return (a, p, q)
        return (p, a, q)  # axis y: poly in (x, z)

    def prism(self, poly, axis, a0, a1, col, holes=(), smooth=False):
        ar = 0
        for i in range(len(poly)):
            p1, p2 = poly[i], poly[(i + 1) % len(poly)]
            ar += p1[0] * p2[1] - p2[0] * p1[1]
        if ar < 0:
            poly = poly[::-1]
        ax = {"z": (0, 0, 1), "x": (1, 0, 0), "y": (0, 1, 0)}[axis]
        # para el eje y, el orden (x, z) es levógiro: invertir normales
        flip = -1 if axis == "y" else 1
        top = [self._map(axis, p, q, a1) for p, q in poly]
        bot = [self._map(axis, p, q, a0) for p, q in poly]
        n_top = tuple(flip * x for x in ax)
        n_bot = tuple(-x for x in n_top)
        def hp(h):
            if len(h) == 3:
                return circle_pts(h[0], h[1], h[2], 28)
            u0, v0, u1, v1 = h
            return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        hd_top = [[self._map(axis, u, v, a1) for u, v in hp(h)] for h in holes]
        hd_bot = [[self._map(axis, u, v, a0) for u, v in hp(h)] for h in holes]
        self.n += 1
        allp = top + bot
        key = (round(min(p[2] for p in allp), 2), sum(self.depth(p) for p in allp) / len(allp), self.n)
        self.faces.append((top, n_top, col, False, hd_top, key))
        self.faces.append((bot[::-1], n_bot, col, False, hd_bot, key))
        for i in range(len(poly)):
            j = (i + 1) % len(poly)
            q = [bot[i], bot[j], top[j], top[i]]
            e = [b - a for a, b in zip(bot[i], bot[j])]
            n = (e[1] * ax[2] - e[2] * ax[1], e[2] * ax[0] - e[0] * ax[2], e[0] * ax[1] - e[1] * ax[0])
            n = tuple(flip * x for x in n)
            ln = math.sqrt(sum(x * x for x in n)) or 1
            self.faces.append((q, tuple(x / ln for x in n), col, smooth, [], key))

    def box(self, x0, x1, y0, y1, z0, z1, col, holes=()):
        self.prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "z", z0, z1, col, holes)

    def cyl(self, cx, cy, z0, z1, d, col, axis="z", hole=None):
        holes = [(cx, cy, hole)] if hole else []
        self.prism(circle_pts(cx, cy, d, 36), axis, z0, z1, col, holes, smooth=True)

    @staticmethod
    def proj(p):
        x, y, z = p
        # cámara en (+1, -1, +1)
        return ((x + y) * C30, (x - y) * 0.5 - z)

    @staticmethod
    def depth(p):
        x, y, z = p
        return x - y + z

    def render(self, sh, bx, by, bw, bh, smax=3.0, label="ISOMÉTRICA"):
        vis = []
        V = (1, -1, 1)
        for pts, n, col, smooth, dec, key in self.faces:
            if sum(a * b for a, b in zip(n, V)) <= 1e-6:
                continue
            d = sum(self.depth(p) for p in pts) / len(pts)
            vis.append((key + (d,), pts, n, col, smooth, dec))
        if not vis:
            return
        allp = [self.proj(p) for _, pts, *_ in vis for p in pts]
        u0, u1 = min(p[0] for p in allp), max(p[0] for p in allp)
        v0, v1 = min(p[1] for p in allp), max(p[1] for p in allp)
        s = min(smax, (bw - 10) / (u1 - u0), (bh - 30) / (v1 - v0))
        ox = bx + bw / 2 - (u0 + u1) / 2 * s
        oy = by + 22 + (bh - 30) / 2 - (v0 + v1) / 2 * s
        sh.text(bx, by + 10, label, "vt")
        vis.sort(key=lambda t: t[0])
        out = []
        for d, pts, n, col, smooth, dec in vis:
            k = 0.62 + 0.42 * max(0, sum(a * b for a, b in zip(n, LIGHT)))
            fc = _shade(col, k)
            pp = " ".join("%.2f,%.2f" % (ox + self.proj(p)[0] * s, oy + self.proj(p)[1] * s) for p in pts)
            if smooth:
                out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="0.6"/>' % (pp, fc, fc))
            else:
                out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="0.9" stroke-linejoin="round"/>' % (pp, fc, INK))
            for h in dec:
                hp = " ".join("%.2f,%.2f" % (ox + self.proj(p)[0] * s, oy + self.proj(p)[1] * s) for p in h)
                out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="0.7"/>' % (hp, _shade(col, 0.35), INK))
        sh.add('<g>%s</g>' % "".join(out))
