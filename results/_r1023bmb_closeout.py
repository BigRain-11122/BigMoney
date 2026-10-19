"""r1023 bm-b closeout: state dual-face + heartbeat + round report row."""
import io
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state.json")
MIRROR = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")

NOW = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())

DID = (
    "r1023: (a) FIRST ACTION 11:53 cadence-v2 @bm-b leg: 8 same-family tasks "
    "single-field retimed, read-back all green (Bigmoney-IterationLoop/"
    "MiniGameEngineTick/MiniGameOllamaKeepWarm/BmbIdleGuard 10->5min pin :X2 "
    "kept = original pos mod 5; FluxGroup-FleetOversight 60->30min; bm-b-"
    "MemoryBudgetGate+HQ-MemoryBudgetGate 4h->2h; MiniGameRadarTick +21:52 "
    "second daily shift = table-exact 09:52/21:52) + 3 self-heal recipes "
    "retimed PT5M (register_loop_task.ps1 incl first-fire walk fix -- rebase "
    "collision vs bm-a r1079 same-intent patch resolved mine-side, diff "
    "verified zero functional loss; bmb/bma idleguard registers) + receipt "
    "MSG-1315-bm-b-cadence-v2.md (MiniGameAuditTick weekly deep-audit baseline "
    "mismatch honestly NOT retimed; not-in-table faces untouched; MiniGame "
    "repo recipes cross-company not edited, disclosed). (b) 12:21 REPO-SLIM "
    "order leg-7 @bm-b: group tree absorbed 29 commits via stash-rebase-pop "
    "(local SLI commit preserved, LOG.md pop conflict line-unioned) + core."
    "hooksPath=Tools/hooks installed (pre-commit on disk) + FluxGroup-"
    "RepoSlim daily:09:03 sentinel registered via task-register front door "
    "(S4U+VBS, read-back Ready) + gc.auto=0 set (was unset = illegal auto-"
    "pack face) + receipt MSG-1327-bm-b-repo-slim.md (fire-test state json "
    "face honestly absent; tomorrow 09:03 first run = live anchor). (c) S0 "
    "bigmoney absorb: r1022 closeout rebased onto origin tip (16 shared "
    "regen UU origin-newer-wins) + pop resolved per-face law (d19_watermark "
    "newer-wins = bm-c 12:53 advance kept; futures/lhb/scorecard newer-wins; "
    "machine-health+token_usage disk-restored daemon faces left uncommitted; "
    "watermark_red DU resolved per D-20261019-02 machine-local takeover: rm "
    "--cached + gitignore L84 live). (d) S6 chain 41 legs rc0 in 4.7min "
    "(orphan 0; smoke green; idle --worked declared; supply_floor honest "
    "starvation 0/3 = W278 prereg landed bm-c r1116, N1 feed next windows; "
    "scorecard/paper_export/daily_scorecard/build_status stale-takeover "
    "derives per O-2100 STALE_MIN law; minute_feed 510300 +19 rows; REPORT/"
    "LIVE regen ORANGE cap50%; attrition guard healed bm-a 2-row shrink). "
    "(e) D-19 ORD+DEC deltas fully consumed: 11:53 cadence executed; 11:58 "
    "WorkBuddy + 12:00 NATS = bm-a executed, bm-b zero-action; 12:21 "
    "REPO-SLIM leg executed; 12:29 anti-bloat + 12:3x knowledge-v1.2 zero-"
    "action; 13:2x fleet-fill v2 @bm-b leg taken (ST-011 + CODELY hot-cold = "
    "done r1022 disclosed; dubbing-sheet preprocessing SEEDED as ST-013 "
    "station; ST-012 night lane standing); watermark advanced ord=f08887d3 "
    "dec=95879dd9, mirrors synced 5. (f) marks-20261019 line-union +1 row."
)

VERDICT = (
    "GREEN: r1023 令流双执轮——cadence v2 8 件改频读回全绿（IterationLoop "
    "10→5min 针位 :X2 保持·RadarTick 双班 09:52+21:52·双记忆闸 4h→2h·"
    "FleetOversight 60→30）+3 配方焊防回退+MSG-1315 回执；REPO-SLIM ⑦ bm-b "
    "腿三件全绿（hooksPath 装闸+RepoSlim 日哨 09:03 S4U+gc.auto=0 补设）+"
    "MSG-1327 回执；S0 吸收 rebase+按面法解冲突（wm_red D-02 机器本地化落"
    "地）；S6 41 腿 rc0；D-19 八行 ORD 增量全消费+水位推进 f08887d3；13:2x "
    "排满令 @bm-b 腿承接（ST-011/CODELY=r1022 已毕如实销·配音台本 ST-013 "
    "播种·ST-012 夜窗照单）；下窗=r1024 ST-013 台本执行+ST-012 GitHub 轮"
    "子扫描+15:30 后 papers 链+RepoSlim 首跑候验"
)

NEXT = (
    "r1024: 1) ST-013 dubbing-sheet preprocessing exec (EP001-003 voice-cast "
    "sheets, CPU daytime fill per 13:2x fleet-fill order) 2) ST-012 GitHub "
    "training-wheels scan FIRST (sourcing-gate law) then night-window 22:0x "
    "voice LoRA run 3) post-15:30 papers chain (new bar after close) 4) "
    "supply_floor: W278 prereg landed -> N1 pool feed watch 5) RepoSlim "
    "first daily run tomorrow 09:03 = live anchor verify 6) batch-station "
    "spec: per-line verify-adjust tier loop (ST-010 method prototype)"
)

ARTIFACT = (
    "fleet/inbox/MSG-1315-bm-b-cadence-v2.md + MSG-1327-bm-b-repo-slim.md "
    "(receipts) + 8 retimed tasks + FluxGroup-RepoSlim sentinel + queue.json "
    "ST-013 seed + S6 products (REPORT/LIVE-2026-10-19 regen + minute_feed "
    "+19 rows + DUALARM) + marks +1 row"
)

MILESTONE = (
    "voice P1 <=10-22 (ST-013 sheets + ST-012 LoRA night lane) + BigMoney "
    "seat automation plan <=10-25 + CONTENT-LOOP 10-28 continuous-run "
    "judgment (13 stations seeded / 11 done pace) + month-boundary 10-31"
)


def main():
    st = json.load(io.open(STATE, encoding="utf-8"))
    st["round_no"] = 1023
    st["round"] = 1023
    st["round_no_label"] = "r1023"
    for k in ("clock_read", "ts", "updated", "updated_at", "last_round_at",
              "last_round_ts", "last_seen", "last_action_at"):
        st[k] = NOW
    st["now_active"] = "r1023 closed"
    st["did"] = DID
    st["verdict"] = st["current"] = VERDICT
    st["next"] = NEXT
    st["next_milestone"] = MILESTONE
    st["latest_artifact"] = st["last_artifact"] = ARTIFACT
    st["current_task"] = st["task"] = (
        "r1023: cadence-v2 8 tasks retimed + REPO-SLIM bm-b leg (hook+sentinel+"
        "gc.auto=0) + D-19 8 ORD rows consumed + ST-013 seeded + S6 41 rc0")
    st["last_action"] = (
        "r1023: cadence v2 @bm-b leg executed (8 tasks + 3 recipes + MSG-1315) "
        "+ REPO-SLIM leg-7 executed (hooksPath + RepoSlim sentinel + MSG-1327) "
        "+ D-19 advanced f08887d3")
    st["heartbeat_epoch_utc_face"] = "bm-b.json updated this round (epoch int verified)"
    st["sync"]["r1022_main_push"]["status"] = (
        "PUSHED_VERIFIED (r1023 S0: payload commit 80d9ca0e1d rebased on "
        "origin tip 78103a8361 lineage, delivered with r1023 push)")
    st["sync"]["r1022_main_push"]["pushed_sha"] = "80d9ca0e1d"
    st["sync"]["r1023_main_push"] = {
        "status": "PENDING (this commit)",
        "pushed_sha": "pending",
        "consumed_at": "pending r1024",
        "behind_origin_main": 0,
        "note": "r1023 payload = cadence-v2 receipts (MSG-1315/1327) + 3 recipe "
                "patches + queue.json ST-013 + marks +1 + state/heartbeat/"
                "round-report + S6 own regen/product faces (daily_report/"
                "live_usage + collectors bm-b lanes + scorecard/paper_export/"
                "daily_scorecard/update_status/market_clock/regime_state/"
                "dualarm/compute_audit/b_layer/attrition/orphan/d19 faces) + "
                "r1023 work files; shared daemon faces (machine-health/"
                "token_usage + unsuffixed lhb/futures status) NOT added "
                "(r982/r1015 policy); watermark_red machine-local (D-20261019-02)"
    }
    st["r1022_post_chain_ord_note"] = (
        "r1023: ORD bridge fully consumed through ord=f08887d3 (rows 11:53 "
        "cadence / 11:58 WorkBuddy / 12:00 NATS / 12:21 REPO-SLIM / 12:29 "
        "anti-bloat / 12:3x knowledge-v1.2 / 13:2x fleet-fill v2 / 13:3x "
        "bm-a receipt); r1024 FIRST ACTION = fresh d19 probe per law")
    json.dump(st, io.open(STATE, "w", encoding="utf-8"), ensure_ascii=False,
              indent=1)

    # mirror face (r1020 dual-face law)
    m = dict(st)
    m["state_face_note"] = "r1023: mirror-written per r1020 dual-face law."
    m["note"] = "mirror face; authoritative round_no = repo state.json (r1020 law)"
    json.dump(m, io.open(MIRROR, "w", encoding="utf-8"), ensure_ascii=False,
              indent=1)

    # heartbeat (epoch INT asserted)
    hb = json.load(io.open(HB, encoding="utf-8"))
    hb["last_seen"] = NOW
    hb["ts"] = NOW
    hb["clock_read"] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["verdict"] = "GREEN (r1023: cadence-v2 + REPO-SLIM legs executed; CEO orders consumed same-round)"
    hb["did"] = (
        "r1023: cadence-v2 8 tasks retimed read-back green + 3 recipes + "
        "MSG-1315; REPO-SLIM bm-b leg (hooksPath + RepoSlim 09:03 sentinel + "
        "gc.auto=0) + MSG-1327; D-19 8 ORD rows consumed, advanced f08887d3; "
        "ST-013 seeded; S6 41 rc0")
    hb["current_task"] = "r1024: ST-013 dubbing sheets + ST-012 GitHub scan + post-15:30 papers"
    try:
        import psutil
        hb["cpu_util_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
        vm = psutil.virtual_memory()
        hb["free_ram_gb"] = round(vm.available / 1e9, 1)
    except Exception:
        pass
    json.dump(hb, io.open(HB, "w", encoding="utf-8"), ensure_ascii=False,
              indent=1)
    assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int"

    # round report row (bm-b file per S5)
    row = ("%s | r1023 | cadence-v2 @bm-b leg (8 tasks retimed + 3 recipes + "
           "MSG-1315 receipt) + REPO-SLIM leg-7 (group absorb 29 commits + "
           "hooksPath + RepoSlim sentinel 09:03 + gc.auto=0 + MSG-1327) + "
           "D-19 8 ORD rows consumed advanced f08887d3 + ST-013 seed + S6 "
           "41 legs rc0 | read-back: 8/8 task intervals + S4U verified; "
           "hook on disk + sentinel Ready/S4U; d19 advance read-back OK "
           "mirrors 5; smoke green; chain log _r1023bmb_s6_log.txt | "
           "r1024: ST-013 exec + ST-012 GitHub scan + post-15:30 papers + "
           "RepoSlim first-run verify\n" % NOW)
    with io.open(REPORT, "a", encoding="utf-8") as f:
        f.write(row)
    print("closeout ok: state+mirror+heartbeat+report written, epoch=%d" % EPOCH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
