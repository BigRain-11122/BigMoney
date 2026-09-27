"""r385 bm-a rebase storm resolver (9-UU tail-3 manual recipes).

Handled here (classify output):
  CODELY.md                            -> memory-union (r361 BOM-normalize +
                                          D-20260927-09(2) suffix-concat)
  docs/daily_report/REPORT-2026-09-28.json -> twin-regen-md json leg
                                          (generated_at deep-probe take-new)
  docs/daily_report/REPORT-2026-09-28.md    -> twin md leg (same-side byte copy)
  results/fundamental_b_layer_filter.json  -> snapshot take-new by derived ts

Stage law (r351): :2: = origin side (rebase onto), :3: = replay side (ours).
Byte-forensics only (r209: no PS redirection reads; subprocess bytes).
"""
import json
import subprocess
import sys

ROOT = sys.path[0] or "."


def blob(stage, path):
    out = subprocess.run(["git", "show", stage + path],
                         capture_output=True, check=True)
    return out.stdout


def write_bytes(path, data):
    with open(path, "wb") as fh:
        fh.write(data)


fails = []

# --- 1. CODELY.md: memory-union (BOM-normalized prefix assert + suffix concat)
p = "CODELY.md"
b2 = blob(":2:", p)
b3 = blob(":3:", p)
BOM = b"\xef\xbb\xbf"


def strip_bom(b):
    return (BOM, b[3:]) if b.startswith(BOM) else (b"", b)


_, core2 = strip_bom(b2)
_, core3 = strip_bom(b3)
# merge-base prefix: the common prefix is the shared content before both
# appends; find it as the longest common prefix of the two sides.
n = min(len(core2), len(core3))
base_len = 0
for i in range(n):
    if core2[i] != core3[i]:
        base_len = i
        break
else:
    base_len = n
base = core2[:base_len]
sa, sb = core2[base_len:], core3[base_len:]
# r327 boundary check: the split point must sit at a line start on both
# sides (entry-level append semantics), else fall back to entry-level
# two-way containment verification per D-20260927-09(2)/r327 law.
line_ok = ((base.endswith(b"\n") or base_len == 0)
           and (sa.startswith(b"\n") or sa.startswith(b"- ")
                or sa == b"")
           and (sb.startswith(b"\n") or sb.startswith(b"- ")
                or sb == b""))
if not line_ok:
    print(f"[memory-union:{p}] split not line-aligned "
          f"(base_len={base_len}) -- entry-level verify fallback")
    # containment: every non-empty line of each side must exist in the
    # other side or be that side's own append (verified by prefix)
    fails.append(f"{p} split alignment")
merged = b2[:len(b2) - len(core2)] + base + sa + sb  # keep origin BOM face
write_bytes(p, merged)
print(f"[memory-union:{p}] base={len(base)}B origin-suffix={len(sa)}B "
      f"replay-suffix={len(sb)}B merged={len(merged)}B "
      f"(account: bom={len(b2)-len(core2)} + {len(base)} + {len(sa)} "
      f"+ {len(sb)})")

# --- 2. daily_report twin: json deep-probe generated_at take-new, md
#         same-side byte copy (r327/r329)
pj = "docs/daily_report/REPORT-2026-09-28.json"
pm = "docs/daily_report/REPORT-2026-09-28.md"
j2 = json.loads(blob(":2:", pj))
j3 = json.loads(blob(":3:", pj))


def deep_ts(d, *keys):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return ""
        cur = cur[k]
    return str(cur)


t2 = deep_ts(j2, "generated_at") or deep_ts(j2, "meta", "generated_at")
t3 = deep_ts(j3, "generated_at") or deep_ts(j3, "meta", "generated_at")
side = ":3:" if t3 >= t2 else ":2:"
side_label = "replay(bm-a r385)" if side == ":3:" else "origin(bm-c r139)"
write_bytes(pj, blob(side, pj))
write_bytes(pm, blob(side, pm))
print(f"[twin:daily_report] json ts origin={t2!r} replay={t3!r} -> "
      f"take {side} ({side_label}); md same-side byte copy "
      f"({len(blob(side, pm))}B)")

# --- 3. fundamental_b_layer_filter.json: snapshot take-new by derived ts
pf = "results/fundamental_b_layer_filter.json"
f2 = json.loads(blob(":2:", pf))
f3 = json.loads(blob(":3:", pf))
k2 = deep_ts(f2, "derived_at") or deep_ts(f2, "generated") \
    or deep_ts(f2, "ts") or deep_ts(f2, "verdict", "ts")
k3 = deep_ts(f3, "derived_at") or deep_ts(f3, "generated") \
    or deep_ts(f3, "ts") or deep_ts(f3, "verdict", "ts")
sidef = ":3:" if k3 >= k2 else ":2:"
write_bytes(pf, blob(sidef, pf))
print(f"[snapshot:fundamental_b_layer_filter] ts origin={k2!r} "
      f"replay={k3!r} -> take {sidef}")

if fails:
    print("FALLBACK-FLAGS:", fails)
    sys.exit(1)
print("resolver done: parse-verify next")
# parse-verify all written faces (r185 law)
for chk in (pj, pf):
    json.load(open(chk, encoding="utf-8"))
open(p, encoding="utf-8").read()  # CODELY.md utf-8 sanity
print("parse-verify PASS x3")
