#!/usr/bin/env python3 -I
"""Real structural comparison of /privacy and /terms (MASTER-GUIDE 3.22).

Rather than trusting the grouping of two routes into one template, this parses the
hydrated live DOM captures (reference/pages/privacy.html and terms.html in the source
project) and diffs their element skeletons: the ordered landmark children under
main#top, and the set of (tag, class) pairs inside the legal document.

Run:  python3 -I extraction/derive_template_comparison.py [--source <project root>] [--write]
Degrades gracefully (WARNING, exit 0) when the source tree is absent; the checked-in
extraction/legal-template-comparison.json is then the evidence of record.
"""
import argparse, html.parser, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, "legal-template-comparison.json")
VOID = {"br", "img", "input", "hr", "meta", "link", "path", "line", "polyline", "circle", "rect", "source"}


class Skel(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.in_main, self.main_depth = [], False, 0
        self.main_children, self.pairs, self.counts = [], set(), {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        cls = " ".join(c for c in cls if c)
        if tag == "main":
            self.in_main, self.main_depth = True, len(self.stack)
        elif self.in_main:
            depth = len(self.stack) - self.main_depth - 1
            if depth == 0:
                self.main_children.append(f"{tag}.{cls}" if cls else tag)
            if tag not in ("svg", "path", "span", "a", "strong", "br", "time") or cls:
                self.pairs.add(f"{tag}.{cls}" if cls else tag)
            key = f"{tag}.{cls}" if cls else tag
            self.counts[key] = self.counts.get(key, 0) + 1
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack and self.stack[-1] != tag:
            self.stack.pop()
        if self.stack:
            self.stack.pop()
        if tag == "main" and len(self.stack) == self.main_depth:
            self.in_main = False


def skeleton(path):
    p = Skel()
    p.feed(open(path, encoding="utf-8", errors="replace").read())
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=os.path.dirname(REPO))
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    d = os.path.join(a.source, "reference", "pages")
    pf, tf = os.path.join(d, "privacy.html"), os.path.join(d, "terms.html")
    if not (os.path.isfile(pf) and os.path.isfile(tf)):
        print("WARNING: reference/pages/{privacy,terms}.html not found (source tree absent); "
              "keeping the checked-in extraction/legal-template-comparison.json unchanged.")
        return 0
    P, T = skeleton(pf), skeleton(tf)
    only_p = sorted(P.pairs - T.pairs)
    only_t = sorted(T.pairs - P.pairs)
    res = {
        "_note": "DERIVED by extraction/derive_template_comparison.py from the hydrated live DOM captures; no copy text is stored.",
        "mainChildrenPrivacy": P.main_children,
        "mainChildrenTerms": T.main_children,
        "sameTopLevelSequence": P.main_children == T.main_children,
        "pairsOnlyInPrivacy": only_p,
        "pairsOnlyInTerms": only_t,
        "sharedPairCount": len(P.pairs & T.pairs),
        "countsPrivacy": {k: P.counts[k] for k in sorted(P.counts) if k.startswith(("p.legal", "h2", "h3", "ul", "section.legal"))},
        "countsTerms": {k: T.counts[k] for k in sorted(T.counts) if k.startswith(("p.legal", "h2", "h3", "ul", "section.legal"))},
        "verdict": "SAME_TEMPLATE" if P.main_children == T.main_children and not [x for x in only_p + only_t if not x.startswith(("h3", "ul", "li", "p.legal-intro"))] else "DIFFERENT",
    }
    text = json.dumps(res, indent=1, ensure_ascii=False)
    if a.write:
        open(OUT, "w", encoding="utf-8").write(text + "\n")
        print("wrote", os.path.relpath(OUT, REPO))
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
