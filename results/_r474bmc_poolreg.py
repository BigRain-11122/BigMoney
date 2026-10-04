"""r474 bm-c pool-face regression adjudication probe (r648/r457/r489 laws):
FUND trio NULLS entries on origin (full fields, fresh fetch) vs local HEAD vs
r473 observed state (claimed, owner_since ~=13:04:19, healthy) + bm-b
heartbeat liveness + bm-a r678 commit parent pool blob comparison.
File-out per r446 probe law; zero console CJK."""
import datetime
import json
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r474bmc_poolreg.txt")

R473_OBS = {
    "ts_probe": "2026-10-04T13:15:49",
    "fund_trio": {"status": "claimed-in-flight (healthy age 11.5min)",
                  "owner_since_inferred": "2026-10-04 13:04:19"},
}


def run(args, cwd=None):
    return subprocess.run(args, capture_output=True, cwd=cwd or ROOT,
                           creationflags=CREATE_NO_WINDOW)


def pool_blob_fund_trio(blob):
    try:
        d = json.loads(blob.decode("utf-8-sig"))
    except Exception as e:  # noqa: BLE001
        return {"parse_error": str(e)}
    out = {}
    for e in d.get("entries", []):
        if e.get("id", "") in ("FUND-VALUE-P1-NULLS", "FUND-QUALITY-P1-NULLS",
                               "FUND-DIVLOWVOL-P1-NULLS"):
            out[e["id"]] = e
    return out


def main():
    lines = []
    now = datetime.datetime.now()
    lines.append("PROBE_TS " + now.isoformat(timespec="seconds"))
    lines.append("R473_OBS " + json.dumps(R473_OBS, ensure_ascii=True))
    # fresh fetch
    r = run(["git", "fetch", "origin"])
    lines.append("FETCH_RC " + str(r.returncode))
    # origin tip
    r = run(["git", "rev-parse", "origin/main"])
    tip = r.stdout.decode().strip()
    lines.append("ORIGIN_TIP " + tip)
    # origin pool FUND trio full fields
    r = run(["git", "show", "origin/main:results/runnable_pool.json"])
    trio = pool_blob_fund_trio(r.stdout)
    lines.append("--- ORIGIN FUND trio full entries ---")
    lines.append(json.dumps(trio, ensure_ascii=True, indent=1))
    # local HEAD side
    r = run(["git", "show", "HEAD:results/runnable_pool.json"])
    trio_h = pool_blob_fund_trio(r.stdout)
    lines.append("--- LOCAL HEAD FUND trio (should == origin post-merge) ---")
    lines.append(json.dumps(trio_h, ensure_ascii=True, indent=1))
    # bm-a r678 commit and its parent pool face
    r = run(["git", "log", "--oneline", "-n", "4", "origin/main"])
    lines.append("--- origin log 4 ---")
    lines.append(r.stdout.decode("utf-8", "replace"))
    # which commit last touched runnable_pool.json
    r = run(["git", "log", "--oneline", "-n", "3", "--", "results/runnable_pool.json"])
    lines.append("--- last commits touching runnable_pool.json (HEAD history) ---")
    lines.append(r.stdout.decode("utf-8", "replace"))
    # bm-b heartbeat
    hb_path = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
    if os.path.exists(hb_path):
        hb = json.load(open(hb_path, encoding="utf-8-sig"))
        lines.append("--- bm-b heartbeat key fields ---")
        keep = {k: hb.get(k) for k in ("last_seen", "heartbeat_epoch_utc",
                                       "round_no", "current_task", "verdict",
                                       "activity_now")}
        lines.append(json.dumps(keep, ensure_ascii=True, indent=1))
        ls = hb.get("last_seen", "")
        try:
            ls_dt = datetime.datetime.fromisoformat(ls)
            lines.append("BM_B_HB_AGE_MIN " + str(round((now - ls_dt).total_seconds() / 60.0, 1)))
        except Exception:  # noqa: BLE001
            lines.append("BM_B_HB_AGE_MIN unreadable: " + ls)
    else:
        lines.append("BM_B_HEARTBEAT_MISSING")
    # nulls file local mtimes + tail growth stamp (are the trio files pushed recently?)
    for fam, rel in (("VALUE", "results/fund_value_p1/nulls.jsonl"),
                     ("QUALITY", "results/fund_quality_p1/nulls.jsonl"),
                     ("DIVLOWVOL", "results/fund_divlowvol_p1/nulls.jsonl")):
        p = os.path.join(ROOT, rel.replace("/", os.sep))
        if os.path.exists(p):
            mt = datetime.datetime.fromtimestamp(os.path.getmtime(p))
            lines.append(f"NULLS_FILE {fam} mtime {mt.isoformat(timespec='seconds')} age_min {round((now - mt).total_seconds() / 60.0, 1)}")
        else:
            lines.append(f"NULLS_FILE {fam} MISSING")
    # crash fuse faces on origin (trio relevant)
    for f in ("results/crash_fuse.json",):
        r = run(["git", "show", "origin/main:" + f])
        if r.returncode == 0:
            try:
                d = json.loads(r.stdout.decode("utf-8-sig"))
                lines.append("--- origin " + f + " (trio keys) ---")
                trio_keys = {k: v for k, v in d.items()
                             if isinstance(k, str) and ("FUND" in k or "fund" in k)}
                lines.append(json.dumps(trio_keys if trio_keys else d,
                                        ensure_ascii=True, indent=1)[:2000])
            except Exception as e:  # noqa: BLE001
                lines.append("CRASH_FUSE parse error " + str(e))
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(lines))
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
