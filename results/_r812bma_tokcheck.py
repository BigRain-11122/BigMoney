# -*- coding: utf-8 -*-
import io, re, ast
t = io.open(r"results\_r811bma_w169_freeze_edits.py", encoding="utf-8", newline="").read()
tree = ast.parse(t)
toks, back = None, None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and tgt.id == "TOK":
                toks = [ (e.elts[0].value if isinstance(e, ast.Constant) else None,
                          e.elts[1].value) for e in node.value.elts ]
            if isinstance(tgt, ast.Name) and tgt.id == "BACK":
                back = [ (e.elts[0].value, e.elts[1].value) for e in node.value.elts ]
tok_names = set(b for a, b in toks)
back_names = set(a for a, b in back)
print("TOK entries:", len(toks), "BACK entries:", len(back))
print("TOK-only (no BACK restore):", sorted(tok_names - back_names))
print("BACK-only (no TOK source):", sorted(back_names - tok_names))
print("--- gate/back-substitution pairs ---")
for a, tok in toks:
    if a and ("gate" in a.lower() or "GATE" in tok):
        v = [bv for bt, bv in back if bt == tok]
        print(repr(a), "->", tok, "->", v)
print("--- TOK entries with non-constant first elts ---")
for a, tok in toks:
    if a is None:
        v = [bv for bt, bv in back if bt == tok]
        print("NON-CONSTANT source for", tok, "->", v)

