from algorithms.borda import borda_count

def nanson(votes):
    """
    votes: list of rankings
    Returns a dict with the result of each iteration
    """
    active_votes = [list(ranking) for ranking in votes]
    rounds = []

    while True:
        scores = borda_count(active_votes)

        if len(scores) == 1:
            winner = list(scores.keys())[0]
            break

        avg = sum(scores.values()) / len(scores)
        eliminated = [alt for alt, pts in scores.items() if pts <= avg]

        rounds.append({
            "scores": scores,
            "avg": round(avg, 2),
            "eliminated": eliminated,
        })

        # Remove eliminated alternatives from all rankings
        remaining = set(scores.keys()) - set(eliminated)

        active_votes = [
            [alt for alt in ranking if alt in remaining]
            for ranking in active_votes
        ]

        if len(remaining) == 1:
            winner = list(remaining)[0]
            break

        if len(remaining) == 0:
            # Perfect tie — all are eliminated simultaneously
            winner = max(scores, key=scores.get)
            break

    return {"rounds": rounds, "winner": winner}
