# Cours : Fusion 360 et concepts du projet

> Cours de référence pour Ayoub, lié au projet `fregate-hydrostatique`.
> À relire avant chaque session de modélisation ou de calcul.

---

# PARTIE 1 — Fusion 360

## 1. L'idée de base : la modélisation paramétrique

Fusion 360 est un logiciel de CAO (Conception Assistée par Ordinateur). Sa
philosophie : tu ne dessines pas une forme figée, tu décris une suite
d'opérations. Chaque opération est enregistrée dans une frise chronologique (la
**timeline**, en bas de l'écran). Si tu changes une cote au début, tout se
recalcule automatiquement jusqu'à la fin. C'est exactement la même logique que
ta carène paramétrique en Python : quelques paramètres pilotent toute la forme.

## 2. L'interface (les 5 zones à connaître)

1. **Le ruban (toolbar)** en haut : les outils, regroupés par **espaces de
   travail** (workspaces). Le menu déroulant en haut à gauche permet de passer
   de **Design** (modélisation) à **Render** (rendu réaliste), etc.
2. **Le navigateur (browser)** à gauche : l'arborescence de ton modèle
   (composants, corps, esquisses, plans, origine). Œil = afficher/masquer.
3. **La zone 3D** au centre : ton modèle.
4. **Le ViewCube** en haut à droite : le petit cube pour t'orienter (clique sur
   une face pour voir de face, de dessus, etc.).
5. **La timeline** en bas : l'historique de tes opérations, modifiable.

### Navigation (souris)
- **Orbiter** (tourner autour) : bouton du milieu + Maj, ou l'icône orbit.
- **Pan** (déplacer) : bouton du milieu enfoncé.
- **Zoom** : molette.
- Raccourci utile : touche **F6** pour "ajuster à l'écran".

## 3. Le flux de travail type

La très grande majorité des pièces se font ainsi :

```
Esquisse 2D  →  Opération 3D  →  Modifications  →  Corps / Composant
 (Sketch)       (Extrude, Revolve, Loft...)   (Fillet, Shell, Scale...)
```

- **Esquisse (Sketch)** : un dessin 2D sur un plan. Tu traces des lignes, des
  arcs, des splines, et tu les contraints (dimensions, parallélisme, etc.).
  Un profil **fermé** peut ensuite devenir un volume.
- **Opérations 3D** : transforment le 2D en 3D.
  - **Extrude** : pousser un profil en ligne droite (un mur, une plaque).
  - **Revolve** : faire tourner un profil autour d'un axe (un arbre, un bol).
  - **Loft (Lissage)** : relier plusieurs profils étagés par une surface lisse.
    **C'est l'opération clé pour une coque** : on lisse entre les couples.
  - **Sweep** : balayer un profil le long d'un chemin.

## 4. Les outils utiles pour TA coque

- **Plans de construction décalés** (Construct → Offset Plane) : pour placer
  chaque couple à sa position longitudinale (espacement 10 m dans ton cas).
- **Loft / Lissage** (Create → Loft) : sélectionne les esquisses de couples dans
  l'ordre, Fusion génère la carène.
- **Surface vs Solide** : une coque est d'abord une **surface** (une peau sans
  épaisseur). L'atelier **Surface** est souvent plus adapté pour lisser des
  formes de coque, puis on **épaissit** (Thicken) pour donner un bordé.
- **Insert Mesh** (Insertion → Maillage) : importer ton `carene.stl`. Pense à
  régler l'unité sur **mètre**.
- **Insert DXF** : importer `sections.dxf` comme esquisses à lofter.
- **Scale (Échelle)** (Modify → Scale) : si l'import arrive trop petit, applique
  un facteur 1000 (passage mm → m).

## 5. Corps (Bodies) vs Composants (Components)

- **Corps** = une masse de matière.
- **Composant** = une "pièce" autonome (avec son origine), qui peut contenir
  plusieurs corps et s'assembler avec d'autres. Bonne pratique : crée un
  composant pour ta coque dès le départ.

## 6. Raccourcis clavier à retenir

| Raccourci | Action |
|---|---|
| `L` | Ligne (dans une esquisse) |
| `D` | Cote / Dimension |
| `E` | Extrude |
| `S` | Menu de recherche d'outils (très pratique au début) |
| `F6` | Ajuster à l'écran |
| `Ctrl + Z` | Annuler |

## 7. Procédure pas à pas pour ta coque (rappel)

Voir `GUIDE_REFAIRE.md`, section "Importer la coque dans Fusion 360".
Voie rapide = STL. Voie pédagogique = import DXF + Loft entre couples.

---

# PARTIE 2 — Les concepts du projet

## 1. Le vocabulaire de la coque

- **Carène** : la partie immergée de la coque (sous la flottaison).
- **Ligne de flottaison** : la ligne où la surface de l'eau coupe la coque.
- **Tirant d'eau (T)** : hauteur immergée, de la quille à la flottaison.
- **Creux (D)** : hauteur totale, de la quille au pont.
- **Franc-bord** : la réserve hors d'eau, D − T. Clé pour la stabilité aux
  grands angles.
- **Maître-couple** : la section transversale la plus large (au milieu).
- **Couples** : les sections transversales (comme des tranches du navire).
- **Lignes d'eau** : les sections horizontales (à différentes hauteurs).
- **Table des cotes (offsets)** : le tableau des demi-largeurs par couple et par
  ligne d'eau. C'est la "carte d'identité" géométrique de la coque.

## 2. La flottabilité (Archimède)

Un corps immergé reçoit une poussée verticale vers le haut égale au poids du
volume d'eau déplacé. À l'équilibre :

```
Poids du navire  =  Poussée  =  ρ × ∇ × g
```

- `∇` (nabla) : le volume immergé (m³).
- `ρ` : masse volumique de l'eau (1.025 t/m³ en mer).
- **Déplacement** `Δ = ρ × ∇` : c'est la masse du navire (en tonnes). Dans ton
  projet : ∇ = 2800 m³ → Δ = 2870 t.

## 3. Les deux points qui gouvernent tout : B et G

- **G, centre de gravité** : le point où s'applique le poids. Sa hauteur au
  dessus de la quille est **KG** (donnée de chargement : 5.4 m dans ton projet).
- **B, centre de carène** : le centre géométrique du volume immergé, là où
  s'applique la poussée. Sa hauteur est **KB** (2.81 m chez toi).

Quand le navire est droit, B et G sont sur le même axe vertical. Quand il gîte,
B se déplace (la forme immergée change), pas G. Ce décalage crée le couple de
redressement.

## 4. Les coefficients de forme

Ils décrivent la finesse de la coque (entre 0 et 1) :

- **Cb (bloc)** : volume / (L×B×T). Mesure le "remplissage". 0.44 chez toi =
  coque fine, typique d'une frégate rapide. Un pétrolier serait à ~0.8.
- **Cm (maître-couple)** : aire de la section max / (B×T).
- **Cp (prismatique)** : volume / (aire max × L). Décrit la répartition du
  volume sur la longueur.
- **Cw (flottaison)** : aire du plan de flottaison / (L×B).

## 5. La stabilité initiale : le métacentre et GM

Quand le navire gîte d'un petit angle, la verticale de la poussée recoupe l'axe
du navire en un point appelé **métacentre M**.

- **BM (rayon métacentrique)** = `I / ∇`, où `I` est l'inertie transversale du
  plan de flottaison. Plus le navire est large, plus I est grand, plus il est
  stable. Chez toi BM = 3.73 m.
- **KM = KB + BM** : hauteur du métacentre (6.55 m).
- **GM = KM − KG** : la **hauteur métacentrique**, LE critère de stabilité
  initiale (1.15 m chez toi).

Interprétation de GM :
- **GM > 0** : navire stable (il revient quand on l'incline). 
- **GM < 0** : navire instable (il chavire). 
- **GM grand** : très raide, roulis rapide et inconfortable.
- **GM petit (mais positif)** : roulis doux. Sur un navire militaire on cherche
  un compromis. 1.15 m est une valeur saine.

## 6. La stabilité à grands angles : la courbe GZ

Aux grands angles, le métacentre ne suffit plus. On utilise le **bras de
redressement GZ** : la distance horizontale entre la verticale du poids (par G)
et celle de la poussée (par B), quand le navire est incliné de θ.

- Le **moment de redressement** = `Δ × GZ`. Plus GZ est grand, plus le navire
  résiste au chavirement.
- La **courbe GZ(θ)** est la signature de stabilité du navire. On y lit :
  - la **pente à l'origine = GM** (lien direct avec la stabilité initiale),
  - le **GZ max** (0.59 m à 45° chez toi) : le moment de redressement maximal,
  - l'**angle d'annulation** (83°) : au-delà, le navire chavire,
  - l'**aire sous la courbe** : la stabilité dynamique (énergie nécessaire pour
    chavirer). Les règlements (OMI) fixent des minima sur ces aires.

## 7. La méthode de Simpson (le calcul numérique)

Pour obtenir ∇, KB, I, etc., il faut **intégrer** la géométrie. Comme la coque
n'a pas de formule d'intégrale simple, on intègre numériquement.

La méthode de Simpson approche la courbe à intégrer par des **paraboles** sur des
paires d'intervalles, ce qui est bien plus précis que des trapèzes :

```
∫ f dx  ≈  (h/3) × [ f₀ + 4f₁ + 2f₂ + 4f₃ + ... + 4f_{N-1} + f_N ]
```

Pondérations : 1 aux extrémités, 4 aux points impairs, 2 aux points pairs
intérieurs. Contrainte : un nombre **pair** d'intervalles. C'est la méthode
historique des architectes navals (le "calcul par les couples").

## 8. Comment tout se relie dans ton code

| Concept | Fichier | Fonction |
|---|---|---|
| Géométrie b(x,z) | `carene.py` | `demi_largeur` |
| Intégration | `outils.py` | `simpson` |
| ∇, Δ, KB, GM | `hydrostatique.py` | `calcul_hydrostatique` |
| Courbe GZ | `stabilite.py` | `courbe_gz` |
| Export Fusion | `exports.py` | `export_stl`, `export_dxf_sections` |

---

## Pour réviser : les 7 nombres clés de ton navire

| Symbole | Valeur | Sens |
|---|---|---|
| Δ | 2870 t | déplacement (masse) |
| Cb | 0.444 | finesse (coque fine) |
| KB | 2.81 m | centre de carène |
| BM | 3.73 m | rayon métacentrique |
| GM | 1.15 m | stabilité initiale (>0 = stable) |
| GZ max | 0.59 m à 45° | redressement maximal |
| Limite | 83° | angle de chavirement |
