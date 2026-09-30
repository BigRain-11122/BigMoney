# -*- coding: utf-8 -*-
"""r499 bm-a: dump all M4 name-key docstring first lines for extractor-rule
design (read-only)."""
import ast
import io
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))
import g2_overlap_census as g2

out = []
for f in g2.export_m4_faces():
    text = g2._read_text(os.path.join(g2.M4_FEATURES_DIR, f["file"]))
    tree = ast.parse(text)
    node = f["body_node"]
    doc = ast.get_docstring(node) or ""
    first = doc.strip().splitlines()[0].strip() if doc.strip() else ""
    if "\u2014" in first:
        first = first.split("\u2014")[0].strip()
    out.append({"face": f["meta_id"], "sub": f["subfamily"], "line": first,
                "extracted": f["doc_formula"]})

with io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "_r499bma_m4_doclines.json"), "w",
             encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print("dumped", len(out))
