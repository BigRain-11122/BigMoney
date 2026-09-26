# _r293bma_resolve.py -- r293 bm-a push-rejection rebase UU resolver (canonical, full batch)
# Window: replaying 23e9a44c (round-293 S6 chain) onto origin/main fc746e7c (bm-b
# same-window S6 chain). 28 UU. Parent commit fe251ac7 (autofill claim) carries a
# marker-poisoned results/autofill_state.json blob (first resolver crashed on a
# junk assert BEFORE write-back -> staged markers -> committed; lesson recorded).
# This resolver: autofill_state = union(origin/main fc746e7c, 23e9a44c) ignoring
# the poisoned ours-side; every other file by classifier recipe:
#   jsonl -> line union | dashboard_status.js -> take-side whole byte |
#   json snapshot -> take-newer by named ts key (fallback: theirs = later regen)
# WRITE FIRST, ASSERT AFTER (r293 lesson); parse-verify before write-back (r185).
import json
import re
import subprocess
import sys

TS_KEYS = ("ts", "generated", "asof", "updated_at", "updated", "date",
           "last_tick_ts", "written_at")


def blob(rev, path):
    spec = f"{rev}{path}" if rev.startswith(":") else f"{rev}:{path}"
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def ours_theirs(path):
    return blob(":2:", path), blob(":3:", path)


def write_bytes(path, data):
    with open(path, "wb") as fh:
        fh.write(data)


def resolve_autofill():
    PATH = "results/autofill_state.json"
    A = json.loads(blob("fc746e7c", PATH))          # origin/main (bm-b)
    C = json.loads(blob("23e9a44c", PATH))          # my S6 capture (superset of claim)
    key = lambda r: (r.get("ts"), r.get("entry"), r.get("shard"),
                     r.get("pid"), r.get("verdict"))
    seen = {}
    for r in A.get("launches", []) + C.get("launches", []):
        seen[key(r)] = r
    union = sorted(seen.values(), key=lambda r: r.get("ts", ""),
                   reverse=True)[:50]
    union.sort(key=lambda r: r.get("ts", ""))       # r245 write-back ts ASC
    lt_a = A.get("last_tick") or {}
    lt_c = C.get("last_tick") or {}
    last_tick = lt_c if (lt_c.get("ts", "") >= lt_a.get("ts", "")) else lt_a
    merged = dict(A)
    merged.update({k: v for k, v in C.items() if k not in ("launches",
                                                           "last_tick")})
    merged["launches"] = union
    merged["last_tick"] = last_tick
    txt = json.dumps(merged, ensure_ascii=False, indent=1)
    if b"\r\n" in (blob("fc746e7c", PATH) or b"\n"):  # CRLF mirror (r223)
        txt = txt.replace("\n", "\r\n")
    write_bytes(PATH, txt.encode("utf-8"))
    rt = json.load(open(PATH, encoding="utf-8"))
    assert isinstance(rt.get("last_tick"), dict), "last_tick not a dict"
    assert len(rt["launches"]) <= 50
    print(f"autofill_state: union {len(A.get('launches', []))}+"
          f"{len(C.get('launches', []))} -> {len(union)} (cap50 ASC); "
          f"last_tick ts={last_tick.get('ts')} [poisoned ours-side ignored]")


def ts_of(obj):
    for k in TS_KEYS:
        v = obj.get(k) if isinstance(obj, dict) else None
        if isinstance(v, str) and len(v) >= 8:
            return v
    return None


def resolve_json_snapshot(path):
    o, t = ours_theirs(path)
    try:
        jo, jt = json.loads(o), json.loads(t)
    except Exception as ex:
        print(f"  {path}: PARSE FAULT ({ex}) -> take theirs whole")
        write_bytes(path, t)
        return
    to, tt = ts_of(jo), ts_of(jt)
    if to is None or tt is None:
        pick, why = t, "ts missing -> theirs (later regen face)"
    else:
        pick, why = (t, f"theirs newer ({tt} > {to})") if tt >= to \
            else (o, f"ours newer ({to} > {tt})")
    write_bytes(path, pick)
    json.loads(open(path, "rb").read())             # parse-verify (r185)
    print(f"  {path}: {why}")


def resolve_jsonl(path):
    o, t = ours_theirs(path)
    lo = [ln for ln in (o or b"").decode("utf-8", "replace").splitlines()
          if ln.strip()]
    lt = [ln for ln in (t or b"").decode("utf-8", "replace").splitlines()
          if ln.strip()]
    seen = list(dict.fromkeys(lo + lt))             # union, order-preserving
    nl = "\r\n" if (o and b"\r\n" in o) else "\n"
    write_bytes(path, (nl.join(seen) + nl).encode("utf-8"))
    print(f"  {path}: union {len(lo)}+{len(lt)} -> {len(seen)} lines")


def main():
    st = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                       text=True).stdout
    uu = [ln[3:].strip() for ln in st.splitlines()
          if ln.startswith("UU") or ln.startswith("AA")]
    print(f"UU/AA batch: {len(uu)}")
    resolve_autofill()
    for p in sorted(uu):
        if p == "results/autofill_state.json":
            continue
        if p.endswith(".jsonl"):
            resolve_jsonl(p)
        elif p == "results/dashboard_status.js":
            _, t = ours_theirs(p)                   # js-wrapper: take-side
            write_bytes(p, t)
            print(f"  {p}: js-wrapper take-side (theirs, later build)")
        elif p.endswith(".json"):
            resolve_json_snapshot(p)
        else:
            _, t = ours_theirs(p)
            write_bytes(p, t)
            print(f"  {p}: non-json take-side (theirs)")
    # post-write tree-wide marker scan (r293 poison lesson)
    bad = []
    for p in [ln[3:].strip() for ln in st.splitlines()
              if ln.startswith("UU") or ln.startswith("AA")]:
        txt = open(p, "rb").read().decode("utf-8", "replace")
        if re.search(r"^(<{7}|>{7}|={7})", txt, re.M):
            bad.append(p)
    if bad:
        print("MARKER RESIDUE:", bad)
        sys.exit(1)
    print("all resolved; zero marker residue")


if __name__ == "__main__":
    main()
