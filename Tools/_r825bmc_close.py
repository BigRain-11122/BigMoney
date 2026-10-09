# -*- coding: utf-8 -*-
"""r825 bm-c close: T-180 -> done, state round 825, heartbeat, ledger row.
Pattern credit: Tools/_r518bmc_close.py. UTF-8 no BOM, epoch int (F7 law)."""
import datetime
import json
import os
import subprocess
import time

import psutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE_NO_WINDOW = 0x08000000

TS = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
CPU = round(psutil.cpu_percent(interval=2))
RAM = round(psutil.virtual_memory().available / 1024 ** 3, 1)
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=CREATE_NO_WINDOW)
    GPU = int((r.stdout or b"").decode().strip().splitlines()[0])
except Exception:
    GPU = 0

# ---- T-180 -> done ----
tp = os.path.join(ROOT, "fleet", "tasks", "T-2026-10-10-180-P1.json")
t = json.load(open(tp, encoding="utf-8-sig"))
assert t.get("status") == "claimed" and t.get("claimed_by") == "bm-c"
t["status"] = "done"
t["completed_at"] = TS
t["result_ref"] = ("scripts/regime_gate_evidence.py v1.0 (dual-arm exporter: "
                   "REGIME-5 index arm x thermo emotion arm, joint_cutoff=min, "
                   "honest lag note, criteria=NONE descriptive face) + "
                   "results/regime_gate_evidence/EVIDENCE-2026-09-22.json + "
                   "evidence_latest.json (index n_labels=3289 cutoff 2026-09-30 "
                   "latest BEAR, emotion cutoff 2026-09-22 seal_rate 0.1192, "
                   "contract_receipt five_state validated vs "
                   "REGIME_STYLE_MATRIX_V1 sec.1) + selftest 4/4 PASS + "
                   "idempotent rerun no-op (content-hash match), verified r825")
t["notes"] = (t.get("notes", "") + " | done r825: predecessor r824 built exporter "
              "+ first evidence burn (03:08); r825 verified selftest 4/4, "
              "idempotent no-op, evidence JSON sane; ticket closed.")
with open(tp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(t, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("T-180 -> done")

DID = ("r825 bm-c: r824 dead-predecessor absorb + CEO-order training live-verified "
       "+ T-180 closed + T-181 claimed with prereg DRAFT v0 (wm-red remediation). "
       "(1) S0-1 anchor bm-c, orphan probe orphans=0 py_faces=15; predecessor r824 "
       "died mid-round after 4 commits (T-180 claim / churn absorb / merge / daemon) "
       "without state/ledger close -> this session r825, state absorbed round number "
       "824 (transient marker for QA driver round-read). (2) S0 fetch 0/0 aligned; "
       "dirty faces all bm-c-owned (predecessor artifacts + daemon live-state). "
       "(3) S0.5: DEC sha b87a92b1 / ORD sha e286f842 both MATCH (zero delta, zero "
       "new dispatch), orders_ack 185 zero unacked, inbox 1 file = MSG-20261009-173x "
       "bm-c->bm-b (addressee bm-b offline, left in place for its revival, not "
       "consumed by bm-c). (4) S1 smoke 49/49. (5) SatEngine status rc0 alive. "
       "(6) CEO order O-20261010-0025 jman training face: all three weights landed "
       "(dl3 direct 8-part download, receipt results/_r824bmc_krea2_dl_receipt.json "
       "overall=PASS, VAE sha gate PASS); predecessor first train attempt rc1 "
       "(ModuleNotFoundError lora_krea2, evidence TRAIN_EXIT_1 + probe file); "
       "relaunched 02:51 via D:/musubi-tuner/train_jman_v1.ps1 (PID 53412 on GPU) "
       "-- live-verified this round: GPU 93% util / 16.1GB used, train_log actively "
       "appending (03:20:45 mtime, 107KB, avr_loss 0.0608, step 5/4096 at 16.4s/it "
       "-- ETA ~18h -> ~21:00 tonight), RAM 0.5GB free (blocks_to_swap face, "
       "CEO-order priority). (7) T-180 closed: exporter selftest 4/4 + idempotent "
       "no-op + evidence JSON dual-arm sane -> status=done with result_ref. "
       "(8) T-181 claimed (only open ticket, claim+start same round) + deliverable "
       "research/THERMO_OVERLAY_P1.md DRAFT v0 (BAN-05 semantic exception "
       "new_data declared; BAN-04 textual false-positive on the word for "
       "combinatorial lattice cured by rewording; banned_direction_gate rc0 PASS "
       "on draft; alpha=behavioral bias with retail-wins answer; anchor "
       "quadruples for both arms incl thermo_daily.csv 1996-12-16 zero-warmup; "
       "evidence_cutoff 2026-09-22 P-5C; exit-axis choice-2 hold-to-end with "
       "default-exit-stack explicitly disabled; era stratification equal-calendar "
       "3-band per order item-5; block-permutation random baseline + N accounting; "
       "DRAFT-NOT-FROZEN banner + 8-item freeze checklist). (9) QA driver r825 "
       "DEFERRED by RAM guard (0.55GB available < 1.5GB threshold, CEO training "
       "protection; r823 pack already collected by predecessor 01:48; r825 pack "
       "next RAM-safe round or post-training). (10) S6 chain NOT re-run: "
       "predecessor's 41-leg chain completed 03:12:03 all-green (zero rc1/2/3) "
       "5 min before this session started -- double-open ban + RAM guard; "
       "watermark probe rerun verdict=insufficient_history (n=2 window). "
       "(11) S7: attrition scan CLEAN rc0, loop task pin=5 phase-ok, watchdog "
       "re-registered, both claws re-installed (LF-normalized), banned gate rc0.")

CURRENT = ("当前活: r825 收口轮——CEO 令 jman 训练在烧（PID 53412·GPU 93%·RAM 0.5GB·"
           "4096 步 ETA ~21:00）+T-180 已翻 done+T-181 已认领 prereg 草案 v0 落盘 | "
           "最近实物: research/THERMO_OVERLAY_P1.md（BAN-05 例外+禁开门 rc0 PASS+"
           "锚四元组+出场轴声明·DRAFT-NOT-FROZEN）+results/regime_gate_evidence/"
           "EVIDENCE-2026-09-22.json（双臂证据件·selftest 4/4）+T-180/181 票面翻新 @ " + TS +
           " | 下个里程碑: 训毕 ~21:00（恢复债=Ollama 双任务 enable+llama-server+ComfyUI 重启）"
           "→jman_val_grid 验证链→LOOKBOARD 上链；T-181 冻结门 8 项（F-04 MSG+episode 日期锚钉死+D6 数值）")

NEXT = ("(a) training watch: PID 53412 to ~21:00, then restore debt (Ollama dual "
        "tasks enable + llama-server + ComfyUI server restart) + jman_val_grid "
        "validation chain + LOOKBOARD. (b) T-181 freeze gate 8 items: episode "
        "date-grid anchor pinning + F-04 inbox MSG + D6 numeric pairs + state-cell "
        "design freeze + science_gates wiring -> freeze commit -> burn (RAM guard, "
        "post-training window). (c) QA r825 pack first RAM-safe round (>=1.5GB). "
        "(d) post-training: RAM freed -> S6 full chain resumes normal cadence; "
        "T-181 burn window. (e) training completion evidence: exit code + loss "
        "curve + outputs/jman_v1_640 artifacts.")

VERIFY = ("receipts: smoke 49/49 + SatEngine rc0 + attrition CLEAN "
          "(results/_attrition_guard_scan.json) + banned_direction_gate rc0 on "
          "THERMO_OVERLAY_P1 draft + regime_gate_evidence selftest 4/4 + "
          "idempotent no-op + train proc PID 53412 live (GPU 93%, log mtime "
          "03:20:45) + T-180 ticket done (result_ref) + T-181 claimed + loop "
          "pin=5 no-op + watchdog registered + both claws installed + DEC/ORD "
          "watermarks MATCH (zero delta) + orders_ack 185 + this close "
          "commit/push_verify.")

S7 = ("S7 quartet: loop task pin=5 phase-ok (no-op) + watchdog registered + "
      "precommit claw installed + prepush claw installed; attrition scan CLEAN "
      "rc0 (4 ledger files, historical healed rows as-recorded); orphan face=0 "
      "(py_faces=15); state round_no 823->824 absorb marker->825 close.")


def main():
    st = os.path.join(ROOT, "state-bm-c.json")
    with open(st, encoding="utf-8-sig") as fh:
        s = json.load(fh)
    s["round_no"] = 825
    s["round_no_label"] = "round 825 (bm-c)"
    s["did"] = DID
    s["last_round"] = ("r825 bm-c: r824 dead-predecessor absorb + training "
                       "live-verified (GPU 93%, avr_loss 0.0608, ETA ~21:00) + "
                       "T-180 done + T-181 claimed w/ prereg DRAFT v0 (banned "
                       "gate rc0) + QA driver RAM-guard deferral + S6 "
                       "double-open ban (predecessor chain all-green 03:12).")
    s["verdict"] = DID
    s["verify"] = VERIFY
    s["next"] = NEXT
    s["current_task"] = CURRENT
    s["current_task_at"] = TS
    s["note"] = S7
    for k in ("ts", "updated", "updated_at", "last_seen", "last_seen_at", "last_ts",
              "last_round_at", "last_round_ts", "clock_read", "last_decisions_read_at"):
        s[k] = TS
    s["cpu_pct"] = CPU
    s["cpu_util_pct"] = CPU
    s["cpu_idle_pct"] = 100 - CPU
    s["idle_ram_gb"] = RAM
    s["ram_free_gb"] = RAM
    s["free_ram_gb"] = RAM
    s["gpu_free_vram_mib"] = GPU
    s["idle_rounds"] = 0
    s["agenda_starved"] = False
    s["latest_artifact"] = ("research/THERMO_OVERLAY_P1.md (T-181 prereg DRAFT v0, "
                            "banned-gate rc0) + results/regime_gate_evidence/"
                            "EVIDENCE-2026-09-22.json (T-180 dual-arm evidence) + "
                            "train PID 53412 live")
    s["next_milestone"] = ("training done ~21:00 -> restore debt + jman_val_grid + "
                           "LOOKBOARD; T-181 freeze gate 8 items; QA r825 pack "
                           "first RAM-safe round")
    with open(st, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(s, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    hb = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    with open(hb, encoding="utf-8-sig") as fh:
        h = json.load(fh)
    h["round_no"] = 825
    h["round_no_label"] = "round 825 (bm-c)"
    h["activity_now"] = ("r825: CEO-order jman training live-verified (GPU 93%, "
                         "avr_loss 0.0608, step ~5/4096, ETA ~21:00; weights all "
                         "landed sha-gate PASS) + T-180 regime-gate dual-arm "
                         "evidence closed (selftest 4/4, idempotent, ticket done) "
                         "+ T-181 thermo-overlay prereg DRAFT v0 (banned gate rc0, "
                         "BAN-05 exception declared) + r824 dead-predecessor "
                         "absorbed + S6 predecessor chain all-green 03:12 + QA "
                         "driver RAM-guard deferred (0.55GB)")
    h["current_task"] = CURRENT
    h["current_task_at"] = TS
    h["last_seen"] = TS
    h["last_seen_at"] = TS
    h["updated_at"] = TS
    h["updated"] = TS
    h["ts"] = TS
    h["clock_read"] = TS
    h["heartbeat_epoch_utc"] = int(EPOCH)
    h["cpu_pct"] = CPU
    h["cpu_util_pct"] = CPU
    h["cpu_idle_pct"] = 100 - CPU
    h["idle_ram_gb"] = RAM
    h["ram_free_gb"] = RAM
    h["free_ram_gb"] = RAM
    h["gpu_free_vram_mib"] = GPU
    h["gpu_free_mb"] = GPU
    h["gpu_idle_vram_mb"] = GPU
    h["gpu_idle_vram_mib"] = GPU
    h["gpu_vram_free_mb"] = GPU
    h["idle_rounds"] = 0
    h["agenda_starved"] = False
    h["latest_artifact"] = ("research/THERMO_OVERLAY_P1.md + results/"
                            "regime_gate_evidence/EVIDENCE-2026-09-22.json + "
                            "T-180/181 ticket flips")
    h["next_milestone"] = ("training done ~21:00 -> restore debt + val grid + "
                           "LOOKBOARD; T-181 freeze gate; QA r825 pack RAM-safe "
                           "round")
    h["verdict"] = DID
    with open(hb, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(h, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    assert isinstance(h["heartbeat_epoch_utc"], int), "epoch must be JSON int (F7 law)"

    rr = os.path.join(ROOT, "round_reports-bm-c.md")
    raw = open(rr, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
    row = (f"{TS} | r825 | dept:工程/研究（CEO 令训练监控+T-180 收口+T-181 认领开动+r824 前驱收编） | "
           f"WM-VERDICT: 红→已处置（red=true lane=runnable-work-idle-low-cpu→remediation=T-181 认领+preereg 草案 v0 同轮开动；"
           f"机面实况=CEO 令训练满载 GPU 93%/RAM 0.55GB→py CPU 15%=结构面非怠工·O-1612 waiver 面如实呈报）｜"
           f"孤儿面=0（py_faces=15）｜r824 前驱亡态定谳：4 commits 落账后中途死·state/轮报缺位·本轮取 r825 续位（state 吸收 824 位号供 QA 驱动轮读）｜"
           f"本轮：①S0-1 锚定 bm-c+孤儿探针 orphans=0；②S0 fetch 0/0 对齐；③S0.5 双扫 DEC b87a92b1/ORD e286f842 双 MATCH 零新派工+orders_ack 185 零未回执"
           f"+inbox 1 件=bm-c→bm-b 非本机收件人留置（bm-b 离线待复活）；④S1 smoke 49/49；⑤SatEngine rc0 活；"
           f"⑥CEO 令 O-20261010-0025：三权重到件（dl3 直连·receipt PASS）→前驱 02:39 首炸 lora_krea2 模块缺→02:51 重发训练在烧"
           f"（PID 53412·GPU 93%·train_log 03:20 活跃·avr_loss 0.0608·5/4096@16.4s/it·ETA ~21:00）——训练监控=本轮关键路径；"
           f"⑦T-180 收口翻 done（regime_gate_evidence v1.0 selftest 4/4+幂等 no-op+双臂证据件 EVIDENCE-2026-09-22 契约回执 validated）；"
           f"⑧T-181 认领（wm-red 唯一 open 票·claim+start 同轮）+预注册草案 v0=research/THERMO_OVERLAY_P1.md"
           f"（BAN-05 语义例外 new_data 声明+BAN-04 文字假阳性治愈〔组合格措辞撞 grid trading 模式→改词〕+banned_direction_gate rc0 PASS"
           f"+α 行为偏差+散户凭什么赢=行为+双臂锚四元组+evidence_cutoff 2026-09-22 P-5C+出场轴②持有到底+块置换随机基线+等历法三段 era 分层"
           f"+DRAFT-NOT-FROZEN 横幅+冻结门 8 项清单）；⑨QA 驱动 r825 包 RAM 守卫让位（0.55GB<1.5GB·训练保护优先·下轮/训毕补跑）；"
           f"⑩S6 免双开（前驱 41 腿链 03:12:03 全绿跑毕·0 rc1/2/3·RAM 守卫+CEO 训练优先）；"
           f"⑪S7 四件套全绿+attrition CLEAN+双爪重装+watchdog 重注册｜验证：smoke 49/49·SatEngine rc0·attrition rc0·"
           f"banned gate rc0·selftest 4/4·训练进程活体亲验（GPU 93%+日志 03:20 mtime）｜"
           f"下轮指针：训练监控至 ~21:00 完训→恢复债（Ollama 双任务 enable+llama-server+ComfyUI 重启）+jman_val_grid 验证链+LOOKBOARD；"
           f"T-181 冻结门 8 项（F-04 MSG+episode 日期锚+D6 数值+状态格设计+science_gates 接线→冻结 commit→烧批错峰训练窗）；"
           f"QA r825 包首个 RAM≥1.5GB 轮补跑｜记分:2+1（T-180 收口=能跑证据面实物〔导出器+证据件+票 done〕；T-181 草案+禁开门实跑=文件改动面）｜"
           f"记账预算:3（state+心跳+轮报=法定簿记）｜方法论捕获=无新方法｜宝藏捕获=无（无五类收口面触发）｜"
           f"登记册零命中断言=不适用（零清扫零 quarantine）｜本地未达 origin commit 数: 见 commit 后 push_verify 行"
           f"{eol.decode()}")
    with open(rr, "ab") as fh:
        fh.write(row.encode("utf-8"))

    print("STATE/HB/LEDGER written")
    print("TS:", TS, "| epoch:", EPOCH, "| cpu:", CPU, "| ram:", RAM, "| gpu:", GPU)


if __name__ == "__main__":
    main()
