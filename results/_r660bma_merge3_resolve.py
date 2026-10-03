r"""r660 closeout wave-3 UU resolver.
17 regen/status faces: latest-scan-wins via stage ts compare (r638/r644 precedent).
compute_audit/token_usage: cross-machine union (r660 precedent, own-side authority).
CODELY.md: line-level union (memory face, append-only semantics, exact-dup dedup).
"""
import json
import re
import subprocess
import sys

REGEN = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]

KEYS = ("generated", "generated_at", "updated", "updated_at", "ts", "asof", "date", "cutoff")


def blob(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True).stdout


def freshness(data_bytes, path):
    if path.endswith((".json", ".js")):
        try:
            d = json.loads(data_bytes.decode("utf-8"))
        except Exception:
            return None
        if isinstance(d, dict):
            for k in KEYS:
                v = d.get(k)
                if isinstance(v, str) and len(v) >= 8:
                    return v
        return None
    m = re.search(rb"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?", data_bytes)
    return m.group(0).decode() if m else None


def main():
    verdicts = []
    for f in REGEN:
        fo = freshness(blob(":2", f), f)
        ft = freshness(blob(":3", f), f)
        if fo is None and ft is None:
            side, why = "ours", "no-ts-fallback"
        elif ft is None:
            side, why = "ours", "theirs-no-ts"
        elif fo is None:
            side, why = "theirs", "ours-no-ts"
        elif fo >= ft:
            side, why = "ours", f"{fo}>={ft}"
        else:
            side, why = "theirs", f"{ft}>{fo}"
        r = subprocess.run(["git", "checkout", f"--{side}", "--", f], capture_output=True)
        subprocess.run(["git", "add", "--", f], check=True)
        verdicts.append((f, side, why))

    # --- cross-machine unions (HEAD vs origin/main inputs) ---
    cap = 201
    ours = json.loads(blob("HEAD", "results/compute_audit.json").decode("utf-8"))
    theirs = json.loads(blob("origin/main", "results/compute_audit.json").decode("utf-8"))
    rows = {}
    for r_ in ours["history"] + theirs["history"]:
        rows[r_["ts"]] = r_
    hist = sorted(rows.values(), key=lambda r_: r_["ts"])[-cap:]
    merged = {"latest": hist[-1], "history": hist}
    with open("results/compute_audit.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    subprocess.run(["git", "add", "results/compute_audit.json"], check=True)
    verdicts.append(("results/compute_audit.json", "union", f"{len(hist)} rows, latest {hist[-1]['ts']}"))

    tu_o = json.loads(blob("HEAD", "results/token_usage.json").decode("utf-8"))
    tu_t = json.loads(blob("origin/main", "results/token_usage.json").decode("utf-8"))
    tu = dict(tu_t)
    machines = dict(tu_o.get("machines", {}))
    for k, v in tu_t.get("machines", {}).items():
        machines.setdefault(k, v)
    if "bm-a" in tu_o.get("machines", {}):
        machines["bm-a"] = tu_o["machines"]["bm-a"]
    tu["machines"] = machines
    tu["generated"] = max(tu_o.get("generated", ""), tu_t.get("generated", ""))
    with open("results/token_usage.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(tu, f, ensure_ascii=False, indent=1)
    subprocess.run(["git", "add", "results/token_usage.json"], check=True)
    verdicts.append(("results/token_usage.json", "union", "machines own-side merge"))

    # --- CODELY.md line-union ---
    o_lines = blob("HEAD", "CODELY.md").decode("utf-8").splitlines()
    t_lines = blob("origin/main", "CODELY.md").decode("utf-8").splitlines()
    seen = set()
    out = []
    for l in o_lines + t_lines:
        if l in seen or not l.strip():
            if l.strip():
                continue
        seen.add(l)
        out.append(l)
    with open("CODELY.md", "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(out) + "\n")
    o_only = sum(1 for l in o_lines if l.strip() and l not in set(t_lines))
    t_only = sum(1 for l in t_lines if l.strip() and l not in set(o_lines))
    subprocess.run(["git", "add", "CODELY.md"], check=True)
    verdicts.append(("CODELY.md", "line-union", f"ours-only {o_only} + theirs-only {t_only} lines kept"))

    for f, s, w in verdicts:
        print(f"{s:9} {f}  # {w}")

    # marker sweep
    bad = []
    for f in REGEN + ["CODELY.md", "results/compute_audit.json", "results/token_usage.json"]:
        b = open(f, "rb").read()
        if b"<<<<<<<" in b or b">>>>>>>" in b:
            bad.append(f)
        elif re.search(rb"^=======$", b, re.M):
            bad.append(f)
    print("MARKER-SWEEP:", "CLEAN" if not bad else f"DIRTY {bad}")
    return 0 if not bad else 2


if __name__ == "__main__":
    sys.exit(main())
