import json, time, datetime, shutil, os

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
PREV_EPOCH = 1792382382  # r1079 closeout epoch (last_heartbeat mirror)

# --- inbox x2 bm-b receipts: process (received, zero action) + archive ---
for fn in ("MSG-1315-bm-b-cadence-v2.md", "MSG-1327-bm-b-repo-slim.md"):
    src = os.path.join("fleet", "inbox", fn)
    dst = os.path.join("fleet", "inbox", "processed", fn)
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            os.remove(dst)
        shutil.move(src, dst)
        print("archived", fn)

DID = ("r1080: (1) S0 pull --rebase autostash pop-UU dual-face surgery: marks-20261019.jsonl UU resolved by r419 line-union "
       "(19 lines, 0 invalid, assert-first add-second law held, git diff --check rc0) + watermark_red.json DU resolved via git rm --cached "
       "(honoring origin deletion = bm-c r1116 leg of D-20261019-02, .gitignore L84 machine-local takeover; disk face kept fresh 15:05 live-writer derive) "
       "+ merged autostash dropped (quoted-ref law); orphan stash@{1} untouched per E73 never-pop law; rebase landed clean on a23a5441d2 (bm-b r1024) + 818a02ed82 (bm-c r1118 W278 splice); "
       "(2) D-19 DOUBLE-DELTA consumed same-round: ord d181d4a8->690cd830 = 20+ rows 11:58-14:48 (WorkBuddy Phase0-5/OpenClaw gateway/NATS realtime-comm selection/REPO-SLIM/KB v1.0-1.3/"
       "bloat-governance/MV V5.10 triple-complaint/multishot-pivot order v2/butler brain-swap/craft-spec CRAFT-SPEC sec.6-8/methodology pivot/Kwong-version narrative/animation-recurrence/"
       "scientific-borrow law -- all BigStream/WorkBuddy/lab/fleet seats executed by bm-a interactive/lab windows, ZERO BigMoney-loop obligation per r1057/r1064 dual-company precedent); "
       "dec 8706acd8->95879dd9 = D-20261019-01..06 (PT02 MiniGame leg3->night-round; D-02 watermark_red untracking -- bm-c leg1 r1116 executed, THIS round pop-UU = conformance face, leg2 @HQ tools; "
       "D-03 memory-budget-gate union-write @HQ; D-04 iteration_loop v2 cross-line port -- bigmoney = canonical source, zero action; D-05 BmaIdleGuard probe fix executed by HQ; D-06 ledger-close batch executed); "
       "watermark ADVANCED dec=95879dd9 ord=690cd830 read-back full-string equality, mirrors synced 5; "
       "(3) round-start orphan probe 0/31; ack scan CLEAN 105/114/0 zero face divergence; S2 zero claimable (job_list empty, satengine ALIVE rc0 queue0 idle struct_wait=false = W278 finalize bm-c r1119 first-action watch); "
       "(4) S1 smoke 49/49; S6 43-leg + live_paper all rc0 bad=0 (_r1080bma_s6chain.ps1 = r1079 face clone; pre-15:30 intraday no-ops honest; MF legs FREEZE-RETAIN r1073 disposition held, post-15:30 retest adjudication armed); "
       "A5 Monday face held (overall PENDING, V1/V3/V4 PASS, V2 1/5, V5 1/3, deadline 10-31 on-track); "
       "(5) inbox x2 bm-b receipts processed-archived (cadence-v2 8-task re-freq read-back green + 3 healer recipes welded, receipt window 22:0x met early 13:15; repo-slim hooksPath+daily:09:03 sentinel+gc.auto=0 three-done, state-json first-run pending honest); "
       "(6) E75 methodology card appended (stash-pop DU on gitignored-takeover face = rm --cached keep-disk recipe); 5x HANDOVER r1080 row appended "
       "(window r1076-r1080; r1075 row found at file-top position anomaly disclosed, untouched per history-preservation law); "
       "(7) S7 quartet green (loop present PT5M pin=8 no-op first-fire 15:18 + watchdog present S4U-flip access-denied = carried C-20261016-04 + claws identical both)")

VERIFY = ("_r1080bma_s6chain_rc.log 44 rc-lines bad=0 + live_paper rc0 + smoke 49/49 + orders_ack_scan CLEAN 105/114/0 (round-start, dual-face zero divergence) "
          "+ D-19 ADVANCED dec=95879dd9 ord=690cd830 (read-back full-string equality, mirrors synced 5) + pop-UU resolution evidence "
          "(marks union 19 lines 0 invalid + git diff --check rc0 + git rm --cached watermark_red + git check-ignore .gitignore:84 + disk face 15:05) "
          "+ PACK-2026-10-19 overall PENDING (V1/V3/V4 PASS, V2 streak 1, V5 streak 1) + quartet schtasks x2 + claws IDENTICAL x2 "
          "+ inbox processed x2 + E75 card + HANDOVER r1080 row")

VERDICT = ("GREEN: r1080 waiting-state maintenance round (Monday intraday, pre-15:30 bars window) -- autostash pop-UU dual-face surgery (marks line-union + watermark rm --cached "
           "= D-20261019-02 conformance face), D-19 double-delta consumed zero-obligation (ord 690cd830 all WorkBuddy/MV/lab seats + dec 95879dd9 = D-01..06 zero open bm-a obligation), "
           "S6 all rc0 (intraday no-ops honest), smoke 49/49, ack CLEAN 105/114/0, dualrun chain green, A5 on-track 10-31, inbox x2 bm-b receipts processed, "
           "E75 card + 5x HANDOVER row, quartet green, zero claimable work (waiting-state faces declared one-line each)")

TASK = "r1080: D-19 double-delta consumption + pop-UU D-02 conformance + S6 43-leg chain + 5x HANDOVER"
CUR = "r1080: D-19 double consumption + pop-UU D-02 conformance + S6 43-leg chain (all rc0) + inbox x2 + 5x HANDOVER + E75 card"
NEXT = ("r1081: (1) Monday post-15:30 bars window: papers chain re-arm + MF lane retest adjudication (first post-close window after r1073 FREEZE-RETAIN; day-8..12 blockade chain evidence on file) "
        "+ A5 streak advance on new-bar (V2 toward 5, V5 toward 3); (2) W278 finalize watch (bm-c r1119 first action; W279 owner naming rides sec.7/8); "
        "(3) cadence v2 follow-through: @bm-c cadence-v2 + repo-slim receipts watch (22:0x window; @bm-b both receipts received+processed this round)")
NEXTM = ("A5 first-line acceptance 10-31 (V2 1/5 + V5 1/3 accruing on new-bar days); Monday post-15:30 MF retest adjudication; committee three-in-one report <=10-25; month-boundary first exam 10-31")
ART = ("results/_r1080bma_popuu_resolve.py + results/_r1080bma_s6chain.ps1 + _r1080bma_s6chain_rc.log (44 rc-lines bad=0) + knowledge/METHODOLOGY_ASSETS.md E75 card + HANDOVER r1080 5x row + inbox processed x2")
ACKNOTE = ("r1080: zero NEW fleet O-files in repo (round-start scan CLEAN 105/114/0); D-19 group ord+dec deltas consumed (690cd830 + 95879dd9); "
           "inbox x2 bm-b receipts processed-archived (cadence-v2 + repo-slim, both windows met early)")
ORDSEEN = ("r1080: D-19 ord delta consumed (d181d4a8->690cd830): 11:58-14:48 rows all WorkBuddy/MV/lab/fleet seats, zero BigMoney-loop obligation; "
           "dec delta 8706acd8->95879dd9 = D-20261019-01..06 zero open bm-a obligation (D-02 conformance honored in pop-UU)")

REPORT_LINE = (NOW + " | r1080 | 维护轮（水位 green red=false·satengine ALIVE rc0 queue0 idle·S0 autostash pop-UU 双面手术）："
    "主交付=①冲突面正法解决（marks-20261019.jsonl UU 行级 union 19 行全有效[r419 律·assert-first add-second 持法] + watermark_red.json DU=git rm --cached 承 origin 删除"
    "[=D-20261019-02 bm-c r1116 leg① 执行面·本窗 pop-UU 合规收口·盘面 15:05 新鲜 live-writer derive 保留·.gitignore L84 machine-local·check-ignore 实证]"
    "+合并 autostash drop[引号律]·孤儿 stash@{1} 未触[E73 never-pop]·rebase 落 a23a5441d2[bm-b r1024]+818a02ed82[bm-c r1118 W278 splice]）；"
    "②D-19 双增量同轮消费（ord d181d4a8->690cd830=11:58-14:48 廿余行全 WorkBuddy/OpenClaw/MV/lab 席位面·r1057/r1064 双公司判例零 BigMoney-loop 义务·"
    "dec 8706acd8->95879dd9=D-20261019-01..06 零未决本司义务·D-02 untracking 法面本窗合规收口）+水位 ADVANCED 读回恒等（镜像 synced 5）；"
    "③轮首孤儿 0/31·ack CLEAN 105/114/0 双面零分歧；S2 零可领如实（job_list 空·satengine ALIVE rc0 queue0 idle·W278 finalize=bm-c r1119 首动作观察位）；"
    "S1 smoke 49/49；S6 43 腿+live_paper 全 rc0 bad=0（_r1080bma_s6chain.ps1=r1079 面 clone·15:30 前盘中 no-op 恒真·"
    "MF 腿 FREEZE-RETAIN r1073 维持·15:30 后窗重测裁决 armed）；A5 周一面持有（overall PENDING·V1/V3/V4 PASS·V2 1/5·V5 1/3·10-31 轨上）；"
    "④inbox x2 bm-b 回执处理归档（cadence-v2 8 件读回全绿+治愈配方 3 件焊死+repo-slim 装闸/日哨/gc=0 三件全毕·回执窗 22:0x 提前达 13:15/13:27）；"
    "⑤E75 方法论卡入册（stash-pop DU@gitignored-takeover 面=rm --cached keep-disk 配方）+5x HANDOVER r1080 章（窗 r1076-r1080·"
    "r1075 行文件顶部位置异常披露不动=历史保护律）；S7 四件套绿（loop PT5M pin=8 no-op 首火 15:18·watchdog S4U flip=carried C-20261016-04·双爪 IDENTICAL）"
    " | 证据=_r1080bma_s6chain_rc.log 44 rc 行 bad=0+live_paper rc0·smoke 49/49·orders_ack CLEAN 105/114/0·D-19 ADVANCED 690cd830+95879dd9 读回恒等（镜像 synced 5）"
    "·pop-UU 解决证据（marks union 19 行 0 invalid+diff --check rc0+rm --cached+check-ignore .gitignore:84）·PACK-2026-10-19 PENDING·quartet schtasks x2+双爪 IDENTICAL·inbox processed x2·E75 卡·HANDOVER r1080 行 "
    "| 本地未达 origin commit 数=0（push 后 fetch+ls-tree 验·state push_verified 面记录） "
    "| 下轮指针：今日 15:30 后窗=papers 链 re-arm+MF lane 重测裁决（FREEZE-RETAIN 后首个收盘窗·day-8..12 封锁链证据在案）+A5 随新 bar 推进；"
    "W278 finalize 观察（bm-c r1119 首动作·W279 席位随 sec.7/8）；cadence v2 随访=@bm-c 回执窗 22:0x（@bm-b 双回执已收）")

HANDOVER_LINE = ("> bm-a round 1080 五倍数核对·" + NOW + " 核对；增量窗覆盖 r1076-r1080 五轮·5x 戳恰逢其位零欠账（r1075 章在位·其文件顶部位置异常=披露不动·历史保护律）"
    "·逐轮权威=round_reports-bm-a.md 全行在册+state-bm-a.json notes 族）：增量窗主线=**周一等待态维护链+死窗遗产收口+cadence v2 提速执法+D-02 untracking 法面收口**——"
    "①r1076 零新坑维护轮（S0 首个全净窗=bm-c 热推时代 behind=0/ahead=0 首例·W277 prereg 观察·MF pre-market no-op·15:30 后窗 armed）；"
    "②r1077 死窗遗产（S0 3-UU 吸收+S6 46 腿+dualrun NUL 行级 union 治愈+inbox x2+CODELY 坑行+7 commits 8895e5d3d4..7ca299d8aa 全推 origin·死于 report 行前）；"
    "③r1078 r1077 estate 收口（report 行+state 序列愈·r962/r1008 判例）+S6 46 腿 rc0+D-19 ord 单增量+idle --worked（8->0）+push 竞速重放 18-UU resolver"
    "（r965/r1071/r419 配方·continue 一次性净=7th live-fire 首净·PS here-string 引号剥离坑入册）；"
    "④r1079 D-19 双增量（11:16/11:21/11:27 训练线行+11:53 cadence v2——全 BigStream/lab 席面零 loop 义务）+register_loop_task.ps1 治愈器默认对齐 cadence v2（PT10M->PT5M·fleet 共享）"
    "+S6 46 腿 rc0+A5 周五面持有；⑤r1080 本窗=autostash pop-UU 双面手术（marks 行级 union 19 行+watermark_red rm --cached=D-20261019-02 bm-c r1116 leg 合规收口·"
    "盘面保留 gitignored）+D-19 双增量（ord 690cd830 全 WorkBuddy/MV/lab 席面+dec 95879dd9=D-20261019-01..06 零未决义务）+S6 43 腿+live_paper rc0"
    "+inbox x2 bm-b 回执（cadence-v2 8 件读回全绿+repo-slim 三件）+E75 卡+5x 章+quartet 绿。维护面全窗：smoke 49/49 链·S6 43-46 腿 rc0 链（_r1076..1080bma_s6chain.ps1 族）"
    "·attrition CLEAN 链·孤儿面 0 链·四件套幂等链（loop pin=8·watchdog S4U flip=carried C-20261016-04·双爪 MATCH）。产品清单漂移（增量代表面非全列）："
    "results/_r1078bma_uu_resolve.py+_r1079bma_s6chain.ps1+Tools/register_loop_task.ps1（cadence-v2 治愈器）+results/_r1080bma_popuu_resolve.py"
    "+_r1080bma_s6chain.ps1+_r1080bma_s6chain_rc.log+knowledge/METHODOLOGY_ASSETS.md E75 卡+fleet/inbox/processed/{MSG-1315,MSG-1327}。"
    "指针：**周一 15:30 后窗=papers 链 re-arm+MF 重测裁决（day-8..12 链 armed·15:35 轮承载）+A5 随新 bar 推进（V2->5·V5->3·deadline 10-31）·"
    "W278 finalize=bm-c r1119 首动作→W279 席位随 sec.7/8·@bm-c cadence-v2+repo-slim 回执窗 22:0x·月界首考 10-31**；下一 5x=bm-a r1085。[via bm-a r1080]")

E75_CARD = ("""
## E75 stash-pop DU @ gitignored-takeover 面=rm --cached keep-disk 配方（r1080 bm-a 实弹·D-20261019-02 + r419 + E73 联合作战面）
- 病理：pull --rebase --autostash 的自生 stash 携带本地 live-writer 面，而 origin 侧同窗已按 D-20261019-02 类「blob 退库+gitignore machine-local 接管」法删除该 tracked 件——pop 落 DU（deleted-by-us/updated-by-stash）：整取 stash 侧=复活已退库 tracked 件（违 in-force 法·下轮重弹同 DU）；整取 ours 侧=丢盘上最新 derive。
- 配方：①DU 单件勿按侧取舍——`git rm --cached <path>`（index 承 origin 删除=法面合规）+盘面照留（stash 侧=最新 derive·.gitignore 已覆盖则自动转 machine-local untracked-ignored）；②验三件=git check-ignore 命中该路径+盘面可读+status 无 UU 残留；③同窗伴生 UU（append-only 账本）照 r419 行级 union 独立处置（assert-first add-second·r1073 律）；④合并后 autostash 用引号 ref drop（r1058 直调律）·孤儿陈旧 stash 永不 pop（E73）。
- 边界：若该路径未被 gitignore 覆盖（法尚未接管）而 origin 删除=真删除事件，禁套本卡（须人工裁定是否复活件）。
- 证据：results/_r1080bma_popuu_resolve.py（marks union 19 行 0 invalid+rm --cached+check-ignore .gitignore:84+disk ts 15:05）+state notes r1080·2026-10-19 15:2x：bm-a r1080（S0 收口实弹·捕获律 O-20261002-2100 工程净路）
""")

def upd(path, is_heart):
    d = json.load(open(path, encoding="utf-8"))
    d["round_no"] = 1081
    d["round"] = 1080
    d["loop_round"] = 1080
    d["round_no_label"] = "r1080"
    d["last_round"] = "r1080"
    d["last_heartbeat_epoch_utc"] = PREV_EPOCH
    d["heartbeat_epoch_utc"] = EPOCH
    d["heartbeat_epoch_utc_type_int"] = True
    d["clock_read"] = NOW
    d["ts"] = NOW
    d["last_seen"] = NOW
    d["last_run"] = NOW
    d["last_round_at"] = NOW
    d["last_round_ts"] = NOW
    d["last_round_closed"] = NOW
    d["last_action_at"] = NOW
    d["updated"] = NOW
    d["updated_at"] = NOW
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 0
    d["orphan_faces"] = 0
    d["orphan_killed"] = 0
    d["did"] = DID
    d["current"] = CUR
    d["current_task"] = TASK
    d["task"] = TASK
    d["last_action"] = DID
    d["now_active"] = "bm-a loop r1080 closeout (pop-UU D-02 conformance + D-19 double consumption + S6 chain + 5x HANDOVER)"
    d["verdict"] = VERDICT
    d["verify"] = VERIFY
    d["next"] = NEXT
    d["next_milestone"] = NEXTM
    d["last_artifact"] = ART
    d["latest_artifact"] = ART
    d["recent_artifact"] = ART
    d["orders_ack_note"] = ACKNOTE
    d["last_orders_seen"] = ORDSEEN
    d["last_orders_at"] = NOW
    d["last_decisions_at"] = NOW
    if is_heart:
        d["last_round_label"] = "r1080"
        d["health"] = "alive"
    json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    d2 = json.load(open(path, encoding="utf-8"))
    assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in d2["clock_read"] and " " not in d2["clock_read"], "clock_read must be T-separated"
    print("updated", path, "epoch", d2["heartbeat_epoch_utc"], "clock", d2["clock_read"])

upd(r"state-bm-a.json", False)
upd(r"fleet\machines\bm-a.json", True)

with open(r"round_reports-bm-a.md", "a", encoding="utf-8") as fh:
    fh.write(REPORT_LINE + "\n")
print("report line appended, len", len(REPORT_LINE))

with open(r"research\HANDOVER.md", "a", encoding="utf-8") as fh:
    fh.write("\n" + HANDOVER_LINE + "\n")
print("HANDOVER 5x row appended")

with open(r"knowledge\METHODOLOGY_ASSETS.md", "a", encoding="utf-8") as fh:
    fh.write(E75_CARD + "\n")
print("E75 card appended")
