import numpy as np

def run_cbim(matrix, alternatives, criteria_types, base_idx, preferences, l_count):
    """
    matrix: 2D list/array with scores (alternatives x criteria)
    alternatives: list of alternative names
    criteria_types: list with 'max' or 'min' for each criterion
    base_idx: index of the currently preferred alternative (h)
    preferences: list of dicts with preferences for each criterion
    l_count: how many alternatives to return in the current ordered set (l)
    """
    matrix = np.array(matrix, dtype=float)
    n_alt, n_crit = matrix.shape
    base_values = matrix[base_idx]

    valid_indices = []
    scores = []

    for i in range(n_alt):
        is_valid = True
        max_diff = -1e9 # For the Chebyshev scalarization

        for j in range(n_crit):
            val = matrix[i, j]
            base_val = base_values[j]
            pref = preferences[j]
            c_type = criteria_types[j]

            # Calculate the difference compared to the base (positive value = improvement)
            if c_type == 'max':
                diff = val - base_val
            else: # min (smaller value is an improvement)
                diff = base_val - val

            # Check the allowed worsening constraint (K_h <=)
            if pref['action'] == 'worsen':
                # If it has worsened by more than the allowed delta threshold
                if diff < -float(pref['delta']):
                    is_valid = False
                    break

            # Chebyshev scalarizing function for improvement criteria (K_h >)
            if pref['action'] == 'improve':
                # We seek to maximize the minimum improvement (we minimize -diff)
                penalty = -diff

                if penalty > max_diff:
                    max_diff = penalty

        if is_valid:
            valid_indices.append(i)
            # If the decision maker hasn't chosen specific criteria for improvement, distance is 0
            scores.append(max_diff if max_diff != -1e9 else 0.0)

    # Sort the alternatives in ascending order by the value of S(i)
    sorted_pairs = sorted(zip(valid_indices, scores), key=lambda x: x[1])

    # Format the result for the top 'l' alternatives
    result = []
    for idx, score in sorted_pairs[:l_count]:
        result.append({
            'index': int(idx),
            'name': alternatives[idx],
            'values': matrix[idx].tolist(),
            'score': round(score, 4)
        })

    return result
