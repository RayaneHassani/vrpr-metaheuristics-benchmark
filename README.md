# VRPR — Vehicle Routing Problem with Restricted edges

> **EN — TL;DR.** Operations Research project (group G3). We solve a multi-vehicle
> routing problem on a road network with **forbidden roads** (impassable edges)
> and **surcharged roads** (more expensive edges). Starting from a depot, every
> client must be visited exactly once while minimising total travel cost. The
> repo provides an instance generator, a greedy (GRASP) initialiser and four
> metaheuristics — **multi-start greedy, tabu search, simulated annealing and a
> genetic algorithm** — together with an OFAT experimental comparison. Full
> write-up (formal model + results) is in [`notebooks/final_nb.ipynb`](notebooks/final_nb.ipynb);
> reusable code is in [`src/vrpr/`](src/vrpr).

---

## Présentation

Ce projet de **Recherche Opérationnelle** modélise et résout une variante du
**problème de tournées de véhicules (VRP)**. Une flotte de véhicules part d'un
**dépôt** (sommet `0`), dessert un ensemble de clients et revient au dépôt. On
cherche la planification qui **minimise le coût total** des déplacements.

Deux contraintes métier s'ajoutent au VRP classique — d'où le nom **VRPR**
(*VRP with Restricted edges*) :

- **Routes fermées** : certaines arêtes sont impraticables (`close = True`).
- **Routes à surcoût** : certaines arêtes restent praticables mais coûtent plus
  cher (`surcout = True`).

## 1. Modèle formel

**Données.** Graphe `G = (V, E)`, dépôt `0`, ensemble de clients `C = V \ {0}`,
flotte `K`, coût `c_ij` sur chaque arête, ensemble `F ⊂ E` des arêtes interdites.

**Variables de décision.**

```
x_ijk = 1 si le véhicule k emprunte l'arête (i, j), 0 sinon
```

**Fonction objectif.** Minimiser le coût total :

```
min  Σ_i Σ_j Σ_k  c_ij · x_ijk
```

**Contraintes.**

| # | Description | Formulation |
|---|-------------|-------------|
| C1 | Chaque client visité une seule fois | `Σ_k Σ_{j≠i} x_ijk = 1   ∀ i ∈ C` |
| C2 | Conservation du flot | `Σ_j x_jik = Σ_j x_ijk   ∀ i ∈ C, ∀ k ∈ K` |
| C3 | Départ du dépôt | `Σ_{j∈C} x_0jk = 1   ∀ k ∈ K` |
| C4 | Retour au dépôt | `Σ_{i∈C} x_i0k = 1   ∀ k ∈ K` |
| C5 | Arêtes interdites | `x_ijk = 0   ∀ (i, j) ∈ F` |

Dans le code, **C5 est intégrée à la fonction de coût** : toute solution
empruntant une arête fermée reçoit un coût infini et est donc écartée.

## 2. Complexité

Le VRP **généralise le problème du voyageur de commerce (TSP)** et est donc
**NP-difficile**. Une résolution exacte est hors de portée au-delà de petites
instances : on a recours à des **métaheuristiques** fournissant de bonnes
solutions approchées en temps raisonnable.

## 3. Approche

1. **Générateur d'instances** (`graph.py`) — réseau routier aléatoire (k plus
   proches voisins ou graphe complet) avec routes fermées et surcoûts.
2. **Solution initiale gloutonne / GRASP** (`greedy.py`) — construction
   round-robin, randomisée par une *restricted candidate list* (`k_rcl`).
3. **Métaheuristiques** :
   - **Recherche tabou** (`tabu.py`) — mémoire courte + critère d'aspiration.
   - **Recuit simulé** (`annealing.py`) — acceptation probabiliste, refroidissement géométrique.
   - **Algorithme génétique** (`genetic.py`) — élitisme, sélection par tournoi, *Ordered Crossover*, mutation.
4. **Plan d'expérience OFAT** (`experiments.py`) — calibrage des paramètres et
   comparaison des approches sur des instances de tailles croissantes.

## Structure du dépôt

```
.
├── README.md
├── requirements.txt
├── LICENSE
├── main.py                  # démo : lance les 4 approches sur une instance
├── notebooks/
│   └── final_nb.ipynb       # livrable : modèle, implémentation, résultats
└── src/vrpr/                # code réutilisable (extrait du notebook)
    ├── graph.py             # générateur d'instances + affichage
    ├── core.py              # coût d'une solution + voisinage
    ├── greedy.py            # glouton / GRASP + multi-start
    ├── tabu.py              # recherche tabou + multi-start
    ├── annealing.py         # recuit simulé + multi-start
    ├── genetic.py           # algorithme génétique
    └── experiments.py       # plan d'expérience & comparaison
```

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

**Notebook (livrable complet) :**

```bash
jupyter notebook notebooks/final_nb.ipynb
```

**Démo en ligne de commande :**

```bash
python main.py
```

**Depuis Python :**

```python
import sys; sys.path.insert(0, "src")
from vrpr import random_graph, multi_start_tabou

G = random_graph(40, k_voisins=3, complet=True)
meilleure, historiques, couts = multi_start_tabou(
    G, nb_restarts=5, taille_tabou=20, iter_max=50, vehicule=3, k_rcl=5
)
print("meilleur coût :", min(couts))
```

**Comparaison des approches :**

```bash
python -m vrpr.experiments        # depuis le dossier src/
```

## Auteurs

**Projet RO — Groupe 3 (G3)**

- Rayane Hassani
- Antonin Mignot-Pilon
- Michée Gondoué Kpan
- _(à compléter)_

> _Liste dérivée des contributeurs Git — corrigez/complétez les noms si besoin._

## Références

- Clarke, G., & Wright, J. W. (1964). *Scheduling of Vehicles from a Central
  Depot to a Number of Delivery Points.* Operations Research, 12(4), 568–581.
- Glover, F., & Laguna, M. (1997). *Tabu Search.* Kluwer Academic Publishers.

## Licence

MIT — voir [`LICENSE`](LICENSE).
