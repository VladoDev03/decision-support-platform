import math


def run_topsis(alternatives, weights, criteria_types):
    """
    alternatives: list of dicts
    weights: list of weights (will be normalised internally)
    criteria_types: list of "max" | "min" for each criterion

    Returns a list of dicts sorted by rank (best first):
    """
    n_alts = len(alternatives)
    n_crit = len(weights)

    if n_alts == 0 or n_crit == 0:
        raise ValueError("Missing input data for alternatives or criteria")

    if len(criteria_types) != n_crit:
        raise ValueError("criteria_types length must match weights length")

    for alt in alternatives:
        if len(alt.get("values", [])) != n_crit:
            raise ValueError(f"Alternative '{alt.get('name')}' has wrong number of values")

    # Normalise weights
    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("Weights must not all be zero")
    weights = [w / total_weight for w in weights]

    names = [alt["name"] for alt in alternatives]
    matrix = [[float(v) for v in alt["values"]] for alt in alternatives]

    # Step 1: Normalise the decision matrix (Euclidean normalisation)
    col_norms = []
    for c in range(n_crit):
        col_sq_sum = sum(matrix[a][c] ** 2 for a in range(n_alts))
        col_norms.append(math.sqrt(col_sq_sum) if col_sq_sum > 0 else 1.0)

    normalised = [
        [matrix[a][c] / col_norms[c] for c in range(n_crit)]
        for a in range(n_alts)
    ]

    # Step 2: Weighted normalised matrix
    weighted = [
        [normalised[a][c] * weights[c] for c in range(n_crit)]
        for a in range(n_alts)
    ]

    # Step 3: Ideal best (A+) and ideal worst (A-)
    ideal_best = []
    ideal_worst = []
    for c in range(n_crit):
        col = [weighted[a][c] for a in range(n_alts)]
        if criteria_types[c] == "max":
            ideal_best.append(max(col))
            ideal_worst.append(min(col))
        else:
            ideal_best.append(min(col))
            ideal_worst.append(max(col))

    # Step 4: Euclidean distances to ideal best and worst
    results = []
    for a in range(n_alts):
        dist_best = math.sqrt(
            sum((weighted[a][c] - ideal_best[c]) ** 2 for c in range(n_crit))
        )
        dist_worst = math.sqrt(
            sum((weighted[a][c] - ideal_worst[c]) ** 2 for c in range(n_crit))
        )

        # Step 5: Closeness coefficient
        denom = dist_best + dist_worst
        score = dist_worst / denom if denom > 0 else 0.0

        results.append({
            "name": names[a],
            "score": round(score, 4),
            "dist_best": round(dist_best, 4),
            "dist_worst": round(dist_worst, 4),
            "values": matrix[a],
        })

    # Step 6: Rank by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    for idx, r in enumerate(results):
        r["rank"] = idx + 1

    return results
