import io, json, subprocess, datetime

OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\trio_burn_eta.json"
TXT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r671bmb_trio_eta.txt"
FAMS = {
    "fund_value_p1": "FUND-VALUE-P1-NULLS",
    "fund_quality_p1": "FUND-QUALITY-P1-NULLS",
    "fund_divlowvol_p1": "FUND-DIVLOWVOL-P1-NULLS",
}
K = 2000
report = {}
lines = []

now_iso = datetime.datetime.now().isoformat(timespec="seconds")

for fam, ent in FAMS.items():
    path = "results/%s/nulls.jsonl" % fam
    # git history: last 8 commits touching this file
    out = subprocess.run(["git", "log", "--format=%H|%aI", "-8", "--", path],
                         capture_output=True).stdout.decode("utf-8", "replace").strip().split("\n")
    samples = []
    for ln in reversed(out):  # oldest -> newest
        if not ln.strip():
            continue
        sha, aiso = ln.split("|", 1)
        b = subprocess.run(["git", "show", "%s:%s" % (sha, path)], capture_output=True).stdout
        n = b.count(b"\n")
        # max k
        mk = -1
        tail = b[-400:]
        try:
            lastrow = [r for r in b.rstrip(b"\n").split(b"\n") if r.strip()][-1]
            mk = json.loads(lastrow).get("k", -1)
        except Exception:
            pass
        samples.append((aiso[:19], n, mk))
    # current working tree
    with io.open(path.replace("/", "\\"), "rb") as f:
        cur = f.read()
    cur_n = cur.count(b"\n")
    cur_mk = -1
    try:
        lastrow = [r for r in cur.rstrip(b"\n").split(b"\n") if r.strip()][-1]
        cur_mk = json.loads(lastrow).get("k", -1)
    except Exception:
        pass
    samples.append(("now", cur_n, cur_mk))

    # rate from oldest git sample to now
    import datetime as dt
    def pti(s):
        return dt.datetime.fromisoformat(s)
    t0, n0, k0 = samples[0]
    t1, n1, k1 = samples[-1]
    hours = 1.0
    if t0 != "now" and t1 == "now" and n1 > n0:
        hours = max(0.1, (dt.datetime.now() - pti(t0)).total_seconds() / 3600.0)
    delta_k = (k1 - k0) if (k1 >= 0 and k0 >= 0) else (n1 - n0)
    rate_h = delta_k / hours if hours else 0.0
    remaining = max(0, K - 1 - max(cur_mk, 0))
    eta_h = (remaining / rate_h) if rate_h > 0 else None
    report[ent] = {
        "family": fam,
        "k_current": cur_mk,
        "rows_current": cur_n,
        "K": K,
        "pct": round(100.0 * (cur_mk + 1) / K, 2),
        "rate_per_h": round(rate_h, 2),
        "window_hours": round(hours, 2),
        "eta_hours": round(eta_h, 1) if eta_h else None,
        "eta_date": (dt.datetime.now() + dt.timedelta(hours=eta_h)).isoformat(timespec="hours") if eta_h else None,
        "samples": [{"t": s[0], "rows": s[1], "k": s[2]} for s in samples],
    }
    lines.append("%s: k=%d/2000 (%.1f%%) rate=%.1f/h over %.1fh ETA=%.1fh -> %s" % (
        ent, cur_mk, 100.0 * (cur_mk + 1) / K, rate_h, hours,
        eta_h if eta_h else -1, report[ent]["eta_date"] or "n/a"))

report["_meta"] = {
    "ts": now_iso,
    "machine": "bm-b",
    "round": "r671",
    "method": "git-history autofill-tick commits (r288 claim-refresh cadence ~40min) + working-tree now sample; k=max index from last row; ETA linear projection",
    "purpose": "trio NULLS finalize candidate window watch (r670 pointer)",
}

with io.open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
with io.open(TXT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written")
