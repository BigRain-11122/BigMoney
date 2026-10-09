# r943 bm-a: THERMO-OVERLAY-P1-BURN pool done-flip surgery (two-layer, r688 law)
# stale-ready root cause: r942 absorbed verdict + claim closed but pool entry flip missed
# -> watermark red lane "pool-batch-runnable-idle-low-cpu"
import json, sys

EID = "THERMO-OVERLAY-P1-BURN"
RESULT_REF = ("results/thermo_overlay_p1/thermo_overlay_p1_results.json "
              "(0/6 full-chain honest multi-cell negative per frozen sec.5; M1 4/6 P100/P500/P1000/H16; "
              "F6 P1000 17<30 per sec.5.3; best P1000 Sharpe 0.6509 +0.047 vs passive, maxdd zero improvement; "
              "gate_attrition judgment row ledger 862,151; prereg sec.7/8 backfilled commit 0039da1c7; "
              "claim closed ok 05:02:41 pid 5476)")
DONE_AT = "2026-10-10T05:02:41+08:00"
FLIP_NOTE = ("r943 bm-a done-flip (stale-ready heal): burn completed 05:02:41 + verdict absorbed r942 "
             "(sec.7/8 + attrition row + T-181 done) but entry flip was missed -- watermark red "
             "pool-batch-runnable-idle-low-cpu root cause; claim file closed-ok evidence "
             "results/pool_claims/THERMO-OVERLAY-P1-BURN/thermo-overlay-p1-burn-0of1.bm-a.json")

def flip(path):
    with open(path, "rb") as f:
        raw = f.read()
    bom = raw[:3] == b"\xef\xbb\xbf"
    txt = raw.decode("utf-8-sig")
    crlf = "\r\n" in txt
    d = json.loads(txt)
    hit = False
    for e in d.get("entries", []):
        if e.get("id") == EID:
            if e.get("status") == "done":
                print(f"[flip] {path}: already done (idempotent skip)")
                hit = True
                break
            assert e.get("status") == "ready", f"unexpected status {e.get('status')}"
            e["status"] = "done"
            e["result_ref"] = RESULT_REF
            e["done_at"] = DONE_AT
            e["note"] = ((e.get("note") or "") + " | " + FLIP_NOTE).strip(" |")
            for s in e.get("shards", []):
                if s.get("status") == "ready":
                    s["status"] = "done"
                    s["done_at"] = DONE_AT
            hit = True
            break
    assert hit, "entry not found"
    out = json.dumps(d, ensure_ascii=False, indent=1)
    if crlf:
        out = out.replace("\n", "\r\n")
    with open(path, "wb") as f:
        if bom:
            f.write(b"\xef\xbb\xbf")
        f.write(out.encode("utf-8"))
    # parse-verify (r185)
    json.loads(open(path, "rb").read().decode("utf-8-sig"))
    # assert done flip stuck
    d2 = json.loads(open(path, "rb").read().decode("utf-8-sig"))
    e2 = [x for x in d2["entries"] if x["id"] == EID][0]
    assert e2["status"] == "done" and all(s["status"] == "done" for s in e2["shards"])
    print(f"[flip] {path}: entry+shards -> done, parse-verified, crlf={crlf} bom={bom}")

if __name__ == "__main__":
    flip("results/runnable_pool.json")
    flip("results/runnable_pool.bm-a.json")
    print("TWO-LAYER FLIP DONE (shared + bm-a lane mirror)")
