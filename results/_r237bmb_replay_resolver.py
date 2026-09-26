# -*- coding: utf-8 -*-
# r237 bm-b rebase resolver (TEMP copy per r231 law: resolver must exist outside repo during replay)
# Handles the 3-commit replay conflict batch vs origin/main (bm-a R238 chain):
#  - ticket add/add (73 yield->renumber 76)
#  - rolling-ledger unions (compute_audit history, regime history/transitions, post_review.jsonl, autofill launches cap50)
#  - snapshot take-new (dashboard twins by twin ts, *_status by named ts key, token_usage, REPORT by ts)
#  - mixed autofill last_tick whole-dict take-new (r203 law: no str() compare)
# Every write probes base-blob CRLF + indent per file (r223/r234 newline law + r237 indent law).
import json, io, sys

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"

def probe(b: bytes):
    crlf = b.count(b"\r\n"); lf = b.count(b"\n") - crlf
    nl = "\r\n" if crlf > 0 and crlf >= lf else "\n"
    # indent: count leading spaces of second line
    lines = b.decode("utf-8", errors="replace").splitlines()
    ind = 1
    for l in lines[1:6]:
        s = l[:8]
        if s.strip():
            ind = len(s) - len(s.lstrip(" "))
            break
    return nl, ind

def load(path):
    return json.load(io.open(path, encoding="utf-8-sig"))

def save(path, obj):
    b = open(path, "rb").read()
    nl, ind = probe(b)
    raw = json.dumps(obj, indent=ind, ensure_ascii=False)
    if nl == "\r\n":
        raw = raw.replace("\n", "\r\n")
    with open(path, "wb") as f:
        f.write(raw.encode("utf-8"))

def save_raw_lines(path, lines):
    b = open(path, "rb").read()
    nl, ind = probe(b)
    with open(path, "wb") as f:
        f.write(nl.join(lines).encode("utf-8") + (nl.encode if False else b""))

def resolve_autofill(ours_path, theirs_path, out_path):
    """ours = base/origin side file, theirs = replay side (mine). Union launches cap50, last_tick take-new inner ts, all other keys take-new by presence."""
    a = load(ours_path); b = load(theirs_path)
    out = dict(b)  # start from mine (replay side carries the newest local tick)
    # union launches by (ts, entry) identity, sort ts, cap 50
    lau = {json.dumps(l, sort_keys=True, ensure_ascii=False) for l in a.get("launches", [])}
    lau |= {json.dumps(l, sort_keys=True, ensure_ascii=False) for l in b.get("launches", [])}
    L = [json.loads(x) for x in lau]
    L.sort(key=lambda x: x.get("ts", ""))
    out["launches"] = L[-50:]
    # last_tick: whole-dict take-new by inner ts (r203), tie -> ours/HEAD(base) side
    lt_a, lt_b = a.get("last_tick", {}), b.get("last_tick", {})
    ta, tb = str(lt_a.get("ts", "")), str(lt_b.get("ts", ""))
    out["last_tick"] = lt_b if tb > ta else lt_a
    assert isinstance(out["last_tick"], dict)
    save(out_path, out)
    return len(out["launches"]), out["last_tick"].get("ts")

def resolve_ledger(ours_path, theirs_path, out_path, ledger_key, ts_field="ts"):
    """union list-of-dicts by ts(+extra id) identity, keep latest-block other keys take-new"""
    a = load(ours_path); b = load(theirs_path)
    out = dict(b)
    la, lb = a.get(ledger_key, []), b.get(ledger_key, [])
    seen = {}
    for r in la + lb:
        k = str(r.get(ts_field, "")) + "|" + str(r.get("machine", r.get("id", "")))[:24]
        if k not in seen or str(r.get(ts_field, "")) >= str(seen[k].get(ts_field, "")):
            seen[k] = r
    merged = sorted(seen.values(), key=lambda r: str(r.get(ts_field, "")))
    out[ledger_key] = merged
    save(out_path, out)
    return len(la), len(lb), len(merged)

def resolve_jsonl_union(ours_path, theirs_path, out_path):
    """line-level union zero-loss for append-log jsonl"""
    A = [l for l in io.open(ours_path, encoding="utf-8-sig").read().splitlines() if l.strip()]
    B = [l for l in io.open(theirs_path, encoding="utf-8-sig").read().splitlines() if l.strip()]
    seen = set(); lines = []
    for l in A + B:
        if l not in seen:
            seen.add(l); lines.append(l)
    b0 = open(out_path, "rb").read()
    nl, _ = probe(b0)
    with open(out_path, "wb") as f:
        f.write((nl.join(lines) + nl).encode("utf-8"))
    return len(A), len(B), len(lines)

def resolve_snapshot_take_new(ours_path, theirs_path, out_path, ts_key="ts", nested=None):
    """take newer side by ts_key (top or nested list of candidates); equal -> ours(base) per r140."""
    a = load(ours_path); b = load(theirs_path)
    def g(d):
        if nested:
            cur = d
            for k in nested: cur = (cur or {}).get(k, {})
            return str(cur.get(ts_key, ""))
        return str(d.get(ts_key, ""))
    pick = b if g(b) > g(a) else a
    save(out_path, pick)
    return g(a), g(b), ("theirs" if g(b) > g(a) else "ours")

def resolve_js_take_side(ours_path, theirs_path, out_path, twin_path):
    """dashboard js: decide by .json twin meta.generated_at, take WHOLE BYTES of chosen side (r226)."""
    import re
    def gen(p):
        t = io.open(p, encoding="utf-8-sig", errors="replace").read()
        m = re.search(r'"generated_at"\s*:\s*"([^"]+)"', t)
        return m.group(1) if m else ""
    ga, gb = gen(twin_path + ".json"), None
    # twin decision must use the two SIDES of the twin too; caller passes side-specific twins via same resolution on .json first
    return None

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "autofill":
        print(resolve_autofill(sys.argv[2], sys.argv[3], sys.argv[4]))
    elif cmd == "ledger":
        print(resolve_ledger(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
    elif cmd == "jsonl":
        print(resolve_jsonl_union(sys.argv[2], sys.argv[3], sys.argv[4]))
    elif cmd == "snap":
        print(resolve_snapshot_take_new(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "ts"))
    elif cmd == "snapnested":
        print(resolve_snapshot_take_new(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6].split(".")))
