# -*- coding: utf-8 -*-
# r955 bm-c closeout: state + heartbeat write (R170/R178 epoch-int law, clock_read ISO8601 T-format)
import json, time, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
R = 956  # counter advance: dead r995 session absorbed; this window = r955, next = r956

VERDICT = ("green: 06:30 closeout DELIVERED (21/21 slots resolved: 17 locked + 4 disclosed C02/C03/C04/R05; "
           "QC-r955.json + I2V-URL-INDEX 51 rows + C04_v2 git delivery @ group-tree 6019c12; MSG-0625 receipt) "
           "+ W227 SEAT PUBLISHED (probe rc0 ADMIT A 514204..516203 + B 516204..516403, seed FREE x2, "
           "anchor W226 920989/K495120; RAM relief 0.2G->4.5G after i2v drain) + smoke 49/49 + dualrun streak 48 "
           "+ attrition CLEAN + quad green; i2v queue 0/0 drained, GPU idle 15G free, lane warm for director re-shakes")

PROD_LANES = ("GPU=i2v deathline batch COMPLETE 21/21 (last C07_v3 06:04:49, queue 0/0, lane warm for 07:00-08:30 "
              "director re-shakes; INT8 model unloaded, 15G VRAM free); CPU=N1 W226 complete + W227 SEATED "
              "(prereg derive = next window first action; RAM 4.5G >= 4G gate cleared)")

NEXT = ("r956: (1) W227 prereg derive (bloodline clone _w226bmc_prereg_derive.py + lineage replay preflight 46/46) "
        "-> five-face freeze splice -> engine self-burn 12/12 -> PRE-FINALIZE six-gate (W212-pattern law) -> finalize "
        "-> five-key + sec.7/8 backfill; (2) Tue 15:30 new-bar window: papers full chain + update family; "
        "(3) i2v director re-shake watch (assembly 07:00, CEO screen 08:30); (4) RAM recovery trio decision post-08:30; "
        "(5) W228+ projection A 516204..518203 / B 516404..516603 re-derive mandate inherited")

DID = ("r955 (absorb dead r955 session estate): (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=2 zero-kill "
       "(MV-lane infra kept); S0 fetch behind=0 clean; (2) ABSORB dead r955 estate: frame extracts + 3 sheets + 4 burn "
       "drivers (track2/c04fix/c07fix/reshake) -- all landings complete through C07_v3 06:04:49, queue 0/0 drained; "
       "(3) S0.5 ORD delta consumed = r954's own track-2 dispatch row (executed full-cycle this window: frames received "
       "04:45 -> pulled 04:54 -> i2v -> QC -> receipt); watermark 4aebbfc3->d559e530 canonical raw-blob sha256; "
       "DEC fb5825cb holds; unacked=0; PS line-join sha attempt caught by pinned-method law (r583/r865) discarded; "
       "(4) S1 smoke 49/49; (5) PRODUCT-1 deathline closeout: 11 new clips verdicted (C09_v2 8.0 LOCKED track-2 rescue "
       "confirmed / R02_v3 8.0 LOCKED ghost healed / C07_v3 8.0 LOCKED palette healed / R06 8.5 LOCKED / B01 7.5 "
       "borderline-PASS / INT2v1 8.0 PASS / INT4v2 6.0-vs-brief + 8.5-craft director-decide [frame has visible face vs "
       "whitelist faceless-plan note -- frame-stage deviation disclosed, i2v faithful] / C03_v2 5.5 FAIL disclosed "
       "[reveal event absent] / C04_v2new 7.0 borderline-FAIL disclosed [frame healed basalt+registers, glyph "
       "line-geometry ceiling] / R05_v2 7.0 FAIL disclosed [frozen tail + exposure ramp] / E03 7.0 borderline-FAIL "
       "[full-res adjudication: glass plane present, man gaze confirmed, woman reads adjacent-silhouette not "
       "carried-in-glass, her face crushed]) -> 21-slot tally 17 locked + 4 disclosed -> QC-r955.json + index 51 rows "
       "+ C04_v2 git delivery (CDN dedup-blocked, STALE row banned) -> group-tree origin 6019c12 + MSG-0625 closeout "
       "receipt to bm-a; (6) PRODUCT-2 W227 SEAT: probe derive boundary bug fixed (generation-shape docstring surgery: "
       "coding-header template -> find(i+3) + t[:i] prefix-preserve; residual assert held) -> probe rc0 ADMIT + seat "
       "MSG-0645 published; (7) S6 light: dualrun ZERO-DRIFT streak 48 + compute_audit FLAG pool_starvation/supply_floor "
       "(structural; W227 seat = supply response) + watermark insufficient_history fresh window + attrition 4 CLEAN; "
       "(8) S7 quad green + idle --worked (idle_rounds=0)")

def patch(path, updates):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    d.update(updates)
    d["round_no"] = R
    d["last_round"] = 955
    d["last_round_at"] = NOW
    d["clock_read"] = NOW
    d["ts"] = NOW
    d["updated"] = NOW
    d["heartbeat_epoch_utc"] = EPOCH
    d["verdict"] = VERDICT
    d["did"] = DID
    d["next"] = NEXT
    d["prod_lanes"] = PROD_LANES
    d["current_task"] = "r955 closeout done (06:30 i2v tally + W227 seat); W227 prereg derive = next first action"
    d["current_task_at"] = NOW
    d["last_round_summary"] = ("r955: 06:30 closeout 21/21 (17 locked + 4 disclosed) + W227 seat published "
                               "(A 514204..516203 / B 516204..516403 ADMIT)")
    d["last_action"] = "r955 closeout (QC-r955 verdicts + W227 seat + S6 light + S7 quad)"
    d["latest_artifact"] = ("QC-r955.json @ group-tree 6019c12 + I2V-URL-INDEX 51 rows + C04_v2 git delivery + "
                            "results/_w227bmc_20261012_probe_receipt.json (W227 ADMIT)")
    d["next_milestone"] = ("W227 prereg derive -> splice -> burn -> PRE-FINALIZE six-gate -> finalize (next window); "
                           "bm-a 07:00 assembly -> 08:30 CEO screen (deathline lane secured)")
    d["last_orders_sha"] = "d559e5300920b87e409cc98ff76d48122eec99cbdd5459fc172f734e6cfba908"
    d["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (canonical, group-tree origin/main git show; "
                                   "r955 consumed r954's own track-2 dispatch row 0bd5cb9; PS line-join FORBIDDEN per "
                                   "r583/r865 -- one line-join attempt caught+discarded this window)")
    d["last_orders_at"] = NOW
    d["last_orders_read_at"] = NOW
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    # self-proof: epoch must be int
    with open(path, encoding="utf-8") as f:
        chk = json.load(f)
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
    assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read not ISO8601 T-format"
    print("patched", path, "round", R, "epoch", chk["heartbeat_epoch_utc"])

patch(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json", {})
patch(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json", {
    "activity_now": "2026-10-13 06:4x | r955 | bm-c: 06:30 closeout 21/21 delivered (17 locked + 4 disclosed, "
                    "QC-r955 @ 6019c12) + W227 seat published (ADMIT A 514204..516203 / B 516204..516403); "
                    "counter 955->956",
    "last_decisions_sha": "fb5825cb68a9524e2e8f2df12caeb537e3cafbda64d09d2f8478943d9986a2a7",
    "free_ram_gb": 4.5, "ram_free_gb": 4.5, "idle_ram_gb": 4.5,
    "gpu_free_vram_mb": 15208, "gpu_idle_vram_mb": 15208,
    "idle_rounds": 0, "agenda_starved": False,
})
print("DONE")
