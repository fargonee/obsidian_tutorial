def shorten_str(s: str, drop_vowels=False, drop_underscores=False, drop=None):
    text = s

    if drop_vowels:
        text = "".join(ch for ch in text if ch.lower() not in "aeiou")

    if drop_underscores:
        parts = text.split("_")
        text = "".join(p.capitalize() if i > 0 else p for i, p in enumerate(parts))

    if isinstance(drop, int):
        n = len(text)
        if n > drop + 1:
            mid = n // 2
            left = max(0, mid - drop // 2)
            right = min(n, left + drop + 1)
            text = text[:left] + "-" + text[right:]

    return text
