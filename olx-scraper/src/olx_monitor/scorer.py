def calculate_score(text, scoring_rules):
    """
    Calculates score for an ad.

    Parameters
    ----------
    text : str
        Combined text from title + URL + page text

    scoring_rules : dict
        Dictionary containing keyword -> score

    Returns
    -------
    int
        Total score based on keyword matches
    """

    score = 0

    text = text.lower()

    for keyword, points in scoring_rules.items():
        if keyword in text:
            score += points

    return score
