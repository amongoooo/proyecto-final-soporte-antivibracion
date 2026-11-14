"""Exportación de los planos a DXF (AutoCAD), una pieza por archivo.

Mientras una pieza está abierta (`with DXF.pieza(...)`), cada trazo que hace
`View` en dibujo.py también se escribe aquí, en mm y a tamaño real (1:1),
sin importar la escala con la que se dibujó en la hoja SVG.

Capas: CONTORNO, OCULTAS, EJES, REFERENCIA, COTAS y TEXTO.
Las cotas son entidades DIMENSION de verdad, así que en AutoCAD se pueden
editar y miden la geometría real. Los isométricos sombreados no se exportan.
"""
import math
import os
from contextlib import contextmanager

try:
    import ezdxf
    from ezdxf.enums import TextEntityAlignment
except ImportError:  # sin ezdxf solo se generan los SVG
    ezdxf = None

# capa: (color ACI, tipo de línea, grosor en centésimas de mm)
CAPAS = {
    "CONTORNO": (7, "Continuous", 50),
    "OCULTAS": (8, "DASHED", 25),
    "EJES": (1, "CENTER", 18),
    "REFERENCIA": (9, "PHANTOM", 18),
    "COTAS": (4, "Continuous", 18),
    "TEXTO": (3, "Continuous", 25),
}

# clase SVG -> capa
CLS_CAPA = {
    "o": "CONTORNO", "of": "CONTORNO", "t": "CONTORNO", "sec": "CONTORNO",
    "rub": "CONTORNO", "stl": "CONTORNO",
    "h": "OCULTAS", "c": "EJES", "ph": "REFERENCIA",
    "d": "COTAS", "x": "COTAS", "dt": "COTAS",
}

# tamaño de letra de cada clase de texto en px de hoja (3 px = 1 mm)
CLS_ALTO = {"dt": 12.5, "nt": 11.5, "vt": 12, "hd": 17, "sb": 12, "tb": 10, "tv": 14, "tvs": 12}

ALIGN = {"start": TextEntityAlignment.LEFT, "middle": TextEntityAlignment.CENTER,
         "end": TextEntityAlignment.RIGHT} if ezdxf else {}


class Exportador:
    def __init__(self):
        self.doc = None
        self.mute = 0
        self.dir = None
        self.archivos = []

    @property
    def activo(self):
        return self.doc is not None and self.mute == 0

    # ---------------- archivo por pieza ----------------
    @contextmanager
    def pieza(self, nombre, titulo, s, px_mm, hoja="", escala="", notas=()):
        """Abre un DXF nuevo; todo lo que se dibuje a escala s va a este archivo."""
        if ezdxf is None or self.dir is None:
            yield self
            return
        self.s, self.px_mm = s, px_mm
        self.k = px_mm / s          # mm de modelo por mm de papel: 2 a 1:2, 0.5 a 2:1
        doc = ezdxf.new("R2018", setup=True, units=ezdxf.units.MM)
        doc.header["$MEASUREMENT"] = 1
        doc.header["$LTSCALE"] = 2.0 * self.k
        doc.header["$PSLTSCALE"] = 0
        st = doc.styles.get("Standard")
        st.dxf.font = "arial.ttf"
        for n, (col, lt, lw) in CAPAS.items():
            doc.layers.add(n, color=col, linetype=lt, lineweight=lw)
        ds = doc.dimstyles.duplicate_entry("Standard", "PLANO")
        ds.dxf.dimscale = self.k
        ds.dxf.dimtxt = 4.0
        ds.dxf.dimasz = 3.0
        ds.dxf.dimexe = 1.0
        ds.dxf.dimexo = 0.7
        ds.dxf.dimgap = 0.8
        ds.dxf.dimdec = 1
        ds.dxf.dimzin = 8       # sin ceros a la derecha: 120, 46.6
        ds.dxf.dimdsep = ord(".")
        ds.dxf.dimtad = 1
        ds.dxf.dimtih = 0
        ds.dxf.dimtoh = 0
        ds.dxf.dimtxsty = "Standard"
        ds.dxf.dimclrd = 256
        ds.dxf.dimclre = 256
        ds.dxf.dimclrt = 256
        self.doc, self.msp = doc, doc.modelspace()
        try:
            yield self
            self._rotulo(titulo, hoja, escala, notas)
            ruta = os.path.join(self.dir, nombre + ".dxf")
            doc.saveas(ruta)
            self.archivos.append(ruta)
        finally:
            self.doc = None

    @contextmanager
    def silencio(self):
        self.mute += 1
        try:
            yield
        finally:
            self.mute -= 1

    # ---------------- conversión de coordenadas ----------------
    def m(self, x, y):
        """Punto de la hoja (px, y hacia abajo) -> modelo (mm, y hacia arriba)."""
        return (x / self.s, -y / self.s)

    def mv(self, view, u, v):
        return self.m(*view.P(u, v))

    def capa(self, cls):
        return CLS_CAPA.get(cls, "CONTORNO")

    # ---------------- primitivas ----------------
    def poly(self, view, pts, cls, close):
        if not self.activo:
            return
        self.msp.add_lwpolyline([self.mv(view, u, v) for u, v in pts], close=close,
                                dxfattribs={"layer": self.capa(cls)})

    def line(self, view, a, b, cls):
        if not self.activo:
            return
        self.msp.add_line(self.mv(view, *a), self.mv(view, *b), dxfattribs={"layer": self.capa(cls)})

    def rect(self, view, u0, v0, u1, v1, cls, r):
        if not self.activo:
            return
        ua, ub, va, vb = min(u0, u1), max(u0, u1), min(v0, v1), max(v0, v1)
        if r <= 0:
            pts = [(ua, va), (ub, va), (ub, vb), (ua, vb)]
            self.poly(view, pts, cls, True)
            return
        b = math.tan(math.radians(90) / 4)
        p = [(ua + r, va, 0), (ub - r, va, b), (ub, va + r, 0), (ub, vb - r, b),
             (ub - r, vb, 0), (ua + r, vb, b), (ua, vb - r, 0), (ua, va + r, b)]
        self.msp.add_lwpolyline([self.mv(view, u, v) + (0, 0, w) for u, v, w in p], format="xyseb",
                                close=True, dxfattribs={"layer": self.capa(cls)})

    def circ(self, view, cu, cv, d, cls):
        if not self.activo:
            return
        self.msp.add_circle(self.mv(view, cu, cv), d / 2, dxfattribs={"layer": self.capa(cls)})

    def slot(self, view, a, b, w, cls):
        if not self.activo:
            return
        du, dv = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(du, dv) or 1
        du, dv = du / ln, dv / ln
        nu, nv = -dv * w / 2, du * w / 2
        p = [(a[0] - nu, a[1] - nv, 0), (b[0] - nu, b[1] - nv, 1),
             (b[0] + nu, b[1] + nv, 0), (a[0] + nu, a[1] + nv, 1)]
        self.msp.add_lwpolyline([self.mv(view, u, v) + (0, 0, k) for u, v, k in p], format="xyseb",
                                close=True, dxfattribs={"layer": self.capa(cls)})

    def _txt(self, t, medida):
        """Texto de la cota: <> si coincide con lo que mide (queda asociativa)."""
        try:
            if abs(float(t) - medida) < 0.051:
                return "<>"
        except (TypeError, ValueError):
            pass
        return t

    def dimh(self, view, u1, u2, vb1, vb2, vd, t):
        if not self.activo:
            return
        d = self.msp.add_linear_dim(base=self.mv(view, (u1 + u2) / 2, vd), p1=self.mv(view, u1, vb1),
                                    p2=self.mv(view, u2, vb2), angle=0, dimstyle="PLANO",
                                    text=self._txt(t, abs(u2 - u1)), dxfattribs={"layer": "COTAS"})
        d.render()

    def dimv(self, view, v1, v2, ub1, ub2, ud, t):
        if not self.activo:
            return
        d = self.msp.add_linear_dim(base=self.mv(view, ud, (v1 + v2) / 2), p1=self.mv(view, ub1, v1),
                                    p2=self.mv(view, ub2, v2), angle=90, dimstyle="PLANO",
                                    text=self._txt(t, abs(v2 - v1)), dxfattribs={"layer": "COTAS"})
        d.render()

    def flecha(self, punta, cola):
        """Punta de flecha rellena (3 mm en el plano impreso)."""
        (x0, y0), (x1, y1) = punta, cola
        a = math.atan2(y1 - y0, x1 - x0)
        L, W = 3.0 * self.k, 1.0 * self.k
        bx, by = x0 + L * math.cos(a), y0 + L * math.sin(a)
        nx, ny = -math.sin(a) * W / 2, math.cos(a) * W / 2
        self.msp.add_solid([(x0, y0), (bx + nx, by + ny), (bx - nx, by - ny)], dxfattribs={"layer": "COTAS"})

    def leader(self, pts_px):
        """Llamada: polilínea en px de hoja con flecha en el primer punto."""
        if not self.activo:
            return
        pts = [self.m(x, y) for x, y in pts_px]
        self.msp.add_lwpolyline(pts, dxfattribs={"layer": "COTAS"})
        self.flecha(pts[0], pts[1])

    def text(self, x, y, t, cls, anchor, alto_px=None, rot=0):
        if not self.activo or not str(t).strip():
            return
        h = (alto_px or CLS_ALTO.get(cls, 12)) * 0.72 / self.s
        capa = "COTAS" if cls == "dt" else "TEXTO"
        e = self.msp.add_text(str(t), height=h, rotation=rot, dxfattribs={"layer": capa, "style": "Standard"})
        e.set_placement(self.m(x, y), align=ALIGN[anchor if anchor in ALIGN else "start"])

    def line_px(self, a, b, capa="CONTORNO"):
        if not self.activo:
            return
        self.msp.add_line(self.m(*a), self.m(*b), dxfattribs={"layer": capa})

    def rect_px(self, x, y, w, h, capa="CONTORNO"):
        if not self.activo:
            return
        self.msp.add_lwpolyline([self.m(x, y), self.m(x + w, y), self.m(x + w, y + h), self.m(x, y + h)],
                                close=True, dxfattribs={"layer": capa})

    # ---------------- rótulo ----------------
    def _rotulo(self, titulo, hoja, escala, notas):
        """Cuadro de datos debajo del dibujo, del ancho que tenga la pieza."""
        from ezdxf import bbox
        caja = bbox.extents(self.msp, fast=True)
        if not caja.has_data:
            return
        k = self.k
        x0, y1 = caja.extmin.x, caja.extmin.y - 12 * k
        filas = [("SOPORTE ANTIVIBRACIÓN DE 2 ETAPAS · VERSIÓN C", 5.0),
                 (titulo, 4.0),
                 ("%s · Unidades: mm · Modelo a tamaño real (1:1) · Imprimir a %s" % (hoja, escala), 3.0),
                 ("Equipo Camaradas · Ing. Mecatrónica · Vibraciones Mecánicas · 14/11/2026", 3.0)]
        filas += [("%d. %s" % (i + 1, n), 2.6) for i, n in enumerate(notas)]
        y = y1
        ancho = max(caja.size.x, 190 * k)
        alto = sum(h * 1.7 for _, h in filas) * k + 4 * k
        self.msp.add_lwpolyline([(x0, y1), (x0 + ancho, y1), (x0 + ancho, y1 - alto), (x0, y1 - alto)],
                                close=True, dxfattribs={"layer": "CONTORNO"})
        for t, h in filas:
            y -= h * 1.7 * k
            e = self.msp.add_text(t, height=h * k, dxfattribs={"layer": "TEXTO", "style": "Standard"})
            e.set_placement((x0 + 2 * k, y), align=TextEntityAlignment.LEFT)


DXF = Exportador()
