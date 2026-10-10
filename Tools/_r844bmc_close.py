# -*- coding: utf-8 -*-
"""r844 bm-c books close: round report line + state face + heartbeat face.
Phase-2 of the two-phase close (phase-1 DELIVERED d771dc969 0/0 self-verified).
Measured stats: ram=1.9 cpu=15 gpu_free=114 @ 2026-10-11T01:45:36+08:00.
JSON-safe python surgery; heartbeat orders_ack untouched (assert)."""
import json
import os
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = "2026-10-11T01:46:00+08:00"
EPOCH = int(time.time())
DELIVERED = "d771dc969"
RAM = 1.9
CPU = 15
GPU = 114

CURRENT_TASK = (
    "当前活: jman LoRA 训练在烧（trainer 21288 活·ep6 cont-000002 已落 00:51·log 01:16 新鲜·ETA ~09:45-10:00 回 SLA 窗内·VRAM 114MB 边缘 OOM watch）"
    "+W206 守望 cron 在位（bfea5373·17min）+W205 finalize 未落=等上游 | "
    "最近实物: Tools/s05_probe.py 常设 S0.5 组合器（r843 技术债 heartbeat 读位修复·自检 10/10+实弹 exit 0）"
    "+W206 freeze executor 三修全验（bm-b MSG-0120 收讫·预检 22/22 PASS）"
    "+S6 43/43 rc0 @ 2026-10-11T01:46:00+08:00 | "
    "下个里程碑: r845 训练完训窗 ~09:45-10:00（val_grid+LOOKBOARD+恢复债三件）+W205 finalize 落链→W206 freeze 即点即燃（≤48h）"
)

DID = (
    "r844 bm-c: (1) round-zero orphan probe 1 face (ComfyUI 8188 idle server, parent-dead+stalled, "
    "read-only no-kill -- recovery-debt trio owns its restart); (2) S0 fetch 0-behind; S0.5 dual watermark "
    "HOLD (ORD 4d33cb4f / DEC 68d13893 zero-delta) + unacked 0 (67 orders / 192 acks); S7 close rescan exit 0 "
    "identical; (3) S1 smoke 49/49; S2 boards empty (job_list 0, fleet tasks 0 open, tech/explore queues all "
    "done/closed); (4) PRODUCT-A Tools/s05_probe.py standing S0.5 composer (r843 queued tech chore): "
    "heartbeat-face fix -- bug: ad-hoc probe lineage read orders_ack from state (key absent = empty set = "
    "false unacked longlist, r843 adjudication); fix = compose d19_watermark probe (face A) + "
    "orders_ack_scan.scan() (face B heartbeat) + exit priority fault>unacked>delta>green; selftest 10/10 "
    "PASS + live run exit 0 matching manual dual-checks; ad-hoc probe lineage retired; (5) S6 43/43 rc0 "
    "(r844 driver clone, weekend honest no-ops; lhb WARN: old status file corrupt -> self-healed fresh "
    "valid JSON cutoff 2026-10-09 -- watch item); (6) PRODUCT-B W206 freeze executor three-fix per bm-b "
    "MSG-20261011-0120 (receipted, moved processed, reply MSG-20261011-0145 outbox): EOL runtime detection "
    "per-file + line_indent parameterized + hardcoded CRLF count-gate removed (deep finding: bm-b measured "
    "origin blob = pure LF; local checkout = autocrlf CRLF uniform crlf_n1=42895 lone_lf=0 -- runtime "
    "detection two-state, supersedes both assumptions); par_sec extraction fixed to PURE estate segment "
    "(full span 51 = 50 estate + 1 W204 upstream leg empirically confirmed; estate cut at W204-leg assert "
    "line start = exactly 50 rows, dual assert estate==50 and full==51); prose arithmetic 4x machine-"
    "derived fmt(w205_a_tail+1)=467_804 (was 465_805 slip) + new leg1.ARITH_A mirror assert; segment "
    "preflight 22/22 PASS against live landed faces (results/_r844bmc_w206_preflight.py); (7) training "
    "follow: trainer 21288 alive (CPU 46.9k s, WS 7.6GB), ep6 checkpoint cont-000002 landed 00:51:54, "
    "train_log fresh 01:16:45, completion ETA ~09:45-10:00 inside SLA; W205 finalize NOT landed -> M8 "
    "watcher armed; (8) push chain: phase-1 commit -> push rejected (bm-b r852/853 landed on origin) -> "
    "rebase 14 UU (regen/runtime faces, per-file ts newer-wins all-mine 01:32-33 > theirs 01:30-31, "
    "resolver _r844bmc_rebase_resolver.py) -> r863 zero-UU churn reject twice (backup+checkout+continue "
    "recipe) -> r808 Terminal-dumb escape (author-script inject + commit -F + continue) -> DELIVERED "
    "d771dc969 0/0 push+fetch self-verified (s05_probe.py blob a3ad7709 on origin); (9) S7 quartet green "
    "(loop pin=5 no-op, watchdog registered, pre-commit/pre-push claws installed) + attrition 4 ledgers "
    "CLEAN; (10) round ledger md resumed after r817 (r818-r843 gap note: those rounds live in commit log "
    "+ state face)."
)

SUMMARY = (
    "r844 close: s05_probe.py standing composer delivered (r843 tech debt, heartbeat face, 10/10+live rc0) "
    "+ W206 executor three-fix per bm-b MSG-0120 (preflight 22/22) + S6 43/43 rc0 + push-race rebase "
    "closed (14 UU ts-newer-wins + r863/r808 pits walked) + training follow (ETA in SLA)"
)

NEXT = (
    "r845: (1) training harvest window ~09:45-10:00: ep8+ checkpoint verify, completion -> jman_val_grid "
    "+ LOOKBOARD_variant_640 + recovery-debt trio (Ollama twin enable + llama-server + ComfyUI restart) "
    "per O-20261010-0025 SLA (10:00 对比板上链); (2) W205 finalize landing follow -> W206 freeze "
    "instant-ignite (executor three-fix in place, preflight 22/22, watcher cron bfea5373 armed 17min); "
    "(3) S0.5 now standing: python Tools\\s05_probe.py (no more ad-hoc clones); (4) lhb status WARN watch "
    "(self-healed; recurrence -> tech queue row); (5) post-training RAM release -> green-idle re-eval + "
    "light opportunistic claim re-eval (O-20261011-0012 sec 2.3)."
)

VERIFY = (
    "receipts: DELIVERED d771dc969 0/0 (push+fetch self-verified, s05_probe.py blob a3ad7709 on origin) + "
    "smoke 49/49 + S6 43/43 rc0 + s05_probe selftest 10/10 + live exit 0 + W206 preflight 22/22 + "
    "attrition 4 CLEAN + quartet green (pin=5 no-op, watchdog, claws) + idle --worked + this books commit"
)

REPORT_LINE = (
    "2026-10-11T01:46:00+08:00 | r844 | dept:工程/舰队（s05_probe 常设组合器交付+W206 executor 三修+S6 43 腿+推送竞窗 rebase 收口·第 133 bm-c 连守轮·md 账本 r817 后恢复〔r818-r843 轮账在 commit log+state 面〕） | "
    "本地未达 origin commit 数=0（phase-1 DELIVERED d771dc969 push+fetch 自证·本 books commit 收口后再自证） | "
    "WM-VERDICT: 绿（red=false·ORD 4d33cb4f hold 零 delta/DEC 68d13893 hold 零 delta·unacked 0〔67 orders〕·S7 收尾双扫 exit 0 恒等〔新常设组合器〕） | "
    "孤儿面=1（只读不杀·ComfyUI 8188 idle server·恢复债三件套含其重启） | "
    + DID +
    " | 下轮指针: " + NEXT
)


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def main():
    # --- state ---
    sp = os.path.join(REPO, "state-bm-c.json")
    st = load(sp)
    for k in ("round_no", "loop_round", "last_round"):
        st[k] = 844
    st["round_no_label"] = "r844"
    for k in ("clock_read", "ts", "last_seen", "last_seen_at", "last_ts", "updated",
              "updated_at", "current_task_at", "last_round_at", "last_round_summary_at",
              "last_orders_read_at", "last_decisions_read_at", "last_decisions_at",
              "last_orders_at", "last_run_at", "last_round_closed", "last_pulled_at",
              "last_round_ts", "last_seen_at"):
        st[k] = NOW
    st["current_task"] = CURRENT_TASK
    st["activity_now"] = CURRENT_TASK
    st["did"] = DID
    st["verdict"] = DID
    st["last_round_summary"] = SUMMARY
    st["note"] = ("r844 = s05_probe.py standing composer delivered (r843 tech debt closed) + W206 "
                  "executor three-fix per bm-b MSG-0120 (preflight 22/22, M8 watcher armed) + training "
                  "ETA in SLA ~09:45-10:00.")
    st["last_action"] = "r844 s05_probe standing composer + W206 three-fix + S6 chain + push-race rebase close"
    st["next_pointer"] = NEXT
    st["next"] = NEXT
    st["next_milestone"] = ("r845: training completion window ~09:45-10:00 (val_grid + LOOKBOARD + "
                            "recovery-debt trio) + W206 freeze on W205-finalize landing (<=48h)")
    st["latest_artifact"] = ("DELIVERED d771dc969 (Tools/s05_probe.py composer) + W206 executor three-fix "
                            "(preflight 22/22) + S6 43/43 rc0")
    st["last_artifact"] = st["latest_artifact"]
    st["recent_artifact"] = st["latest_artifact"]
    st["verify"] = VERIFY
    st["head_sha"] = DELIVERED
    st["health"] = "ok"
    st["orphan_face"] = 1
    st["orphan_faces"] = 1
    st["idle_rounds"] = 0
    st["agenda_starved"] = False
    st["free_ram_gb"] = RAM
    st["ram_free_gb"] = RAM
    st["idle_ram_gb"] = RAM
    st["cpu_pct"] = CPU
    st["cpu_util_pct"] = CPU
    st["cpu_idle_pct"] = 100 - CPU
    st["gpu_free_vram_mib"] = GPU
    st["gpu_free_vram_mb"] = GPU
    st["gpu_idle_vram_mib"] = GPU
    st["gpu_vram_free_mb"] = GPU
    st["sync"] = {
        "ahead_behind": "0/0",
        "origin_tip": DELIVERED,
        "ts": NOW,
        "note": ("r844 delivery: phase-1 commit -> push rejected (bm-b r852/853 on origin) -> rebase "
                 "14 UU per-file ts newer-wins (all-mine 01:32-33 > theirs 01:30-31) -> r863 zero-UU "
                 "churn recipe x2 + r808 author-inject commit -F -> push f6c13fba0..d771dc969 landed "
                 "0/0 self-verified"),
    }
    st["d19_watermark_guard"] = {
        "tool": "Tools/s05_probe.py (standing composer, r844)",
        "probe": "results/_s05_probe.bm-c.json",
        "probe_evidence": os.path.join(REPO, "results", "_s05_probe.bm-c.json"),
        "method_decisions": "sha256",
        "method_orders": "sha1",
        "verbatim": True,
        "advance": True,
        "round_ref": 844,
        "ts": NOW,
    }
    st["last_orders_sha_method"] = ("s05_probe composer face A (d19_watermark.py probe delegation); r844: "
                                    "ORD hold 4d33cb4f zero-delta, facts-driven from results/_s05_probe.bm-c.json")
    st["last_decisions_sha_method"] = ("s05_probe composer face A (d19_watermark.py probe delegation); r844: "
                                       "DEC hold 68d13893 zero-delta, facts-driven from results/_s05_probe.bm-c.json")
    save(sp, st)
    st2 = load(sp)
    assert st2["round_no"] == 844 and isinstance(st2["d19_watermark_guard"]["round_ref"], int)

    # --- heartbeat ---
    hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
    h = load(hp)
    ack_before = len(h.get("orders_ack", []))
    h["heartbeat_epoch_utc"] = EPOCH
    h["clock_read"] = NOW
    h["ts"] = NOW
    h["last_seen"] = NOW
    h["current_task"] = CURRENT_TASK
    h["activity_now"] = CURRENT_TASK
    h["last_round"] = 844
    h["round_no"] = 844
    h["free_ram_gb"] = RAM
    h["ram_free_gb"] = RAM
    h["cpu_pct"] = CPU
    h["cpu_idle_pct"] = 100 - CPU
    h["cpu_cores"] = 32
    h["cores"] = 32
    h["gpu_free_vram_mib"] = GPU
    h["gpu_free_vram_mb"] = GPU
    h["gpu_idle_vram_mib"] = GPU
    h["verdict"] = SUMMARY
    h["idle_rounds"] = 0
    h["agenda_starved"] = False
    h["health"] = "ok"
    save(hp, h)
    h2 = load(hp)
    assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
    assert len(h2.get("orders_ack", [])) == ack_before, "orders_ack mutated!"
    print("heartbeat updated: epoch int OK:", h2["heartbeat_epoch_utc"],
          "acks:", ack_before, "clock:", h2["clock_read"])

    # --- round report line (md ledger resumed post-r817 with gap note) ---
    rp = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
    with open(rp, "a", encoding="utf-8") as fh:
        fh.write(REPORT_LINE + "\n")
    with open(rp, encoding="utf-8") as fh:
        tail = fh.readlines()[-1]
    assert "r844" in tail, "report line append failed"
    print("round report line appended (md ledger resumed post-r817)")
    print("books close OK")


if __name__ == "__main__":
    main()
