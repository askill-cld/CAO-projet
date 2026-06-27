"""
stabilite.py
============
Calcul de la STABILITE A GRANDS ANGLES : la fameuse courbe GZ(theta).

GZ est le "bras de levier de redressement" : quand le navire gite d'un angle
theta, la poussee d'Archimede (au centre de carene B) et le poids (au centre de
gravite G) forment un couple qui tend a redresser le navire. GZ est la distance
horizontale entre ces deux forces. Plus GZ est grand, plus le navire est stable.

Methode (calcul direct, valable a tout angle) :
  1. On incline le navire d'un angle theta.
  2. On cherche la ligne de flottaison qui garde le MEME volume immerge que
     le navire droit (le poids ne change pas, donc le volume non plus).
  3. On calcule la nouvelle position du centre de carene B (centroide du
     volume immerge).
  4. GZ = distance horizontale (dans le repere de la mer) entre G et B.

On valide ce calcul direct contre la "formule des murailles droites" aux
petits angles : GZ ~= (GM + 0.5*BM*tan^2(theta)) * sin(theta).
"""

import numpy as np
from outils import simpson, aire_centroide_polygone, decoupe_demi_plan

# numpy >= 2.0 a renomme trapz en trapezoid ; on gere les deux versions.
_trapeze = getattr(np, "trapezoid", getattr(np, "trapz", None))


def _proprietes_immergees(carene, xs, polygones, phi, c):
    """
    Pour un angle de gite phi (rad) et un niveau d'eau c, calcule le volume
    immerge et son centroide (centre de carene B) en coordonnees navire.

    La surface de l'eau est horizontale dans le repere de la mer. Dans le
    repere du navire incline, elle devient la droite :  z*cos(phi) - y*sin(phi) = c
    On garde la partie de chaque section telle que  z*cos(phi) - y*sin(phi) <= c
    (c'est la partie immergee).
    """
    a_coef = -np.sin(phi)   # coefficient de y
    b_coef = np.cos(phi)    # coefficient de z

    aires = np.zeros(len(xs))
    ymom = np.zeros(len(xs))   # moment de l'aire * y (pour le centroide en y)
    zmom = np.zeros(len(xs))   # moment de l'aire * z (pour le centroide en z)

    for i, poly in enumerate(polygones):
        immergee = decoupe_demi_plan(poly, a_coef, b_coef, c)
        aire, yc, zc = aire_centroide_polygone(immergee)
        aires[i] = aire
        ymom[i] = aire * yc
        zmom[i] = aire * zc

    volume = simpson(aires, xs)
    if volume <= 1e-9:
        return 0.0, 0.0, 0.0
    ybar = simpson(ymom, xs) / volume
    zbar = simpson(zmom, xs) / volume
    return volume, ybar, zbar


def _trouve_flottaison(carene, xs, polygones, phi, volume_cible, c_min, c_max):
    """
    Trouve par dichotomie le niveau d'eau c tel que le volume immerge soit egal
    au volume cible (celui du navire droit). Le volume croit avec c, donc la
    dichotomie converge proprement.
    """
    for _ in range(60):
        c = 0.5 * (c_min + c_max)
        vol, _, _ = _proprietes_immergees(carene, xs, polygones, phi, c)
        if vol < volume_cible:
            c_min = c
        else:
            c_max = c
    return 0.5 * (c_min + c_max)


def courbe_gz(carene, KG, volume_droit, angles_deg=None, n_stations=41, nz=81):
    """
    Calcule la courbe de stabilite GZ(theta).

    Parametres
    ----------
    carene       : objet Carene
    KG           : hauteur du centre de gravite (m)
    volume_droit : volume immerge du navire droit (m^3), a deplacement constant
    angles_deg   : liste des angles de gite a calculer (degres)
    n_stations   : nombre de sections le long de la coque (impair -> Simpson)
    nz           : finesse de discretisation de chaque section

    Retour
    ------
    dict avec les angles, la courbe GZ, et les indicateurs cles.
    """
    if angles_deg is None:
        angles_deg = np.arange(0, 81, 5)
    angles_deg = np.asarray(angles_deg, dtype=float)

    xs = carene.stations(n_stations)
    polygones = [carene.polygone_section(x, nz=nz) for x in xs]

    GZ = np.zeros(len(angles_deg))
    bras = []
    for k, ang in enumerate(angles_deg):
        phi = np.radians(ang)
        # bornes pour la dichotomie du niveau d'eau
        c = _trouve_flottaison(carene, xs, polygones, phi,
                               volume_droit, c_min=0.0, c_max=carene.D * 1.5)
        vol, ybar, zbar = _proprietes_immergees(carene, xs, polygones, phi, c)
        # Bras de redressement : distance horizontale (repere mer) entre B et G.
        # G est sur l'axe (y=0, z=KG). Coordonnee transversale "mer" d'un point :
        #   Y_mer = y*cos(phi) + z*sin(phi)
        GZ[k] = (ybar * np.cos(phi) + (zbar - KG) * np.sin(phi))

    res = {
        "angles_deg": angles_deg,
        "GZ": GZ,
    }
    res.update(_indicateurs_stabilite(angles_deg, GZ))
    return res


def gz_murailles_droites(angles_deg, GMt, BMt):
    """
    Courbe GZ approchee par la formule des murailles droites (wall-sided).
    Valable tant que le livet de pont n'est pas immerge et que le bouchain ne
    sort pas de l'eau (petits a moyens angles). Sert de verification.
        GZ = (GM + 0.5 * BM * tan^2(theta)) * sin(theta)
    """
    a = np.radians(np.asarray(angles_deg, dtype=float))
    return (GMt + 0.5 * BMt * np.tan(a) ** 2) * np.sin(a)


def _indicateurs_stabilite(angles_deg, GZ):
    """
    Extrait les indicateurs cles de la courbe GZ :
      - GZ maximal et l'angle correspondant
      - l'angle d'annulation (limite de stabilite statique)
      - la pente a l'origine (= GM theorique)
      - les aires sous la courbe a 30 et 40 degres (stabilite dynamique)
    """
    a_rad = np.radians(angles_deg)

    # GZ max
    imax = int(np.argmax(GZ))
    gz_max = GZ[imax]
    angle_gz_max = angles_deg[imax]

    # Angle d'annulation : la ou GZ repasse par 0 apres le max (interpolation)
    angle_annulation = None
    for i in range(imax, len(GZ) - 1):
        if GZ[i] >= 0 >= GZ[i + 1]:
            t = GZ[i] / (GZ[i] - GZ[i + 1])
            angle_annulation = angles_deg[i] + t * (angles_deg[i + 1] - angles_deg[i])
            break

    # Pente a l'origine -> GM (en utilisant les deux premiers points)
    if len(angles_deg) >= 2 and a_rad[1] > 0:
        gm_pente = GZ[1] / a_rad[1]
    else:
        gm_pente = float("nan")

    # Aires sous la courbe (en m.rad) jusqu'a 30 et 40 degres
    aire30 = _aire_jusqu_a(angles_deg, GZ, 30.0)
    aire40 = _aire_jusqu_a(angles_deg, GZ, 40.0)

    return {
        "gz_max": gz_max,
        "angle_gz_max": angle_gz_max,
        "angle_annulation": angle_annulation,
        "gm_pente": gm_pente,
        "aire_30deg": aire30,
        "aire_40deg": aire40,
    }


def _aire_jusqu_a(angles_deg, GZ, angle_max):
    """Aire sous la courbe GZ de 0 a angle_max (trapezes, en m.rad)."""
    a = np.radians(angles_deg)
    g = np.array(GZ, dtype=float)
    amax = np.radians(angle_max)
    # on tronque proprement a angle_max
    mask = angles_deg <= angle_max
    aa = list(a[mask])
    gg = list(g[mask])
    if angles_deg.max() >= angle_max and aa[-1] < amax:
        # interpolation du dernier point a angle_max
        i = np.searchsorted(a, amax)
        t = (amax - a[i - 1]) / (a[i] - a[i - 1])
        gg.append(g[i - 1] + t * (g[i] - g[i - 1]))
        aa.append(amax)
    return float(_trapeze(gg, aa))
