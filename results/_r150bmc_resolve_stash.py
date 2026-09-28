# -*- coding: utf-8 -*-
"""r150 bm-c stash-pop mirror-storm resolver (r85/r120/r143/r324 canon).

Faces (stage2=ours=origin/HEAD post-rebase, stage3=theirs=my stashed S7):
  CODELY.md            -> origin base + re-apply my r150 pitlaw entry
                          (my batch-39 pointer/archive = superseded by
                          bm-b r369 origin-first batch-39; r392 stays hot
                          per origin; zero-loss verified)
  memory-archive      -> origin verbatim (my dup batch-39 section dropped;
                          unique r392 text still in hot CODELY)
  daily_report md+json -> ours (twin same-side law r328b, fresher regen)
  compute_audit.json   -> history union by ts-key (zero-loss r85 law)
  status faces x6      -> take-new by ts (r109 law)
Every resolved .json must parse; CODELY <=10,240B; assertions guard."""
import io
import json
import subprocess


def side(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"],
                       capture_output=True)
    assert r.returncode == 0, f"stage {n} missing for {path}"
    return r.stdout.decode("utf-8")


def write(path, text):
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


TS_KEYS = ("ts", "asof", "updated_at", "updated", "generated")


def ts_of(obj):
    for k in TS_KEYS:
        if isinstance(obj, dict) and k in obj and obj[k]:
            return str(obj[k])
    return ""


REPORT_MD = "docs/daily_report/REPORT-2026-09-28.md"
REPORT_JSON = "docs/daily_report/REPORT-2026-09-28.json"
ARCHIVE = "research/memory-archive/202609.md"
STATUS_FACES = ["results/fundamental_b_layer_filter.json",
                "results/futures_update_status.json",
                "results/lhb_update_status.json",
                "results/update_status.json",
                "results/regime_state.json",
                "results/token_usage.json"]

# ---- CODELY.md: origin base + re-apply my r150 entry ----
ours_codely = side("CODELY.md", 2)
theirs_codely = side("CODELY.md", 3)
mine_lines = [ln for ln in theirs_codely.split("\n")
             if ln.startswith("- [2026-09-28 09:0x r150 bm-c] 坑律：")]
assert len(mine_lines) == 1, f"r150 entry in stash side: {len(mine_lines)}"
assert "- [2026-09-28 09:0x r150 bm-c]" not in ours_codely, \
    "r150 entry already on origin side?"
# zero-loss: r392 stays hot on origin; r149/r368 archived by bm-b batch-39
assert any(ln.startswith("- [2026-09-28 08:2x r392 bm-a] 坑律：")
           for ln in ours_codely.split("\n")), "r392 not hot on origin"
res_codely = ours_codely
if not res_codely.endswith("\n"):
    res_codely += "\n"
res_codely += mine_lines[0] + "\n"
write("CODELY.md", res_codely)
sz = len(res_codely.encode("utf-8"))
assert sz <= 10240, f"CODELY over line: {sz}"
print(f"[1] CODELY: origin base + r150 entry; hot={sz}B (UNDER 10240)")

# ---- memory-archive: origin verbatim + zero-loss proof ----
ours_arch = side(ARCHIVE, 2)
theirs_arch = side(ARCHIVE, 3)
for tag in ("- [2026-09-28 08:3x r149 bm-c]",
            "- [2026-09-28 08:3x r368 bm-b]"):
    assert tag in ours_arch, f"origin archive missing {tag}"
# my dup section's unique content (r392) still present in hot CODELY
assert "- [2026-09-28 08:2x r392 bm-a]" in res_codely
write(ARCHIVE, ours_arch)
print("[2] archive: origin verbatim (dup batch-39 superseded per "
      "origin-first numbering; r392 text preserved in hot; zero-loss "
      "verified)")

# ---- daily_report twins: ours, consistent pair ----
md2, md3 = side(REPORT_MD, 2), side(REPORT_MD, 3)
js2, js3 = side(REPORT_JSON, 2), side(REPORT_JSON, 3)
json.loads(js2), json.loads(js3)          # both parse
write(REPORT_MD, md2)
write(REPORT_JSON, js2)
print("[3] daily_report twins: ours (origin regen, same-side pair law)")

# ---- compute_audit.json: history union by ts-key ----
ca2, ca3 = json.loads(side("results/compute_audit.json", 2)), \
    json.loads(side("results/compute_audit.json", 3))
h2 = ca2.get("history", [])
h3 = ca3.get("history", [])
by = {}
for row in h2 + h3:
    key = row.get("ts")
    if key not in by or str(row) > str(by[key]):
        by[key] = row
union = [by[k] for k in sorted(by)]
res_ca = dict(ca2)
res_ca["history"] = union
write("results/compute_audit.json",
      json.dumps(res_ca, ensure_ascii=False, indent=1) + "\n")
json.load(io.open("results/compute_audit.json", encoding="utf-8"))
print(f"[4] compute_audit history union: {len(h2)}|{len(h3)} -> {len(union)} "
      f"(zero-loss ts-key merge)")

# ---- status faces: take-new by ts ----
for f in STATUS_FACES:
    o = json.loads(side(f, 2))
    t = json.loads(side(f, 3))
    pick = o if ts_of(o) >= ts_of(t) else t
    write(f, json.dumps(pick, ensure_ascii=False, indent=1) + "\n")
    json.load(io.open(f, encoding="utf-8"))
    print(f"[5] {f}: take-new (ours-ts={ts_of(o)[:19]!r} vs "
          f"theirs-ts={ts_of(t)[:19]!r})")

print("resolver OK")
