"""r698 bm-c S3 facts probe: task-board open tickets, saturation engine
status (bm-c instance = Tools/saturation_engine.py per S3 canon),
watermark red flag, py_watermark verdict, bandit advisory next_pick,
W14-JUDGE burn watch (runner liveness + checkpoint growth + pool entry),
W16-GENERATE double-burn convergence watch (pool entry + claim faces +
product faces). Facts JSON -> results/_r698bmc_s3_facts.json.
Pattern credit: Tools/_r695bmc_s3_probe.py."""
import subprocess
import json
import glob
import os
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PY = os.sys.executable


def fstats(p):
    try:
        st = os.stat(p)
        return {"size": st.st_size,
                "mtime": datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="minutes")}
    except Exception:
        return None


def main():
    facts = {"round": 698, "ts": datetime.datetime.now().isoformat()}

    # 1. task board census
    open_t, claimed, total = [], [], 0
    for f in sorted(glob.glob(os.path.join(REPO, "fleet", "tasks", "*.json"))):
        total += 1
        try:
            with open(f, encoding="utf-8") as fh:
                t = json.load(fh)
            st = t.get("status", "")
            if st == "open":
                open_t.append(os.path.basename(f))
            elif st in ("claimed", "in_progress"):
                claimed.append((os.path.basename(f), st, t.get("claimed_by", "")))
        except Exception:
            open_t.append(os.path.basename(f) + " (unreadable)")
    facts["board_total"] = total
    facts["board_open"] = open_t
    facts["board_claimed_count"] = len(claimed)

    # 2. saturation engine status (bm-c instance face)
    try:
        p = subprocess.run([PY, os.path.join(REPO, "Tools", "saturation_engine.py"),
                            "status"], cwd=REPO, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        facts["satengine_rc"] = p.returncode
        out = (p.stdout or "") + (p.stderr or "")
        facts["satengine_tail"] = "\n".join(out.strip().splitlines()[-8:])
    except Exception as e:
        facts["satengine_rc"] = -1
        facts["satengine_tail"] = repr(e)[:300]

    # 3. watermark red flag
    wr = os.path.join(REPO, "results", "watermark_red.json")
    if os.path.exists(wr):
        with open(wr, encoding="utf-8") as fh:
            w = json.load(fh)
        facts["watermark_red"] = w.get("red", None)
        facts["watermark_reason"] = w.get("reason", "")[:200]
    else:
        facts["watermark_red"] = "file-missing"

    # 3b. py_watermark verdict (advisory face)
    pw = os.path.join(REPO, "results", "watermark.jsonl")
    verdict = None
    if os.path.exists(pw):
        lines = open(pw, encoding="utf-8", errors="replace").read().strip().splitlines()
        if lines:
            try:
                last = json.loads(lines[-1])
                verdict = {"verdict": last.get("verdict"), "ts": last.get("ts"),
                           "machine": last.get("machine")}
            except Exception:
                verdict = {"parse_error": True}
    facts["py_watermark_last"] = verdict

    # 4. bandit advisory next_pick
    np_ = os.path.join(REPO, "results", "bandit_advisory_next.json")
    if os.path.exists(np_):
        try:
            with open(np_, encoding="utf-8") as fh:
                facts["bandit_next_pick"] = json.load(fh)
        except Exception:
            facts["bandit_next_pick"] = "unreadable"
    else:
        facts["bandit_next_pick"] = None

    # 5. W14-JUDGE burn watch
    w14 = {"dir": {}, "checkpoint": {}, "pool_entry": None, "runner": None}
    for f in sorted(glob.glob(os.path.join(REPO, "results", "trial_labor_w14", "*"))):
        rel = os.path.relpath(f, REPO)
        s = fstats(f)
        if s:
            w14["dir"][os.path.basename(f)] = s
    ck = os.path.join(REPO, "results", "trial_labor_w14", "checkpoint")
    if os.path.isdir(ck):
        files = sorted(glob.glob(os.path.join(ck, "*")))
        w14["checkpoint"] = {"count": len(files),
                             "latest": [os.path.basename(x) for x in files[-5:]],
                             "mtime": (fstats(files[-1]) or {}).get("mtime") if files else None}
    # pool entry
    try:
        with open(os.path.join(REPO, "results", "runnable_pool.json"), encoding="utf-8") as fh:
            pool = json.load(fh)
        entries = pool if isinstance(pool, list) else pool.get("entries", pool.get("items", []))
        hits = []
        for e in entries:
            blob = json.dumps(e, ensure_ascii=False)
            if "W14-JUDGE" in blob or "W16-GENERATE" in blob:
                hits.append({k: e.get(k) for k in
                             ("id", "name", "status", "claimed_by", "claimed_at",
                              "lane_owner", "runner", "shards", "entry_id")
                             if k in e} or {"raw": blob[:400]})
        w14["pool_hits"] = hits
    except Exception as e:
        w14["pool_hits"] = {"error": repr(e)[:200]}
    # runner liveness (r697 judge pid 34320; scan cmdline for judge runner too)
    try:
        import psutil
        procs = []
        for pr in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
            try:
                cl = " ".join(pr.info["cmdline"] or [])
            except Exception:
                cl = ""
            low = cl.lower()
            if ("judge" in low and "w14" in low) or "w16" in low and "generate" in low:
                procs.append({"pid": pr.info["pid"], "cmd": cl[:160],
                             "age_min": round((datetime.datetime.now().timestamp()
                                               - pr.info["create_time"]) / 60, 1)})
        w14["runner"] = {"pid34320_alive": psutil.pid_exists(34320),
                         "pid36336_alive": psutil.pid_exists(36336),
                         "scanned": procs[:10]}
    except Exception as e:
        w14["runner"] = {"error": repr(e)[:200]}
    facts["w14_judge"] = w14

    # 6. W16-GENERATE double-burn convergence watch
    w16 = {"claims": {}, "products": []}
    cdir = os.path.join(REPO, "results", "pool_claims", "TRIAL-LABOR-W16-GENERATE")
    for f in sorted(glob.glob(os.path.join(cdir, "*.json"))):
        s = fstats(f)
        try:
            d = json.load(open(f, encoding="utf-8"))
            s = {**s, **{k: d.get(k) for k in
                         ("claimed_by", "claimed_at", "status", "owner_since", "pid")}}
        except Exception:
            pass
        w16["claims"][os.path.basename(f)] = s
    for f in sorted(glob.glob(os.path.join(REPO, "results", "**", "w16*"), recursive=True)):
        rel = os.path.relpath(f, REPO)
        if "_r6" in rel or "checkpoint" in rel:
            continue
        s = fstats(f)
        if s:
            w16["products"].append({"path": rel, **s})
    facts["w16_generate"] = w16

    out = os.path.join(REPO, "results", "_r698bmc_s3_facts.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print(json.dumps(facts, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
