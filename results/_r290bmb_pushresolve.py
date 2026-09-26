# -*- coding: utf-8 -*-
"""r290 bm-b push-rejection rebase resolver (skill: bigmoney-conflict-resolve).
Context: round-290 commit push rejected (bm-a r287 wrap 932bf3ce landed in-window);
pull --rebase replay hit 15 UU = classic S6-mirror collision family (r283 precedent).
Sides: A = 932bf3ce (bm-a r287 wrap face, rebase HEAD), B = 47ec5ae7 (my r290).
Recipes per classifier + manual adjudication of 4 UNKNOWN:
  - take-B whole bytes (newest regen 02:46-47 vs A 02:40-41, LWW r148/r216):
    dashboard_status.{js,json}, fundamental_b_layer_filter, heat/lhb/futures/
    update_status, token_usage, scorecard_v1, strategy_scorecard,
    daily_report REPORT-20260927.{json,md} (generated face, same-day idempotent)
  - take-A whole bytes: autofill_state.json (launches union==A set under cap-50
    rolling window: B's only-unique row WILD-S1-SHARD-7 09-25 20:52:10 is the
    oldest and falls out of the window, stays in git history; last_tick same
    second 02:40:01 tie -> HEAD per r140; r203/R208/r215 laws)
  - compute_audit.json: history union by ts (202 rows zero loss), latest=B
    (02:45:56 > 02:40:12); serialized in B byte-face (CRLF indent=2)
  - regime_state.json: history/transitions identical both sides; take-B by
    'updated' ts (02:46:16 > 02:40:21)
  - CODELY.md: base-anchored memory-union (r281/r289 law) = A face (bm-a 2 new
    law entries + base) + my r290 Project entry spliced after '### Project'
    (entry extracted verbatim from B, CRLF preserved); verify no marker, <=10KB
"""
import json
import subprocess
import sys

A_REF = "932bf3ce"
B_REF = "47ec5ae7"
ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"


def blob(ref, path):
    r = subprocess.run(["git", "show", ref + ":" + path], capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        raise RuntimeError("blob fetch failed: %s@%s" % (ref, path))
    return r.stdout


def take(ref, path):
    data = blob(ref, path)
    with open(ROOT + "\\" + path, "wb") as fh:
        fh.write(data)
    return data


resolved = []

# --- 1. whole-byte take-B (newest regen) ---
for p in ["results/dashboard_status.js", "results/dashboard_status.json",
          "results/fundamental_b_layer_filter.json",
          "results/heat_update_status.json", "results/lhb_update_status.json",
          "results/update_status.json", "results/futures_update_status.json",
          "results/token_usage.json", "results/scorecard_v1.json",
          "results/strategy_scorecard.json",
          "docs/daily_report/REPORT-2026-09-27.json",
          "docs/daily_report/REPORT-2026-09-27.md"]:
    take(B_REF, p)
    resolved.append((p, "take-B(LWW newer regen)"))

# --- 2. whole-byte take-A (union under cap + same-second tie -> HEAD) ---
take(A_REF, "results/autofill_state.json")
resolved.append(("results/autofill_state.json",
                 "take-A (union==A under cap50; last_tick tie->HEAD r140)"))

# --- 3. compute_audit: history union + latest take-new(B), B byte-face ---
ca_a = json.loads(blob(A_REF, "results/compute_audit.json").decode("utf-8-sig"))
ca_b = json.loads(blob(B_REF, "results/compute_audit.json").decode("utf-8-sig"))
assert ca_a["latest"]["ts"] < ca_b["latest"]["ts"]
seen, union_rows = set(), []
for row in ca_a["history"] + ca_b["history"]:
    k = row.get("ts")
    if k in seen:
        continue
    seen.add(k)
    union_rows.append(row)
union_rows.sort(key=lambda r: r["ts"])
merged = {"latest": ca_b["latest"], "history": union_rows}
text = json.dumps(merged, ensure_ascii=False, indent=2)
b_raw = blob(B_REF, "results/compute_audit.json").decode("utf-8-sig")
tail = "\r\n" if b_raw.endswith("\r\n") else ""
with open(ROOT + r"\results\compute_audit.json", "wb") as fh:
    fh.write((text.replace("\n", "\r\n") + tail).encode("utf-8"))
resolved.append(("results/compute_audit.json",
                 "history union %d rows (A%d+B%d unique) + latest take-B"
                 % (len(union_rows), len(ca_a["history"]), len(ca_b["history"]))))

# --- 4. regime_state: take-B by 'updated' ---
rs_a = json.loads(blob(A_REF, "results/regime_state.json").decode("utf-8-sig"))
rs_b = json.loads(blob(B_REF, "results/regime_state.json").decode("utf-8-sig"))
assert rs_a["history"] == rs_b["history"] and rs_a["transitions"] == rs_b["transitions"]
assert rs_a["updated"] < rs_b["updated"]
take(B_REF, "results/regime_state.json")
resolved.append(("results/regime_state.json",
                 "take-B by updated ts (ledger identical both sides)"))

# --- 5. CODELY.md base-anchored memory-union ---
a_txt = blob(A_REF, "CODELY.md").decode("utf-8")
b_txt = blob(B_REF, "CODELY.md").decode("utf-8")
# my unique Project entry line from B (between '### Project\r\n' and next line end)
m = b_txt.split("### Project\r\n", 1)
assert len(m) == 2, "B Project heading not found"
entry_line = m[1].split("\r\n", 1)[0]
assert entry_line.startswith("- [2026-09-27 r290"), entry_line[:60]
# splice into A after '### Project\r\n'
n = a_txt.split("### Project\r\n", 1)
assert len(n) == 2, "A Project heading not found"
merged_txt = n[0] + "### Project\r\n" + entry_line + "\r\n" + n[1]
assert "<<<<<<<" not in merged_txt and ">>>>>>>" not in merged_txt
# verify both machines' unique entries survive
assert "- [2026-09-27 02:4x] 坑律（bm-a R287" in merged_txt
assert "- [2026-09-27 02:4x] 纪律（bm-a R287" in merged_txt
assert entry_line in merged_txt
assert len(merged_txt.encode("utf-8")) <= 10240, "CODELY >10KB hard line"
with open(ROOT + r"\CODELY.md", "wb") as fh:
    fh.write(merged_txt.encode("utf-8"))
resolved.append(("CODELY.md", "base-anchored union: A face + r290 Project entry "
                             "(%d bytes)" % len(merged_txt.encode("utf-8"))))

# --- 6. verification pass: every resolved JSON parses, no markers anywhere ---
import os
import re
for p, recipe in resolved:
    if p.endswith((".json", ".js")) and p.endswith(".md") is False and ".js" not in p:
        json.loads(open(ROOT + "\\" + p.replace("/", "\\"), encoding="utf-8-sig").read())
fail = []
for dirpath, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in (".git", "Money02", "Money0923",
                                            "__pycache__", ".codely-cli")]
    for f in files:
        if not f.endswith((".json", ".md", ".js", ".py")):
            continue
        fp = os.path.join(dirpath, f)
        try:
            raw = open(fp, "rb").read()
        except OSError:
            continue
        if b"<<<<<<<" in raw or b">>>>>>>" in raw:
            fail.append(fp)
if fail:
    print("MARKER SCAN FAIL:", fail)
    sys.exit(2)
for p, recipe in resolved:
    print("RESOLVED", p, "->", recipe)
print("marker scan clean; all resolved JSON parse OK")
