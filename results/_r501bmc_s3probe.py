"""r501 bm-c S3 probe: fleet tasks open scan + watermark red flag + N2-W15 pool
seat watch + fund-trio trio watch. Read-only; receipt to results/_r501bmc_s3probe.json.
Laws: r692 claim truth = entries[].shards[].owner layer; r646 same-shape
set comparison; r446 probe-to-file.
"""
import glob
import json
import os
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = "_r501bmc"


def main():
    out = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "round": "r501 bm-c"}

    # 1. fleet tasks: status summary (open / claimed / in_progress)
    tasks = []
    for p in sorted(glob.glob(os.path.join(REPO, "fleet", "tasks",
                                           "*.json"))):
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

    # 3. pool seats: N2-W15 + fund trio + W3 judge + CONTEST (shared face)
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

    # 4. mass_trial product faces (w3 judge product presence)
    prod = os.path.join(REPO, "results", "mass_trial", "w3_judge.json")
    out["w3_judge_product"] = os.path.exists(prod)
    if out["w3_judge_product"]:
        out["w3_judge_mtime"] = time.strftime(
            "%Y-%m-%dT%H:%M:%S", time.localtime(os.path.getmtime(prod)))

    with open(os.path.join(REPO, "results", TAG + "_s3probe.json"), "w",
              encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    slim = {
        "active_tasks_count": out["active_tasks_count"],
        "watermark_red": out.get("watermark_red", {}).get("red"),
        "w3_judge_product": out["w3_judge_product"],
        "seats": {k: v.get("entry_status") for k, v in seats.items()
                  if isinstance(v, dict)},
    }
    print(json.dumps(slim, ensure_ascii=False))
    for t in tasks:
        print("TASK", json.dumps(t, ensure_ascii=False))
    for k, v in seats.items():
        if isinstance(v, dict) and v.get("shards"):
            print("SEAT", k, json.dumps(v["shards"], ensure_ascii=False))


if __name__ == "__main__":
    main()
