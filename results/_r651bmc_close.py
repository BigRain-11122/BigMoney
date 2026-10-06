# -*- coding: utf-8 -*-
# r651 bm-c close driver: (a) new pit entry appended to CODELY.md main file
# (law: new pits land in main first, then future batches migrate); (b) S5
# ledger line to CANONICAL per-machine path (r645 epoch law); (c) state-bm-c
# round_no increment + summaries; (d) heartbeat with live metrics + 3-line
# CEO face; epoch int self-assert (smoke F7). ASCII-only console output.
import json, os, time, datetime, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---------- (a) CODELY.md new-pit entry (main-file first, per law) ----------
PIT = ("- [2026-10-07 04:1x r651 bm-c] **拆件断言层 marker 扫域过宽=引文文本误判坑（r419/r420 假阳性族第四连·当场自愈零 origin 伤害）**："
       "mini-split 终扫把全 pit 族文件纳入 marker 扫——pit 坑律正文合法引用冲突标记文档文本（r806 条目自身即含 `<<<<<<<`）→行内引文命中=整批断言炸；"
       "时序=盘面写已全部落盘后才败=断言层后置自纠型（receipt 未写·finalize 驱动从 HEAD blob 前面×盘面后面全量重构恒等收口·r645 七验范式）。"
       "正法=①marker 扫域限定=本轮写面（主件+目标件+登记册）非全族只读件；②判据=行首级（冲突标记起行）非子串级——git --check 同口径；"
       "③写后断言败=HEAD blob 重构恒等收口勿重放手术。How to apply：迁移仪式终扫模板改行首级+写面限定；pre-commit 爪 git --check 口径为唯一权威。").encode("utf-8")

mp = os.path.join(ROOT, "CODELY.md")
mb = open(mp, "rb").read()
assert mb.endswith(b"\r\n") and PIT not in mb
open(mp, "wb").write(mb + PIT + b"\r\n")
new_main_blob = (len(mb) + len(PIT) + 2) - (mb.count(b"\r\n") + 1)
assert new_main_blob <= 30720, "gate breach"

# ---------- live metrics ----------
def sh(args, flag=True):
    return subprocess.run(args, capture_output=True, creationflags=0x08000000 if flag else 0)
try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=1.0), 1)
    ram_free = round(psutil.virtual_memory().available / (1 << 30), 1)
except Exception:
    cpu, ram_free = 0.0, 0.0
gpu_free = 0
try:
    g = sh(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"])
    gpu_free = int(g.stdout.decode("ascii", "replace").strip().splitlines()[0])
except Exception:
    gpu_free = 0

def load_json(p):
    raw = open(p, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return json.loads(raw.decode("utf-8-sig")), bom

def save_json(p, obj, bom):
    with open(p, "w", encoding="utf-8-sig" if bom else "utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)

# ---------- three-line CEO face ----------
face3 = ("当前活: r651 值守轮收口（P0 承接：CODELY 主件 D-06 mini-split 5 行/4 坑迁出 30,570→26,496B·150B 余量红线解除→4,224B"
         "+S6 38/38+QA 包 r651 显式轮标 5/5） | 最近实物: results/_r651bmc_codely_increment.json（mini-split receipt·5 条 verbatim"
         "+HEAD×盘面重构恒等）+qa/smoke-r651.md（5/5·93 trades·determinism=True·equity 终值 1,017,839 面恒等 r642-650）"
         "@ {ts} | 下个里程碑: fund-trio Q 完成窗 pool dual-flip watch（r668 律）+D finalize ~10-08（bm-b 车道）；10-09 复市数据链 re-arm"
         "+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r655〔HANDOVER 窗〕").format(ts=TS)
latest = ("results/_r651bmc_codely_increment.json (mini-split receipt, 5-entry verbatim + reconstruction identity; main 30,570->26,496B)"
          " + qa/smoke-r651.md 5/5 (explicit --round 651, 93 trades, determinism=True, face-identical r642-650)"
          " + results/_r651bmc_s6_log.txt 38/38 rc0 @ {ts}").format(ts=TS)
milestone = ("fund-trio Q completion pool dual-flip watch (r668 law) + D finalize ~10-08 (bm-b lane); 10-09 market reopen"
             " (data-chain re-arm + regime_guard v3 first bar); monthly exam 10-31; next 5x = r655")

did = ("r651 bm-c: golden-week standing-guard round + r650-tail P0 discharge (D-06 mini-split: main 30,570->26,496B blob, "
       "5 rows/4 pits verbatim migrated r646-ledger->pit-protocol-lane / r646-receipt->pit-lineage / r648->pit-git-resolver / "
       "r649->pit-ps / r806->pit-git-staged, prescan rc3 logged, full reconstruction identity, receipt _r651bmc_codely_increment.json; "
       "150B razor headroom -> 4,224B). (1) S0: round-start dirty = 2 own-lane sat-engine daemon faces -> targeted checkpoint 83f90098a "
       "(r642 zero-autostash law); claws reinstalled at S0 (r806 law); pull up-to-date. (2) S0.5 double-sweep (s05 + s7close): "
       "DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta at both sweeps; fleet orders 164/164 zero unacked. (3) S1 smoke 48/48. "
       "S3: board open=0 (Codely jobs 0, fleet 176 zero open/in_progress); watermark green (red=false, next_pick=claimed moneyflow IC "
       "source-blocked bm-a lane legal; py_watermark py_low_board_clear = golden-week legal idle); SAT alive (Tools face status rc0, "
       "wave 167). Trio V 2000/2000 COMPLETE, Q 1883/2000, D 1559/2000 (bm-b rightful burner lane, pool 2 batches ready for bm-b; "
       "no proxy burn by bm-c). Trial-labor line satisfied by in-flight trio judge batches, no new drafting. (4) S6 chain 38/38 rc0 "
       "(dualrun ZERO-DRIFT streak 51 @403; compute_audit FLAG supply_gap,supply_floor = known golden-week structural face re-eval 10-09+; "
       "regime ORANGE shadow; regime_guard enforce requested -> honest date-gate downgrade until first post-gate bar 10-09). "
       "(5) QA pack r651: detached pid 5432 with EXPLICIT --round 651 (r758/r640 law), polled terminal before close -- 5/5, 93 trades, "
       "determinism=True, equity 800 pts final 1,017,839 face-identical r642-r650. (6) Attrition guard CLEAN; loop pin=5 no-op; "
       "watchdog registered. Zero fleet-level new pits; one self-caught driver-assert over-bread (marker scan scope) healed in-window, "
       "pit entry appended to main file first per law.")

verdict = ("alive: r651 standing-guard round complete (P0 mini-split discharged: main 30,570->26,496B blob, 4-pit verbatim migration "
           "receipted; QA pack r651 5/5 zero-mislabel explicit --round 651; S6 38/38 rc0; smoke 48/48; board open=0; satengine alive; "
           "DEC/ORD double-sweep zero-delta 164/164; attrition CLEAN; trio V complete Q1883/D1559 bm-b rightful lane; golden-week no-bar "
           "until 10-09)")

# ---------- (b) S5 ledger line (canonical path, r645 law) ----------
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
rb = open(RR, "rb").read()
assert rb.endswith(b"\r\n")
row = ("{ts} | r651 bm-c | dept:工程/舰队 | watermark verdict=绿（red=false·next_pick=claimed moneyflow IC source-blocked bm-a 车道合法"
       "·py_watermark py_low_board_clear=黄金周合法 idle 白名单）+SAT 引擎活（Tools face rc0·W167 带）+板 open=0 | "
       "P0 承接收口=r650 尾注 D-06 mini-split：CODELY 主件 5 行/4 坑 verbatim 迁出（r646 账本路径坑→pit-protocol-lane〔907B〕"
       "+r646 尺寸收据坑→pit-lineage〔1097B〕+r648 :N: 空读坑→pit-git-resolver〔1086B〕+r649 silent-git 绑定坑→pit-ps〔850B〕"
       "+r806 marker-gate 坑→pit-git-staged〔965B〕）主件 30,570→26,496B blob（150B 余量红线→4,224B）·prescan rc3 留痕"
       "·HEAD×盘面全量重构恒等·receipt _r651bmc_codely_increment.json | S6 38/38 rc0（dualrun ZERO-DRIFT streak 51@403"
       "·compute_audit FLAG supply_gap/supply_floor=黄金周已知结构面 re-eval 10-09+·regime ORANGE shadow·t24/live enforce 请求"
       "→日期门诚实降级至 10-09 首 bar）| QA 包 r651 显式 --round 651 分离 pid 5432 终态 5/5·93 trades·determinism=True"
       "·面恒等 r642-650 | S0.5 双扫（s05+s7close）DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta·fleet 164/164 零未回执 | "
       "attrition CLEAN·loop pin=5 no-op·watchdog 在册·双爪 S0 幂等重装 | 本轮自纠坑 1 条入册（拆件断言层 marker 扫域过宽"
       "=引文误判·当场自愈零 origin 伤害）| 本地未达 origin commit 数=见 S7 close addendum 行（commit+push+fetch 自证） | "
       "下轮指针：r652 值守（trio Q/D 进度 watch·bm-b 正主车道）+10-09 复市数据链 re-arm 预检\n").format(ts=TS)
open(RR, "wb").write(rb + row.encode("utf-8").replace(b"\n", b"\r\n"))

# ---------- (c) state-bm-c.json ----------
SP = os.path.join(ROOT, "state-bm-c.json")
st, bom = load_json(SP)
for k in ("clock_read", "ts", "last_seen", "last_seen_at", "updated", "updated_at", "last_round_at",
          "last_run_at", "last_ts", "last_decisions_read_at", "last_decisions_at", "last_round_ts",
          "current_task_at"):
    st[k] = TS
st["round_no"] = 652
st["round_no_label"] = "round 651 (bm-c)"
st["did"] = did
st["last_round"] = did
st["last_round_summary"] = ("r651: standing-guard round + P0 mini-split discharge (main 30,570->26,496B, 5 rows/4 pits verbatim, "
                            "receipt _r651bmc_codely_increment.json; headroom 150B->4,224B); QA r651 5/5 explicit --round zero-mislabel; "
                            "S6 38/38; DEC/ORD double-sweep zero-delta 164/164; attrition CLEAN; trio V complete Q1883/D1559 bm-b lane; "
                            "smoke 48/48; zero fleet-level new pits")
st["last_action"] = did
st["current_task"] = face3
st["activity_now"] = face3
st["next"] = ("(a) fund-trio Q ~2000 completion window: pool dual-flip watch per r668 law; D finalize ~10-08 (bm-b lane). "
              "(b) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar. (c) watch bm-a reply to MSG-2026-10-07-0250 "
              "(marker-pollution self-audit). (d) monthly exam 10-31 assembly face. (e) next 5x = r655 (HANDOVER window).")
st["note"] = ("r651: P0 mini-split discharged (main 26,496B, headroom 4,224B); QA r651 5/5 explicit --round; S6 38/38; "
              "DEC/ORD double-sweep MATCH; attrition CLEAN; trio V complete, Q 1883, D 1559 (bm-b lane); one self-healed "
              "driver-assert pit logged (marker-scan scope).")
st["verify"] = ("receipts: qa/smoke-r651.md 5/5 (explicit --round 651) + qa/equity-curve-r651.png + results/_r651bmc_s6_log.txt "
                "38/38 rc0 + results/_r651bmc_s05_facts.json (double-sweep s05+s7close: DEC 635C3024 + ORD 437E9CDD) + "
                "results/_r651bmc_codely_increment.json (mini-split 5-entry verbatim + reconstruction identity) + "
                "results/_attrition_guard_scan.json CLEAN + results/_r651bmc_trio_watch.json + research/HANDOVER.md (r650 line)")
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r651 double-sweep s05+s7close "
                        "both scans = 635C3024 MATCH zero-delta; value facts-driven from results/_r651bmc_s05_facts.json, "
                        "64hex shape-asserted, never hand-typed (r583 S4 law))")
st["ord_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r651 double-sweep s05+s7close both "
                        "scans = 437E9CDD MATCH zero-delta; fleet orders 164/164 ack at BOTH sweeps (double-sweep law); value "
                        "facts-driven from results/_r651bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["cpu_pct"] = st["cpu_util_pct"] = cpu
st["cpu_idle_pct"] = round(100 - cpu, 1)
st["free_ram_gb"] = st["idle_ram_gb"] = st["ram_free_gb"] = ram_free
for k in ("gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_idle_vram_mib", "gpu_idle_vram_mb", "gpu_free_mb",
          "gpu_idle_mb", "gpu_vram_free_mb", "gpu_free_mib"):
    st[k] = gpu_free
save_json(SP, st, bom)

# ---------- (d) heartbeat ----------
HP = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb, bom2 = load_json(HP)
for k in ("clock_read", "ts", "last_seen", "last_seen_at", "updated", "updated_at", "current_task_at"):
    hb[k] = TS
hb["heartbeat_epoch_utc"] = EPOCH
hb["round_no"] = 652
hb["round_no_label"] = "round 651 (bm-c)"
hb["current_task"] = face3
hb["activity_now"] = face3
hb["latest_artifact"] = latest
hb["next_milestone"] = milestone
hb["verdict"] = verdict
hb["prod_lanes"] = ("r651 值守轮（P0 承接 mini-split 收口：主件 30,570→26,496B·5 行/4 坑 verbatim·receipt 在案+S6 38/38"
                    "+QA r651 5/5 显式轮标；板 open=0；watermark 绿；SAT 引擎活；黄金周无 bar 车道至 10-09；下个 5x=r655〔HANDOVER 窗〕")
hb["health"] = ("alive (all-hands resume IN EFFECT per O-20261006-2257: machine-state MODE=resume, ollama=True, comfy=True, "
                "6 GPU tasks Ready, CRON active=5; r651: D-06 mini-split P0 landed (main 26,496B, headroom restored), claws "
                "reinstalled at S0, loop pin=5, watchdog registered)")
hb["cpu_pct"] = hb["cpu_util_pct"] = cpu
hb["cpu_idle_pct"] = round(100 - cpu, 1)
hb["free_ram_gb"] = hb["idle_ram_gb"] = hb["ram_free_gb"] = ram_free
for k in ("gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_idle_vram_mib", "gpu_idle_vram_mb", "gpu_free_mb",
          "gpu_idle_mb", "gpu_vram_free_mb", "gpu_free_mib"):
    hb[k] = gpu_free
save_json(HP, hb, bom2)

# ---------- self-verify (smoke F7 face) ----------
hb2 = json.loads(open(HP, "rb").read().decode("utf-8-sig"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"] and hb2["clock_read"].endswith("+08:00")
st2 = json.loads(open(SP, "rb").read().decode("utf-8-sig"))
assert st2["round_no"] == 652
print("CLOSE_OK ts=%s cpu=%s ram=%s gpu=%d main_blob=%d" % (TS, cpu, ram_free, gpu_free, new_main_blob))
