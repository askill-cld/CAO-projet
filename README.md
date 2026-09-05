# Carène de frégate — Outil d'hydrostatique et de stabilité

Outil d'architecture navale développé en Python : il génère une **carène de
frégate paramétrique**, calcule son **hydrostatique** (déplacement, centre de
carène, hauteur métacentrique GM) et trace sa **courbe de stabilité GZ(θ)**, puis
exporte la coque vers la CAO (Fusion 360 / SolidWorks).

> Projet personnel d'Ayoub — Licence Physique CUPGE (UBS Lorient).
> Objectif : projet personnel d'architecture navale pour candidature en école
> d'ingénieur (ENSTA, Centrale Nantes) et contacts industriels (Naval Group).

---

## Ce que fait le programme

1. Définit une carène de frégate par quelques paramètres (L, B, T, D).
2. Calcule toute l'hydrostatique du navire droit par la **méthode de Simpson**.
3. Calcule la **courbe de stabilité GZ(θ)** par intégration directe du volume
   immergé incliné, à déplacement constant.
4. Valide le calcul de deux façons indépendantes (GM par l'hydrostatique vs GM
   par la pente de la courbe GZ, et formule des murailles droites).
5. Génère 4 graphiques et 3 fichiers CAO.

## Résultats principaux (frégate L=100 m)

| Grandeur | Valeur |
|---|---|
| Déplacement | 2 870 t |
| Coefficient de bloc Cb | 0.444 (coque fine, typique frégate) |
| KB (centre de carène) | 2.81 m |
| BMt (rayon métacentrique) | 3.73 m |
| **GMt (hauteur métacentrique)** | **1.15 m** (stabilité initiale positive) |
| GZ max | 0.59 m à 45° |
| Limite de stabilité | 83° |

## Lancer le projet

```bash
pip install -r requirements.txt
python main.py
```

Tout est régénéré : `figures/`, `exports/`, et `resultats.json`.

## Structure du code

| Fichier | Rôle |
|---|---|
| `carene.py` | Géométrie paramétrique de la coque |
| `outils.py` | Méthode de Simpson + géométrie des polygones |
| `hydrostatique.py` | Hydrostatique du navire droit |
| `stabilite.py` | Courbe de stabilité GZ(θ) à grands angles |
| `exports.py` | Export STL, DXF, table des cotes |
| `graphiques.py` | Génération des figures |
| `main.py` | Orchestration de tout le projet |

| Dossier | Contenu |
|---|---|
| `figures/` | Plan des formes, courbe des aires, vue 3D, courbe GZ |
| `exports/` | `carene.stl`, `sections.dxf`, `table_des_cotes.csv` |

## Documentation

- `RAPPORT.md` : le rapport technique (théorie, méthode, résultats).
- `COURS.md` : cours sur les concepts d'architecture navale mobilisés et sur
  la prise en main de Fusion 360.
- `GUIDE_REFAIRE.md` : guide pas à pas pour reconstruire le projet soi-même
  et importer la coque dans Fusion 360.

## Genèse du projet et usage de l'IA

Par souci de transparence : **ce projet a été développé avec l'assistance de
Claude (Anthropic)**, et l'historique Git en porte la trace.

La répartition est la suivante. J'ai défini le sujet, le type de navire, ses
paramètres principaux et le périmètre technique retenu ; l'assistant a écrit
l'implémentation Python et la documentation. L'import et l'exploitation de la
géométrie dans Fusion 360 sont de mon fait.

Le dépôt contient délibérément un guide de reconstruction (`GUIDE_REFAIRE.md`)
et un cours sur les concepts mobilisés (`COURS.md`) : la finalité de ce projet
est avant tout pédagogique, et mon objectif est de réimplémenter l'outil
moi-même, module par module, afin d'en maîtriser chaque étape.

## Limites et pistes d'amélioration (phase 2)

- Coque à murailles droites au-dessus de la flottaison (pas de tonture ni de
  quête réaliste). Amélioration : ajouter de l'évasement.
- Stabilité calculée en gîte pure (pas d'assiette libre couplée).
- À ajouter ensuite : estimation de la résistance à l'avancement et de la
  puissance moteur ; étude d'un navire de soutien offshore (OSV).
