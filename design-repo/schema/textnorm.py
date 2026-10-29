"""String normalisation shared by extraction/build_source_identity.py (which DERIVES the generation-mode
leakage registry from the real source) and schema/semantic_validate.py (which MATCHES PageSpec strings
against it). One implementation, so the two sides cannot normalise differently.

Detection is string-based: NFKC, zero-width/soft-hyphen removal, curly quotes -> straight, dash variants ->
'-', lower-case, then tokenised to [a-z0-9]+ words. It does not catch paraphrase, translation, images of
text or deliberate misspelling.
"""
import hashlib, re, unicodedata

ZERO_WIDTH = re.compile("[­᠎​-‏‪-‮⁠-⁤﻿]")
QUOTES = {"‘": "'", "’": "'", "‚": "'", "‛": "'", "′": "'", "“": '"', "”": '"', "„": '"', "″": '"', "«": '"', "»": '"'}
DASHES = re.compile("[‐-―−﹘﹣－]")
WORD = re.compile(r"[a-z0-9]+")
SHINGLE = 5


def normalize(s):
    s = unicodedata.normalize("NFKC", str(s))
    s = ZERO_WIDTH.sub("", s)
    s = "".join(QUOTES.get(c, c) for c in s)
    s = DASHES.sub("-", s)
    return s.lower()


def tokens(s):
    # apostrophes inside words are dropped so "what's" and "whats" tokenise alike
    return WORD.findall(normalize(s).replace("'", ""))


def contains_terms(text_tokens, term_tokens):
    n = len(term_tokens)
    if not n:
        return False
    for i in range(len(text_tokens) - n + 1):
        if text_tokens[i:i + n] == term_tokens:
            return True
    return False


def shingle_hashes(s, n=SHINGLE):
    t = tokens(s)
    return {hashlib.sha256(" ".join(t[i:i + n]).encode()).hexdigest()[:16] for i in range(len(t) - n + 1)}
