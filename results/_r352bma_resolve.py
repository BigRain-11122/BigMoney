"""R352 bm-a push-cycle storm resolver vs bmc-r103: 25 snapshot/union faces in one pass.

SIDE-MAPPING ASSERTION (r351 pitlaw, verified this window): rebase replay window =>
  :2: = HEAD = replayed base = PEER bmc-r103 face; :3: = replayed commit = MINE r352 face.
Empirical proof: stage3 update_status.updated=20:29:25 (my batch A leg 20:29:24), stage2=20:27:52.

Adapted from _r351bma_resolve_stop8.py (same S6 double-run family, r351 pass-3 zero-mod precedent)
with the CODELY.md memory-union block REMOVED -- CODELY.md is NOT in this window's conflict set.
Canons: snapshot take-new VERBATIM winner bytes by DEEP ts probe (r311/r345/r350: key stem
strip '_/-', value-shape gate time-bearing ^20..[T ]HH:MM -- no EXCLUDE lists, date-only values
cannot win); twin coupling (daily_report json+md r329 / dashboard json+js / paper_export pair);
token_usage machines BUCKET merge (r100 law); x2 jsonl ts-sorted line union (r188).
Parse-verify every winner blob before write (r185). Tie -> HEAD/:2: (r140).
"""
import subprocess, json, re

def blob(rev, path):
    out = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"git show {rev}:{path} rc={out.returncode}: {out.stderr[:150]!r}")
    return out.stdout

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
KEY_HINTS = ("ts", "generated", "updated", "asof", "last", "checked", "written", "attempt", "seen", "run")

def deep_ts(obj):
    best = [""]
    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                kk = str(k).lstrip("_-").lower()
                if isinstance(v, str) and TS_RE.match(v) and any(h in kk for h in KEY_HINTS):
                    if v > best[0]:
                        best[0] = v
                walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)
    walk(obj)
    return best[0]

def winner_side(path):
    oB, tB = blob(":2", path), blob(":3", path)
    oJ, tJ = json.loads(oB.decode("utf-8-sig")), json.loads(tB.decode("utf-8-sig"))
    ots, tts = deep_ts(oJ), deep_ts(tJ)
    side = "ours" if ots >= tts else "theirs"  # tie -> ours/:2:/HEAD (r140)
    return side, oB, tB, ots, tts

def write_bytes(path, data, note=""):
    json.loads(data.decode("utf-8-sig"))  # parse-verify winner before write (r185)
    with open(path, "wb") as f:
        f.write(data)
    print(f"  {path}: {note}")

def snap(path):
    side, oB, tB, ots, tts = winner_side(path)
    data = oB if side == "ours" else tB
    write_bytes(path, data, f"take-{side} side2_ts={ots!r} side3_ts={tts!r}")
    return side

def main():
    report = {"snap_ours": [], "snap_theirs": []}

    # --- Group A: independent snapshot probes (stage blobs, never working tree) ---
    snaps = [
        "results/daily_scorecard.json",
        "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json",
        "results/heat_update_status.json",
        "results/lhb_update_status.json",
        "results/paper/COMPOSITE-CE-01_paper.json",
        "results/paper/COMPOSITE-CE-02_paper.json",
        "results/paper/DROUGHT-CE-01_paper.json",
        "results/paper/ENGULF-CE-01_paper.json",
        "results/paper/NEEDLE-DE-01_paper.json",
        "results/paper/VOLATILITY-CE-01_paper.json",
        "results/prospect_paper/_summary.json",
        "results/prospect_promotion/_summary.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
        "results/t35_open_fill_verify.json",
        "results/update_status.json",
        "results/paper_export/export-2026-09-24.json",
        "docs/daily_report/REPORT-2026-09-27.json",
        "results/dashboard_status.json",
    ]
    for p in snaps:
        side = snap(p)
        report["snap_ours" if side == "ours" else "snap_theirs"].append(p)

    # --- Group B: coupled copies (same side bytes, NO json re-parse of md/js) ---
    for lead, follower in [
        ("docs/daily_report/REPORT-2026-09-27.json", "docs/daily_report/REPORT-2026-09-27.md"),
        ("results/dashboard_status.json", "results/dashboard_status.js"),
        ("results/paper_export/export-2026-09-24.json", "results/paper_export/latest.json"),
    ]:
        side, oB, tB, _, _ = winner_side(lead)
        fB = blob(":2" if side == "ours" else ":3", follower)
        with open(follower, "wb") as f:
            f.write(fB)  # md/js/raw twin: byte copy, no parse (r329)
        print(f"  {follower}: coupled take-{side} (lead {lead})")

    # --- token_usage bucket merge (r100 law: machines buckets per-key take-new) ---
    p = "results/token_usage.json"
    oB, tB = blob(":2", p), blob(":3", p)
    oJ, tJ = json.loads(oB.decode("utf-8-sig")), json.loads(tB.decode("utf-8-sig"))
    out = dict(oJ)
    if str(tJ.get("generated", "")) > str(oJ.get("generated", "")):
        out["generated"] = tJ["generated"]
    oM, tM = oJ.get("machines", {}), tJ.get("machines", {})
    kept_theirs = 0
    for k, v in tM.items():
        if k not in oM:
            out.setdefault("machines", {})[k] = v
            kept_theirs += 1
        else:
            if deep_ts(v) > deep_ts(oM[k]):
                out["machines"][k] = v
                kept_theirs += 1
    for k in oM:
        out.setdefault("machines", {})[k] = oM[k]
    crlf = b"\r\n" in oB
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if crlf:
        text = text.replace("\n", "\r\n")
    if oB.endswith(b"\n"):
        text += "\r\n" if crlf else "\n"
    with open(p, "wb") as f:
        f.write(text.encode("utf-8"))
    json.loads(open(p, encoding="utf-8").read())
    print(f"  {p}: bucket-merge machines={len(out.get('machines', {}))} side3_buckets_taken={kept_theirs} generated={out.get('generated')!r}")

    # --- x2_watch_log.jsonl: line union, ts-sorted (append-log r188) ---
    p = "results/x2_watch_log.jsonl"
    oB, tB = blob(":2", p), blob(":3", p)
    oL = oB.decode("utf-8-sig").splitlines()
    tL = tB.decode("utf-8-sig").splitlines()
    oS = set(oL)
    extra = [l for l in tL if l not in oS]
    merged = oL + extra
    def lts(l):
        m = re.search(r'"ts":\s*"([^"]+)"', l)
        return m.group(1) if m else ""
    try:
        merged.sort(key=lts)
    except Exception:
        pass
    tail = "\r\n" if b"\r\n" in oB else "\n"
    with open(p, "wb") as f:
        f.write((tail.join(merged) + tail).encode("utf-8"))
    print(f"  {p}: line-union side2={len(oL)} side3={len(tL)} merged={len(merged)} added={len(extra)}")

    print(json.dumps({"snap_side2": len(report["snap_ours"]), "snap_side3": len(report["snap_theirs"]), "side3_fresh_faces": report["snap_theirs"]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
