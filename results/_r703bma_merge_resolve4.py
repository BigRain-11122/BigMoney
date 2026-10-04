# r703 bm-a merge resolver leg-4: bm-c r504 S6 regen wave (0:1x newer than ours 23:56-58)
# ts-newer-wins + post_review.jsonl union + token per-key union
import subprocess, json

UU = """docs/live_usage/LIVE-latest.json
docs/live_usage/LIVE-latest.md
results/compute_audit.json
results/dashboard_status.js
results/dashboard_status.json
results/fundamental_b_layer_filter.json
results/futures_update_status.json
results/lhb_update_status.json
results/post_review.jsonl
results/post_review/REPORT-20261005.md
results/regime_state.json
results/scorecard_v1.json
results/strategy_scorecard.json
results/token_usage.json
results/update_status.json""".splitlines()

def blob(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True).stdout

TS = {
    "docs/live_usage/LIVE-latest.json": lambda d: d.get("generated"),
    "results/compute_audit.json": lambda d: (d.get("latest") or {}).get("generated"),
    "results/dashboard_status.json": lambda d: (d.get("meta") or {}).get("generated") or (d.get("meta") or {}).get("generated_at"),
    "results/fundamental_b_layer_filter.json": lambda d: d.get("updated"),
    "results/futures_update_status.json": lambda d: d.get("updated"),
    "results/lhb_update_status.json": lambda d: d.get("updated"),
    "results/regime_state.json": lambda d: d.get("updated"),
    "results/scorecard_v1.json": lambda d: d.get("generated"),
    "results/strategy_scorecard.json": lambda d: d.get("generated"),
    "results/update_status.json": lambda d: d.get("updated"),
}

json_side = {}
for p in UU:
    if p == "results/post_review.jsonl":
        o = blob(":2", p).decode("utf-8", errors="replace").splitlines()
        t = blob(":3", p).decode("utf-8", errors="replace").splitlines()
        seen, merged = set(), []
        for line in o + t:
            k = line.strip()[:150]
            if k and k not in seen:
                seen.add(k)
                merged.append(line)
        open(p, "w", encoding="utf-8", newline="").write("\n".join(merged) + ("\n" if merged else ""))
        subprocess.run(["git", "add", p], capture_output=True)
        print(f"UNION jsonl {p}: ours={len(o)} theirs={len(t)} merged={len(merged)}")
        continue
    if p == "results/token_usage.json":
        o = json.loads(blob(":2", p).decode("utf-8", errors="replace"))
        t = json.loads(blob(":3", p).decode("utf-8", errors="replace"))
        merged, picks = {}, {"ours": 0, "theirs": 0}
        for k in set(list(o.keys()) + list(t.keys())):
            ov, tv = o.get(k), t.get(k)
            if isinstance(ov, dict) and isinstance(tv, dict):
                og, tg = str(ov.get("generated", "")), str(tv.get("generated", ""))
                if og >= tg:
                    merged[k] = ov; picks["ours"] += 1
                else:
                    merged[k] = tv; picks["theirs"] += 1
            elif ov is not None:
                merged[k] = ov; picks["ours"] += 1
            else:
                merged[k] = tv; picks["theirs"] += 1
        open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(merged, ensure_ascii=False, indent=1) + "\n")
        subprocess.run(["git", "add", p], capture_output=True)
        print(f"UNION token {p}: keys={len(merged)} picks={picks}")
        continue
    if p in TS:
        try:
            o = json.loads(blob(":2", p).decode("utf-8", errors="replace"))
            t = json.loads(blob(":3", p).decode("utf-8", errors="replace"))
            to, tt = str(TS[p](o) or ""), str(TS[p](t) or "")
            side = "ours" if to >= tt else "theirs"
        except Exception as e:
            side, to, tt = "theirs", "?", "?"  # unparseable -> origin canon (r437 default-safe)
        json_side[p] = side
        subprocess.run(["git", "checkout", "--" + side, p], capture_output=True)
        subprocess.run(["git", "add", p], capture_output=True)
        print(f"RESOLVED {side}: {p} (ours={to} theirs={tt})")
        continue
    # md/js twins + report md: defer to twin/derived decision
    print(f"DEFER: {p}")

# twins: LIVE-latest.md -> LIVE-latest.json ; dashboard_status.js -> .json ; post_review REPORT md -> bm-c newer whole-file derived face
for tp, jp in [("docs/live_usage/LIVE-latest.md", "docs/live_usage/LIVE-latest.json"),
               ("results/dashboard_status.js", "results/dashboard_status.json")]:
    side = json_side.get(jp, "theirs")
    subprocess.run(["git", "checkout", "--" + side, tp], capture_output=True)
    subprocess.run(["git", "add", tp], capture_output=True)
    print(f"RESOLVED {side} (twin-locked): {tp}")

# post_review report md: derived face, theirs (bm-c 0:1x) newer than dead-session 0:01 -- but zero-loss:
# archive ours variant as evidence copy before taking theirs
import shutil
ours_report = blob(":2", "results/post_review/REPORT-20261005.md")
open("results/_r703bma_postreview_ours_variant.md", "wb").write(ours_report)
subprocess.run(["git", "checkout", "--theirs", "results/post_review/REPORT-20261005.md"], capture_output=True)
subprocess.run(["git", "add", "results/post_review/REPORT-20261005.md"], capture_output=True)
print("RESOLVED theirs + ours-variant archived: results/post_review/REPORT-20261005.md")
