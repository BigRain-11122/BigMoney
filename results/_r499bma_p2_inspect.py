# -*- coding: utf-8 -*-
"""r499 bm-a: P2 census post-burn engineering inspection (read-only).
Check (a) empty doc_formula faces, (b) the 4 DUP-FORMULA-VERIFIED hits,
(c) near-miss identity samples (old_028 vs WQ#3 sign-convention), (d) corpus
sizes vs prediction inputs."""
import io
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))
import g2_overlap_census as g2

doc = json.load(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "g2_overlap_census_p2.json"), encoding="utf-8"))
rows = doc["rows"]

empty_fml = [r["face"] for r in rows
             if r["leg"].startswith("M4") and not r["doc_formula"]]
print("M4 empty-doc_formula faces:", len(empty_fml), empty_fml[:12])

print()
print("DUP-FORMULA-VERIFIED hits:")
for r in rows:
    if r["verdict"] == "DUP-FORMULA-VERIFIED":
        print(" ", r["face"], "->", r["corpus_hit"]["family"], r["corpus_hit"]["number"],
              "| status:", r["corpus_hit"]["status"])

print()
print("near-miss sample: old_028 identity check vs corpus")
for r in rows:
    if r["face"] == "old_028":
        print("  row verdict:", r["verdict"], "| note:", r["note"])
        print("  doc_formula:", r["doc_formula"])
a = g2.norm_formula_v2("corr(rank(open), rank(volume), 10)")
b = g2.norm_formula_v2("-1 * correlation(rank(open), rank(volume), 10)")
print("  norm a:", a)
print("  norm b:", b)
print("  equal:", a == b)

# corpus size + sign-prefixed share
m1 = g2.export_m1()
wq_verd = g2.load_wq101_verdicts()
gtja_verd = g2.load_gtja191_verdicts()
wq_f = [f["formula_latex"] for f in m1["alpha101"] if f["formula_latex"]]
gt_f = [f["formula_latex"] for f in m1["gtja191"] if f["formula_latex"]]
print()
print("corpus: wq101 formulas non-empty:", len(wq_f), "| gtja191:", len(gt_f))
sign1 = sum(1 for f in wq_f if f.strip().startswith("-1") or f.strip().startswith("- 1"))
sign1g = sum(1 for f in gt_f if f.strip().startswith("-1") or f.strip().startswith("- 1"))
print("sign-prefixed (-1*): wq101", sign1, "| gtja191", sign1g)

# how many M4 name-key formulas would match if '-1*' sign unification existed
m4 = g2.export_m4_faces()
corpus = {}
for face in m1["alpha101"]:
    s = g2.norm_formula_v2(face["formula_latex"] or face["doc_formula"])
    if s:
        corpus.setdefault(s, "wq101#%s" % face["number"])
for face in m1["gtja191"]:
    s = g2.norm_formula_v2(face["formula_latex"] or face["doc_formula"])
    if s:
        corpus.setdefault(s, "gtja191#%s" % face["number"])


def strip_sign(t):
    for p in ("-1*", "-1*", "(-1)*"):
        if t.startswith(p):
            return t[len(p):]
    return t


corpus_nosign = {}
for k, v in corpus.items():
    corpus_nosign.setdefault(strip_sign(k), v)
hits_now = 0
hits_nosign = 0
for f in m4:
    if f["subfamily"] in ("alpha", "cs"):
        continue
    s = g2.norm_formula_v2(f["doc_formula"]) if f["doc_formula"] else ""
    if not s:
        continue
    if s in corpus:
        hits_now += 1
    elif strip_sign(s) in corpus_nosign or strip_sign(s) in corpus:
        hits_nosign += 1
        if hits_nosign <= 8:
            print("sign-only miss:", f["meta_id"], "->",
                  corpus_nosign.get(strip_sign(s)) or corpus.get(strip_sign(s)),
                  "|", f["doc_formula"][:70])
print()
print("name-key identity hits (frozen):", hits_now,
      "| sign-only near-misses:", hits_nosign)
