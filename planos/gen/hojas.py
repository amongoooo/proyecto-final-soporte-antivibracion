"""Genera las hojas SVG de la versión C en planos/.

Uso:  python3 planos/gen/hojas.py
Hojas: 1 conjunto, 2 base, 3 bujes, 4 caja, 5 cables, 6 guia, 7 porta.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dibujo import Sheet
import piezas as P
import conjunto as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TOTAL = 7
HOJAS = []


def hoja(fn):
    HOJAS.append(fn)
    return fn


def save(sh, name):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        fh.write(sh.svg())


@hoja
def conjunto():
    sh = Sheet("Conjunto y lista de piezas", 1, TOTAL, "1:2", notas=[
        "Ejes: X sobre el manubrio, Y adelante-atrás (acelerar y frenar), Z arriba.",
        "Alturas sin celular, con 0 en la cara superior de la placa base.",
        "Punteado: Galaxy S26 Ultra con funda (249 g) como referencia.",
        "Cordón (19) de la placa superior a la placa base: si un cable falla, el celular no cae."])
    sh.text(30, 44, "Soporte antivibración de 2 etapas · versión C", "hd")
    sh.text(30, 64, "Cables a 100 mm y guía de láminas en el piso 2", "sb")
    s = 1.5
    V = C.frontal(sh, 150, 470, s)
    sh.text(50, 600, "VISTA FRONTAL", "vt")
    C.iso_conjunto(sh, (630, 530, 550, 225))
    L = C.lateral(sh, 420, 470, s)
    sh.text(310, 600, "VISTA LATERAL IZQ.", "vt")
    C.tabla(sh, 626, 40)
    save(sh, "conjunto.svg")


@hoja
def base():
    sh = Sheet("Placa base y bloque en V", 2, TOTAL, "1:1", notas=[
        "Bujes en X = ±58, Y = ±23.3 (versión C, placas de 120 mm de fondo).",
        "Las ranuras de la abrazadera no cambian con la versión: 28 mm entre ejes.",
        "Apretar la abrazadera poco a poco: el PETG cede con el tiempo."])
    P.placa_base(sh, 20, 20, 3, lat=False, isob=(520, 470, 360, 270))
    P.bloque_v(sh, 560, 20, 3, isob=(890, 290, 280, 220))
    save(sh, "base.svg")


@hoja
def bujes():
    sh = Sheet("Bujes, tornillería y abrazadera", 3, TOTAL, "2:1 y 1:1", notas=[
        "Buje a 2:1; tornillo, corte de montaje y abrazadera a 1:1.",
        "No imprimir los bujes en TPU sólido: quedarían mucho más rígidos que k₁.",
        "Apretar el nyloc solo hasta asentar la arandela; el buje no debe quedar aplastado."])
    P.buje(sh, 20, 20, 6, isob=(260, 440, 150, 170))
    P.tornillo(sh, 470, 20, 3)
    P.montaje_buje(sh, 470, 210, 3)
    P.abrazadera(sh, 880, 20, 3)
    save(sh, "bujes.svg")


@hoja
def caja():
    sh = Sheet("Caja de m₁, lastre y tope", 4, TOTAL, "1:1 y 1:2", notas=[
        "Caja y tope a 1:1; lastre a 1:2.",
        "Los postes se imprimen junto con la caja. Ranuras de 0.8 mm para las láminas (hoja 6).",
        "Lastre pegado con epóxico; el tornillo M4 central sujeta caja, lastre y tope."])
    P.caja(sh, 20, 20, 3, isob=(540, 300, 320, 260))
    P.solera(sh, 870, 20, 1.5, isob=(890, 300, 280, 110))
    P.tope(sh, 870, 440, 3, isob=(1070, 540, 100, 170))
    save(sh, "caja.svg")


@hoja
def cables():
    sh = Sheet("Barras y cables", 5, TOTAL, "1:1", notas=[
        "Huecos de Ø1.2 repasados con broca después de imprimir.",
        "Los huecos de la barra superior van desfasados medio paso (9 mm) de los de la inferior.",
        "Cable: 6 vueltas de D = 39 entre barras; amarrar el cordón (19) a la barra superior."])
    P.barra(sh, 20, 20, 3, sup=False, iso=False)
    P.barra(sh, 470, 20, 3, sup=True, iso=False)
    P.barra_isos(sh, (870, 340, 300, 130), (870, 480, 300, 130))
    P.cable(sh, 20, 370, 3)
    save(sh, "cables.svg")


@hoja
def guia():
    sh = Sheet("Guía de láminas", 6, TOTAL, "2:1 y 1:1", notas=[
        "Lámina a 2:1; guía montada a 1:1; detalle A a 3:1.",
        "Propuesta: probar primero en la mesa. Pegar las láminas con epóxico en las ranuras.",
        "Supuesto sin medir: 30 N·m/rad al giro, 20 000 N/m horizontal y 60 N/m vertical."])
    P.lamina(sh, 20, 20, 6)
    P.guia_conjunto(sh, 20, 380, 3)
    P.ranura_detalle(sh, 520, 380, 9)
    P.guia_iso(sh, (770, 370, 400, 380))
    save(sh, "guia.svg")


@hoja
def porta():
    sh = Sheet("Placa superior y porta-celular", 7, TOTAL, "1:2 y 1:1", notas=[
        "Placa superior, escuadra y respaldo a 1:2; repisa y mordaza a 1:1.",
        "Placa superior: 4× Ø3.4 para las barras (11), 4× Ø4.5 para la escuadra, 2 ventanas de 20 × 40; punteado: postes.",
        "M4 × 12 para escuadra-placa y respaldo-escuadra; perillas M4 en las mordazas.",
        "Cojines de EVA (18) y banda de silicón alrededor del celular."])
    P.placa_sup(sh, 20, 20, 1.5, isob=(300, 260, 200, 170))
    P.respaldo(sh, 520, 20, 1.5, isob=(570, 470, 230, 270))
    P.repisa(sh, 830, 20, 3, iso=False)
    P.mordaza(sh, 830, 330, 3, iso=False)
    P.escuadra(sh, 20, 460, 1.5, isob=(330, 520, 200, 220))
    save(sh, "porta.svg")


if __name__ == "__main__":
    for fn in HOJAS:
        fn()
    print("ok:", ", ".join(fn.__name__ for fn in HOJAS))
