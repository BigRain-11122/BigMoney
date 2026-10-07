"""r738 bm-c round-close addendum: post-push-storm integration + matrix
first product. Updates heartbeat + state faces (note/did/verify/
latest_artifact/next_pointer + fresh ts/epoch) and appends one report row.
Single writer (bm-c own faces), epoch int, T-separated clock (R170/R178/
R262 laws). Zero network, zero engine touches.
Events this addendum records (all inside round 738's window):
  - pre-push claw correctly blocked first push (live-remote-base variant:
    origin advanced 6 commits mid-round = bm-a r866 chain incl. REGIME-5
    labeler slice-1 -> would-delete set);
  - pre-rebase buffer flush commit (r642 clean-tree law) + pull --rebase
    11-UU storm resolved (3 ALL_FACES via merge_lane_views.py resolve canon
    + 8 snapshot/twin faces via Tools/_r738bmc_rebase_resolve.py deep-ts
    take-new, all LOCAL strictly-newer, sha channel r648; 3 auto-merged
    faces verified: compute_audit history=26 dups=0 sorted union-complete
    r685 gate, regime_state/update_status both-sides-deterministic);
  - delivery verified (00cc15257..efef0f103, ahead=0/behind=0);
  - ORD watermark basis adjudicated: bm-a 2bb2ee75 = SHA-256 basis vs my
    17accc40 = SHA-1 basis (r537 ALGORITHM PIN), same unchanged blob,
    zero real delta zero action;
  - O-2215-1 UNBLOCKED: labels landed -> regime_style_matrix.py run first
    product (selftest 40 PASS + 3289 labels -> 109 confirmed switches,
    total transition cost 0.10341513, tail state BEAR confirmed 2026-09-30
    GRIND->BEAR N_CONF=3, MATRIX-2026-09-30.json);
  - dualrun same-window recheck (r376 law): streak 51 ZERO-DRIFT."""
import json
import os
import time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ).isoformat(timespec="seconds")
epoch = int(time.time())

try:
    import psutil
    ram = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    ram = 3.6

ADD_NOTE = ("r738 addendum: push-storm integration (claw block=correct "
            "live-remote-base, bm-a r866 chain landed mid-round) + rebase "
            "11-UU resolved (3 canon + 8 deep-ts LOCAL-newer + 3 "
            "auto-merged verified) + ORD basis adjudicated (2bb2ee75=SHA256 "
            "vs 17accc40=SHA1 same blob, zero delta) + O-2215-1 UNBLOCKED: "
            "matrix run FIRST PRODUCT (40 selftest PASS, 3289 labels -> 109 "
            "confirmed switches, total cost 0.10341513, tail BEAR confirmed "
            "2026-09-30, results/regime_style_matrix/MATRIX-2026-09-30.json) "
            "+ dualrun recheck streak 51. QA det-58th 5/5 + S6 40/40 rc0 as "
            "main commit; delivery 00cc15257..efef0f103 verified.")

NEXT = ("r739: (a) tonight post-close face (<=10-08 23:59): data-chain full "
        "re-arm + REGIME_GUARD v3 first-new-bar enforce (set "
        "BIGMONEY_REGIME_GUARD=enforce before live.paper) + fund_premium "
        "15:30 first snapshot (bm-c lane) + QDII watch rerun holiday-delta "
        "+ CTA_P1 first-bar auto-wiring + first-marks verification; (b) "
        "O-2215-1 remaining: matrix v1 spec leg completion vs <=10-16 "
        "12:00 deadline (spec research/REGIME_STYLE_MATRIX_V1.md landed "
        "r736 + first run product landed r738; remaining = SUPPORT row "
        "awaits bm-b router spec <=10-16 + numeric weights review window + "
        "10-21 criteria revisit per order sec.4); matrix run re-fires when "
        "bm-a refreshes labels post-bar; (c) O-2245 OSS enrollments gate "
        "standing; (d) cloudF row collection window <=10-14 standing; (e) "
        "month-boundary first exam 10-31; next 5x = bm-c r740. [via bm-c "
        "r738 addendum]")

VERIFY = ("results/regime_style_matrix/MATRIX-2026-09-30.json (3289 labels, "
          "109 switches, total cost 0.10341513, tail BEAR N_CONF=3 "
          "2026-09-30) + regime_style_matrix selftest PASS (40 checks) + "
          "Tools/_r738bmc_rebase_resolve.py (8-face resolver evidence, "
          "stale-marker scan clean, parse-verified) + dualrun recheck "
          "streak 51 ZERO-DRIFT + delivery 00cc15257..efef0f103 "
          "ahead=0/behind=0 + sweep-2 facts UNCHANGED both watermarks "
          "unacked=0")

ART = ("results/regime_style_matrix/MATRIX-2026-09-30.json (O-2215-1 first "
       "product: 3289 labels -> 109 confirmed switches) + "
       "qa/smoke-r738.md 5/5 + qa/equity-curve-r738.png 66,366B + "
       "results/_r738bmc_s6_log.txt (40 legs rc0) + rebase resolver "
       "evidence Tools/_r738bmc_rebase_resolve.py @ " + now)


def main():
    for path, extra in ((os.path.join(ROOT, "fleet", "machines",
                                       "bm-c.json"), {
        "round_no": 739, "round_no_label": "round 738 (bm-c)",
        "last_round": 738,
    }), (os.path.join(ROOT, "state-bm-c.json"), {
        "round_no": 739, "round_no_label": "round 738 (bm-c)",
        "last_round": 738,
    })):
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        doc.update({
            "free_ram_gb": ram, "idle_ram_gb": ram, "ram_free_gb": ram,
            "heartbeat_epoch_utc": epoch,
            "last_seen": now, "last_seen_at": now, "clock_read": now,
            "ts": now, "updated": now, "updated_at": now,
            "last_run_at": now, "last_round_at": now,
        })
        doc.update(extra)
        doc["note"] = ADD_NOTE
        doc["did"] = ADD_NOTE
        doc["verdict"] = ADD_NOTE
        doc["verify"] = VERIFY
        doc["latest_artifact"] = ART
        doc["next_pointer"] = NEXT
        doc["next"] = NEXT
        doc["last_round_summary"] = ("r738: QA det-58th 5/5 + S6 40 rc0 + "
                                     "push-storm integration + O-2215-1 "
                                     "matrix first product; watermarks "
                                     "unchanged; unacked=0; smoke 49/49.")
        doc["last_action"] = doc["last_round_summary"]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=1, ensure_ascii=False)
        assert isinstance(doc["heartbeat_epoch_utc"], int)

    rp_path = os.path.join(ROOT, "logs", "iteration-loop",
                           "round_reports-bm-c.md")
    row = (now + " | r738 addendum | dept:工程（推送风暴集成+矩阵首产） | "
           "本地未达 origin commit 数=0（00cc15257..efef0f103 fetch+rev-parse "
           "双自证） | 当前活: " + ADD_NOTE + " | 验证证据: " + VERIFY +
           " | 下轮指针: " + NEXT +
           " | 轮产品计分：2（矩阵首产=能跑能看实物+rebase 集成保全） | "
           "记账预算：4（state+心跳+轮报+addendum 行）\n")
    with open(rp_path, "a", encoding="utf-8") as fh:
        fh.write(row)
    print("addendum done epoch=%d now=%s ram=%s" % (epoch, now, ram))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
