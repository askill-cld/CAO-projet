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

## Importer la coque dans SolidWorks

Les fichiers exportés sont universels, donc le même projet se refait sous
SolidWorks sans rien changer au code. C'est le logiciel le plus reconnu en
bureau d'études, et il appartient à la même famille que CATIA (Dassault
Systèmes), l'outil de Naval Group.

### Voie A — Importer le maillage STL

1. **Ouvrir** → sélectionne `exports/carene.stl`.
2. Dans la boîte de dialogue, clique sur **Options** et choisis d'importer en
   tant que **corps graphique** ou **corps solide**, avec l'unité en **mètres**.
   Sans ça, SolidWorks interprète le fichier en millimètres et ta frégate fera
   10 cm de long.
3. Un corps STL est lourd et peu modifiable : garde cette voie pour visualiser
   et faire des rendus, pas pour travailler la géométrie.

### Voie B — Reconstruire par lissage à partir des couples (recommandé)

1. **Ouvrir** → `exports/sections.dxf`, en choisissant **Importer vers une
   nouvelle pièce** comme esquisse 2D.
2. Crée des **plans de référence parallèles** espacés de 10 m
   (Insertion → Géométrie de référence → Plan, avec un décalage).
3. Place une esquisse de couple sur chaque plan.
4. **Insertion → Bossage/Base → Lissage** : sélectionne les esquisses dans
   l'ordre, de la poupe vers l'étrave. Utilise l'atelier **Surfaces** si tu veux
   une peau de coque plutôt qu'un volume plein.
5. Ferme le pont et la quille, puis **Insertion → Surface → Épaissir** pour
   donner une épaisseur de bordé.

### Le vrai bonus : SolidWorks sait calculer une partie de ton hydrostatique

Une fois la coque en solide, **Outils → Évaluer → Propriétés de masse** te donne
le volume et la position du centre de gravité. Si tu coupes la coque au niveau
de la flottaison, tu obtiens le **volume immergé** et le **centre de carène**.

C'est un excellent exercice : compare ces valeurs à celles de ton code Python
(volume 2 800 m³, KB 2,81 m). Si elles concordent, tu as validé ton outil par
une troisième méthode, complètement indépendante. Ce serait un argument très
solide en entretien.

---

## Pour aller plus loin (phase 2, 2027)

- Ajouter de l'évasement de coque au-dessus de la flottaison.
- Coupler gîte et assiette.
- Estimer la résistance à l'avancement et la puissance moteur.
- Refaire l'étude pour un navire de soutien offshore (OSV).
