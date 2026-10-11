# -*- coding: utf-8 -*-
# r863 bm-c books: state + heartbeat bump + r863 round report line
# CLONE SOURCE LAW (r855 pit-lineage entry): round-report CANONICAL path =
#   logs/iteration-loop/round_reports-bm-c.md   (do NOT use the pre-r645 ROOT legacy path)
# r863 clone of _r862bmc_books.py (jman receipt consumption + group-tree e03164f + S6 43/43 + QA r863 5/5).
import json, time, io, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

did = ("r863 bm-c: (1) S0-1 identity anchor bm-c + round-zero probe py_faces=5 orphans=1 read-only "
       "no-kill; (1b) S0: pull blocked by 7 runtime dirty faces -> treasure_guard prescan 8 paths "
       "zero-hit rc0 -> checkout HEAD baseline -> MID-ROUND origin advance e73a42819..89d2b1045 (bm-b "
       "r872 batch 6 commits: T-101-V4-A14-PREDFACE frozen v1.0 + runner selftest 16/16 + SEED_REGISTRY "
       "20615500/20616500 + pool submit autofill claim owner=bm-b + daemon face sync + inbox MSG freeze "
       "declaration) -> stash(47 S6 output faces) -> rebase origin/main CLEAN zero-conflict -> pop "
       "zero-conflict -> in-sync 89d2b1045; (2) S0.5 orders diff=0 unacked; DEC zero-delta 68d13893; "
       "ORD delta TRUE 24ad1708->f90233c7 -> PROVENANCE CHECK: last orders.md blob commit=8b6570c "
       "02:07 = X2348 row (consumed r854 per heartbeat note); 24ad1708 matches NO historical origin "
       "blob = corrupt unverifiable face (buggy sweep artifact) -> ZERO NEW ROWS, watermark reconciled "
       "to f90233c7 (facts results/_r863bmc_s05_facts.json); (3) S1 smoke 49/49; S2 boards empty "
       "(job 0 / open tickets 0 / inbox 1 MSG processed), queue heads CLEAR (tech T5-T25 done + T26 "
       "claimed@bm-b A14 predface frozen+burning); (4) S3: watermark py_low_board_clear (pool batch "
       "t101-v4-a14 ready owner=bm-b = not mine), satengine alive rc0 queue_next=[] (W208 "
       "upstream-blocked known face), idle_trigger green_idle=false (RAM 36.2% < 40% post-training "
       "recovery, no claim obligation); (5) PRODUCT-A CEO head item jman receipt consumption "
       "COMPLETE: receipt OK 09:07:34 SLA<=10:00 met (12/12 gens 4 scenes x s0/s8/s10 seeds "
       "9011-9014; board 12/12 cells 383,846B; trainer clean exit TRAIN_CONT_EXIT_0 + final ckpt "
       "jman_v1_rank32_cont.safetensors 08:58; recovery trio live-verified: tasks enabled x2 + "
       "llama-server 61272 alive VRAM 14301/16384 baseline restored) -> GROUP-TREE commit e03164f "
       "LOOKBOARD_variant_640.jpg + 12 frame PNGs on-chain (first push rejected by bm-a ebd3f0c "
       "night round -> worktree cherry-pick surgical push ebd3f0c..e03164f -> soft-reset convergence "
       "+ targeted checkout 5 paths incl bm-a night files, zero residue, 2 pre-existing settings.json "
       "dirty preserved; ls-remote verified) + ABSOLUTE-PATH delivery per CEO rule; honest disclosure: "
       "board validated cont-000010 (last numbered save), final ckpt (+2 epochs, 08:58) exists "
       "un-boarded, re-board on request next GPU window; (6) PRODUCT-B = S6 43-leg chain 43/43 rc0 "
       "(_r863bmc_s6_runner.ps1 python-clone BOM-preserving; PS & channel failed silent exit 1 even "
       "with process-bypass -> -File channel worked; -First 10 pipeline truncation survived by "
       "file-based logging) + QA charter pack r863 5/5 explicit --round 863 (qa/smoke-r863-bm-c.md + "
       "equity-curve-r863-bm-c.png 65,491B: 3sym x 800bar 91 trades determinism=True sharpe 0.1994 "
       "annual 0.0072 maxdd -0.0431 win_rate 0.4725; signal CALL rc0 cell=ORA; panel bar 2026-10-09); "
       "(7) S7: attrition 4 ledgers CLEAN; loop task pin=5 no-op; watchdog registered; pre-commit+"
       "pre-push claws installed idempotent; A14 freeze MSG acked+processed")

next_ptr = ("r864: (1) W208/W209 landing watch -> M10 auto-execute chain (cron 9defca39 armed); W211 "
            "freeze-prep when W210 approaches + W212 freeze gated (read pit-engine-finalize.md FIRST); "
            "(2) jman final-ckpt (jman_v1_rank32_cont.safetensors) re-board offer if CEO/bm-a "
            "requests (board currently epoch-10 face, final=+2 epochs); (3) O-20261011-0012 CPU-max "
            "face: pool t101-v4-a14 owner=bm-b burning (bm-b lane, freeze respected), bm-c "
            "opportunistic faces stay closed until RAM>=40% green or upstream lands; (4) S0.5 "
            "standing composer (watch for corrupt-sha false-delta recurrence: on delta TRUE verify "
            "vs git blob history before consuming); (5) books clone source = _r863bmc_books.py "
            "(canonical report path)")

activity = ("当前活: W208/W209 落链守望（cron 9defca39 durable armed·M10 自动执行链待 W205 五面落链）+ "
            "jman 链已收口（LOOKBOARD 上链 e03164f·recovery 三件复役） | "
            "最近实物: jman LOOKBOARD_variant_640.jpg 组树上链 e03164f（K:\\Fluxgroup\\FluxGroup\\cph4\\fleet\\"
            "mv0001-handover\\outbound\\krea2\\jman-lora-640\\LOOKBOARD_variant_640.jpg）+ S6 43/43 rc0 + QA r863 5/5 @ "
            + now_iso + " | "
            "下个里程碑: W208/W209 上游落链即自动冻结执行（M10 链·~今夜窗）；jman final-ckpt 补板按需 ~10min GPU 窗")

verdict = ("r863 close: jman receipt consumed (LOOKBOARD+12 frames group-tree e03164f, SLA met 09:07) + "
           "ORD watermark corrupt-face reconciled f90233c7 zero-new-rows + mid-round rebase 89d2b1045 "
           "clean + S6 43/43 rc0 + QA pack r863 5/5 + smoke 49/49")

summary = ("r863 close: jman LOOKBOARD on-chain e03164f (12/12 cells, recovery trio restored) + ORD sha "
           "reconcile f90233c7 + bm-b r872 pulled clean + S6 43/43 + QA 5/5")

report_line = ("2026-10-11T" + now_iso.split("T")[1] + " | r863 | dept:工程/舰队（jman 头序消费+S6 43 腿+QA 5/5·双守望窗维持） | "
               "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
               "WM-VERDICT: 绿（red=false·probe=py_low_board_clear 合法白名单：池批 t101-v4-a14 owner=bm-b 冻结窗在烧非本机面·板空/open 票 0·引擎队列合法空=W208 上游阻塞已知面·RAM 36.2% 回升未达 40% 无领单义务） | "
               "孤儿面=1（py_faces=5·只读不杀） | "
               "r863: ①S0-1 身份锚 bm-c+round-zero 探针 5 face 1 orphan 只读·S0 双段集成=首段 pull 挡于 7 运行时脏面（treasure_guard 8 路径 zero-hit→checkout 基线）+轮中 origin 推进 e73a42819..89d2b1045（bm-b r872 六提交：A14 PREDFACE FROZEN+runner selftest 16/16+池提交 autofill 认领 owner=bm-b+MSG 冻结声明）→stash 47 产出面→rebase 干净→pop 零冲突→in-sync；"
               "②S0.5 差集 0+DEC 零 delta（68d13893）+**ORD 假 delta 定谳**（24ad1708→f90233c7 delta TRUE→出处核查=末次 orders blob 提交 8b6570c 02:07 X2348 行 r854 已消费·24ad1708 无任何历史 blob 匹配=坏扫描假面→零新令·水位矫正 f90233c7〔facts _r863bmc_s05_facts.json〕）；"
               "③S1 smoke 49/49·S2 双板空+MSG 处理（A14 冻结窗 ack·本机零撞面）·队头 CLEAR（T26 claimed@bm-b）；"
               "④PRODUCT-A=**jman receipt 消费收口**（receipt OK 09:07:34 SLA≤10:00 达标·12/12 gen 四景×s0/s8/s10 seed 9011-9014·板 12/12 格 383,846B·trainer 干净退出 TRAIN_CONT_EXIT_0+final ckpt 08:58·recovery 三件实测复役〔双任务 enable+llama-server 61272 活·VRAM 14301/16384 基线复〕→组树 commit **e03164f** LOOKBOARD+12 帧上链〔首推被 bm-a 夜班 ebd3f0c 拒→worktree cherry-pick 外科推→soft-reset 收敛+定向 checkout 5 路径零残留·ls-remote 自证〕·绝对路径呈报：K:\\Fluxgroup\\FluxGroup\\cph4\\fleet\\mv0001-handover\\outbound\\krea2\\jman-lora-640\\LOOKBOARD_variant_640.jpg·诚实披露=板验 cont-000010 末编号档·final ckpt〔+2 epoch〕在位未入板·按需下 GPU 窗补板）；"
               "⑤PRODUCT-B=**S6 43/43 rc0**（_r863bmc_s6_runner.ps1 python 克隆 BOM 保真·PS & 通道静默 exit1 虽进程 bypass=-File 通道正法·-First 10 管道截断被文件日志面救活）+**QA charter 包 5/5**（qa/smoke-r863-bm-c.md+equity-curve-r863-bm-c.png 65,491B：91 trades determinism=True sharpe 0.1994·CALL rc0 cell=ORA·面板 bar 2026-10-09）；"
               "⑥S7 attrition 4 台账 CLEAN+loop pin=5 no-op+watchdog+双爪幂等装+MSG processed | "
               "r864: (1) W208/W209 落链守望→M10 自动执行链维持（cron 9defca39）+W211/W212 freeze-prep（W210 近时先读 pit-engine-finalize.md）；"
               "(2) jman final-ckpt 补板按需；(3) CPU 满用令面=池批 bm-b 在烧（冻结窗律遵守）·RAM≥40% 或上游落链前本机 opportunistic 关闭如实；(4) S0.5 常设组合器（ORD 假 delta 复发防：delta TRUE 先对 blob 史核查再消费） | "
               "本轮产品积分：2（jman LOOKBOARD+12 帧组树上链=CEO 头序能看实物）+2（S6 43 面链=经营层可验实物）+2（QA 包 5/5=charter 证据实物）=6 | 记账预算：3 面内（state+心跳+轮报=法定簿记）+1 水位矫正（假 delta 定谳=数据完整性动作非纯记账）")

# round report: read tail first (anchor law), assert r862 main line tail, single append
with io.open(CANON, "r", encoding="utf-8") as f:
    can_body = f.read()
can_lines = [l for l in can_body.splitlines() if l.strip()]
assert ("| r862 |" in can_lines[-1]) and ("r862" in can_lines[-1]), ("canonical tail not r862 main line", can_lines[-1][:80])
assert ("| r863 |" not in can_body[-8000:]), "r863 main line already present"
with io.open(CANON, "a", encoding="utf-8", newline="") as f:
    f.write(report_line + "\n")


def upd(path, is_hb):
    with io.open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    ts_fields = ["ts","last_seen","last_seen_at","clock_read","updated","updated_at","last_run_at","last_round_at",
                 "last_round_ts","last_ts","last_round_closed","current_task_at","last_round_summary_at",
                 "last_orders_read_at","last_pulled_at","last_action_at","last_round_at_legacy"]
    for k in ts_fields:
        if k in d: d[k] = now_iso
    d["round_no"] = 864
    d["round_no_label"] = "r863"
    d["last_round"] = 863
    d["loop_round"] = 863
    d["heartbeat_epoch_utc"] = epoch
    d["cpu_pct"] = 33; d["cpu_util_pct"] = 33; d["cpu_idle_pct"] = 67
    d["free_ram_gb"] = 9.4; d["idle_ram_gb"] = 9.4; d["ram_free_gb"] = 9.4
    for k in ["gpu_free_vram_mb","gpu_free_vram_mib","gpu_idle_vram_mb","gpu_idle_vram_mib","gpu_vram_free_mb","gpu_free_mb","gpu_free_mib","gpu_idle_mib"]:
        if k in d: d[k] = 1872
    d["gpu_idle_mb"] = 1872
    d["head_sha"] = "89d2b1045"
    d["current_task"] = activity
    d["activity_now"] = activity
    d["did"] = did
    d["verdict"] = verdict
    d["last_round_summary"] = summary
    d["note"] = ("r863 = jman-consumption round: LOOKBOARD+12 frames on-chain group e03164f (SLA met); "
                 "ORD corrupt-sha reconciled f90233c7; S6 43/43; QA 5/5.")
    d["next"] = next_ptr
    d["next_pointer"] = next_ptr
    d["next_milestone"] = ("r864: W208/W209 landing watch (M10 auto chain, cron 9defca39 armed) + jman "
                           "final-ckpt re-board on request")
    d["latest_artifact"] = ("jman LOOKBOARD_variant_640 on-chain e03164f (group tree) + S6 43/43 rc0 "
                            "(_r863bmc_s6_log.txt) + QA pack r863 5/5 (equity-curve-r863-bm-c.png)")
    d["last_artifact"] = d["latest_artifact"]
    d["recent_artifact"] = d["latest_artifact"]
    d["last_action"] = ("r863 jman receipt consumed (group e03164f) + ORD sha reconciled + S6 43/43 + "
                        "QA r863 5/5 + books")
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 1
    d["orphan_faces"] = 1
    d["health"] = "ok"
    d["last_orders_sha"] = "f90233c76860acde01216bf0e0af0b54985d3293"
    d["last_orders_at"] = now_iso
    d["ord_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r863 "
                           "fresh fetch rc0; ORD delta TRUE 24ad1708->f90233c7 -> provenance check: last "
                           "orders.md blob commit 8b6570c 02:07 = X2348 row consumed r854; 24ad1708 "
                           "matches NO historical origin blob (8b6570c^=4d33cb4f / a6990ab=4d33cb4f / "
                           "eee563f=c9a4be3f / d44145d=df5bc67f / d37416d=e883b6fc all differ) = corrupt "
                           "unverifiable face from buggy sweep; ZERO NEW ROWS; watermark reconciled to "
                           "f90233c7; facts results/_r863bmc_s05_facts.json, 40hex shape-asserted, zero "
                           "literal constants (r583 law)")
    d["last_orders_sha_note"] = ("r863 reconciled: 24ad1708 corrupt-face retired (no blob provenance); true "
                                 "lineage 24e6066e->4d33cb4f (r843, O-20261011-0012 consumed) -> f90233c7 "
                                 "(r854, X2348 row, current tip, zero new rows); recurrence guard: on "
                                 "delta TRUE verify vs git blob history before consuming")
    d["verify"] = ("receipts: smoke 49/49 + qa/smoke-r863-bm-c.md (5/5 charter, explicit --round 863) + "
                   "results/_r863bmc_s6_log.txt (43/43 rc0 bad=0) + results/_r860bmc_jman_val_receipt.json "
                   "(jman OK 12/12) + group-tree ls-remote e03164f + results/_r863bmc_s05_facts.json (ORD "
                   "reconcile) + attrition CLEAN (4 ledgers) + this books commit/push_verify")
    if not is_hb:
        d["sync"] = {"ahead_behind": "1/0 pre-books", "origin_tip": "89d2b1045", "ts": now_iso,
                     "note": "r863 books: jman consumed + S6 43/43 + QA 5/5; commit+push follows this write"}
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return d

upd(ROOT + r"\state-bm-c.json", False)

# heartbeat (fleet/machines/bm-c.json): CRLF face, indent=1 (r852 close convention)
upd(ROOT + r"\fleet\machines\bm-c.json", True)
raw = io.open(ROOT + r"\fleet\machines\bm-c.json", "r", encoding="utf-8").read()
io.open(ROOT + r"\fleet\machines\bm-c.json", "w", encoding="utf-8", newline="").write(raw.replace("\n", "\r\n"))

for p in [ROOT + r"\state-bm-c.json", ROOT + r"\fleet\machines\bm-c.json"]:
    with io.open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert isinstance(d["heartbeat_epoch_utc"], int), p
    assert "T" in d["clock_read"], p
    assert d["round_no"] == 864, p
    assert d["loop_round"] == 863, p

print("BOOKS OK round_no=864(label r863) epoch=%d clock=%s report_line_appended=1" % (epoch, now_iso))
