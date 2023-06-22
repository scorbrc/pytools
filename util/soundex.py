

SOUNDEX_DIGITS = {l:d for l, d in zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                      '01230120022455012623010202')}

def soundex(word, size=4):
    """
    Produces an English soundex for 'word' up to 'size' characters long.
    See https://en.wikipedia.org/wiki/Soundex.
    """
    uword = ''.join([c for c in word.upper() if c.isalpha()])
    if not len(uword):
        return word
    snd = [uword[0]] + ['0'] * (size - 1)
    i = 1
    for ch in uword[1:]:
        dg = SOUNDEX_DIGITS[ch]
        if dg != snd[i-1] and dg != '0':
            snd[i] = dg
            i += 1
            if i == size:
                break
    return ''.join(snd)
