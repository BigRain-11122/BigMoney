"""r485 bm-c merge #4 mini-resolver: 3 UU only (CODELY block-union r675/r479,
compute_audit per-face ts newer-wins r440, token per-key union r456+r466)."""
import json
import os
import re
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
OUTLOG = os.path.join(REPO, "results", "_r485bmc_merge_resolve2_out.txt")
lines = []


def show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                       cwd=REPO, creationflags=CNW)
    if r.returncode != 0:
        raise SystemExit(f"RESOLVER-FAIL: git show {ref}:{path} rc={r.returncode}")
    return r.stdout


def norm_ts(v):
    if not v:
        return None
    return v.strip().replace("T", " ")[:19]


# ---- 1. compute_audit.json: {latest,history} face -- r466 hist-union canon:
# latest = two-side ts probe newer-wins; history = row-level union with
# both-sides containment assertions (latest ts lives nested) ----
CA = "results/compute_audit.json"
o_raw, t_raw = show("HEAD", CA), show("MERGE_HEAD", CA)
o_ca, t_ca = json.loads(o_raw), json.loads(t_raw)


def _latest_ts(d):
    lat = d.get("latest")
    if isinstance(lat, dict):
        for k in ("ts", "generated", "updated", "as_of"):
            v = lat.get(k)
            if isinstance(v, str) and ":" in v:
                return norm_ts(v)
    return norm_ts(d.get("ts") or d.get("generated") or d.get("updated"))


o_ts = _latest_ts(o_ca)
t_ts = _latest_ts(t_ca)
assert o_ts and t_ts, "RESOLVER-FAIL: compute_audit latest ts missing"
o_hist = o_ca.get("history", [])
t_hist = t_ca.get("history", [])
key = lambda r: json.dumps(r, ensure_ascii=False, sort_keys=True)
o_keys, t_keys = {key(r) for r in o_hist}, {key(r) for r in t_hist}
union_rows = list(o_hist) + [r for r in t_hist if key(r) not in o_keys]
assert o_keys <= {key(r) for r in union_rows} and t_keys <= {key(r) for r in union_rows}
winner = dict(o_ca if o_ts >= t_ts else t_ca)
winner["history"] = union_rows
with open(os.path.join(REPO, CA.replace("/", os.sep)), "wb") as f:
    f.write(json.dumps(winner, ensure_ascii=False, indent=1).encode("utf-8"))
json.load(open(os.path.join(REPO, CA), encoding="utf-8"))
lines.append(f"compute_audit: latest ours={o_ts} theirs={t_ts} -> "
             f"{'ours' if o_ts >= t_ts else 'theirs'}; history union "
             f"{len(o_hist)}+{len(t_hist)} -> {len(union_rows)} rows")

# ---- 2. token_usage.json: per-key union (r456) w/ r466 fallback ----
TU = "results/token_usage.json"
o_raw, t_raw = show("HEAD", TU), show("MERGE_HEAD", TU)
o, t = json.loads(o_raw), json.loads(t_raw)
o_m, t_m = o.get("machines", {}), t.get("machines", {})
side_pick = 0
union_m = {}
for k in sorted(set(o_m) | set(t_m)):
    ov, tv = o_m.get(k), t_m.get(k)
    if ov == tv:
        union_m[k] = ov
    elif k not in t_m or k not in o_m:
        union_m[k] = ov if k not in t_m else tv
        side_pick += 1
    else:
        o_ts2 = ov.get("ts") if isinstance(ov, dict) else None
        t_ts2 = tv.get("ts") if isinstance(tv, dict) else None
        if o_ts2 and t_ts2:
            union_m[k] = ov if norm_ts(o_ts2) >= norm_ts(t_ts2) else tv
        else:
            union_m[k] = ov if str(ov) >= str(tv) else tv
        side_pick += 1
o_gen = norm_ts(o.get("generated"))
t_gen = norm_ts(t.get("generated"))
assert o_gen and t_gen, "RESOLVER-FAIL: token faces lack generated ts"
if side_pick == 0:
    winner = o if o_gen >= t_gen else t
    lines.append(f"token: zero side-pick -> whole-face "
                 f"{'ours' if o_gen >= t_gen else 'theirs'} (r466)")
else:
    winner = dict(o if o_gen >= t_gen else t)
    winner["machines"] = union_m
    lines.append(f"token: per-key union side_pick={side_pick}")
with open(os.path.join(REPO, TU.replace("/", os.sep)), "wb") as f:
    f.write(json.dumps(winner, ensure_ascii=False, indent=1).encode("utf-8"))
json.load(open(os.path.join(REPO, TU), encoding="utf-8"))

# ---- 3. CODELY.md block-union (r675 + r479 containment) ----
CO = "CODELY.md"
o_raw, t_raw = show("HEAD", CO), show("MERGE_HEAD", CO)
o_txt, t_txt = o_raw.decode("utf-8"), t_raw.decode("utf-8")
missing = [ln for ln in o_txt.splitlines()
           if ln.strip() and ln not in t_txt]
true_new = [ln for ln in missing if ln not in t_txt]
assert len(true_new) == 1 and "r485 bm-c" in true_new[0], \
    f"RESOLVER-FAIL: CODELY true-new != 1 ({len(true_new)})"
base = t_txt if t_txt.endswith("\n") else t_txt + "\n"
union = base + true_new[0] + "\n"
assert union.startswith(t_txt.rstrip("\n") + "\n") or union.startswith(t_txt)
assert union.count(true_new[0]) == 1
assert not any(ln.startswith(("<<<<<<<", "=======", ">>>>>>>"))
               for ln in union.splitlines())
with open(os.path.join(REPO, CO), "wb") as f:
    f.write(union.encode("utf-8"))
lines.append(f"CODELY union: theirs-preserved (incl r687 pit) + 1 true-new, "
             f"result_lines={len(union.splitlines())}")

# ---- 4. final marker sweep on the 3 resolved faces ----
for p in (CA, TU, CO):
    body = open(os.path.join(REPO, p.replace("/", os.sep)), "rb").read()
    for ln in body.decode("utf-8", "replace").splitlines():
        if ln.startswith(("<<<<<<<", ">>>>>>>")):
            raise SystemExit(f"RESOLVER-FAIL: marker in {p}")
lines.append("marker sweep: clean")

with open(OUTLOG, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines))
print("RESOLVE2_DONE_WROTE", OUTLOG)
