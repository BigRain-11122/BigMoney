# -*- coding: utf-8 -*-
# r855 bm-c books: ROUND-REPORT PATH-DRIFT SURGERY + state/heartbeat bump + r855 line
# WARNING (clone bloodline law): the round-report CANONICAL path is
#   logs/iteration-loop/round_reports-bm-c.md
# r851-r854 books scripts carried a dead ROOT path (pre-r645 legacy face) -- do NOT
# verbatim-clone that constant; this script is the corrected clone source.
import json, time, io, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
LEGACY = ROOT + r"\round_reports-bm-c.md"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# ---------- 1) union-migrate r851..r854 lines (legacy tail) -> canonical ----------
leg_body = io.open(LEGACY, "r", encoding="utf-8").read()
leg_lines = [l for l in leg_body.splitlines() if l.strip()]
migrate = leg_lines[-6:]
need = ["| r851 |", "| r852 |", "r852 bm-c addendum", "r852 bm-c pre3 addendum", "| r853 |", "| r854 |"]
for l, tag in zip(migrate, need):
    assert tag in l, ("migrate-face mismatch", tag, l[:80])
assert "| r850 |" not in migrate[-1]

can_body = io.open(CANON, "r", encoding="utf-8").read()
can_lines = [l for l in can_body.splitlines() if l.strip()]
assert can_lines[-1].startswith("2026-10-11T04:16:30+08:00 | r850 |"), ("canonical tail not r850", can_lines[-1][:60])
for tag in need:
    assert (tag not in can_body[-8000:]) or tag.startswith("r852"), ("already migrated?", tag)

report_line = ("2026-10-11T" + now_iso.split("T")[1] + " | r855 | dept:工程/舰队（守望窗+账本完整性修复轮·S6 43 腿 streak 31·r851-r854 轮报行 union 回迁·HANDOVER 5x 戳） | "
               "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
               "WM-VERDICT: 绿（red=false·probe=py_low_with_work_cands 判读=合法承载非违令：唯一 work cand=local_batch=1 jman 训练批在飞〔trainer 21288 活〕+板空/pool 0/open 票 0/bandit 0 机读·引擎队列合法空=W208 上游阻塞已知面） | "
               "孤儿面=1（py_faces=16·ComfyUI 8188 idle server 同 r850-r854·只读不杀） | "
               "r855: ①S0 本机 6 runtime faces absorb commit f73f1a617+rebase up-to-date（W208 未落链=origin 零新 commit 实读）·S0.5 常设组合器=ORD 24ad1708/DEC 68d13893 双哈希恒等零新行+unacked 0+inbox 空；"
               "②S1 smoke 49/49·S2 双板空（job 0/open 票 0）·satengine 活 rc0（queue_next=[]/burns=[]）；"
               "③守望面一行声明=W208 未落链+MSG-20261011-0535 无应答（bm-a 暗 ~8.3h·last_seen 21:52）+M10 cron 9defca39 在位 17min+jman 21288 活 CPU ~39.6h step ETA ~08:37-09:00 不变；"
               "④PRODUCT-A=S6 43/43 rc0（_r855bmc_s6_chain.ps1 r854 verbatim clone·DONE 06:11:05·dualrun ZERO-DRIFT streak 30→31·compute_audit 三旗=已知定谳面照录）；"
               "⑤PRODUCT-B=**账本完整性手术**：r851-r854 四轮 6 轮报行误落 ROOT 旧位（books 血统克隆携带 r645 前死路径常量）——行级 union 迁回正典位 logs/iteration-loop/round_reports-bm-c.md（零删除零改写·根文件追加墓碑警卫行）+"
               "坑律直写 pit-lineage.md（r666 直写先例·CODELY 热层 29,942B 近帽）+HANDOVER 5x 戳 r855 补盖（r846-r855·r850 缺戳 OVERDUE-DISCLOSED）；"
               "⑥S7 attrition 4 台账 CLEAN+idle --worked（idle_rounds=0）+四件套绿（loop next 06:15/watchdog next 06:14/双爪 LF 归一 IN-PLACE） | "
               "r856: (1) W208 落链守望→M10 自动执行链（freeze→selftest→pathspec push→2-cycle n1_w209 点火→MSG 回执+翻 M10+删 cron 9defca39）·MSG-0535 应答观察（yield→r578 六步收养·GM 改派随令即执行）；"
               "(2) jman 完训窗 ~08:37-09:00 三件（val_grid+LOOKBOARD_variant_640+恢复债三件 per O-20261010-0025·≤48h SLA）；(3) W211 freeze-prep（W210 近时先读 pit-engine-finalize.md）；"
               "(4) S0.5 常设组合器 | 本轮产品积分：2（S6 43 面再生+账本完整性修复=可验实物） | 记账预算：3 面内（state+心跳+轮报=法定簿记）")

with io.open(CANON, "a", encoding="utf-8", newline="") as f:
    for l in migrate:
        f.write(l + "\n")
    f.write(report_line + "\n")

guard = ("[2026-10-11 r855 bm-c BOOKS-SURGERY] r851-r854 六行已行级 union 迁入 logs/iteration-loop/round_reports-bm-c.md 正典位；"
         "本文件=r645 前旧位，books 血统禁再写此处（路径坑律=research/pit-lineage.md r855 条）")
with io.open(LEGACY, "a", encoding="utf-8", newline="") as f:
    f.write(guard + "\n")

# ---------- 2) pit entry -> research/pit-lineage.md (r666 direct-write precedent; CODELY hot layer 29,942B near-cap) ----------
pit = ("\n- [2026-10-11 06:2x r855 bm-c] **books 血统克隆携带死路径常量坑（轮报行落位错面·4 轮实弹·行级 union 治愈零损失）**：r851-r854 四轮 books 脚本（_r85Nbmc_books.py verbatim-clone 血统）把轮报行 append 到 `ROOT+\\round_reports-bm-c.md`（r645 前旧位）而非正典位 `logs/iteration-loop/round_reports-bm-c.md`——commit message 照写 \"round report\"（假绿四连）直至 r855 会话读尾行才揭穿。根因=克隆源（早代 books 模板）内路径常量从未随 r645 迁移面更新，N-1→N 双替换律只换轮号 token 不换路径。正法=①克隆 books 血统先 grep 路径行验目标位（本 r855 脚本=矫正后克隆源·头部 WARNING 常驻）；②发现落位错行=行级 union 迁回正典位（S0-restore 分类门：轮报类禁删禁重写·只许 union）+旧位追加墓碑警卫行；③commit message 里的簿记宣称须与文件落位断言同窗机器自证（assert tail prefix）——只写不验=假绿。How to apply：一切 verbatim-clone 产线脚本在克隆后必 grep 死常量面（路径/阈值/机号三类 token）；轮报落位以 logs/iteration-loop/round_reports-<id>.md 为唯一正典。")
with io.open(ROOT + r"\research\pit-lineage.md", "a", encoding="utf-8", newline="") as f:
    f.write(pit + "\n")

# ---------- 3) HANDOVER 5x stamp (r855; covers r846-r855; r850 miss OVERDUE-DISCLOSED) ----------
stamp = ("> bm-c round 855 五倍数核对（2026-10-11 06:2x·增量窗 r846-r855·r850 5x 戳未落=OVERDUE-DISCLOSED〔r851-r854 books 落位错面本窗手术治愈·r850 行在 ROOT 旧位经 union 回迁零损失〕·本窗按 r770/r790/r830/r845 单窗紧凑覆盖范式收口·零回改零伪造·逐轮权威=round_reports-bm-c.md 全行在册）：窗口主线=**W206 收口→席位链三连发布→W208 停滞守望**——r846 W206 finalize one-pass（ledger 870,371/K=451,120·§5 四预键 PASS·push 36075a41c）→r847 W209 席位发布（A 474_604..476_603/B 476_604..476_803·阶梯第 69 例）→r848 W209 freeze-prep 三件套（prereg+全动态 freeze 脚本+M10 行+备份守望 cron 9defca39）→r849 W211 席位发布（A 479_004..481_003/B 481_004..481_203·第 71 例）+bm-b W207/W210 双消费→r850-r855 守望窗六连（S6 43 腿正典 streak 26→31·W208 bm-a 五面+finalize 未落链→r853 停滞通报 MSG-20261011-0535〔无应答续览〕→r854 MSG-0455 pool-EOL 跨机裁定闭环〔bm-b r863 pf selftest 9/9 green〕）→r855 账本完整性手术（r851-r854 六轮报行 union 回迁正典位+pit-lineage 路径坑律+本 5x 戳）。窗口 CEO 线=jman LoRA 640 训练 r841 点火→r855 68% step ETA ~08:37-09:00（val_grid+LOOKBOARD+恢复债三件待完训·O-20261010-0025 ≤48h SLA）+O-20261011-0012 CPU 满用令消费（r843）。产品清单漂移=Tools/s05_probe.py（r844 常设 S0.5 组合器）+results/_w2{06,09,11}bmc_*（席位/冻结/探针族）+research/PERPETUAL_N1_W209_PREREG.md+qa/smoke-r85{3,4}-bm-c.md+equity-curve 族+S6 驱动 _r84x-_r855bmc_s6_chain.ps1 族+pit-* r839-r855 split/直写族。指针：**W209 freeze（W208 落链/yield/GM 改派即 M10 自动执行·cron 9defca39 在位）→jman 完训三件 ~08:37-09:00→W211 freeze-prep（W210 近时·先读 pit-engine-finalize.md）→月界首考 10-31**；下一 5x=bm-c r860。")
with io.open(ROOT + r"\research\HANDOVER.md", "a", encoding="utf-8", newline="") as f:
    f.write(stamp + "\n")

# ---------- 4) state + heartbeat ----------
did = ("r855 bm-c: (1) S0-1 identity anchor bm-c + round-zero probe py_faces=16 orphans=1 read-only "
       "(idle ComfyUI 8188 face same as r850-r854, no-kill); S0 own 6 runtime faces absorb-commit f73f1a617 "
       "+ rebase up-to-date (origin zero new commits = W208 still not landed); (2) S0.5 standing composer: "
       "ORD 24ad1708 / DEC 68d13893 both zero-delta, unacked=0, inbox empty; (3) S1 smoke 49/49; S2 boards "
       "empty (job 0 / open tickets 0); satengine alive rc0 (queue_next=[], burns 0 = W208 upstream-blocked "
       "known face); (4) WATCH: W208 not landed, MSG-20261011-0535 unanswered (bm-a dark ~8.3h), M10 cron "
       "9defca39 alive 17min; jman 21288 alive CPU ~39.6h, ETA ~08:37-09:00; (5) PRODUCT-A = S6 43-leg "
       "chain 43/43 rc0 (DONE 06:11:05, dualrun ZERO-DRIFT streak 30->31); PRODUCT-B = round-report "
       "path-drift surgery: r851-r854 six lines union-migrated from ROOT legacy face to canonical "
       "logs/iteration-loop/round_reports-bm-c.md + guard tombstone in legacy + pit-lineage.md direct-write "
       "(r666 precedent, CODELY hot layer near-cap) + HANDOVER 5x stamp r855 (r846-r855, r850 miss "
       "OVERDUE-DISCLOSED); (6) S7: attrition 4 ledgers CLEAN; idle --worked (idle_rounds=0); quartet "
       "green (loop next 06:15, watchdog next 06:14, pre-commit/pre-push claws IN-PLACE LF-normalized)")

next_ptr = ("r856: (1) W208 landing watch -> M10 auto-execute chain (freeze -> selftest default-wave -> pathspec "
            "push -> 2-cycle n1_w209 ignition -> MSG receipt + flip M10 + delete cron 9defca39); stall "
            "escalation live: MSG-20261011-0535 answer watch (bm-a freeze-prep push OR yield MSG -> adoption "
            "per r578 six-step on yield receipt; GM re-dispatch order = execute same-round); (2) jman "
            "completion window ~08:37-09:00 (val_grid + LOOKBOARD_variant_640 + recovery-debt trio per "
            "O-20261010-0025, <=48h SLA); (3) W211 freeze-prep when W210 approaches (read pit-engine-finalize.md "
            "FIRST); (4) S0.5 standing composer; (5) books clone source = _r855bmc_books.py (canonical "
            "report path fixed, header WARNING)")

activity = ("当前活: 守望窗（W208 未落链·MSG-0535 待 bm-a 响应/yield/GM 改派·M10 cron 9defca39 armed 17min 节奏·"
            "jman trainer 21288 在烧 ETA ~08:37-09:00）| 最近实物: S6 43 腿 rc0 streak 31 + 账本完整性手术 "
            "（r851-r854 六轮报行 union 回迁正典位+pit 坑律+HANDOVER 5x 戳）@ " + now_iso + " | "
            "下个里程碑: W209 freeze（W208 落链/yield/改派即执行）+ jman 完训验证三件 ~08:37-09:00（≤48h SLA）")

verdict = ("r855 close: watch round (W208/MSG-0535 hold) + S6 43/43 rc0 (streak 31) + books integrity surgery "
           "(report-path drift union-healed, pit landed, HANDOVER 5x stamp) + smoke 49/49")

summary = ("r855 close: watch holds + S6 43/43 streak 31 + round-report path-drift surgery (6 lines "
           "union-migrated + pit + 5x stamp) + jman ETA ~08:37")

def upd(path, is_hb):
    with io.open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    ts_fields = ["ts","last_seen","last_seen_at","clock_read","updated","updated_at","last_run_at","last_round_at",
                 "last_round_ts","last_ts","last_round_closed","current_task_at","last_round_summary_at",
                 "last_orders_read_at","last_pulled_at","last_action_at","last_round_at_legacy"]
    for k in ts_fields:
        if k in d: d[k] = now_iso
    d["round_no"] = 856
    d["round_no_label"] = "r855"
    d["last_round"] = 855
    d["loop_round"] = 855
    d["heartbeat_epoch_utc"] = epoch
    d["cpu_pct"] = 49; d["cpu_util_pct"] = 49; d["cpu_idle_pct"] = 51
    d["free_ram_gb"] = 3.3; d["idle_ram_gb"] = 3.3; d["ram_free_gb"] = 3.3
    for k in ["gpu_free_vram_mb","gpu_free_vram_mib","gpu_idle_vram_mb","gpu_idle_vram_mib","gpu_vram_free_mb","gpu_free_mb","gpu_free_mib","gpu_idle_mib"]:
        if k in d: d[k] = 107
    d["gpu_idle_mb"] = 16277
    d["current_task"] = activity
    d["activity_now"] = activity
    d["did"] = did
    d["verdict"] = verdict
    d["last_round_summary"] = summary
    d["note"] = ("r855 = watch + surgery round: W208 no-answer holds (MSG-0535 live), jman ETA ~08:37-09:00; "
                 "S6 43/43 streak 31; round-report path-drift healed (r851-r854 union-migrated to canonical).")
    d["next"] = next_ptr
    d["next_pointer"] = next_ptr
    d["next_milestone"] = ("r856: W209 freeze on W208 landing/yield/GM-redispatch (M10 auto-execute, cron armed) "
                           "+ jman completion window ~08:37-09:00 (val_grid + LOOKBOARD_variant_640 + "
                           "recovery-debt trio) <=48h SLA")
    d["latest_artifact"] = ("S6 43-leg chain rc0 streak 31 + books surgery (r851-r854 report lines "
                            "union-migrated to logs/iteration-loop/round_reports-bm-c.md + pit-lineage "
                            "path-drift entry + HANDOVER 5x stamp r855)")
    d["last_artifact"] = d["latest_artifact"]
    d["recent_artifact"] = d["latest_artifact"]
    d["last_action"] = "r855 W208 watch + S6 43-leg chain (streak 31) + round-report path-drift surgery + books"
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 1
    d["orphan_faces"] = 1
    d["health"] = "ok"
    d["verify"] = ("receipts: smoke 49/49 + results/_r855bmc_s6_log.txt (43/43 rc0 streak 31, DONE 06:11:05) "
                   "+ attrition CLEAN (4 ledgers) + quartet green (claws IN-PLACE) + idle --worked + "
                   "union-migrate asserts (6-face prefix + canonical-tail r850) + this books commit/push_verify")
    if not is_hb:
        d["sync"] = {"ahead_behind": "0/0 pre-books", "origin_tip": "36f2df813", "ts": now_iso,
                     "note": "r855 books: surgery round + S6 product; books commit follows this write"}
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
    assert d["round_no"] == 856, p
    assert d["loop_round"] == 855, p

print("BOOKS OK round_no=856(label r855) epoch=%d clock=%s migrated=6 report_line_appended=1" % (epoch, now_iso))
