def electre_i(alternatives, weights, criteria_types, c_threshold, d_threshold):
    """
    ELECTRE I implementation.
    alternatives: list of dicts
    weights: list of weights (will be normalised internally so they don't have to sum to 1)
    criteria_types: list of directions ["min" | "max"]
    c_threshold: concordance threshold (0.0 to 1.0)
    d_threshold: discordance threshold (0.0 to 1.0)
    """
    n_alts = len(alternatives)
    n_crit = len(weights)

    if n_alts == 0 or n_crit == 0:
        return {"error": "Missing input data for criteria or alternatives"}

    if len(criteria_types) != n_crit:
        return {"error": "criteria_types length must match weights length"}

    for alt in alternatives:
        if len(alt.get("values", [])) != n_crit:
            return {"error": f"Alternative '{alt.get('name')}' has wrong number of values"}

    # Normalise weights so they sum to 1.0
    total_weight = sum(weights)
    if total_weight == 0:
        return {"error": "Weights must not all be zero"}
    weights = [w / total_weight for w in weights]

    names = [alt["name"] for alt in alternatives]
    matrix = [alt["values"] for alt in alternatives]

    # Calculate the range (interval) for each criterion (needed for discordance)
    ranges = []
    for c in range(n_crit):
        col_values = [matrix[a][c] for a in range(n_alts)]
        col_range = max(col_values) - min(col_values)
        ranges.append(col_range if col_range != 0 else 1.0)

    # Build Concordance (C) and Discordance (D) matrices
    concordance_matrix = [[0.0] * n_alts for _ in range(n_alts)]
    discordance_matrix = [[0.0] * n_alts for _ in range(n_alts)]

    for j in range(n_alts):
        for k in range(n_alts):
            if j == k:
                continue

            c_sum = 0.0
            max_d_diff = 0.0

            for c in range(n_crit):
                v_j = matrix[j][c]
                v_k = matrix[k][c]

                # Concordance: j is better than or equal to k on criterion c
                if criteria_types[c] == "max":
                    is_better_or_equal = (v_j >= v_k)
                    diff = v_k - v_j  # positive when j is worse → discordance
                else:  # min
                    is_better_or_equal = (v_j <= v_k)
                    diff = v_j - v_k  # positive when j is worse → discordance

                if is_better_or_equal:
                    c_sum += weights[c]
                else:
                    norm_diff = diff / ranges[c]
                    if norm_diff > max_d_diff:
                        max_d_diff = norm_diff

            concordance_matrix[j][k] = round(c_sum, 3)
            discordance_matrix[j][k] = round(max_d_diff, 3)

    # Determine outranking relations through thresholds
    dominance_relations = []
    dominated_set = set()

    for j in range(n_alts):
        for k in range(n_alts):
            if j == k:
                continue
            if (concordance_matrix[j][k] >= c_threshold and
                    discordance_matrix[j][k] <= d_threshold):
                dominance_relations.append({"from": names[j], "to": names[k]})
                dominated_set.add(names[k])

    # The kernel consists of alternatives not outranked by any other
    kernel = [name for name in names if name not in dominated_set]

    return {
        "names": names,
        "weights": [round(w, 4) for w in weights],
        "concordance": concordance_matrix,
        "discordance": discordance_matrix,
        "relations": dominance_relations,
        "kernel": kernel
    }

