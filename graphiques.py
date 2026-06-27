"""
graphiques.py
=============
Genere les figures du projet (enregistrees en PNG dans figures/).

  1. Plan des formes (body plan) : les sections vues de face.
  2. Courbe des aires de section A(x).
  3. Vue 3D de la coque.
  4. Courbe de stabilite GZ(theta) avec les points cles.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # pas d'affichage interactif, on enregistre des fichiers
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (active la 3D)


def plan_des_formes(carene, chemin, n_sections=11, nz=81):
    """Body plan : couples avant a droite, couples arriere a gauche."""
    fig, ax = plt.subplots(figsize=(7, 6))
    xs = np.linspace(-carene.L / 2.0, carene.L / 2.0, n_sections)
    zs = np.linspace(0.0, carene.D, nz)
    for x in xs:
        b = carene.demi_largeur(x, zs)
        cote = 1.0 if x >= 0 else -1.0   # avant a droite, arriere a gauche
        ax.plot(cote * b, zs, color="#1f4e79", lw=1.0)
    ax.axhline(carene.T, color="#c00000", ls="--", lw=1.2, label="Flottaison (T)")
    ax.axvline(0, color="0.6", lw=0.8)
    ax.set_xlabel("Demi-largeur y (m)   [arriere | avant]")
    ax.set_ylabel("Hauteur z (m)")
    ax.set_title("Plan des formes (couples)")
    ax.legend(loc="lower right")
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(chemin, dpi=130)
    plt.close(fig)


def courbe_aires(res, chemin):
    """Courbe des aires de section immergee A(x)."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(res["xs"], res["A_x"], color="#1f4e79", lw=2)
    ax.fill_between(res["xs"], res["A_x"], alpha=0.15, color="#1f4e79")
    ax.set_xlabel("Position longitudinale x (m)")
    ax.set_ylabel("Aire de section immergee (m2)")
    ax.set_title("Courbe des aires de section")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(chemin, dpi=130)
    plt.close(fig)


def vue_3d(carene, chemin, nx=60, nz=30):
    """Vue 3D de la surface de coque."""
    xs = np.linspace(-carene.L / 2.0, carene.L / 2.0, nx)
    zs = np.linspace(0.0, carene.D, nz)
    X, Z = np.meshgrid(xs, zs)
    Y = np.array([[carene.demi_largeur(x, z) for x in xs] for z in zs])

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(X, Y, Z, color="#1f4e79", alpha=0.95,
                    rstride=1, cstride=2, edgecolor="#16365c", linewidth=0.15)
    ax.plot_surface(X, -Y, Z, color="#2e75b6", alpha=0.95,
                    rstride=1, cstride=2, edgecolor="#16365c", linewidth=0.15)
    ax.set_xlabel("x (m)  longueur")
    ax.set_ylabel("y (m)  largeur")
    ax.set_zlabel("z (m)  hauteur")
    ax.set_title("Carene 3D (fregate)")
    # proportions accentuees en largeur/hauteur pour bien voir la forme
    try:
        ax.set_box_aspect((carene.L, carene.B * 4, carene.D * 4))
    except Exception:
        pass
    ax.view_init(elev=26, azim=-50)   # vue 3/4 lisible
    fig.tight_layout()
    fig.savefig(chemin, dpi=130)
    plt.close(fig)


def courbe_gz(res_gz, chemin, res_ws=None):
    """Courbe de stabilite GZ(theta) avec annotations des points cles."""
    ang = res_gz["angles_deg"]
    gz = res_gz["GZ"]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(ang, gz, color="#1f4e79", lw=2.2, label="GZ (calcul direct)")
    if res_ws is not None:
        # La formule des murailles droites n'est valable qu'aux angles moderes
        # (son terme tan^2 diverge). On ne la trace que jusqu'a 40 degres.
        masque = ang <= 40
        ax.plot(ang[masque], np.asarray(res_ws)[masque], color="#c00000",
                ls="--", lw=1.4, label="GZ (murailles droites, <40 deg)")
    ax.axhline(0, color="0.5", lw=0.8)
    # echelle verticale basee sur la courbe reelle
    ax.set_ylim(min(0, gz.min()) - 0.05, gz.max() * 1.25)

    # point de GZ max
    ax.plot(res_gz["angle_gz_max"], res_gz["gz_max"], "o", color="#c00000")
    ax.annotate(f"GZ max = {res_gz['gz_max']:.3f} m\na {res_gz['angle_gz_max']:.0f} deg",
                xy=(res_gz["angle_gz_max"], res_gz["gz_max"]),
                xytext=(res_gz["angle_gz_max"] + 3, res_gz["gz_max"] * 0.6),
                fontsize=9)

    # tangente a l'origine = GM
    gm = res_gz["gm_pente"]
    a_petit = np.array([0, 15])
    ax.plot(a_petit, gm * np.radians(a_petit), ":", color="green", lw=1.4,
            label=f"Pente initiale = GM = {gm:.2f} m")

    if res_gz["angle_annulation"] is not None:
        ax.axvline(res_gz["angle_annulation"], color="0.7", ls=":")
        ax.annotate(f"Limite de stabilite\n{res_gz['angle_annulation']:.0f} deg",
                    xy=(res_gz["angle_annulation"], 0),
                    xytext=(res_gz["angle_annulation"] - 18, gz.max() * 0.15),
                    fontsize=9)

    ax.set_xlabel("Angle de gite theta (degres)")
    ax.set_ylabel("Bras de redressement GZ (m)")
    ax.set_title("Courbe de stabilite GZ(theta)")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(chemin, dpi=130)
    plt.close(fig)
