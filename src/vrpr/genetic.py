"""Genetic algorithm for the VRPR problem.

A chromosome is a list of ``num_vehicles`` routes covering every client once.
Selection is elitist + tournament, crossover is Ordered Crossover (OX) on the
flattened genome, and mutation swaps two clients between two vehicles. Infeasible
children (using a closed edge) are rejected via an infinite fitness.
"""

import random

import numpy as np


def genetic_algorithm_vrp_advanced(G, num_vehicles, pop_size=50, generations=100, taux_mutation=0.2):
    # Vérification de la faisabilité : chaque véhicule doit pouvoir sortir et revenir au dépôt (nœud 0)
    if G.degree(0) < num_vehicles * 2:
        raise ValueError(f"Problème insoluble : Le dépôt a un degré de {G.degree(0)}, "
                         f"mais il faut au moins {num_vehicles * 2} arêtes pour {num_vehicles} véhicules.")

    nodes = [n for n in G.nodes if n != 0]

    def get_edge_cost(u, v):
        if not G.has_edge(u, v) or G[u][v].get('close', False):
            return float('inf')
        return G[u][v].get('cout', 1)

    def fitness(individual):
        total_cost = 0
        for route in individual:
            if not route:
                continue
            full_path = [0] + route + [0]
            route_cost = 0
            for i in range(len(full_path) - 1):
                cost = get_edge_cost(full_path[i], full_path[i + 1])
                if cost == float('inf'):
                    return float('inf')
                route_cost += cost
            total_cost += route_cost
        return total_cost

    def create_individual():
        shuffled = random.sample(nodes, len(nodes))
        # Découpe aléatoire en m segments pour varier les tailles de tournées
        splits = sorted(random.sample(range(1, len(nodes)), num_vehicles))
        return [list(x) for x in np.split(shuffled, splits)]

    population = list()
    while len(population) < pop_size:
        chromosome = create_individual()
        if fitness(chromosome) != float('inf'):
            population.append(chromosome)

    cout_initial = list(map(fitness, population))
    cout_initial = sum(cout_initial) / len(cout_initial)

    for gen in range(generations):
        population = sorted(population, key=lambda x: fitness(x))

        # Élitisme : on garde les deux meilleurs
        new_gen = population[:2]

        while len(new_gen) < pop_size:
            # Sélection par tournoi
            parent1, parent2 = random.sample(population[:pop_size // 2], 2)

            flat_p1 = [item for sublist in parent1 for item in sublist]
            flat_p2 = [item for sublist in parent2 for item in sublist]

            # Ordered Crossover (OX) sur la version plate
            start, end = sorted(random.sample(range(len(nodes)), 2))
            child_flat = [None] * len(nodes)
            child_flat[start:end] = flat_p1[start:end]

            rem = [n for n in flat_p2 if n not in child_flat]
            cursor = 0
            for i in range(len(child_flat)):
                if child_flat[i] is None:
                    child_flat[i] = rem[cursor]
                    cursor += 1

            # Re-découpage en sous-chromosomes (longueurs des routes du parent 1)
            child = []
            curr = 0
            for route in parent1:
                child.append(child_flat[curr:curr + len(route)])
                curr += len(route)

            # Mutation : échange de deux villes entre deux véhicules
            if random.random() < taux_mutation:
                v1, v2 = random.sample(range(num_vehicles), 2)
                if child[v1] and child[v2]:
                    idx1 = random.randrange(len(child[v1]))
                    idx2 = random.randrange(len(child[v2]))
                    child[v1][idx1], child[v2][idx2] = child[v2][idx2], child[v1][idx1]

            if fitness(child) == float('inf'):
                continue

            new_gen.append(child)

        population = new_gen

    best = min(population, key=lambda x: fitness(x))
    return best, fitness(best), cout_initial
