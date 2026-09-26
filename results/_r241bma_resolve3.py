# -*- coding: utf-8 -*-
"""R241 bm-a resolver #3 (rebase onto 0879d9d0, wrap-commit 7 UU files, skill canon).

- compute_audit.json       rolling-ledger: history union zero-loss + latest take-new (r188/R208)
- regime_state.json        snapshot take-new by ts
- dashboard twins           json take-new by meta ts; js whole-bytes SAME side (twin law R209/r226)
- token_usage/update_status snapshot take-new by ts
- daily_report REPORT.md/.json generated: take-mine; S6 daily_report.py run regenerates canonically

Format mirror: indent per base blob (r230), EOL per base blob (r223/r234),
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
    json.load(open(path, encoding="utf-8"))  # r185 parse-verify
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
    print(f"{path}: take-new -> {winner} ({t2} vs {t3})")


# 1) compute_audit.json -- history union + latest take-new
P = "results/compute_audit.json"
b2, b3 = blob(":2", P), blob(":3", P)
d2, d3 = json.loads(b2), json.loads(b3)
h2, h3 = d2["history"], d3["history"]
key = lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False)
seen = set(key(r) for r in h2)
union_rows = list(h2)
for r in h3:
    k = key(r)
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

# 2-5) snapshots
for p in ("results/regime_state.json", "results/token_usage.json",
          "results/update_status.json"):
    take_new(p)

# 6) dashboard twins -- json take-new by meta ts (r226 law: js via twin's meta)
P = "results/dashboard_status.json"
b2, b3 = blob(":2", P), blob(":3", P)
d2, d3 = json.loads(b2), json.loads(b3)
t2 = (d2.get("meta") or {}).get("generated_at") or ts_of(d2)
t3 = (d3.get("meta") or {}).get("generated_at") or ts_of(d3)
js_side = ":3" if t3 >= t2 else ":2"
obj, base_bytes = (d3, b3) if t3 >= t2 else (d2, b2)
write_json(P, obj, base_bytes)
print(f"dashboard_status.json: {'mine' if t3 >= t2 else 'base'} ({t3} vs {t2})")
P = "results/dashboard_status.js"
b = blob(js_side, P)
with open(P, "wb") as f:
    f.write(b)
assert b.startswith(b"window."), "js wrapper must be preserved (R209 law)"
subprocess.run(["git", "add", P], cwd=REPO, check=True)
print(f"dashboard_status.js: whole-bytes {js_side} (wrapper preserved)")

# 7) daily_report generated products -- take-mine, S6 regenerates
for p in ("docs/daily_report/REPORT-2026-09-26.md",
          "docs/daily_report/REPORT-2026-09-26.json"):
    with open(p, "wb") as f:
        f.write(blob(":3", p))
    subprocess.run(["git", "add", p], cwd=REPO, check=True)
    print(f"{p}: take-mine + added")
print("resolver3 done: 7 files")
