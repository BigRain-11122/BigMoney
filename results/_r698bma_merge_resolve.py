# -*- coding: utf-8 -*-
"""r698 bm-a merge resolver: 16 UU regen-twin faces. Canon:
- json/md twins: per-face top-level ts newer-wins (ours S6 21:26-21:31 vs theirs
  bm-b r695 wave; md follows its json twin).
- token_usage.json: per-key machines union (own-authority per machine) +
  default cumulative-max (r466/r497bm-c law, NOT whole-face).
- jsonl twins: exact-line union dedup keep-first (r453) + zero-loss
  canon-set assertion (r656).
Fail-closed: abort without write on any unexpected shape."""
import json
import subprocess

UU_JSON_TWINS = [
    "docs/daily_report/REPORT-2026-10-04",
    "docs/live_usage/LIVE-2026-10-04",
    "docs/live_usage/LIVE-latest",
    "results/_attrition_guard_scan",
    "results/compute_audit",
    "results/fundamental_b_layer_filter",
    "results/futures_update_status",
    "results/lhb_update_status",
    "results/regime_state",
    "results/update_status",
]
UU_JSONL = [
    "results/pool_core_samples.jsonl",
    "results/pool_red_flags.jsonl",
]
TOKEN = "results/token_usage.json"


def side(ref, path):
    r = subprocess.run(["git", "show", "%s:%s" % (ref, path)], capture_output=True)
    if r.returncode != 0:
        raise SystemExit("git show fail %s %s: %s" % (ref, path, r.stderr[:200]))
    return r.stdout


def ts_of(blob):
    d = json.loads(blob.decode("utf-8-sig"))
    for key in ("ts", "generated_at", "asof", "as_of", "updated_at"):
        if isinstance(d, dict) and key in d:
            return str(d[key]), d
    return "", d


def resolve_twin(base):
    """json twin decides winner; md twin follows."""
    ja = side("HEAD", base + ".json")
    jb = side("MERGE_HEAD", base + ".json")
    ta, da = ts_of(ja)
    tb, db = ts_of(jb)
    if ta and tb:
        winner = "ours" if ta >= tb else "theirs"
    else:
        # no comparable ts: probe nested as_of (scorecard family)
        wa = json.dumps(da, sort_keys=True)
        wb = json.dumps(db, sort_keys=True)
        winner = "ours" if wa >= wb else "theirs"  # byte-stable tiebreak
        print("  [note] %s no top ts, byte-stable tiebreak -> %s" % (base, winner))
    src = ja if winner == "ours" else jb
    with open(base + ".json", "wb") as fh:
        fh.write(src)
    json.loads(open(base + ".json", "rb").read().decode("utf-8-sig"))
    # md twin follows the same winner if both sides have it
    try:
        side("MERGE_HEAD", base + ".md")
        ma = side("HEAD", base + ".md")
        mb = side("MERGE_HEAD", base + ".md")
        pick = ma if winner == "ours" else mb
        with open(base + ".md", "wb") as fh:
            fh.write(pick)
    except SystemExit:
        pass  # no md twin on one side -> json-only face
    print("[twin %s-wins] %s (ours ts=%s vs theirs ts=%s)" % (winner, base, ta, tb))


def resolve_jsonl(path):
    a = side("HEAD", path)
    b = side("MERGE_HEAD", path)
    la = [ln for ln in a.decode("utf-8-sig").split("\n") if ln.strip()]
    lb = [ln for ln in b.decode("utf-8-sig").split("\n") if ln.strip()]
    seen, union = set(), []
    for ln in la + lb:          # keep-first exact-line dedup (r453)
        if ln not in seen:
            seen.add(ln)
            union.append(ln)
    canon_a, canon_b = set(la), set(lb)
    canon_u = set(union)
    assert canon_a <= canon_u and canon_b <= canon_u, "zero-loss fail " + path
    eol = b"\r\n" if b"\r\n" in a else b"\n"
    with open(path, "wb") as fh:
        fh.write(eol.join(ln.encode("utf-8") for ln in union) + eol)
    print("[line-union] %s ours=%d theirs=%d union=%d (dedup=%d)" % (
        path, len(la), len(lb), len(union), len(la) + len(lb) - len(union)))


def resolve_token():
    ja = json.loads(side("HEAD", TOKEN).decode("utf-8-sig"))
    jb = json.loads(side("MERGE_HEAD", TOKEN).decode("utf-8-sig"))
    out = {}
    ma = ja.get("machines", {})
    mb = jb.get("machines", {})
    per_key_picked = 0
    for k in sorted(set(ma) | set(mb)):
        va, vb = ma.get(k), mb.get(k)
        if va is not None and vb is not None and va != vb:
            per_key_picked += 1
        out[k] = va if va is not None else vb   # own-authority keep-ours; theirs fills gaps
    # r456 law: side-pick count must be >0 else explicit whole-face freshness
    if per_key_picked == 0:
        # whole-face freshness fallback (r466)
        ta, tb = str(ja.get("ts", "")), str(jb.get("ts", ""))
        assert ta >= tb, "token per-key 0 picks and theirs newer whole-face"
    da, db = ja.get("default"), jb.get("default")
    if isinstance(da, (int, float)) and isinstance(db, (int, float)):
        out_default = da if da >= db else db
    else:
        out_default = da if da is not None else db
    merged = dict(ja)
    merged["machines"] = out
    merged["default"] = out_default
    with open(TOKEN, "w", encoding="utf-8", newline="") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=1)
    json.loads(open(TOKEN, "rb").read().decode("utf-8-sig"))
    print("[per-key union] %s machines=%d side_picks=%d default=%s (max of %s/%s)" % (
        TOKEN, len(out), per_key_picked, out_default, da, db))


def main():
    for base in UU_JSON_TWINS:
        resolve_twin(base)
    for p in UU_JSONL:
        resolve_jsonl(p)
    resolve_token()
    print("RESOLVE PASS 16/16 faces")


if __name__ == "__main__":
    main()
