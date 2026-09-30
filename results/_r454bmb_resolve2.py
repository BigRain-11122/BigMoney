# r454 bm-b push-collision batch resolver (12 UU faces, rebase stop r454-on-bm-c-r262)
# 11 snapshot faces -> deep ts-probe take-new (twins forced same side, r98/r99/r100/r439bmb/R216/R208)
# 1 UNKNOWN (results/_attrition_guard_scan.json) -> manual adjudication: scan-evidence snapshot,
#   deterministic guard output regenerated per scan; take-new by embedded ts (fail-closed: if no ts
#   probe found on either side, fall back to wall-clock blob comparison and record it).
import json, re, subprocess, sys

FACES = [
    # group key -> paths that MUST take the same side
    ("report", ["docs/daily_report/REPORT-2026-09-30.md", "docs/daily_report/REPORT-2026-09-30.json"]),
    ("live", ["docs/live_usage/LIVE-2026-09-30.md", "docs/live_usage/LIVE-2026-09-30.json",
              "docs/live_usage/LIVE-latest.md", "docs/live_usage/LIVE-latest.json"]),
    ("b_layer", ["results/fundamental_b_layer_filter.json"]),
    ("futures", ["results/futures_update_status.json"]),
    ("lhb", ["results/lhb_update_status.json"]),
    ("token", ["results/token_usage.json"]),
    ("update", ["results/update_status.json"]),
    ("attrition", ["results/_attrition_guard_scan.json"]),
]

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")
# wall-clock-of-day probe (R350: wall-clock values require time-of-day): HH:MM[:SS]


def blob(rev):
    return subprocess.run(["git", "show", rev], capture_output=True, check=True).stdout.decode("utf-8", "replace")


def probe_ts(text):
    """Max ISO-like ts in the blob; also capture max HH:MM:SS wall-clock as tiebreak."""
    tss = TS_RE.findall(text) or []
    all_ts = TS_RE.finditer(text)
    stamps = [m.group(0) for m in all_ts]
    best = max(stamps) if stamps else ""
    hh = re.findall(r"\b(\d{2}:\d{2}:\d{2})\b", text)
    best_hh = max(hh) if hh else ""
    return best, best_hh


results = {}
for group, paths in FACES:
    probes = {}
    for p in paths:
        o = blob(":" + "2" + ":" + p)  # ours (replayed r454)
        t = blob(":" + "3" + ":" + p)  # theirs (bm-c r262)
        po, ho = probe_ts(o)
        pt, ht = probe_ts(t)
        probes[p] = (po, ho, pt, ht)
    # group decision: compare best ts across the group's faces (ours vs theirs)
    ours_best = max((v[0] for v in probes.values()), default="")
    theirs_best = max((v[2] for v in probes.values()), default="")
    if ours_best == "":
        ours_best = max((v[1] for v in probes.values()), default="")
    if theirs_best == "":
        theirs_best = max((v[3] for v in probes.values()), default="")
    # take-new: strictly newer wins; tie -> theirs (origin side, r140 same-second-take-HEAD family -> here origin landed first)
    if theirs_best > ours_best:
        side = "theirs"
    elif ours_best > theirs_best:
        side = "ours"
    else:
        side = "theirs"
    for p in paths:
        src = ":" + ("2" if side == "ours" else "3") + ":" + p
        data = subprocess.run(["git", "show", src], capture_output=True, check=True).stdout
        # parse-verify json faces before write-back (r185); md faces skip parse
        if p.endswith(".json"):
            try:
                json.loads(data.decode("utf-8", "replace"))
            except Exception as e:
                print("PARSE-FAIL", p, "side", side, e)
                sys.exit(2)
        with open(p, "wb") as f:
            f.write(data)
        subprocess.run(["git", "add", p], check=True)
    results[group] = {"side": side, "ours_ts": ours_best, "theirs_ts": theirs_best,
                      "faces": [probes[p] for p in paths]}
    print(group, "->", side, "| ours:", ours_best, "| theirs:", theirs_best)

# zero-loss/sanity echo
print(json.dumps(results, ensure_ascii=False, default=str)[:800])
