"""
carene.py
=========
Definition de la GEOMETRIE de la coque (la carene) de façon parametrique.

Idee cle : au lieu de dessiner une coque a la main, on la decrit par une
formule mathematique pilotee par quelques parametres principaux. Changer un
parametre (par ex. la largeur B) regenere instantanement toute la coque.

On s'inspire de la "carene de Wigley", une coque parabolique classique utilisee
dans la recherche en hydrodynamique navale. Elle est lisse, analytique, et donne
naturellement une coque FINE, typique d'une fregate (coefficient de bloc ~0.44).

Systeme de coordonnees
----------------------
  x : position longitudinale, de -L/2 (arriere) a +L/2 (avant)
  y : demi-largeur (transversale). La coque est symetrique : -y et +y.
  z : hauteur depuis la quille. z=0 a la quille, z=T a la flottaison,
      z=D au pont (depth = creux).
"""

import numpy as np


class Carene:
    """Une carene parametrique de type fregate."""

    def __init__(self, L=100.0, B=14.0, T=4.5, D=9.0, kp=1.0, kv=2.0):
        """
        Parametres principaux (les seuls "boutons" du modele) :
          L  : longueur entre perpendiculaires (m)
          B  : largeur maximale a la flottaison (m)
          T  : tirant d'eau de projet, profondeur immergee (m)
          D  : creux, hauteur quille -> pont (m). Le franc-bord vaut D - T.
          kp : exposant de finesse longitudinale (1 = parabole de Wigley).
               Plus c'est grand, plus les extremites (etrave/poupe) sont fines.
          kv : exposant de la distribution verticale (2 = Wigley).
               Controle la forme en U/V des sections.
        """
        self.L = L
        self.B = B
        self.T = T
        self.D = D
        self.kp = kp
        self.kv = kv

    def facteur_longitudinal(self, x):
        """
        P(x) : comment la largeur varie de l'arriere a l'avant.
        Vaut 1 au maitre-couple (x=0, section la plus large) et 0 aux
        extremites (x = +/- L/2). Forme parabolique.
        """
        x = np.asarray(x, dtype=float)
        base = 1.0 - (2.0 * x / self.L) ** 2
        base = np.clip(base, 0.0, None)   # pas de valeur negative hors coque
        return base ** self.kp

    def facteur_vertical(self, z):
        """
        V(z) : comment la largeur varie de la quille vers le pont.
          - sous la flottaison (z <= T) : forme parabolique de Wigley,
            largeur nulle a la quille (z=0), maximale a la flottaison (z=T).
          - au-dessus de la flottaison (T < z <= D) : flancs verticaux
            (coque "a murailles droites"). Hypothese simple et tres classique
            pour un premier calcul de stabilite.
        """
        z = np.asarray(z, dtype=float)
        sous_eau = 1.0 - ((self.T - z) / self.T) ** self.kv
        v = np.where(z <= self.T, sous_eau, 1.0)
        return np.clip(v, 0.0, None)

    def demi_largeur(self, x, z):
        """
        b(x, z) : demi-largeur de la coque a la position longitudinale x
        et a la hauteur z. C'est LA fonction qui definit toute la geometrie.
        """
        return (self.B / 2.0) * self.facteur_longitudinal(x) * self.facteur_vertical(z)

    # ------------------------------------------------------------------
    # Aides pour generer des grilles de points (stations, sections, maillage)
    # ------------------------------------------------------------------
    def stations(self, n=101):
        """n positions longitudinales reparties de -L/2 a +L/2."""
        return np.linspace(-self.L / 2.0, self.L / 2.0, n)

    def hauteurs(self, n=101, zmax=None):
        """n hauteurs de 0 (quille) a zmax (par defaut le pont D)."""
        if zmax is None:
            zmax = self.D
        return np.linspace(0.0, zmax, n)

    def polygone_section(self, x, nz=61):
        """
        Construit le contour ferme d'une section transversale a la position x,
        sous forme de polygone (liste de points (y, z)).

        Le contour fait le tour complet de la section :
          quille (0,0) -> remontee du flanc tribord -> traversee du pont ->
          descente du flanc babord -> retour quille.
        On ferme au pont (z=D) : on suppose la coque etanche jusqu'au pont,
        hypothese standard pour un calcul de stabilite (flottabilite intacte).
        """
        zs = np.linspace(0.0, self.D, nz)
        b = self.demi_largeur(x, zs)
        tribord = np.column_stack([b, zs])             # flanc +y, de la quille au pont
        babord = np.column_stack([-b[::-1], zs[::-1]])  # flanc -y, du pont a la quille
        return np.vstack([tribord, babord])
