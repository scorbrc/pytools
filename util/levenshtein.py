import re

ALPHANUM_EXP = re.compile("[^A-Za-z0-9]+")

def levenshtein(s1, s2):
    """
    Levenshtein distance for measuring the difference between strings
    's1' and 's2'. Returns a score (0 <= score <= 1).
    Higher the value the closer the match.
    See https://en.wikipedia.org/wiki/Levenshtein_distance
    """
    w1 = re.sub(ALPHANUM_EXP, '', s1).lower()
    w2 = re.sub(ALPHANUM_EXP, '', s2).lower()
    if len(w1) < 2 or len(w2) < 2:
        return 0
    dst = [[0] * (len(w2) + 1) for _ in range(len(w1) + 1)]
    for i in range(1, len(w1) + 1):
        dst[i][0] = i
    for i in range(1, len(w2) + 1):
        dst[0][i] = i
    for c in range(1, len(w2) + 1):
        for r in range(1, len(w1) + 1):
            x = dst[r - 1][c] + 1
            y = dst[r][c - 1] + 1
            z = dst[r - 1][c - 1]
            if w1[r - 1] != w2[c - 1]:
                z += 1
            if x < y and x < z:
                dst[r][c] = x
            elif y < x and y < z:
                dst[r][c] = y
            else:
                dst[r][c] = z
    return 1 - dst[-1][-1] / max(len(w1), len(w2))
