# r345 bm-b S7 push-rejection fold resolve (15-UU same-window S6 double-run
# family, r338 spectrum). Side mapping per r351 law: :2: = HEAD = replayed
# base = upstream/origin face; :3: = being-replayed commit = THIS chain
# (bm-b r345). Deep-ts probe per r353 key-normalization (re.sub strip) +
# r100/r350 value-shape gates; twins coupled same-side enforced
# programmatically (r110/r338 law); compute_audit history union zero-loss
# (r334/r188 law); js wrapper whole bytes (R209 law). Verify-then-write
# (r185 law). UU-membership guard per r355 law.
import json
import re
import subprocess

UU = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/autofill_state.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
TS_SHAPE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
COUPLES = [
    ("docs/daily_report/REPORT-2026-09-27.json",
     "docs/daily_report/REPORT-2026-09-27.md"),
    ("results/scorecard_v1.json", "results/strategy_scorecard.json"),
]


def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {spec} rc={r.returncode}")
    return r.stdout


def probe_ts(obj, best=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-/]", "", str(k)).lower()
            if isinstance(v, str) and TS_SHAPE.match(v):
                for stem in ("asof", "updated", "generatedat", "generated",
                             "lasttick", "ts", "cutoff", "lastrun", "now",
                             "writtenat", "ranat"):
                    if nk.startswith(stem):
                        if v > best:
                            best = v
                        break
            best = probe_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = probe_ts(v, best)
    return best


def side_face(path, side):
    """(raw_bytes, probe_ts) for one side of one path."""
    raw = blob(f"{side}{path}")
    if path.endswith(".json"):
        return raw, probe_ts(json.loads(raw.decode("utf-8")))
    cand = re.findall(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}",
                      raw.decode("utf-8", "replace"))
    return raw, (max(cand) if cand else "")


def union_history(a, b):
    ha, hb = a.get("history", []), b.get("history", [])
    seen = {}
    for e in ha + hb:
        k = e.get("ts") or probe_ts(e) or json.dumps(e, sort_keys=True)[:80]
        if k not in seen or str(e) > str(seen[k]):
            seen[k] = e
    return list(seen.values())


def main():
    r = subprocess.run(["git", "ls-files", "-u"], capture_output=True, text=True)
    ufiles = sorted({l.split("\t")[1] for l in r.stdout.splitlines() if l.strip()})
    assert ufiles == sorted(UU), f"UU set mismatch: {ufiles}"
    print(f"UU membership verified: {len(ufiles)} files")

    faces = {}
    for path in UU:
        faces[path] = {s: side_face(path, s) for s in (":2:", ":3:")}

    # couple side decisions: ONE side per couple, decided by the couple's
    # freshest json face (twins must never split, r110 law)
    couple_side = {}
    for lead, _ in COUPLES:
        t2 = faces[lead][":2:"][1]
        t3 = faces[lead][":3:"][1]
        couple_side[lead] = "ours" if t3 >= t2 else "theirs"

    report = []
    for path in UU:
        (raw2, t2), (raw3, t3) = faces[path][":2:"], faces[path][":3:"]
        lead = next((l for l, _ in COUPLES if path in (l, dict(COUPLES)[l])), None)
        if lead:
            side = couple_side[lead]
            raw = raw3 if side == "ours" else raw2
            if path.endswith(".json"):
                json.loads(raw.decode("utf-8"))
            report.append(f"{path}: take-{side} WHOLE (couple-led by {lead}; "
                          f"t2={t2} t3={t3})")
        elif path == "results/compute_audit.json":
            a = json.loads(raw2.decode("utf-8"))
            b = json.loads(raw3.decode("utf-8"))
            merged = dict(b if t3 >= t2 else a)
            u = union_history(a, b)
            keys_a = {e.get("ts") for e in a.get("history", [])}
            keys_b = {e.get("ts") for e in b.get("history", [])}
            assert len(u) == len(keys_a | keys_b), "union row loss"
            merged["history"] = u
            report.append(f"{path}: UNION history "
                          f"{len(keys_a)}|{len(keys_b)}->{len(u)} "
                          f"(|AuB|={len(keys_a | keys_b)}) snapshot="
                          f"{'ours' if t3 >= t2 else 'theirs'} (t2={t2} t3={t3})")
            raw = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
        elif path == "results/autofill_state.json":
            # mixed-dict+ledger (r203/R208/r245): launches union by ts
            # key, cap 50 keeping NEWEST, write-back re-sorted ts ASC;
            # last_tick take-new by internal ts dict compare (r140:
            # tie -> HEAD = :2: side in a rebase replay).
            a = json.loads(raw2.decode("utf-8"))
            b = json.loads(raw3.decode("utf-8"))
            la = {e.get("ts"): e for e in a.get("launches", [])}
            lb = {e.get("ts"): e for e in b.get("launches", [])}
            merged_launches = {**la, **lb}
            newest = sorted(merged_launches.values(),
                            key=lambda e: str(e.get("ts")), reverse=True)[:50]
            newest.sort(key=lambda e: str(e.get("ts")))   # asc write-back
            lt2, lt3 = a.get("last_tick", {}), b.get("last_tick", {})
            lt = lt2 if str(lt2.get("ts", "")) >= str(lt3.get("ts", "")) \
                else lt3
            assert isinstance(lt, dict), "last_tick not dict (r140)"
            merged = {"last_tick": lt, "launches": newest}
            # format mirror: producer = indent 1 + trailing newline
            raw = (json.dumps(merged, ensure_ascii=False, indent=1)
                   + "\n").encode("utf-8")
            report.append(f"{path}: last_tick take-"
                          f"{'theirs' if str(lt2.get('ts','')) >= str(lt3.get('ts','')) else 'ours'}"
                          f" (t2={lt2.get('ts')} t3={lt3.get('ts')}) "
                          f"launches union {len(la)}|{len(lb)}->"
                          f"{len(newest)} cap50 asc-resort (r245)")
        elif path == "results/regime_state.json":
            # rolling-ledger (r188/R208): history union by per-entry
            # ts/asof key zero-loss; snapshot fields take-new by probe.
            a = json.loads(raw2.decode("utf-8"))
            b = json.loads(raw3.decode("utf-8"))
            merged = dict(b if t3 >= t2 else a)
            ha = {json.dumps(e, sort_keys=True): e for e in a.get("history", [])}
            hb = {json.dumps(e, sort_keys=True): e for e in b.get("history", [])}
            merged["history"] = list({**ha, **hb}.values())
            report.append(f"{path}: history union {len(ha)}|{len(hb)}->"
                          f"{len(merged['history'])} snapshot="
                          f"{'ours' if t3 >= t2 else 'theirs'} (t2={t2} t3={t3})")
            raw = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
        elif path == "results/dashboard_status.js":
            side = "ours" if t3 >= t2 else "theirs"
            raw = raw3 if side == "ours" else raw2
            assert raw.startswith(b"window.DASH_DATA"), "js wrapper stripped"
            report.append(f"{path}: take-{side} whole-bytes R209 (t2={t2} t3={t3})")
        else:
            side = "ours" if t3 >= t2 else "theirs"
            raw = raw3 if side == "ours" else raw2
            json.loads(raw.decode("utf-8"))
            report.append(f"{path}: take-{side} whole-doc (t2={t2} t3={t3})")
        with open(path, "wb") as fh:
            fh.write(raw)
    print("\n".join(report))


if __name__ == "__main__":
    main()
