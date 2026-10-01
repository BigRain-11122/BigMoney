"""r500 bm-b rebase resolver: runnable_pool.json + perpetual_faces_state.json
cherry-pick 7ed9c5d78 conflict (bm-c r307 N1-W5 vs bm-b r500 N3-R1 same-window).

Canon (bigmoney-conflict-resolve skill + r294/r491 laws):
- runnable_pool.json: entries union by id -- disjoint adds (12 W5 origin-side
  + 12 N3 mine); ids present in BOTH sides must be byte-equal content or the
  claim/status face takes the newer semantic (assert-and-inspect, never
  silent). AA product-envelope law r481/r499: only audit-envelope keys
  (elapsed/workers/machine) may differ; science payload must be identical.
- perpetual_faces_state.json: waves[] append-only record union (both waves
  kept); flags/last_supply = newer ts wins (whole-dict, ts compared as
  string ISO, never str()-of-dict).
Resolve-verify-then-write: json.loads validated before write; format mirror
probed from the ours-blob bytes (indent/EOL/trailing).
"""
import json
import subprocess
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"


def blob(stage, path):
    return subprocess.check_output(
        ["git", "-C", ROOT, "show", f":{stage}:{path}"])


def probe(b: bytes):
    indent, crlf, trailing = 2, True, False
    nl = b.count(b"\n")
    crlf = b.count(b"\r\n") >= max(1, nl) // 2
    trailing = b.endswith(b"\n")
    for line in b.decode("utf-8", errors="replace").split("\n"):
        s = line.strip()
        if s.startswith('"'):
            indent = len(line) - len(line.lstrip(" "))
            break
    return indent, crlf, trailing


def write_mirror(path, obj, face):
    indent, crlf, trailing = face
    s = json.dumps(obj, ensure_ascii=False, indent=indent)
    if crlf:
        s = s.replace("\n", "\r\n")
    if trailing and not s.endswith("\n"):
        s += "\r\n" if crlf else "\n"
    with open(path, "wb") as f:
        f.write(s.encode("utf-8"))


def main():
    ok = True
    # ---------------- runnable_pool.json ----------------
    p_pool = "results/runnable_pool.json"
    ours = json.loads(blob(2, p_pool).decode("utf-8"))
    theirs = json.loads(blob(3, p_pool).decode("utf-8"))
    o_ents = {e["id"]: e for e in ours.get("entries", [])}
    t_ents = {e["id"]: e for e in theirs.get("entries", [])}
    both = sorted(set(o_ents) & set(t_ents))
    diffs = []
    for eid in both:
        o, t = o_ents[eid], t_ents[eid]
        if json.dumps(o, sort_keys=True) != json.dumps(t, sort_keys=True):
            # which keys differ?
            keys = {k for k in set(o) | set(t)
                    if json.dumps(o.get(k), sort_keys=True)
                    != json.dumps(t.get(k), sort_keys=True)}
            diffs.append((eid, sorted(keys)))
    print(f"pool: ours={len(o_ents)} theirs={len(t_ents)} shared={len(both)} "
          f"content_diffs={len(diffs)}")
    for eid, keys in diffs[:10]:
        print(f"  DIFF {eid}: {keys}")
    # shared-id diffs: claim/status face takes the NEWER semantic.
    # ours = origin side (bm-c daemon flips kept arriving) -> for status
    # transitions ready->running/done, origin side is by construction the
    # later writer (bm-c daemon committed after my 09:33 commit was made
    # on a pre-origin base). Take OURS for shared ids with status/owner
    # face diffs; assert the diff is confined to the status/owner/audit
    # face (never science payload: id/runner/args/prereg/shards.key).
    allowed = {"status", "owner", "owner_since", "done_at", "done_by",
               "updated_at", "park_note", "entered_at"}
    for eid, keys in diffs:
        if set(keys) - allowed:
            print(f"  ILLEGAL DIFF outside status/owner face: {eid} {keys}")
            ok = False
    merged_ents = dict(o_ents)          # origin side = shared-id winner
    for eid, e in t_ents.items():
        if eid not in merged_ents:      # disjoint add (the N3 twelve)
            merged_ents[eid] = e
    # preserve origin-side entry ORDER for shared ids, append this side's
    # new ids in their commit order (stable, deterministic)
    order = [e["id"] for e in ours.get("entries", [])]
    new_ids = [e["id"] for e in theirs.get("entries", [])
               if e["id"] not in o_ents]
    merged = {"version": ours.get("version", 1),
              "law_ref": ours.get("law_ref"),
              "schema": ours.get("schema"),
              "entries": [merged_ents[i] for i in order + new_ids]}
    merged["updated_at"] = ours.get("updated_at") or theirs.get("updated_at")
    n_n3 = sum(1 for e in merged["entries"]
               if str(e.get("id", "")).startswith("PERPETUAL-N3-"))
    n_w5 = sum(1 for e in merged["entries"]
               if str(e.get("id", "")).startswith("PERPETUAL-N1-W5-"))
    print(f"pool merged: total={len(merged['entries'])} "
          f"N3={n_n3} W5={n_w5}")
    if n_n3 != 12 or n_w5 != 12:
        print("FAIL: expected 12 N3 + 12 W5 entries in union")
        ok = False

    # ---------------- perpetual_faces_state.json ----------------
    p_state = "results/perpetual_faces_state.json"
    so = json.loads(blob(2, p_state).decode("utf-8"))
    st_ = json.loads(blob(3, p_state).decode("utf-8"))
    wo = so.get("waves", [])
    wt = st_.get("waves", [])
    seen = {json.dumps(w, sort_keys=True) for w in wo}
    waves = list(wo) + [w for w in wt
                        if json.dumps(w, sort_keys=True) not in seen]
    lo, lt = so.get("last_supply") or {}, st_.get("last_supply") or {}
    newer = lt if str(lt.get("generated_at") or "") > \
        str(lo.get("generated_at") or "") else lo
    state = {**so, "waves": waves, "last_supply": newer,
             "flags": (st_.get("flags") if str(lt.get("generated_at")
                                               or "") >
                       str(lo.get("generated_at") or "")
                       else so.get("flags"))}
    print(f"state merged: waves={len(waves)} (ours {len(wo)} + theirs "
          f"{len(wt)}, dup-collapsed) last_supply winner ts="
          f"{newer.get('generated_at')}")

    if not ok:
        return 2
    face_pool = probe(blob(2, p_pool))
    face_state = probe(blob(2, p_state))
    write_mirror(f"{ROOT}\\{p_pool}".replace("\\\\", "\\"), merged, face_pool)
    write_mirror(f"{ROOT}\\{p_state}".replace("\\\\", "\\"), state, face_state)
    # post-write parse verify (r185 law)
    json.load(open(f"{ROOT}\\results\\runnable_pool.json", encoding="utf-8"))
    json.load(open(f"{ROOT}\\results\\perpetual_faces_state.json",
                   encoding="utf-8"))
    print("resolve OK: both files re-parsed clean post-write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
