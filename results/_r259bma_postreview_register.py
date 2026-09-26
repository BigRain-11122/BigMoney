# -*- coding: utf-8 -*-
"""R259 bm-a: register T-73-STYLE-ROT-S1 post_review claim row (O-2115 /
R246 law: same-round registration; checks reference only pre-frozen prereg
faces + product field consistency, R256 anchor on stable artifact files)."""
import io
import json
import subprocess

P = "results/post_review_criteria.json"
raw = subprocess.run(["git", "show", f"HEAD:{P}"], capture_output=True,
                     check=True).stdout
print("HEAD byte faces: BOM:", raw.startswith(b"\xef\xbb\xbf"),
      "CRLF:", b"\r\n" in raw, "trailing_nl:", raw.endswith(b"\n"),
      "esc:", "\\u" in raw.decode("utf-8-sig"))
d = json.loads(raw.decode("utf-8-sig"))
assert isinstance(d.get("items"), list)
assert not any(i.get("id") == "T-73-STYLE-ROT-S1" for i in d["items"])

d["items"].append({
    "id": "T-73-STYLE-ROT-S1",
    "claim": ("T-73 s2 slice-E style-rotation full arc (last remaining s2 "
              "topic -> s2 COMPLETE): prereg freeze commit cb2e0e84 BEFORE "
              "first burn (runner header + SEED_REGISTRY t73_style_rot_s1 "
              "base 20261030 same-commit one-step R250; band rg-scan clean) "
              "-> selftest 10-leg PASS -> run T73-STYLE-ROT-S1 (2 judged "
              "faces STYLE-MOM-252-63 alive both sides THIN 1.04x/1.08x "
              "null-p95 margins, STYLE-MOM-63-21 frozen one-sided NOT "
              "alive, OOS -0.192 beyond null = quarter-reversal post-hoc "
              "hypothesis) + 100 within-month leg-permutation null draws -> "
              "ledger 187585+102=187687 single-count -> descriptive "
              "clean_value bridge face (narrative confirmed 2017 core/2024 "
              "dividend, partial 2021 growth, modest 2023 micro; 4 fund "
              "artifacts caught +248%/+176%/-51%/-12.7%) -> run1 "
              "raw-face-descriptive defect self-caught pre-digest, "
              "archived defective + ledger self-echo intermediate "
              "discarded in-round with prev-echo guard added -> digest "
              "DIGEST-20260926-t73-s2-sliceE-rotation.md"),
    "claim_source": ("scripts/t73_s2_style_rotation.py frozen header "
                     "(prereg, freeze commit cb2e0e84 precedes any run) + "
                     "scripts/science_gates.py SEED_REGISTRY row (same "
                     "freeze commit) + results/t73_s2/style_rotation.json "
                     "product + run1 archive "
                     "style_rotation_run1_descriptive_defective.json + "
                     "digest research/digests/"
                     "DIGEST-20260926-t73-s2-sliceE-rotation.md"),
    "status": "pending",
    "checks": [
        {"kind": "file_exists", "args": ["scripts/t73_s2_style_rotation.py"]},
        {"kind": "file_exists",
         "args": ["results/t73_s2/style_rotation.json"]},
        {"kind": "file_exists",
         "args": ["results/t73_s2/style_rotation_run1_descriptive_defective.json"]},
        {"kind": "file_exists",
         "args": ["research/digests/DIGEST-20260926-t73-s2-sliceE-rotation.md"]},
        {"kind": "json_field",
         "args": ["results/t73_s2/style_rotation.json",
                  "faces.STYLE-MOM-252-63.blocks.is.mean", 0.10038]},
        {"kind": "json_field",
         "args": ["results/t73_s2/style_rotation.json",
                  "faces.STYLE-MOM-252-63.blocks.oos.mean", 0.15126]},
        {"kind": "json_field",
         "args": ["results/t73_s2/style_rotation.json",
                  "faces.STYLE-MOM-63-21.blocks.oos.mean", -0.19173]},
        {"kind": "json_field",
         "args": ["results/t73_s2/style_rotation.json",
                  "verdict.STYLE-MOM-252-63.alive_oos", True]},
        {"kind": "json_field",
         "args": ["results/t73_s2/style_rotation.json",
                  "verdict.STYLE-MOM-63-21.alive_oos", False]},
        {"kind": "json_field",
         "args": ["results/t73_s2/style_rotation.json",
                  "trials_ledger.total", 187687]},
        {"kind": "json_field",
         "args": ["results/t73_s2/style_rotation.json",
                  "trials_ledger.prev_total", 187585]},
        {"kind": "json_field",
         "args": ["results/t73_s2/style_rotation.json",
                  "trials_N.seed_base", 20261030]},
        {"kind": "json_field",
         "args": ["results/t73_s2/style_rotation.json",
                  "evidence_cutoff", "2026-09-22"]},
        {"kind": "file_contains",
         "args": ["scripts/science_gates.py", "t73_style_rot_s1"]},
    ],
})

face = {"bom": raw.startswith(b"\xef\xbb\xbf"), "crlf": b"\r\n" in raw,
        "trailing_nl": raw.endswith(b"\n")}
if face["bom"]:
    out = json.dumps(d, ensure_ascii=False, indent=1).encode("utf-8")
    out = b"\xef\xbb\xbf" + out
else:
    out = json.dumps(d, ensure_ascii=False, indent=1).encode("utf-8")
if face["trailing_nl"] and not out.endswith(b"\n"):
    out += b"\n"
io.open(P, "wb").write(out)
print("registered T-73-STYLE-ROT-S1; n items:", len(d["items"]))
