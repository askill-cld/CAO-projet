# Guide pas à pas — Refaire le projet toi-même

Ce guide te fait reconstruire le projet de zéro. Le code des fichiers `.py` est
ta **correction** : essaie d'abord, puis compare. Chaque étape correspond à un
module du projet.

---

## Étape 0 — Préparer l'environnement

```bash
python -m pip install numpy matplotlib
```

Crée un dossier de projet et travaille dedans. Lance `python main.py` à la fin
de chaque étape pour vérifier au fur et à mesure.

## Étape 1 — La méthode de Simpson (`outils.py`)

C'est la brique de base. Écris une fonction `simpson(f, x)` qui intègre un
tableau de valeurs.

- Rappel de la formule : `(h/3)·[f₀ + 4·(impairs) + 2·(pairs intérieurs) + f_N]`.
- Contrainte : nombre **pair** d'intervalles (nombre impair de points).
- Teste-la sur une fonction connue : `∫₀¹ x² dx = 1/3`. Tu dois retrouver 0.333.

## Étape 2 — La géométrie de la coque (`carene.py`)

Écris une classe `Carene(L, B, T, D)` avec la fonction de demi-largeur :

```
b(x, z) = (B/2) · P(x) · V(z)
```

- `P(x) = (1 − (2x/L)²)` : pense à couper les valeurs négatives (hors coque).
- `V(z)` : `1 − ((T−z)/T)²` sous la flottaison, `1` au-dessus.
- Vérifie à la main : au maître-couple (x=0) et à la flottaison (z=T), tu dois
  trouver `b = B/2`. À la quille (z=0), `b = 0`.

## Étape 3 — L'hydrostatique droite (`hydrostatique.py`)

Dans l'ordre, en intégrant par Simpson :

1. La courbe des aires `A(x)` (intègre `2·b` sur la hauteur immergée 0→T).
2. Le volume `∇ = ∫ A dx`, le déplacement `Δ = ρ·∇`.
3. `KB` (intègre `z·2·b`), `LCB` (intègre `x·A`).
4. Le plan de flottaison : `Aw`, `LCF`, puis `It = ∫ (2/3)·b³ dx`.
5. `BMt = It/∇`, `KMt = KB + BMt`, `GMt = KMt − KG`.

Repère de validation : tu dois retrouver `Cb ≈ 0.44`, `Δ ≈ 2870 t`,
`GMt ≈ 1.15 m`. Si c'est le cas, ton hydrostatique est juste.

## Étape 4 — La courbe de stabilité (`stabilite.py`)

La partie la plus exigeante. Pour chaque angle θ :

1. Représente chaque section comme un **polygone fermé** (`polygone_section`).
2. Découpe le polygone par la droite de flottaison inclinée
   `z·cosθ − y·sinθ = c` (algorithme de Sutherland-Hodgman).
3. Calcule l'aire et le centroïde immergés (formule du lacet).
4. Trouve `c` par **dichotomie** pour conserver le volume du navire droit.
5. `GZ(θ) = ȳ_B·cosθ + (z̄_B − KG)·sinθ`.

**Test de validation indispensable** : la pente de ta courbe GZ à l'origine doit
être égale à GM (≈ 1.15 m). Si oui, ta géométrie et tes signes sont corrects.

## Étape 5 — Les graphiques (`graphiques.py`)

Avec matplotlib : plan des formes, courbe des aires, vue 3D, et la courbe GZ.
Astuce : pour la courbe GZ, n'affiche la formule des murailles droites que
jusqu'à 40° (au-delà elle diverge).

## Étape 6 — Les exports CAO (`exports.py`)

- **STL** : maille la surface `y = ±b(x,z)` en triangles + un pont pour fermer.
- **DXF** : une polyligne fermée par section (couple).
- **CSV** : la table des cotes (demi-largeurs par station et ligne d'eau).

---

## Importer la coque dans Fusion 360

Tu as deux voies. La voie B est la plus pédagogique.

### Voie A — Importer le maillage STL (rapide)

1. Fusion 360 → menu **Insertion** → **Insérer un maillage**.
2. Choisis `exports/carene.stl`. Règle l'unité sur le **mètre**.
3. Le maillage apparaît. Pour le convertir en solide : clic droit sur le corps
   maillé → **Convertir un maillage** (BRep). Utile pour des rendus propres.

### Voie B — Reconstruire par loft à partir des sections (recommandé)

1. Fusion 360 → **Insertion** → **Insérer un DXF**.
2. Choisis `exports/sections.dxf`. Chaque couple devient une esquisse.
3. Place les esquisses aux bonnes positions longitudinales (l'espacement entre
   couples = L / (nombre de couples − 1) = 100/10 = 10 m).
4. Outil **Lissage / Loft** (atelier Surface ou Solide) : sélectionne les
   esquisses dans l'ordre de l'avant vers l'arrière. Fusion génère la coque.
5. Ferme le pont et la quille, puis épaissis si tu veux une coque réaliste.

Cette voie t'apprend le vrai geste de l'architecte naval : dessiner les couples,
puis lisser la carène entre eux.

---

## Pour aller plus loin (phase 2, 2027)

- Ajouter de l'évasement de coque au-dessus de la flottaison.
- Coupler gîte et assiette.
- Estimer la résistance à l'avancement et la puissance moteur.
- Refaire l'étude pour un navire de soutien offshore (OSV).
