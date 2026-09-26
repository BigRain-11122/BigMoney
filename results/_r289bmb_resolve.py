# -*- coding: utf-8 -*-
"""r289 bm-b rebase resolver (bigmoney-conflict-resolve skill recipes).
Runs at each rebase stop; resolves all UU files by class:
- CODELY.md: merge-base(:1) anchored byte union (r281: base + both append suffixes)
- compute_audit.json / regime_state.json: ledger union zero-loss + take-new scalars
- autofill_state.json (if conflicted): launches union cap50 ts-asc + last_tick by ts (r203/R208/r245)
- snapshots (incl. UNKNOWN-classified regen products): take-new by recursive ts probe (r267,
  T/space normalized, tie->ours stage2 per r140)
- js-wrapper + report md: take the SIDE chosen by their json twin (R209 / producer-pair law)
Byte-safe git reads per R269 (python subprocess, no PS redirection).
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None

TS_KEYS = re.compile(r"^(generated|generated_at|updated|updated_at|ts|at|"
                     r"last_seen|last_round_ts|probe_ts|written_at)$")

def flat_ts(obj, depth=0, path="", acc=None):
    if acc is None: acc = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = path + "." + k if path else k
            if isinstance(v, str) and TS_KEYS.match(k) and len(v) >= 8:
                acc.append((p, v))
            elif isinstance(v, (dict, list)) and depth < 2:
                flat_ts(v, depth + 1, p, acc)
    elif isinstance(obj, list) and depth < 2:
        for i, v in enumerate(obj[:8]):
            flat_ts(v, depth + 1, "%s[%d]" % (path, i), acc)
    return acc

def norm_ts(s):
    return s.replace("T", " ")[:19]

def newer(b2, b3):
    try:
        t2 = [norm_ts(v) for _, v in flat_ts(json.loads(b2.decode("utf-8-sig")))]
        t3 = [norm_ts(v) for _, v in flat_ts(json.loads(b3.decode("utf-8-sig")))]
        m2, m3 = max(t2 or [""]), max(t3 or [""])
        if m3 > m2: return 3
        return 2          # newer or tie -> ours (r140 tie->HEAD; ours=base side in rebase)
    except Exception:
        return 2

def write(path, data):
    with open(path, "wb") as f:
        f.write(data)

def jsonl_bytes(d):
    return json.dumps(d, ensure_ascii=False, indent=1).encode("utf-8")

def union_rows(a, b, keyfn):
    seen, out = set(), []
    for row in a + b:
        k = keyfn(row)
        if k in seen: continue
        seen.add(k)
        out.append(row)
    return out

def conflicted():
    r = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                       text=True, encoding="utf-8")
    return [l[3:] for l in r.stdout.splitlines()
            if l[:2] in ("UU", "AA")]

def resolve():
    files = conflicted()
    if not files:
        print("no UU files -- nothing to do")
        return 0
    report = []
    for path in files:
        b1, b2, b3 = blob(1, path), blob(2, path), blob(3, path)
        if path == "CODELY.md":
            # r281: base-anchored byte union -- r289 law: BOTH sides must be
            # strict base+append (len >= base AND full-prefix identity); a side
            # that compacted/rewrote the file (len < base) makes the head-N
            # probe pass while silently dropping its whole face (resurrection
            # bug live-fire: 8a00f514 compaction reverted by union) -- such
            # sides fall to take-side/manual, never suffix-union.
            assert b1 and b2 and b3, "missing stage blob"
            strict = (len(b2) >= len(b1) and b2.startswith(b1)
                      and len(b3) >= len(b1) and b3.startswith(b1))
            if not strict:
                side = 2 if len(b2) <= len(b3) else 3   # keep compact/newer face
                write(path, blob(side, path))
                report.append((path, "memory compact-face take-side(%d)" % side,
                               "len base=%d ours=%d theirs=%d" %
                               (len(b1), len(b2), len(b3))))
            else:
                s2 = b2[len(b1):]
                s3 = b3[len(b1):]
                out = b1 + s2 + (b"\n" if (s2 and not s2.endswith(b"\n"))
                                 else b"") + s3
                write(path, out)
                report.append((path, "memory-union base-anchored",
                               "base=%dB +ours=%dB +theirs=%dB" %
                               (len(b1), len(s2), len(s3))))
        elif path == "results/compute_audit.json":
            d2 = json.loads(b2.decode("utf-8-sig"))
            d3 = json.loads(b3.decode("utf-8-sig"))
            h2, h3 = d2.get("history", []), d3.get("history", [])
            u = union_rows(h2, h3, lambda r: json.dumps(r, sort_keys=True))
            u.sort(key=lambda r: str(r.get("ts", "")))
            top = d3 if newer(b2, b3) == 3 else d2
            top["history"] = u
            write(path, json.dumps(top, ensure_ascii=False, indent=1).encode("utf-8"))
            report.append((path, "ledger-union", "hist %d+%d->%d" %
                           (len(h2), len(h3), len(u))))
        elif path == "results/regime_state.json":
            d2 = json.loads(b2.decode("utf-8-sig"))
            d3 = json.loads(b3.decode("utf-8-sig"))
            top = d3 if newer(b2, b3) == 3 else d2
            merged = 0
            for k in ("transitions", "history", "launches"):
                if k in d2 or k in d3:
                    a = d2.get(k, []); b = d3.get(k, [])
                    u = union_rows(a, b, lambda r: json.dumps(r, sort_keys=True))
                    merged += len(u) - max(len(a), len(b))
                    top[k] = u
            write(path, json.dumps(top, ensure_ascii=False, indent=1).encode("utf-8"))
            report.append((path, "ledger-union", "merged_extra=%d" % merged))
        elif path == "results/autofill_state.json":
            d2 = json.loads(b2.decode("utf-8-sig"))
            d3 = json.loads(b3.decode("utf-8-sig"))
            l2 = d2.get("launches", []); l3 = d3.get("launches", [])
            u = union_rows(l2, l3, lambda r: json.dumps(r, sort_keys=True))
            u.sort(key=lambda r: str(r.get("ts", "")))       # r245: ts asc write-back
            u = u[-50:] if len(u) > 50 else u                # cap50 keep-newest
            top = d3 if newer(b2, b3) == 3 else d2
            top["launches"] = u
            lt2, lt3 = d2.get("last_tick"), d3.get("last_tick")
            if isinstance(lt2, dict) and isinstance(lt3, dict):
                t2 = norm_ts(str(lt2.get("ts", "")))
                t3 = norm_ts(str(lt3.get("ts", "")))
                top["last_tick"] = lt3 if t3 > t2 else lt2
            assert isinstance(top.get("last_tick"), dict)
            eol = b"\r\n" if b2.find(b"\r\n") >= 0 else b"\n"  # r223 mirror probe
            body = json.dumps(top, ensure_ascii=False, indent=1)
            write(path, (body + "\n").replace("\n", eol.decode()) .encode("utf-8"))
            report.append((path, "mixed-dict+ledger", "launches %d+%d->%d" %
                           (len(l2), len(l3), len(u))))
        else:
            # snapshot family (incl. UNKNOWN-classified regen products) + pairs
            if path.endswith(".jsonl"):
                # append-log: line-level union zero-loss (r188)
                l2 = [l for l in b2.decode("utf-8-sig").splitlines() if l.strip()]
                l3 = [l for l in b3.decode("utf-8-sig").splitlines() if l.strip()]
                seen, u = set(), []
                for l in l2 + l3:
                    if l in seen: continue
                    seen.add(l)
                    u.append(l)
                def lts(l):
                    m = re.search(r'"(ts|at|generated)"\s*:\s*"([^"]+)"', l)
                    return norm_ts(m.group(2)) if m else ""
                try: u.sort(key=lts)
                except Exception: pass
                eol = b"\r\n" if b2.find(b"\r\n") >= 0 else b"\n"
                write(path, eol.join(x.encode("utf-8") for x in u) + eol)
                report.append((path, "append-log line-union",
                               "%d+%d->%d" % (len(l2), len(l3), len(u))))
            elif path.endswith(".js"):
                twin = path[:-3] + ".json"
                side = newer(blob(2, twin), blob(3, twin))
                write(path, blob(side, path))
                report.append((path, "js-wrapper take-side(%d)" % side, ""))
            elif path.endswith("REPORT-2026-09-27.md"):
                twin = path[:-3] + ".json"
                side = newer(blob(2, twin), blob(3, twin))
                write(path, blob(side, path))
                report.append((path, "report-md take-side(%d)" % side, ""))
            else:
                side = newer(b2, b3)
                write(path, blob(side, path))
                report.append((path, "snapshot take-side(%d)" % side, ""))
    # verification gate (r185): every resolved JSON must parse
    for path, recipe, detail in report:
        if path.endswith(".json"):
            json.loads(open(path, "rb").read().decode("utf-8-sig"))
    for path, recipe, detail in report:
        print("RESOLVED %-46s %-28s %s" % (path, recipe, detail))
    for path, _, _ in report:
        subprocess.run(["git", "add", "--", path], capture_output=True)
    return 0

if __name__ == "__main__":
    sys.exit(resolve())
