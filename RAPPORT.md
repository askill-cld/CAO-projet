# Rapport technique — Hydrostatique et stabilité d'une carène de frégate

**Auteur :** Ayoub — Licence Physique CUPGE, UBS Lorient
**Date :** juin 2026

---

## 1. Objectif

Concevoir une carène de frégate de façon paramétrique, puis calculer par le code
ses caractéristiques hydrostatiques et sa stabilité transversale. Le but est de
montrer la maîtrise du lien entre **physique** (poussée d'Archimède, moments,
stabilité), **géométrie** (génération de la coque) et **programmation** (calcul
numérique par la méthode de Simpson).

## 2. Modèle géométrique

La coque est décrite par une fonction de demi-largeur :

```
b(x, z) = (B/2) · P(x) · V(z)
```

- `P(x) = (1 − (2x/L)²)^kp` : affinement longitudinal (1 au maître-couple, 0 aux
  extrémités). Forme parabolique de type carène de Wigley.
- `V(z)` : distribution verticale, parabolique sous la flottaison
  (`1 − ((T−z)/T)²`), murailles droites au-dessus.

Paramètres retenus pour la frégate :

| Paramètre | Symbole | Valeur |
|---|---|---|
| Longueur entre perpendiculaires | L | 100 m |
| Largeur à la flottaison | B | 14 m |
| Tirant d'eau de projet | T | 4.5 m |
| Creux (quille → pont) | D | 9 m |
| Centre de gravité (chargement) | KG | 5.4 m |

## 3. Méthode de calcul

### 3.1 Intégration par Simpson

Toutes les intégrales (volumes, aires, moments) sont calculées par la **méthode
de Simpson composite**, qui approche la courbe par des paraboles :

```
∫ f dx ≈ (h/3) · [f₀ + 4(f₁+f₃+…) + 2(f₂+f₄+…) + f_N]
```

C'est la méthode de référence des architectes navals (calcul sur les couples).

### 3.2 Hydrostatique du navire droit

- **Courbe des aires** `A(x)` : aire immergée de chaque section.
- **Volume immergé** `∇ = ∫ A(x) dx` ; **déplacement** `Δ = ρ·∇` (ρ = 1.025 t/m³).
- **Centre de carène** : `LCB` (longitudinal) et `KB` (vertical), barycentres du
  volume immergé.
- **Plan de flottaison** : aire `Aw`, centre `LCF`, inertie transversale
  `It = ∫ (2/3)·b³ dx`.
- **Métacentre** : `BMt = It/∇`, `KMt = KB + BMt`, et la grandeur clé
  **`GMt = KMt − KG`**.

### 3.3 Stabilité à grands angles (courbe GZ)

Pour chaque angle de gîte θ :

1. La surface de l'eau devient, dans le repère du navire incliné, la droite
   `z·cosθ − y·sinθ = c`.
2. On cherche par dichotomie le niveau `c` qui conserve le volume immergé égal à
   celui du navire droit (déplacement constant).
3. On calcule le nouveau centre de carène B (centroïde du volume immergé), par
   découpe des sections (algorithme de Sutherland-Hodgman) et formule du lacet.
4. Le bras de redressement vaut :
   `GZ(θ) = ȳ_B·cosθ + (z̄_B − KG)·sinθ`.

## 4. Résultats

### 4.1 Hydrostatique

| Grandeur | Valeur | Commentaire |
|---|---|---|
| Volume immergé ∇ | 2 800 m³ | |
| Déplacement Δ | 2 870 t | cohérent pour une frégate de 100 m |
| KB | 2.81 m | centre de carène |
| Aire de flottaison Aw | 933 m² | |
| It | 10 453 m⁴ | inertie transversale |
| BMt | 3.73 m | rayon métacentrique |
| KMt | 6.55 m | hauteur du métacentre |
| **GMt** | **1.15 m** | **stabilité initiale positive** |
| Cb | 0.444 | coque fine, typique d'une frégate |
| Cm | 0.667 | coefficient de maître-couple |
| Cp | 0.667 | coefficient prismatique |
| Cw | 0.667 | coefficient de flottaison |
| TPC | 9.57 t/cm | tonnes par cm d'enfoncement |

### 4.2 Stabilité

| Indicateur | Valeur |
|---|---|
| GZ maximal | 0.59 m |
| Angle du GZ max | 45° |
| Limite de stabilité statique | 83° |
| Aire sous GZ à 30° | 0.134 m·rad |
| Aire sous GZ à 40° | 0.226 m·rad |

### 4.3 Validation

Le calcul est validé de deux manières indépendantes :

- **GM par l'hydrostatique** = 1.146 m **vs GM par la pente de la courbe GZ** à
  l'origine = 1.131 m. Écart < 1.5 % : les deux approches concordent.
- La **formule des murailles droites** `GZ = (GM + ½·BM·tan²θ)·sinθ` coïncide
  avec le calcul direct aux petits angles, puis diverge au-delà (limite connue
  de cette formule), ce qui confirme le comportement attendu.

## 5. Interprétation physique

- Un **GMt positif (1.15 m)** garantit la stabilité initiale : écarté de sa
  position droite, le navire revient.
- Le GM modéré (et non excessif) évite un roulis trop "raide", ce qui est
  recherché sur un navire militaire pour le confort et la tenue des systèmes.
- La **plage de stabilité jusqu'à 83°** indique une bonne réserve de stabilité
  aux grands angles, apportée par le franc-bord (D − T = 4.5 m).

## 6. Limites

- Coque à murailles droites au-dessus de la flottaison (pas d'évasement réaliste).
- Gîte pure, sans couplage à l'assiette.
- Pas de calcul de résistance/puissance (prévu en phase 2).

## 7. Figures

1. `figures/1_plan_des_formes.png` — plan des formes (couples).
2. `figures/2_courbe_des_aires.png` — courbe des aires de section.
3. `figures/3_vue_3d.png` — vue 3D de la carène.
4. `figures/4_courbe_gz.png` — courbe de stabilité GZ(θ).
