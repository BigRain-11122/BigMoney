"""r507 bm-c S3 probe: fleet tasks open scan + watermark red + pool seats
(N2-W15/W3-judge/fund-trio/contest) + w3 judge product presence + post_review
today verdict scan + n2_w15_judge_state summary. Read-only; receipt to
results/_r507bmc_s3probe.json. Laws: r692 claim truth = shards[].owner layer;
r646 same-shape set comparison; r446 probe-to-file. Base=r501 probe + post_review.
"""
import glob
import json
import os
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = "_r507bmc"
TODAY = "2026-10-05"


def main():
    out = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "round": "r507 bm-c"}

    # 1. fleet tasks: status summary (open / claimed / in_progress)
    tasks = []
    for p in sorted(glob.glob(os.path.join(REPO, "fleet", "tasks", "*.json"))):
        try:
            d = json.load(open(p, encoding="utf-8-sig"))
        except Exception as e:
            tasks.append({"file": os.path.basename(p), "err": str(e)[:80]})
            continue
        s = d.get("status")
        if s in ("open", "claimed", "in_progress"):
            tasks.append({
                "file": os.path.basename(p),
                "status": s,
                "title": (d.get("title") or d.get("subject") or "")[:80],
                "claimed_by": d.get("claimed_by"),
                "immediate": d.get("immediate"),
            })
    out["active_tasks"] = tasks
    out["active_tasks_count"] = len(tasks)

    # 2. watermark red flag
    wr = os.path.join(REPO, "results", "watermark_red.json")
    if os.path.exists(wr):
        try:
            d = json.load(open(wr, encoding="utf-8-sig"))
            out["watermark_red"] = {
                "red": d.get("red"),
                "reason": (d.get("reason") or "")[:200],
                "next_pick": d.get("next_pick"),
                "ts": d.get("ts"),
            }
        except Exception as e:
            out["watermark_red"] = {"err": str(e)[:80]}
    else:
        out["watermark_red"] = {"absent": True}

    # 3. pool seats
    pool_p = os.path.join(REPO, "results", "runnable_pool.json")
    seats = {}
    try:
        pool = json.load(open(pool_p, encoding="utf-8-sig"))
        for e in pool.get("entries", []):
            eid = e.get("id", "")
            low = eid.lower()
            if ("n2-w15" in low or "w3-judge" in low
                    or "fund-" in low or "contest" in low):
                seats[eid] = {
                    "entry_status": e.get("status"),
                    "shards": [
                        {"key": s.get("key"), "status": s.get("status"),
                         "owner": s.get("owner"),
                         "owner_since": s.get("owner_since")}
                        for s in e.get("shards", [])
                    ],
                }
    except Exception as e:
        seats["_err"] = str(e)[:120]
    out["pool_seats"] = seats

    # 4. w3 judge product presence
    prod = os.path.join(REPO, "results", "mass_trial", "w3_judge.json")
    out["w3_judge_product"] = os.path.exists(prod)
    if out["w3_judge_product"]:
        out["w3_judge_mtime"] = time.strftime(
            "%Y-%m-%dT%H:%M:%S", time.localtime(os.path.getmtime(prod)))

    # 5. post_review today verdict scan (r506 caliber; FAIL rows = P0)
    pr_p = os.path.join(REPO, "results", "post_review.jsonl")
    counts, reds = {}, []
    try:
        with open(pr_p, encoding="utf-8", errors="replace") as f:
            for ln in f:
                ln = ln.strip()
                if not ln or TODAY not in ln:
                    continue
                try:
                    d = json.loads(ln)
                except Exception:
                    continue
                v = str(d.get("verdict") or d.get("result") or "?")
                counts[v] = counts.get(v, 0) + 1
                if v not in ("YES", "PASS"):
                    reds.append({k: str(d.get(k))[:60] for k in
                                 ("ts", "id", "verdict", "reason")
                                 if d.get(k) is not None})
    except Exception as e:
        counts = {"err": str(e)[:80]}
    out["post_review_today"] = {"counts": counts, "red_rows": reds[:10],
                                "red_count": len(reds)}

    # 6. n2_w15_judge_state summary (judge chain face)
    js_p = os.path.join(REPO, "results", "n2_w15_judge_state.json")
    if os.path.exists(js_p):
        try:
            d = json.load(open(js_p, encoding="utf-8-sig"))
            shards = d.get("shards") or d.get("entries") or []
            if isinstance(shards, dict):
                out["n2_judge_state"] = {
                    "ts": d.get("ts") or d.get("updated"),
                    "keys": len(shards),
                    "statuses": sorted({str(v.get("status"))
                                        for v in shards.values()
                                        if isinstance(v, dict)})[:8],
                }
            else:
                out["n2_judge_state"] = {
                    "ts": d.get("ts") or d.get("updated"),
                    "n_shards": len(shards),
                    "statuses": sorted({str(s.get("status"))
                                        for s in shards})[:8],
                }
        except Exception as e:
            out["n2_judge_state"] = {"err": str(e)[:80]}
    else:
        out["n2_judge_state"] = {"absent": True}

    with open(os.path.join(REPO, "results", TAG + "_s3probe.json"), "w",
              encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    slim = {
        "active_tasks_count": out["active_tasks_count"],
        "watermark_red": out.get("watermark_red", {}).get("red"),
        "w3_judge_product": out["w3_judge_product"],
        "post_review_today": counts,
        "post_review_reds": len(reds),
        "seats": {k: v.get("entry_status") for k, v in seats.items()
                  if isinstance(v, dict)},
    }
    print(json.dumps(slim, ensure_ascii=False))
    for t in tasks:
        print("TASK", json.dumps(t, ensure_ascii=False))
    for k, v in seats.items():
        if isinstance(v, dict) and v.get("shards"):
            print("SEAT", k, json.dumps(v["shards"], ensure_ascii=False))
    for r in reds[:10]:
        print("PRRED", json.dumps(r, ensure_ascii=False))
    print("N2J", json.dumps(out.get("n2_judge_state", {}), ensure_ascii=False))


if __name__ == "__main__":
    main()
