import re
import logging

log = logging.getLogger(__name__)


def calculate_score(text: str, scoring_rules: dict) -> int:
    """
    Scores an ad based on keyword matches.

    Improvements over v1:
    - Word boundary matching: 'sql' won't match inside 'mysql' accidentally
    - Frequency cap: a keyword scores once, not once per occurrence
    - Logs which keywords matched, so you can tune the rules over time

    Parameters
    ----------
    text : str
        Combined text from title + URL + page content
    scoring_rules : dict
        Keyword -> point value mapping from config.yml

    Returns
    -------
    int
        Total score
    """
    if not text or not scoring_rules:
        return 0

    text = text.lower()
    total_score = 0
    matched = []

    for keyword, points in scoring_rules.items():
        keyword_lower = keyword.lower()

        # re.escape handles multi-word keywords like "home office" safely
        # \b means word boundary — prevents 'dados' matching inside 'agradados'
        pattern = r"\b" + re.escape(keyword_lower) + r"\b"

        if re.search(pattern, text):
            total_score += points
            matched.append(f"{keyword}(+{points})")

    if matched:
        log.debug(f"Matched: {', '.join(matched)} → total={total_score}")

    return total_score
