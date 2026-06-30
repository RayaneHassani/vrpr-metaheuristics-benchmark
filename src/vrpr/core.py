"""Core evaluation: solution cost and neighbourhood generation.

A solution is a list of tours, one per vehicle, each tour starting and ending
at the depot (node 0), e.g. ``[[0, 3, 1, 0], [0, 2, 0]]``.

The restricted-edge constraint is enforced here: any tour using a closed edge
(or a missing edge) is given an infinite cost and therefore discarded.
"""


def cout_solution(G, solution):
    """Total cost of a solution; ``inf`` if it uses a closed or missing edge."""
    total = 0
    for tournee in solution:
        for idx in range(len(tournee) - 1):
            i, j = tournee[idx], tournee[idx + 1]
            if not G.has_edge(i, j) or G[i][j]['close']:
                return float('inf')
            total += G[i][j]['cout']
    return total


def voisinage(G, solution):
    """Generate neighbour solutions via intra-tour swap and inter-tour relocate."""
    voisins = []

    for k in range(len(solution)):
        tournee = solution[k]
        for i in range(1, len(tournee) - 1):
            for j in range(i + 1, len(tournee) - 1):
                nouvelle = [list(t) for t in solution]
                nouvelle[k][i], nouvelle[k][j] = nouvelle[k][j], nouvelle[k][i]
                voisins.append(nouvelle)

    for k1 in range(len(solution)):
        for k2 in range(len(solution)):
            if k1 == k2:
                continue
            for i in range(1, len(solution[k1]) - 1):
                for j in range(1, len(solution[k2])):
                    nouvelle = [list(t) for t in solution]
                    ville = nouvelle[k1].pop(i)
                    nouvelle[k2].insert(j, ville)
                    if len(nouvelle[k1]) >= 3:
                        voisins.append(nouvelle)

    return voisins
