"""
exports.py
==========
Genere les fichiers a importer dans un logiciel de CAO (Fusion 360, SolidWorks).

Trois sorties :
  - un maillage STL de la coque (Insertion > Maillage dans Fusion)
  - un fichier DXF des sections (Fusion l'importe comme esquisses a "lofter")
  - une table des cotes (offsets) en CSV : le tableau classique de l'architecte
    naval, demi-largeurs par station et par ligne d'eau.
"""

import numpy as np


def export_stl(carene, chemin, nx=81, nz=41):
    """
    Ecrit un maillage STL (ASCII) de la surface de la coque.

    On maille la surface y = +/- b(x, z) sur une grille (stations x hauteurs),
    on ajoute le pont pour fermer le dessus. Aux extremites (b=0) et a la quille
    (b=0) la surface se referme naturellement.
    """
    xs = np.linspace(-carene.L / 2.0, carene.L / 2.0, nx)
    zs = np.linspace(0.0, carene.D, nz)

    triangles = []

    def ajoute_quad(p1, p2, p3, p4):
        """Un quadrilatere = deux triangles."""
        triangles.append((p1, p2, p3))
        triangles.append((p1, p3, p4))

    # --- Flancs tribord (+y) et babord (-y) ---
    for signe in (+1.0, -1.0):
        for i in range(nx - 1):
            for j in range(nz - 1):
                b00 = signe * carene.demi_largeur(xs[i], zs[j])
                b10 = signe * carene.demi_largeur(xs[i + 1], zs[j])
                b11 = signe * carene.demi_largeur(xs[i + 1], zs[j + 1])
                b01 = signe * carene.demi_largeur(xs[i], zs[j + 1])
                p1 = (xs[i], b00, zs[j])
                p2 = (xs[i + 1], b10, zs[j])
                p3 = (xs[i + 1], b11, zs[j + 1])
                p4 = (xs[i], b01, zs[j + 1])
                ajoute_quad(p1, p2, p3, p4)

    # --- Pont (z = D) pour fermer le dessus ---
    for i in range(nx - 1):
        bd0 = carene.demi_largeur(xs[i], carene.D)
        bd1 = carene.demi_largeur(xs[i + 1], carene.D)
        p1 = (xs[i], bd0, carene.D)
        p2 = (xs[i], -bd0, carene.D)
        p3 = (xs[i + 1], -bd1, carene.D)
        p4 = (xs[i + 1], bd1, carene.D)
        ajoute_quad(p1, p2, p3, p4)

    with open(chemin, "w") as f:
        f.write("solid carene_fregate\n")
        for (a, b, c) in triangles:
            f.write("  facet normal 0 0 0\n")
            f.write("    outer loop\n")
            for p in (a, b, c):
                f.write(f"      vertex {p[0]:.5f} {p[1]:.5f} {p[2]:.5f}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")
        f.write("endsolid carene_fregate\n")
    return len(triangles)


def export_dxf_sections(carene, chemin, n_sections=11, nz=61):
    """
    Ecrit un DXF minimal contenant les sections transversales (couples), en
    coordonnees (y, z). Importable dans Fusion comme esquisses pour faire un
    loft entre les couples.
    """
    positions = np.linspace(-carene.L / 2.0, carene.L / 2.0, n_sections)

    with open(chemin, "w") as f:
        f.write("0\nSECTION\n2\nENTITIES\n")
        for x in positions:
            poly = carene.polygone_section(x, nz=nz)
            f.write("0\nLWPOLYLINE\n8\nSECTIONS\n")
            f.write(f"90\n{len(poly)}\n70\n1\n")   # 70=1 : polyligne fermee
            for (y, z) in poly:
                f.write(f"10\n{y:.5f}\n20\n{z:.5f}\n")
        f.write("0\nENDSEC\n0\nEOF\n")
    return n_sections


def export_table_cotes(carene, chemin, n_stations=11, n_lignes_eau=10):
    """
    Ecrit la table des cotes (offsets) en CSV : demi-largeurs (m) pour un
    quadrillage de stations (colonnes) et de lignes d'eau (lignes).
    """
    xs = np.linspace(-carene.L / 2.0, carene.L / 2.0, n_stations)
    zs = np.linspace(0.0, carene.D, n_lignes_eau)

    with open(chemin, "w") as f:
        entete = "z (m) \\ x (m)," + ",".join(f"{x:.1f}" for x in xs)
        f.write(entete + "\n")
        for z in zs:
            valeurs = [f"{carene.demi_largeur(x, z):.3f}" for x in xs]
            f.write(f"{z:.2f}," + ",".join(valeurs) + "\n")
    return (n_stations, n_lignes_eau)
