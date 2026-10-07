"""r695 bm-c S3 facts probe: task-board open tickets, saturation engine
status (bm-c instance = Tools/saturation_engine.py per S3 canon),
watermark red flag, bandit advisory next_pick, NULLS burn watch
(bm-b lane, FUND-DIVLOWVOL-P1-NULLS). Facts JSON ->
results/_r695bmc_s3_facts.json. Pattern credit: Tools/_r694bmc_s3_probe.py."""
import subprocess
import json
import glob
import os
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PY = os.sys.executable


def main():
    facts = {"round": 695, "ts": datetime.datetime.now().isoformat()}

    # 1. task board: open tickets census
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
    facts["board_claimed"] = claimed

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

    # 5. NULLS burn watch (bm-b lane, fund-divlowvol nulls.jsonl growth)
    nz = os.path.join(REPO, "results", "fund_divlowvol", "nulls.jsonl")
    if not os.path.exists(nz):
        cand = glob.glob(os.path.join(REPO, "results", "**", "nulls.jsonl"),
                         recursive=True)
        nz = cand[0] if cand else None
    if nz and os.path.exists(nz):
        try:
            n = sum(1 for _ in open(nz, encoding="utf-8", errors="replace"))
            mt = datetime.datetime.fromtimestamp(os.path.getmtime(nz)).isoformat()
            facts["nulls_burn"] = {"path": os.path.relpath(nz, REPO),
                                   "lines": n, "mtime": mt}
        except Exception as e:
            facts["nulls_burn"] = {"error": repr(e)[:200]}
    else:
        facts["nulls_burn"] = None

    out = os.path.join(REPO, "results", "_r695bmc_s3_facts.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print(json.dumps(facts, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
