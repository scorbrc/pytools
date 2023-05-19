from enum import Enum
import re


class TextMatcher:
    """
    Matches text using Levenshtein distance, caching alreadt matched pairs.
    See https://en.wikipedia.org/wiki/Levenshtein_distance.
    """

    ALPHANUM_EXP = re.compile("[^A-Za-z0-9]+")
    MatchType = Enum('MatchType', ['BASE_REF', 'SOURCE_REF', 'INDEPENDENT'])

    def __init__(self,
                 match_type=MatchType.INDEPENDENT,
                 case_sensitive=False,
                 min_size=2):
        """
        Create a TextMatcher with 'match' to match with reference to
        base string, reference to source string or independent of base or
        source, 'case_sensitive' to indicate whether lower and upper case_sensitive
        are treated differently, and 'min_size' as the minimum alhanumeric
        characters for base and source strings for matching.
        """
        self.match_type = match_type
        self.case_sensitive = case_sensitive
        self.min_size = min_size
        self.__word_cache = {}
        self.__cache_n = 0
        self.__crunch_n = 0

    def match(self, base, src):
        """
        Match string 'src' to string 'base' returning a score from 0 to 1
        indicating the strength of the match.
        """
        base = re.sub(TextMatcher.ALPHANUM_EXP, '', base)
        src = re.sub(TextMatcher.ALPHANUM_EXP, '', src)
        if len(base) < self.min_size or len(src) < self.min_size:
            return 0

        if not self.case_sensitive:
            base = base.lower()
            src = src.lower()

        key = (base, src)
        try:
            score = self.__word_cache[key]
            self.__cache_n += 1
        except KeyError:
            dst = [[0] * (len(src) + 1) for _ in range(len(base) + 1)]
            for i in range(1, len(base) + 1):
                dst[i][0] = i
            for i in range(1, len(src) + 1):
                dst[0][i] = i
            for c in range(1, len(src) + 1):
                for r in range(1, len(base) + 1):
                    x = dst[r - 1][c] + 1
                    y = dst[r][c - 1] + 1
                    z = dst[r - 1][c - 1]
                    if base[r - 1] != src[c - 1]:
                        z += 1
                    if x < y and x < z:
                        dst[r][c] = x
                    elif y < x and y < z:
                        dst[r][c] = y
                    else:
                        dst[r][c] = z
            if self.match_type == TextMatcher.MatchType.BASE_REF:
                n = len(src)
            elif self.match_type == TextMatcher.MatchType.SOURCE_REF:
                n = len(base)
            else:
                n = (len(base) + len(src)) / 2
            score = min(max(1 - dst[-1][-1] / n, 0), 1)
            self.__word_cache[key] = score
            self.__crunch_n += 1
        return score

    def __str__(self):
        return "TextMatcher(cache=%d,crunch=%d)" % \
            (self.__cache_n, self.__crunch_n)
