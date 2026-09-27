# -*- coding: utf-8 -*-
"""r333 bm-b push-collision resolver (rebase replay of dcaa14ff vs origin 6-commit window).

Mirror of results/_r330bmb_resolve.py (same file family, proven manual verdicts)
with r334/r335 refinements: future-sentinel in deep_ts (ts > now skipped --
plan-face fields never win a take-side pick), T-form normalization BEFORE
compare (T 0x54 > space 0x20), all paths DERIVED from git ls-files output
(byte-exact, no hand-typed path strings), fail-closed coverage assert.

Side map (rebase): :1=base, :2=ours(HEAD=origin landed face), :3=theirs(MY
replaying commit dcaa14ff).
Recipes per SKILL.md: rolling-ledger union (r188/R208) + js-wrapper whole-bytes
(R209) + append-log line union (r188/r217) + coupled paper/export side (r85)
+ daily_report twins coupled via json-ts probe + snapshot take-new deep-ts
(tie->HEAD r140).
"""
import datetime
import io
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def git(*a):
    return subprocess.run(["git", *a], capture_output=True).stdout


def blobs(path):
    return git("show", f":1:{path}"), git("show", f":2:{path}"), git("show", f":3:{path}")


def deep_ts(obj):
    best = [""]
    KEYS = ("ts", "generated", "generated_at", "updated", "updated_at", "asof",
            "last_run", "written_at")

    def scan(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in KEYS and isinstance(v, str) and len(v) >= 16:
                    nv = v.replace(" ", "T")[:19]     # r335: normalize T-form first
                    if nv > NOW:
                        continue                      # r334: future sentinel
                    if nv > best[0]:
                        best[0] = nv
                scan(v)
        elif isinstance(o, list):
            for v in o:
                scan(v)
    scan(obj)
    return best[0]


def take_new_json(path):
    b, o, t = blobs(path)
    jo, jt = json.loads(o), json.loads(t)
    so, st = deep_ts(jo), deep_ts(jt)
    win = "ours(:2)" if (so, "") >= (st, "") else "theirs(:3)"  # tie -> HEAD
    data = jo if win.startswith("ours") else jt
    nb = b"\r\n" if b"\r\n" in b else b"\n"
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1)
                + ("\r\n" if nb == b"\r\n" else "\n"))
    json.loads(io.open(path, encoding="utf-8").read())
    print(f"  {path}: take_new {win} ts_ours={so or '-'} ts_theirs={st or '-'}")


uu = [l.decode().strip() for l in subprocess.run(
    ["git", "diff", "--name-only", "--diff-filter=U"],
    capture_output=True).stdout.splitlines() if l.strip()]
print("UU files:", len(uu))
assert len(uu) == 27, f"expected 27 UU, got {len(uu)}: {uu}"

verdicts = []
PAPER = sorted(p for p in uu if p.startswith("results/paper/"))
EXPORT = sorted(p for p in uu if p.startswith("results/paper_export/"))
DAILY = sorted(p for p in uu if p.startswith("docs/daily_report/REPORT-"))
X2 = [p for p in uu if p.endswith(".jsonl")]
JS = [p for p in uu if p.endswith(".js")]
ROLL = [p for p in uu if p in ("results/compute_audit.json", "results/regime_state.json")]

# ---------------------------------------------------- 1. rolling-ledger union
def rolling_union(path, ledger_keys):
    b, o, t = blobs(path)
    jo, jt = json.loads(o), json.loads(t)
    out = dict(jo)
    for lk in ledger_keys:
        lo, lt = jo.get(lk, []), jt.get(lk, [])
        if not isinstance(lo, list) or not isinstance(lt, list):
            continue

        def k(r):
            return tuple(r.get(f) if isinstance(r, dict) else r
                         for f in ("ts", "machine", "pid", "runner_sha256",
                                   "entry", "shard", "asof"))  # r334: asof=regime rows' time key (ts-only tuple collapsed 2+2->1, row loss)
        seen, un = {}, []
        for r in lo + lt:
            kk = k(r)
            if kk not in seen:
                seen[kk] = r
                un.append(r)
        try:
            un.sort(key=lambda r: (r.get("ts") or r.get("asof") or "")
                    if isinstance(r, dict) else "")
        except Exception:
            pass
        out[lk] = un
        print(f"  {path}[{lk}]: |ours|={len(lo)} |theirs|={len(lt)} -> union={len(un)}")
    so, st = deep_ts(jo), deep_ts(jt)
    pick = jo if (so, "") >= (st, "") else jt
    for k in set(jo) | set(jt):
        if k not in ledger_keys:
            out[k] = pick.get(k, jo.get(k, jt.get(k)))
    print(f"  {path}: snapshot take_new ts_ours={so or '-'} ts_theirs={st or '-'}")
    nb = b"\r\n" if b"\r\n" in b else b"\n"
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1)
                + ("\r\n" if nb == b"\r\n" else "\n"))
    json.loads(io.open(path, encoding="utf-8").read())
    verdicts.append((path, "rolling-ledger union + snapshot take-new"))

for p in ROLL:
    rolling_union(p, ("history", "transitions") if "regime" in p else ("history",))

# ---------------------------------------------------- 2. js-wrapper whole bytes
for p in JS:
    b, o, t = blobs(p)
    mo = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$", o.decode("utf-8"), re.S)
    mt = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$", t.decode("utf-8"), re.S)
    so = deep_ts(json.loads(mo.group(1))) if mo else ""
    st = deep_ts(json.loads(mt.group(1))) if mt else ""
    data = o if (so, "") >= (st, "") else t
    with io.open(p, "wb") as f:
        f.write(data)
    print(f"  {p}: js-wrapper take-side whole bytes ({'ours' if data is o else 'theirs'})"
          f" ts {so or '-'} vs {st or '-'}")
    verdicts.append((p, "js-wrapper whole-bytes take-side"))

# ---------------------------------------------------- 3. append-log line union
for p in X2:
    b, o, t = blobs(p)
    bl = b.decode("utf-8").splitlines()
    ol, tl = o.decode("utf-8").splitlines(), t.decode("utf-8").splitlines()
    seen = set(bl)
    out = list(bl)
    n_o = n_t = 0
    for l in ol:
        if l and l not in seen:
            seen.add(l)
            out.append(l)
            n_o += 1
    for l in tl:
        if l and l not in seen:
            seen.add(l)
            out.append(l)
            n_t += 1
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + ("\n" if out else ""))
    print(f"  {p}: line union base={len(bl)} +ours {n_o} +theirs {n_t} -> {len(out)}")
    verdicts.append((p, f"append-log line union +{n_o}+{n_t}"))

# ------------------------------------------- 4. paper+export coupled same side
side_ts = {"ours": "", "theirs": ""}
for p in PAPER:
    b, o, t = blobs(p)
    side_ts["ours"] = max(side_ts["ours"], deep_ts(json.loads(o)))
    side_ts["theirs"] = max(side_ts["theirs"], deep_ts(json.loads(t)))
win = "ours" if (side_ts["ours"], "") >= (side_ts["theirs"], "") else "theirs"
for p in PAPER + EXPORT:
    b, o, t = blobs(p)
    with io.open(p, "wb") as f:
        f.write(o if win == "ours" else t)
    json.loads(io.open(p, encoding="utf-8").read())
print(f"  paper x{len(PAPER)}+export x{len(EXPORT)}: coupled side={win} "
      f"(ts {side_ts['ours'] or '-'} vs {side_ts['theirs'] or '-'})")
verdicts.append(("results/paper/*_paper.json+paper_export/*",
                 f"coupled-side {win} whole-bytes x{len(PAPER)+len(EXPORT)}"))

# ------------------------------------------- 5. daily_report twins coupled side
if DAILY:
    pj = [p for p in DAILY if p.endswith(".json")][0]
    b, o, t = blobs(pj)
    so, st = deep_ts(json.loads(o)), deep_ts(json.loads(t))
    win2 = "ours" if (so, "") >= (st, "") else "theirs"
    for p in DAILY:
        b, o, t = blobs(p)
        with io.open(p, "wb") as f:
            f.write(o if win2 == "ours" else t)
    json.loads(io.open(pj, encoding="utf-8").read())
    print(f"  daily_report twins: coupled side={win2} (json ts {so or '-'} vs {st or '-'})")
    verdicts.append(("docs/daily_report/REPORT-2026-09-27.*",
                     f"coupled-side {win2} via json ts probe"))

# ------------------------------------------- 6. remainder = snapshot take-new
special = set(ROLL) | set(JS) | set(X2) | set(PAPER) | set(EXPORT) | set(DAILY)
rest = [p for p in uu if p not in special]
for p in rest:
    take_new_json(p)
    verdicts.append((p, "snapshot take-new deep-ts future-sentinel (tie->HEAD)"))

covered = set()
for v in verdicts:
    covered.add(v[0])
covered.update(PAPER)
covered.update(EXPORT)
covered.update(DAILY)
missing = [p for p in uu if p not in covered]
assert not missing, f"UNRESOLVED: {missing}"
print(f"\nALL {len(uu)} UU RESOLVED ({len(verdicts)} verdict lines):")
for p, v in verdicts:
    print("  -", p, "::", v)
print("RESOLVE-OK")
