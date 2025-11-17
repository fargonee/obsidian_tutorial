from utils.shorten_str import shorten_str
from utils.constants import sep as separator

def make_valid_filename(string: str, sep: str = separator, max_len: int = 254):
    """
    Creates a safe filename with a 'fingerprint' portion preserved.
    Features:
        - Drops vowels or underscores if too long
        - Progressive shortening from middle if needed
        - Keeps a max length
    """

    # Split into main part and optional fingerprint if sep exists
    if sep in string:
        parts = string.rsplit(sep, 1)
        base, fp = parts[0], parts[1]
    else:
        base, fp = string, ""

    def packed(s):
        return f"{s}{sep}{fp}" if fp else s

    # 1. original
    if len(packed(base)) <= max_len:
        return packed(base)

    # 2. drop vowels
    sv = shorten_str(base, drop_vowels=True)
    if len(packed(sv)) <= max_len:
        return packed(sv)

    # 3. drop vowels + underscores
    su = shorten_str(base, drop_vowels=True, drop_underscores=True)
    if len(packed(su)) <= max_len:
        return packed(su)

    # 4. drop vowels + underscores + trim middle progressively
    drop = 1
    while True:
        st = shorten_str(base, drop_vowels=True, drop_underscores=True, drop=drop)
        if len(packed(st)) <= max_len:
            return packed(st)
        drop += 1
