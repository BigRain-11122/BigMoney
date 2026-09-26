# -*- coding: utf-8 -*-
"""R240 bm-a rebase resolver step 2 (14 UU files, canonical recipes per skill).

- CODELY.md                memory-union: base + my appended line (dedupe)
- compute_audit.json       rolling-ledger: history union zero-loss + latest take-new
- regime_state.json        current shape = pure snapshot (no history key) -> take-new by 'updated'
- dashboard_status.json    snapshot take-new; dashboard_status.js whole-bytes SAME side (twin consistency)
- fundamental/futures/heat/lhb/token_usage/update_status snapshot take-new by ts key
- daily_report REPORT.md/.json + daily_scorecard.json generated products: take-mine,
  deterministic regeneration post-rebase (daily_report.py run + daily_scorecard.py)

Format mirror laws: indent per base blob (r230), EOL per base blob (r223/r234),
json.loads parse-verify before write+add (r185).
"""
import json
import subprocess

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def blob(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True,
                       cwd=REPO)
    if r.returncode != 0:
        raise SystemExit(f"git show failed {rev}:{path}: {r.stderr[:150]}")
    return r.stdout


def detect_indent(b):
    for line in b.decode("utf-8").split("\n")[1:6]:
        s = line[: len(line) - len(line.lstrip())]
        if s.strip() == "" and line.strip():
            return len(s)
    return 1


def detect_eol(b):
    return "\r\n" if b"\r\n" in b else "\n"


def write_json(path, obj, base_bytes):
    eol = detect_eol(base_bytes)
    txt = json.dumps(obj, ensure_ascii=False, indent=detect_indent(base_bytes),
                     default=str)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(txt + eol)
    json.load(open(path, encoding="utf-8"))  # parse-verify
    subprocess.run(["git", "add", path], cwd=REPO, check=True)


def ts_of(d):
    for k in ("ts", "updated", "updated_at", "generated", "generated_at",
              "asof"):
        v = d.get(k)
        if isinstance(v, str) and v:
            return v
    if isinstance(d.get("latest"), dict):
        return d["latest"].get("ts") or ""
    if isinstance(d.get("meta"), dict):
        return d["meta"].get("generated_at") or ""
    return ""


def take_new(path):
    b2, b3 = blob(":2", path), blob(":3", path)
    d2, d3 = json.loads(b2), json.loads(b3)
    t2, t3 = ts_of(d2), ts_of(d3)
    winner = "mine" if t3 >= t2 else "base"
    obj, base_bytes = (d3, b3) if winner == "mine" else (d2, b2)
    write_json(path, obj, base_bytes)
    print(f"{path}: take-new -> {winner} (base {t2} vs mine {t3})")


def take_side_bytes(path, side):
    b = blob(side, path)
    with open(path, "wb") as f:
        f.write(b)
    subprocess.run(["git", "add", path], cwd=REPO, check=True)
    print(f"{path}: whole-bytes {side}")


# 1) CODELY.md -- memory-union: base + my appended line (dedupe identical)
P = "CODELY.md"
b2, b3 = blob(":2", P), blob(":3", P)
t2 = b2.decode("utf-8").replace("\r\n", "\n")
t3 = b3.decode("utf-8").replace("\r\n", "\n")
l2 = [l for l in t2.split("\n") if l.strip()]
l3 = [l for l in t3.split("\n") if l.strip()]
seen = set(l2)
added = [l for l in l3 if l not in seen]
union = l2 + [l for l in added]
eol = "\r\n" if b"\r\n" in b2 else "\n"
with open(P, "w", encoding="utf-8", newline="") as f:
    f.write(eol.join(union) + eol)
print(f"CODELY.md: union base {len(l2)} + mine-unique {len(added)} lines")

# 2) compute_audit.json -- history union + latest take-new
P = "results/compute_audit.json"
b2, b3 = blob(":2", P), blob(":3", P)
d2, d3 = json.loads(b2), json.loads(b3)
h2, h3 = d2["history"], d3["history"]
key = [json.dumps(r, sort_keys=True, ensure_ascii=False) for r in h2]
seen = set(key)
union_rows = list(h2)
for r in h3:
    k = json.dumps(r, sort_keys=True, ensure_ascii=False)
    if k not in seen:
        union_rows.append(r)
        seen.add(k)
merged = {**d2}
merged["history"] = union_rows
lt2 = (d2.get("latest") or {}).get("ts", "")
lt3 = (d3.get("latest") or {}).get("ts", "")
merged["latest"] = d3["latest"] if lt3 >= lt2 else d2["latest"]
write_json(P, merged, b2)
print(f"compute_audit: history {len(h2)}+{len(h3)} -> union {len(union_rows)}; "
      f"latest {'mine' if lt3 >= lt2 else 'base'}")

# 3) regime_state.json -- snapshot take-new
take_new("results/regime_state.json")

# 4/5) dashboard twins -- json take-new by meta ts; js whole-bytes same side
P = "results/dashboard_status.json"
b2, b3 = blob(":2", P), blob(":3", P)
d2, d3 = json.loads(b2), json.loads(b3)
t2 = (d2.get("meta") or {}).get("generated_at") or ts_of(d2)
t3 = (d3.get("meta") or {}).get("generated_at") or ts_of(d3)
js_side = ":3" if t3 >= t2 else ":2"
obj, base_bytes = (d3, b3) if t3 >= t2 else (d2, b2)
write_json(P, obj, base_bytes)
print(f"dashboard_status.json: take-new ({'mine' if t3 >= t2 else 'base'} {t3} vs {t2})")
take_side_bytes("results/dashboard_status.js", js_side)

# 6-11) snapshot take-new by ts
for p in ("results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json",
          "results/heat_update_status.json",
          "results/lhb_update_status.json",
          "results/token_usage.json",
          "results/update_status.json"):
    take_new(p)

# 12-14) generated products: take-mine, regenerate post-rebase
for p in ("docs/daily_report/REPORT-20260926.md",
          "docs/daily_report/REPORT-20260926.json",
          "results/daily_scorecard.json"):
    take_side_bytes(p, ":3")

subprocess.run(["git", "add", "CODELY.md"], cwd=REPO, check=True)
print("all 14 resolved + added; parse-verify passed")
