def electre_i(alternatives, weights, criteria_types, c_threshold, d_threshold):
    """
    ELECTRE I implementation.
    alternatives: list of dicts
    weights: list of weights [0.4, 0.6]
    criteria_types: list of directions ["min", "max"]
    c_threshold: concordance threshold (0.0 to 1.0)
    d_threshold: discordance threshold (0.0 to 1.0)
    """
    n_alts = len(alternatives)
    n_crit = len(weights)

    if n_alts == 0 or n_crit == 0:
        return {"error": "Missing input data for criteria or alternatives"}

    names = [alt["name"] for alt in alternatives]
    matrix = [alt["values"] for alt in alternatives]

    # Calculate the range (interval) for each criterion (needed for the discordance matrix)
    ranges = []

    for c in range(n_crit):
        col_values = [matrix[a][c] for a in range(n_alts)]
        ranges.append(max(col_values) - min(col_values) if max(col_values) - min(col_values) != 0 else 1.0)

    # Build the Concordance (C) and Discordance (D) Matrices
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

                # Concordance check (whether j is better than or equal to k)
                if criteria_types[c] == "max":
                    is_better_or_equal = (v_j >= v_k)
                    diff = v_k - v_j  # discordance if v_j < v_k
                else:  # min
                    is_better_or_equal = (v_j <= v_k)
                    diff = v_j - v_k  # discordance if v_j > v_k

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
            if concordance_matrix[j][k] >= c_threshold and discordance_matrix[j][k] <= d_threshold:
                dominance_relations.append({"from": names[j], "to": names[k]})
                dominated_set.add(names[k])

    # The kernel consists of alternatives that are not outranked by any other
    kernel = [name for name in names if name not in dominated_set]

    return {
        "names": names,
        "concordance": concordance_matrix,
        "discordance": discordance_matrix,
        "relations": dominance_relations,
        "kernel": kernel
    }
