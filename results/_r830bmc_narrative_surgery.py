"""r830 bm-c mid-rebase narrative surgery: rewrite r830 faces to the true
D-07 yield story (bm-b r832 canonical reached origin first; bm-c parallel
implementation yielded; canonical re-verified 28/28 on this machine)."""
import json, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = "2026-10-10T12:3x+08:00"

# ---- 1. round report: replace the r830 row (last line) ----
RR = os.path.join(ROOT, "round_reports-bm-c.md")
with open(RR, "r", encoding="utf-8") as f:
    lines = f.read().splitlines(keepends=True)
assert lines and "| r830 |" in lines[-1], "last line is not the r830 row"
row = (
    NOW + " | r830 | dept:工程/舰队（决策消费+撞面让路轮：D-04 Bonsai 关单+DEC/ORD 双 delta 消费+D-07 消费验证让路·第 127 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
    "WM-VERDICT: 红→已处置（red=true lane=pool-batch-runnable-idle-low-cpu→结构性面：9 W17 shard ready 全被 RAM 门 4GB 挡·RAM 0.1GB=CEO 影片链〔H3 i2v 生成中〕优先合法等待〔r829 判例·O-1612 waiver〕·本轮实工=决策消费+验证+关单非怠工） | "
    "孤儿面=1（只读·probe py_faces=7 orphans=1·ComfyUI 8188 影片链服务面勿杀） | "
    "r830: ①S0-1 锚定 bm-c+孤儿探针只读+S0 fetch 0/0 起态（收口窗内 origin 进 7 commit=bm-a r952 尾×4+bm-b r832 系·rebase 竞速入序）；"
    "②S0.5 双扫=DEC delta b87a92b1→6d60855e 消费（午班拍板批 D-20261010-04~10·涉本司两件：D-04 关单面〔本轮落地见⑤〕+D-07 爪修法〔dispatched→撞面让路见④〕；D-05 写腿=10-11 00:00 常务轮首位非本司窗；D-06/08/09/10 他司域零动作）+"
    "ORD delta e286f842→7bf646b7 消费（五新行：O-20261010-1035 jman SLA 追单〔已由 r821-829 执行+杀训披露回执 d8db73b 闭环零新动作〕+O-1105/113x/115x/修订三 mv0001 机队出片段系〔@bm-c 面=影片窗会话在飞车道·本循环零 GPU 触碰零干扰〕+115x @BigMoney bm-a 回测授面〔执行司=bm-a 计算面·bm-c 零新义务〕）+orders 60/0 未回执+inbox 0；"
    "③S1 smoke 49/49+SatEngine rc0 活；"
    "④**D-20261010-07 爪窄门消费+撞面让路（本轮撞面主事件）**：本窗平行实现完成（git_claw.py qa/ 窄门+moved[] 精确对表+sha256 内容校验+selftest 31/31 含 8 新腿）→push 前 rebase 撞 bm-b r832（62b8ae411 先到 origin：同域第四类放行〔membership-only=决策字母「爪只验成员关系」正身〕+legacy files[] 形判别+selftest 28/28+HQ-FEEDBACK 执行段状态 closed）→"
    "按撞认领 commit 时序后到让路律（fleet README §4）**取 bm-b 正典版**（git_claw.py+HQ-FEEDBACK 双面 origin 侧）+**本机复验其 selftest 28/28 全绿**（含 legacy files[] not-a-proof 腿）——bm-c 平行实现随让路弃（sha256 内容校验=超决策字母的 belt·随弃不留尾不回改）·r830 D-07 角色=消费+验证+让路注记；"
    "⑤**D-20261010-04 Bonsai 关单面（本轮净产品）**：T-99/T-100 双票 closeout 注记落账（observe 维持不转正+复评条件=GPU 空窗 tg128 实测+新硬需求触发·幂等脚本 results/_r830bmc_bonsai_closeout.py+双票验证在案）；"
    "⑥S6=免三开（当日两绿跑在档：09:48 43 腿 crosscheck 焊入版 CLEAN bad=0〔前驱跑毕·r828 链指针②就此收口〕+12:11 41 腿影片窗版 CLEAN·周六零数据漂移·RAM 0.1GB 影片链保护=r825/r829 免双开判例线·43 腿正典脚本 .codely-cli/scratch/_r830bmc_s6_chain.py 在位=下轮起正常轮跑）；"
    "⑦QA r825 包续让位（RAM 0.1GB<1.5GB·影片链毕/训毕首窗补跑）；"
    "⑧pit 直写 research/pit-git-parse.md（集团树 git log 本地 HEAD 假史坑〔D-20260930-13 的 log 延伸面〕·878B·sha16 9ae3f57c435fdffe·verbatim 对账·29,236B<30KB 帽·r666/r819 范式·receipt results/_r830bmc_pit_append.json）；"
    "⑨idle --worked 清零+HANDOVER 5x 戳（r811-r830 单窗紧凑覆盖+r815/820/825 断档 OVERDUE 披露）+S7 四件套全绿（loop pin=5+watchdog 12:32 首火+双爪 LF 归一重装）+attrition 4 台账 CLEAN；"
    "⑩W17 6 shard RAM 门等待态（0.1GB<4GB·影片链毕 autofill 自愈续烧）+训练 killed 11:18（r829 判例五件套·续训明晨 10:00 SLA）双等待态一行声明不重扫 | "
    "验证证据: claw selftest 28/28（bm-b 正典版本机复验 rc0） + smoke 49/49 + SatEngine rc0 + attrition CLEAN + DEC 6d60855e/ORD 7bf646b7 双消费水位更新 + results/_r830bmc_s05_facts2.json（fetch rc0·unacked 0·inbox 0） + bonsai closeout 双票 key 验证 + pit receipt verbatim_in_file=true + 43 腿链 09:48 CLEAN 在档（results/_r830bmc_s6_log.txt SUMMARY bad=0） + push 送达自证 | "
    "下轮指针: r831 续作: ①W17 shard RAM 门观察（影片链毕 RAM≥4GB autofill 自愈续烧→checkpoint 推进盯梢）②训毕恢复债（Ollama 双任务 enable+llama-server+ComfyUI 重启·影片窗域·明晨 10:00 SLA）+jman_val_grid 验证链+LOOKBOARD③QA r825 包首个 RAM≥1.5GB 轮补跑④S6 链正常轮跑（43 腿正典）⑤T-181 bm-a 烧批 finalize 消费面盯梢⑥D-20261010-05 写腿=10-11 00:00 常务轮首位（非本司窗） | "
    "本轮产品计分：1（D-04 双票关单+DEC/ORD 双 delta 消费+撞面让路处置=D-07 主产品让路 bm-b 后的本轮净产出=文件改动与账本面·诚实不计虚） | "
    "记账预算：5（state/心跳/轮报三法定+pit 收据+s05 facts 件） | 方法论捕获:无新方法 | 宝藏捕获:无（无五类收口面触发） | 登记册零命中断言:不适用（零清扫零 quarantine·treasure_guard prescan 未触发面） | [via bm-c r830]\n"
)
lines[-1] = row
with open(RR, "w", encoding="utf-8", newline="") as f:
    f.write("".join(lines))

# ---- 2. HANDOVER: fix segment 4 ----
HO = os.path.join(ROOT, "research", "HANDOVER.md")
with open(HO, "r", encoding="utf-8") as f:
    ho = f.read()
old4 = ("④r830 决策消费执行双落地（D-20261010-07 pre-push 爪 qa/ quarantine-manifest 窄门修法 selftest 31/31"
        "+D-20261010-04 Bonsai T-99/T-100 关单注记）+")
new4 = ("④r830 决策消费双面（D-20261010-07 爪窄门=bm-b r832 正典先到 62b8ae411·bm-c 平行实现后到让路随弃"
        "+本机复验 28/28；D-20261010-04 Bonsai T-99/T-100 关单注记=bm-c 落地）+")
assert old4 in ho, "HO segment not found"
ho = ho.replace(old4, new4)
with open(HO, "w", encoding="utf-8", newline="") as f:
    f.write(ho)

# ---- 3. state: narrative fields ----
SP = os.path.join(ROOT, "state-bm-c.json")
with open(SP, "r", encoding="utf-8") as f:
    st = json.load(f)
did = ("r830 bm-c: D-20261010-07 consumed+verified with yield (bm-b r832 canonical implementation reached "
       "origin first, commit-order yield law; bm-c parallel implementation dropped; canonical claw selftest "
       "28/28 re-verified on this machine) + D-20261010-04 Bonsai T-99/T-100 formal closeout + DEC/ORD "
       "double-delta consumed (b87a92b1->6d60855e / e286f842->7bf646b7, zero unacked, inbox 0) + smoke 49/49 "
       "+ SatEngine rc0 + S6 rest-day triple-skip (2 in-day green runs: 43-leg crosscheck-welded CLEAN 09:48 "
       "+ 41-leg CLEAN 12:11, RAM 0.1GB CEO-video-chain protection) + attrition CLEAN + S7 quartet green.")
activity = ("当前活: r830 收口——D-20261010-07 爪窄门消费+撞面让路（bm-b r832 正典先到·本机复验 selftest 28/28）"
            "+D-04 Bonsai 两票关单+DEC/ORD 双 delta 消费；CEO 影片链在本机 GPU 在跑（H3 i2v 生成中·RAM 0.1GB 让路保护） | "
            "最近实物: T-99/T-100 closeout 注记+results/_r830bmc_s05_facts2.json+pit-git-parse r830 条（sha16 9ae3f57c）"
            "+HQ-FEEDBACK bm-b 执行段在位 @ 2026-10-10T12:3x+08:00 | "
            "下个里程碑: RAM≥4GB（影片链毕）→W17 6 shard 自愈续烧+训毕恢复债（Ollama+llama-server+ComfyUI·明晨 10:00 SLA 窗）"
            "+jman_val_grid+LOOKBOARD；QA r825 包首个 RAM≥1.5GB 轮补跑")
st["did"] = did
st["verdict"] = did
st["last_round"] = did
st["current_task"] = activity
st["activity_now"] = activity
st["last_round_summary"] = row.strip()
st["last_action"] = row.strip()
st["latest_artifact"] = ("T-99/T-100 closeout + claw selftest 28/28 (bm-b canonical, bm-c re-verified rc0) "
                         "+ results/_r830bmc_s05_facts2.json + pit-git-parse r830 entry (sha16 9ae3f57c)")
st["last_decisions_sha_method"] = st["last_decisions_sha_method"].replace(
    "bigmoney faces consumed IN-ROUND (D-04 closeout + D-07 claw gate implemented)",
    "bigmoney faces consumed IN-ROUND (D-04 closeout by bm-c; D-07 execution = bm-b r832 canonical 62b8ae411 "
    "[bm-c parallel implementation yielded per commit-order law, canonical re-verified 28/28 here])")
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# ---- 4. heartbeat verdict + activity ----
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(HB, "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["verdict"] = ("r830: D-07 consumed+verified with yield (bm-b r832 canonical first-to-origin, selftest 28/28 "
                 "re-verified here) + D-04 Bonsai closeout x2 + DEC/ORD double-delta consumed + smoke 49/49 + "
                 "SatEngine rc0 + S6 rest-day skip (2 in-day green runs) + watermark red=structural (W17 RAM "
                 "gate, CEO video chain priority).")
hb["current_task"] = activity
hb["activity_now"] = activity
with open(HB, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

print("NARRATIVE_SURGERY_OK")
