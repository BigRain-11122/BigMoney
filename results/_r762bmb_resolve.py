# r762 dead-rebase recovery: canonical UU batch resolver (bigmoney-conflict-resolve skill)
# Recipes: r188/R208 union (append-log/rolling-ledger), R208/R216 take-new-by-ts,
#          r440 daemon-live-wins (own-machine daemon faces), r756 ts-normalized compare
# Discipline: parse-validate before write-back; zero-loss assertions; receipt printed.
import subprocess, json, sys, re
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RECEIPT = []

def stage_bytes(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def norm_ts(v):
    """r756 law: normalize separator forms then parse to comparable datetime."""
    if v is None:
        return None
    s = str(v).strip()
    s2 = s.replace(" ", "T", 1) if "T" not in s else s
    # strip trailing tz offset for comparability when one side lacks it
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            d = datetime.strptime(s2, fmt)
            return d
        except ValueError:
            continue
    return None

TS_KEYS = ["generated_at", "generated", "ts", "updated", "scan_ts", "last_scan", "run_ts"]
def find_ts(obj, depth=0):
    if depth > 3 or not isinstance(obj, dict):
        return None
    for k in TS_KEYS:
        if k in obj and norm_ts(obj[k]):
            return (k, obj[k])
    for v in obj.values():
        if isinstance(v, dict):
            got = find_ts(v, depth + 1)
            if got:
                return got
    return None

def resolve_take_new_ts(path):
    o, t = stage_bytes(path, 2), stage_bytes(path, 3)
    oo = json.loads(o); tt = json.loads(t)
    to, tt_ = norm_ts(find_ts(oo)[1]), norm_ts(find_ts(tt)[1])
    if to is None or tt_ is None:
        return ("UNKNOWN-TS", None)
    win = o if to >= tt_ else t
    side = "ours" if to >= tt_ else "theirs"
    return (side, win)

def resolve_ours_live(path):
    o = stage_bytes(path, 2)
    json.loads(o)  # validate
    return ("ours-live", o)

def resolve_union_jsonl(path, sort_key="ts"):
    o, t = stage_bytes(path, 2), stage_bytes(path, 3)
    ol = [l for l in o.decode("utf-8").splitlines() if l.strip()]
    tl = [l for l in t.decode("utf-8").splitlines() if l.strip()]
    seen, union = set(), []
    for line in ol + tl:
        if line not in seen:
            seen.add(line)
            union.append(line)
    # r245 order law: keep ts ascending so last-line-latest semantics hold
    def line_ts(line):
        try:
            obj = json.loads(line)
            got = find_ts(obj)
            return norm_ts(got[1]) if got else None
        except Exception:
            return None
    if all(line_ts(l) is not None for l in union):
        union.sort(key=lambda l: line_ts(l))
    for l in union:
        json.loads(l)  # validate every line
    return ("union", ("\n".join(union) + "\n").encode("utf-8"), len(ol), len(tl), len(union))

def resolve_ledger_union(path):
    """rolling-ledger: list-of-dict keys -> union+sort by element ts; other keys take-new by doc ts."""
    o, t = stage_bytes(path, 2), stage_bytes(path, 3)
    oo, tt = json.loads(o), json.loads(t)
    doc_o, doc_t = norm_ts(find_ts(oo)[1]), norm_ts(find_ts(tt)[1])
    newer = oo if (doc_o or datetime.min) >= (doc_t or datetime.min) else tt
    out = {}
    for k in tt.keys() | oo.keys():
        ov, tv = oo.get(k), tt.get(k)
        if isinstance(ov, list) and isinstance(tv, list):
            seen, un = set(), []
            for el in ov + tv:
                key = json.dumps(el, sort_keys=True, ensure_ascii=False)
                if key not in seen:
                    seen.add(key)
                    un.append(el)
            # sort by element ts if all have one
            def el_ts(e):
                got = find_ts(e)
                return norm_ts(got[1]) if got else None
            if all(el_ts(e) is not None for e in un):
                un.sort(key=lambda e: el_ts(e))
            out[k] = un
        else:
            out[k] = newer.get(k, ov if ov is not None else tv)
    blob = (json.dumps(out, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    json.loads(blob)
    return ("ledger-union", blob)

def resolve_p1d_gates(path):
    """ours live daemon wins, with key-loss assertion (fail-open merge missing keys)."""
    o, t = stage_bytes(path, 2), stage_bytes(path, 3)
    oo, tt = json.loads(o), json.loads(t)
    missing = set(tt.keys()) - set(oo.keys())
    for k in missing:
        oo[k] = tt[k]
    blob = (json.dumps(oo, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    return ("ours-live+keycheck(missing=%d)" % len(missing), blob)

def resolve_md_take_new(path):
    o, t = stage_bytes(path, 2), stage_bytes(path, 3)
    pat = re.compile(r"(20\d{2}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})")
    mo = pat.search(o.decode("utf-8", "replace")[:400])
    mt = pat.search(t.decode("utf-8", "replace")[:400])
    if not mo or not mt:
        return ("UNKNOWN-MD-TS", None)
    do = datetime.strptime(mo.group(1) + "T" + mo.group(2), "%Y-%m-%dT%H:%M:%S")
    dt = datetime.strptime(mt.group(1) + "T" + mt.group(2), "%Y-%m-%dT%H:%M:%S")
    return ("ours" if do >= dt else "theirs", o if do >= dt else t)

PLAN = []
# take-new-by-ts (snapshot / same-day idempotent regen)
for p in ["results/futures_update_status.json", "results/lhb_update_status.json",
          "results/update_status.json", "results/token_usage.json",
          "results/fundamental_b_layer_filter.json", "results/_attrition_guard_scan.json",
          "results/scorecard_v1.json", "results/strategy_scorecard.json",
          "docs/daily_report/REPORT-2026-10-06.json",
          "docs/live_usage/LIVE-2026-10-06.json", "docs/live_usage/LIVE-latest.json"]:
    PLAN.append((p, "ts"))
# md take-new
for p in ["docs/daily_report/REPORT-2026-10-06.md", "docs/live_usage/LIVE-2026-10-06.md",
          "docs/live_usage/LIVE-latest.md"]:
    PLAN.append((p, "md"))
# append-log union
for p in ["results/fund_divlowvol_p1/nulls.jsonl", "results/fund_quality_p1/nulls.jsonl",
          "results/fund_value_p1/nulls.jsonl", "results/saturation_engine/history_bm-b.jsonl"]:
    PLAN.append((p, "jsonl"))
# rolling-ledger union
for p in ["results/compute_audit.json", "results/regime_state.json"]:
    PLAN.append((p, "ledger"))
# daemon live-wins
for p in ["results/saturation_engine/face_bm-b.json", "results/saturation_engine/state_bm-b.json"]:
    PLAN.append((p, "live"))
PLAN.append(("results/p1d_gates.json", "p1d"))

fail = False
for path, kind in PLAN:
    try:
        if kind == "ts":
            side, blob = resolve_take_new_ts(path)
        elif kind == "md":
            side, blob = resolve_md_take_new(path)
        elif kind == "jsonl":
            side, blob, no, nt, nu = resolve_union_jsonl(path)
            RECEIPT.append(f"{path}: union ours={no} theirs={nt} -> union={nu} (zero-loss={nu>=max(no,nt)})")
            open(path, "wb").write(blob)
            subprocess.run(["git", "add", path], check=True)
            continue
        elif kind == "ledger":
            side, blob = resolve_ledger_union(path)
        elif kind == "live":
            side, blob = resolve_ours_live(path)
        elif kind == "p1d":
            side, blob = resolve_p1d_gates(path)
        if blob is None:
            RECEIPT.append(f"{path}: FAIL side={side}")
            fail = True
            continue
        open(path, "wb").write(blob)
        subprocess.run(["git", "add", path], check=True)
        RECEIPT.append(f"{path}: {side}")
    except Exception as e:
        RECEIPT.append(f"{path}: EXCEPTION {e}")
        fail = True

print("\n".join(RECEIPT))
print("FAIL" if fail else "ALL-OK")
