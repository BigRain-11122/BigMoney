"""r965 bm-a rebase conflict resolver - 37 UU faces (same-window dual S6 chain writes).

Law anchors: r351 (three-stage read, :2:=origin/ours base, :3:=theirs=local replay),
r140 (same-second tie -> HEAD), r209 (subprocess bytes, real git path),
r311/D-09 (ts deep-scan nested), r223/r234 (byte-side mirror, no reserialize when possible).

Shapes:
- .jsonl            -> line-level union
- .md               -> take side bytes chosen by twin json ts (CALL md is twin of call_latest.json)
- snapshot json     -> deep-ts newer side; tie -> :2:; equal bytes -> either
- ledger list       -> per-row fingerprint union; rows keyed by date-like unique key -> dedup by key, newer side wins
"""
import subprocess, json, sys

G = r"C:\Program Files\Git\cmd\git.exe"
APPLY = "--apply" in sys.argv

TS_KEYS = ["updated", "ts", "as_of", "cutoff", "generated", "generated_at",
           "updated_at", "last_run", "asof", "date", "generated_utc"]

def git(args):
    r = subprocess.run([G] + args, capture_output=True)
    return r.stdout

def blob(sha):
    return git(["cat-file", "blob", sha])

def deep_ts(obj, depth=0):
    """Deep-scan for the first ts-like value; return (key_path, value) or None."""
    if depth > 4 or not isinstance(obj, dict):
        return None
    for k in TS_KEYS:
        if k in obj and isinstance(obj[k], str) and len(obj[k]) >= 8:
            return (k, obj[k])
    for k in ("latest", "last_tick", "status", "summary", "meta"):
        v = obj.get(k)
        if isinstance(v, dict):
            r = deep_ts(v, depth + 1)
            if r:
                return (k + "." + r[0], r[1])
    return None

def uniq_key_of(row):
    """Fingerprint of a ledger row (sorted scalar items)."""
    return json.dumps(row, sort_keys=True, ensure_ascii=False)

def resolve_rows(a, b):
    """Union of two list-of-dict rows. Date-keyed rows dedup by date key, newer side wins.
    Returns (merged_rows, note)."""
    if not (isinstance(a, list) and isinstance(b, list)):
        return None
    rows_a = [x for x in a if isinstance(x, dict)]
    rows_b = [x for x in b if isinstance(x, dict)]
    if not rows_a and not rows_b:
        return None
    # date-like unique key present in both sides' rows?
    keyf = None
    for cand in ("date", "ts", "day", "as_of", "cutoff", "id"):
        if rows_a and rows_b and all(cand in r for r in rows_a) and all(cand in r for r in rows_b):
            keyf = cand
            break
    if keyf and keyf != "ts" or (keyf == "ts" and keyf in (rows_a[0] if rows_a else {})):
        if keyf == "ts":
            pass  # ts-keyed also dedup by value below
    if keyf:
        mapA = {r[keyf]: r for r in rows_a}
        mapB = {r[keyf]: r for r in rows_b}
        merged = {}
        collisions = 0
        for k in set(mapA) | set(mapB):
            ra, rb = mapA.get(k), mapB.get(k)
            if ra is not None and rb is not None and ra != rb:
                collisions += 1
                ta = deep_ts(ra) or (None, "")
                tb = deep_ts(rb) or (None, "")
                merged[k] = rb if (tb[1] or "") >= (ta[1] or "") else ra
            else:
                merged[k] = ra if ra is not None else rb
        ordered = [merged[k] for k in sorted(merged, key=str)]
        return (ordered, f"key-dedup[{keyf}] coll={collisions}")
    # fingerprint union
    seen, out = set(), []
    for r in rows_a + rows_b:
        fp = uniq_key_of(r)
        if fp not in seen:
            seen.add(fp)
            out.append(r)
    return (out, f"fp-union in={len(rows_a)}+{len(rows_b)} out={len(out)}")

def merge_dict(a, b, note=""):
    """Key-level union; lists via resolve_rows; scalars: equal or newer-ts side."""
    out = {}
    for k in sorted(set(a) | set(b)):
        va, vb = a.get(k), b.get(k)
        if va is None: out[k] = vb
        elif vb is None: out[k] = va
        elif va == vb: out[k] = va
        elif isinstance(va, dict) and isinstance(vb, dict):
            out[k] = merge_dict(va, vb)
        elif isinstance(va, list) and isinstance(vb, list):
            rr = resolve_rows(va, vb)
            if rr:
                out[k] = rr[0]
            else:
                out[k] = va  # scalar list, take ours (r140 tie semantics)
                note += f" list-scalar-{k}"
        else:
            # scalar conflict -> deep ts on the smallest enclosing value
            out[k] = vb if k in TS_KEYS and str(vb) >= str(va) else va if k in TS_KEYS else va
    return out, note

def pick_newer_side(da, db, path):
    ta, tb = deep_ts(da), deep_ts(db)
    if ta and tb:
        if tb[1] > ta[1]:
            return "b", f"ts {ta[1]}<{tb[1]}"
        if ta[1] > tb[1]:
            return "a", f"ts {ta[1]}>{tb[1]}"
        return "a", f"tie {ta[1]} -> HEAD(r140)"
    return "union", f"no-ts keys"

def main():
    out = git(["ls-files", "-u"]).decode("utf-8", "replace")
    faces = {}
    for line in out.splitlines():
        mode, sha, stage, path = line.split("\t")[0].split()[0], line.split()[1], line.split()[2], line.split("\t")[1]
        faces.setdefault(path, {})[int(stage)] = sha
    plan = []
    for path, st in sorted(faces.items()):
        s2, s3 = st.get(2), st.get(3)
        b2, b3 = blob(s2), blob(s3)
        if b2 == b3:
            plan.append((path, "equal", b3, "bytes equal"))
            continue
        if path.endswith(".jsonl"):
            la, lb = b2.decode("utf-8").splitlines(), b3.decode("utf-8").splitlines()
            merged = la + [x for x in lb if x not in set(la)]
            plan.append((path, "jsonl-union", ("\n".join(merged) + "\n").encode("utf-8"),
                         f"lines {len(la)}+{len(lb)}->{len(merged)}"))
            continue
        if path.endswith(".md"):
            # twin: pick by call_latest.json side when in same batch, else deep scan for ts text
            plan.append((path, "md-pending", None, "handled after json sides"))
            continue
        try:
            d2, d3 = json.loads(b2), json.loads(b3)
        except Exception as e:
            plan.append((path, "MANUAL", None, f"json parse fail: {e}"))
            continue
        # SPECIAL: polluted observation face - take newer side, do not union garbage rows
        if path == "fleet/machine-health.json":
            ta, tb = deep_ts(d2), deep_ts(d3)
            pick = b3 if (tb and ta and tb[1] >= ta[1]) else b2
            plan.append((path, "snapshot-polluted-face", pick,
                         f"ts {ta[1] if ta else '?'} vs {tb[1] if tb else '?'} -> newer side"))
            continue
        # SPECIAL: ledger faces - state fields take-newer + list keys union (skill law)
        if path in ("results/compute_audit.json", "results/regime_state.json"):
            ta, tb = deep_ts(d2), deep_ts(d3)
            base = d3 if (tb and ta and tb[1] >= ta[1]) else d2
            base_ts = "b" if base is d3 else "a"
            merged = dict(base)
            for k in ("history", "transitions", "launches"):
                if k in d2 or k in d3:
                    la = d2.get(k) or []
                    lb = d3.get(k) or []
                    rr = resolve_rows(la, lb)
                    merged[k] = rr[0] if rr else (la or lb)
                    note = rr[1] if rr else "one-side"
            payload = json.dumps(merged, ensure_ascii=False, indent=2).encode("utf-8")
            if not payload.endswith(b"\n"):
                payload += b"\n"
            plan.append((path, f"ledger-{base_ts}", payload,
                         f"state fields ts {ta[1] if ta else '?'} vs {tb[1] if tb else '?'} -> {base_ts}; lists unioned"))
            continue
        # snapshot faces -> newer side
        side, why = pick_newer_side(d2, d3, path)
        if side == "b":
            plan.append((path, "take-b", b3, why + " -> theirs(965 local replay)"))
        elif side == "a":
            plan.append((path, "take-a", b2, why + " -> ours(HEAD)"))
        else:
            if isinstance(d2, list) and isinstance(d3, list):
                rr = resolve_rows(d2, d3)
                if rr is None:
                    plan.append((path, "MANUAL", None, "list-scalar top-level")); continue
                merged, note = rr[0], rr[1]
            elif isinstance(d2, dict) and isinstance(d3, dict):
                merged, note = merge_dict(d2, d3)
            else:
                plan.append((path, "MANUAL", None, f"type mismatch {type(d2).__name__}/{type(d3).__name__}")); continue
            payload = json.dumps(merged, ensure_ascii=False, indent=2).encode("utf-8")
            if not payload.endswith(b"\n"):
                payload += b"\n"
            plan.append((path, "dict-union", payload, note))
    # md twins: take side by newest json in same dir family
    latest_side = "a"
    for p, action, data, why in plan:
        if p.endswith("call_latest.json") and action == "take-b":
            latest_side = "b"
    for i, (p, action, data, why) in enumerate(plan):
        if action == "md-pending":
            st = faces[p]
            plan[i] = (p, "md-twin", blob(st[3] if latest_side == "b" else st[2]),
                       f"twin side={latest_side}")
    print("== PLAN ==")
    for p, action, data, why in plan:
        print(f"{action:>10}  {p}  [{why}] size={len(data) if data else 0}")
    if APPLY:
        print("== APPLYING ==")
        import os
        for p, action, data, why in plan:
            if action == "MANUAL":
                print("SKIP-MANUAL", p); continue
            with open(p, "wb") as f:
                f.write(data)
            if p.endswith(".json"):
                json.loads(open(p, "rb").read())  # parse-verify (r185)
            subprocess.run([G, "add", "--", p], capture_output=True)
            print("wrote+added", p)
    else:
        print("(dry-run; pass --apply to write)")

main()
