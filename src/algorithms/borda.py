def borda_count(votes):
    """
    votes: list of rankings
    Returns a dict with the scores of each alternative
    """
    scores = {}

    for ranking in votes:
        n = len(ranking)

        for position, alternative in enumerate(ranking):
            points = n - 1 - position  # first place → n-1 points, last → 0
            scores[alternative] = scores.get(alternative, 0) + points

    return scores


def borda_winner(votes: list[list[str]]) -> str:
    """Returns the Borda winner."""
    scores = borda_count(votes)
    return max(scores, key=scores.get)
