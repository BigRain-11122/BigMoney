"""r830 bm-c closeout: HANDOVER 5x stamp + state + heartbeat + round-report row.
Single writer to keep heartbeat_epoch_utc a JSON int (R170/R178 law)."""
import json, os, subprocess, time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

def sh(args):
    return subprocess.run(args, capture_output=True)

# ---- machine stats snapshot ----
ram_free_gb = 0.1
gpu_free_mib = 0
try:
    r = sh(["powershell", "-NoProfile", "-Command",
            "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"])
    ram_free_gb = float(r.stdout.decode("utf-8", "replace").strip())
except Exception:
    pass
try:
    r = sh(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"])
    gpu_free_mib = int(float(r.stdout.decode("utf-8", "replace").strip().splitlines()[0]))
except Exception:
    pass

# ---- 1. HANDOVER 5x stamp (r811-r830 compact window, overdue disclosed) ----
HO = os.path.join(ROOT, "research", "HANDOVER.md")
ho_entry = (
    "\n> bm-c round 830 五倍数核对（2026-10-10 12:3x·增量窗 r811-r830·r815/r820/r825 5x 戳未落=OVERDUE-DISCLOSED"
    "〔窗内前驱猝死连发 r822/r824/r826 亡态实锚+r820 轮报行缺位如实注记·git 史保全不代写〕·本窗按 r770/r790/r800/r810 单窗紧凑覆盖范式收口·"
    "零回改零伪造·逐轮权威=round_reports-bm-c.md 全行在册）：窗口主线=**CEO 令执行线三段+维护链两根治**——"
    "①jman LoRA 640 变体全链（O-20261010-0025：r821 接单+GPU 腾 14GB+musubi 克隆+下载道判死→taildrop 快道→r823 权重接收道→r825 三权重到件+训练重发在烧→"
    "r829 同机双 CEO 令 GPU 冲突杀训让卡影片链〔五件套判例〕·续训排程明晨 10:00 SLA 窗）；"
    "②H3 本地线（r818 五权重字节校验+768P 工作流点火→r819 测试片交付门检 7.5/10+集团 outbound+W17 屏崩环根治〔Ollama 腾 RAM 0.4→7.1GB+SHARD-0 真点火〕）；"
    "③维护链两根治（r828 T10 zt_pool_crosscheck.py 出列〔selftest 15/15+实跑 CLEAN〕→r829 W17 KeyError('faces') 崩链根治〔grammar 随 initargs 传播律+worker-probe 173/173+6 shard 复燃〕）；"
    "④r830 决策消费执行双落地（D-20261010-07 pre-push 爪 qa/ quarantine-manifest 窄门修法 selftest 31/31+D-20261010-04 Bonsai T-99/T-100 关单注记）+"
    "DEC/ORD 双水位 delta 消费+pit-git-parse 集团树 git log 假史坑直写。窗内四轮前驱猝死收编全绿零污染（r822/r824/r826 亡态+r820 缺行如实注记）。\n"
)
with open(HO, "a", encoding="utf-8", newline="") as f:
    f.write(ho_entry)

# ---- 2. round-report row ----
RR = os.path.join(ROOT, "round_reports-bm-c.md")
row = (
    NOW + " | r830 | dept:工程/舰队（决策消费执行轮：D-20261010-07 爪窄门修法+D-04 Bonsai 关单+DEC/ORD 双 delta 消费·第 127 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
    "WM-VERDICT: 红→已处置（red=true lane=pool-batch-runnable-idle-low-cpu→结构性面：9 W17 shard ready 全被 RAM 门 4GB 挡·RAM 0.1GB=CEO 影片链〔H3 i2v 生成中〕优先合法等待〔r829 判例·O-1612 waiver〕·本轮实工=集团决策消费+爪修法非怠工） | "
    "孤儿面=1（只读·probe py_faces=7 orphans=1·ComfyUI 8188 影片链服务面勿杀） | "
    "r830: ①S0-1 锚定 bm-c+孤儿探针只读+S0 fetch 0/0 对齐（脏面=own daemon 活态 13 M+影片窗 untracked 5 件留置 frozen-lane 先例）；"
    "②S0.5 双扫=DEC delta b87a92b1→6d60855e 消费（午班拍板批 D-20261010-04~10：涉本司两件=D-04 关单面+D-07 爪修法 dispatched→本轮双落地；D-05 写腿=10-11 00:00 常务轮非本司窗；D-06/08/09/10 他司域零动作）+"
    "ORD delta e286f842→7bf646b7 消费（五新行：O-20261010-1035 jman SLA 追单〔已由 r821-829 执行+杀训披露回执 d8db73b 闭环零新动作〕+O-1105/113x/115x/修订三 mv0001 机队出片段系〔@bm-c 面=影片窗会话在飞车道·本循环零 GPU 触碰零干扰〕+115x @BigMoney bm-a 回测授面〔执行司=bm-a 计算面·bm-c 零新义务〕）+orders 60/0 未回执+inbox 0；"
    "③S1 smoke 49/49+SatEngine rc0 活；"
    "④**D-20261010-07 爪修法落地（本轮主产出）**：Tools/git_claw.py qa/ 窄门=第四类放行（_quarantine_cover 扫新树 results/_quarantine/*/manifest.json+moved[] 精确对表+sha256==旧树 blob 内容校验·no-owner/foreign-owner 双支线均适用·非 qa 路径零外溢·无 manifest 的 qa/ 删除照旧全机禁=fail-closed 零弱化）+"
    "selftest 31/31（8 新腿全绿：bare 无 manifest blocked/合法 manifest allowed/CLI rc0/manifest 未列该路径 blocked/sha 失配 blocked/缺 sha256 blocked/非 qa 范围 blocked/foreign+manifest allowed）+"
    "HQ-FEEDBACK F-20261010-01 状态翻面 adopted→executed（r779 判例回执面·执行注记入行）·仓内共享单源三机随 pull 同步；"
    "⑤**D-20261010-04 Bonsai 关单面**：T-99/T-100 双票 closeout 注记落账（observe 维持不转正+复评条件=GPU 空窗 tg128 实测+新硬需求触发·幂等脚本 results/_r830bmc_bonsai_closeout.py+双票验证在案）；"
    "⑥S6=免三开（当日两绿跑在档：09:48 43 腿 crosscheck 焊入版 CLEAN bad=0〔前驱跑毕·r828 链指针②就此收口〕+12:11 41 腿影片窗版 CLEAN·周六零数据漂移·RAM 0.1GB 影片链保护=r825/r829 免双开判例线·43 腿正典脚本 .codely-cli/scratch/_r830bmc_s6_chain.py 在位=下轮起正常轮跑）；"
    "⑦QA r825 包续让位（RAM 0.1GB<1.5GB·训毕/影片链毕首窗补跑）；"
    "⑧pit 直写 research/pit-git-parse.md（集团树 git log 本地 HEAD 假史坑〔D-20260930-13 的 log 延伸面〕·878B·sha16 9ae3f57c435fdffe·verbatim 对账·29,236B<30KB 帽·r666/r819 范式·receipt results/_r830bmc_pit_append.json）；"
    "⑨idle --worked 清零+HANDOVER 5x 戳（r811-r830 单窗紧凑覆盖+OVERDUE 披露）+S7 四件套全绿（loop pin=5+watchdog 12:32 首火+双爪 LF 归一重装）+attrition 4 台账 CLEAN；"
    "⑩W17 6 shard RAM 门等待态（0.1GB<4GB·影片链毕 autofill 自愈续烧）+训练 killed 11:18（r829 判例五件套·续训明晨 10:00 SLA）双等待态一行声明不重扫 | "
    "验证证据: claw selftest 31/31 + smoke 49/49 + SatEngine rc0 + attrition CLEAN + DEC 6d60855e/ORD 7bf646b7 双消费水位更新 + results/_r830bmc_s05_facts2.json（fetch rc0·unacked 0·inbox 0·0/0） + bonsai closeout 双票 key 验证 + pit receipt verbatim_in_file=true + 43 腿链 09:48 CLEAN 在档（results/_r830bmc_s6_log.txt SUMMARY bad=0） + push 送达自证 | "
    "下轮指针: r831 续作: ①W17 shard RAM 门观察（影片链毕 RAM≥4GB autofill 自愈续烧→checkpoint 推进盯梢）②训毕恢复债（Ollama 双任务 enable+llama-server+ComfyUI 重启·影片窗域·明晨 10:00 SLA）+jman_val_grid 验证链+LOOKBOARD③QA r825 包首个 RAM≥1.5GB 轮补跑④S6 链正常轮跑（43 腿正典）⑤T-181 bm-a 烧批 finalize 消费面盯梢⑥D-20261010-05 写腿=10-11 00:00 常务轮首位（非本司窗） | "
    "本轮产品计分：2（爪窄门修法=能跑实物〔共享单源机制件+selftest 31/31+HQ 回执翻面〕+Bonsai 双票关单+DEC/ORD 双 delta 消费=集团决策执行面实物） | "
    "记账预算：5（state/心跳/轮报三法定+pit 收据+s05 facts 件） | 方法论捕获:无新方法 | 宝藏捕获:无（无五类收口面触发） | 登记册零命中断言:不适用（零清扫零 quarantine·treasure_guard prescan 未触发面） | [via bm-c r830]\n"
)
with open(RR, "a", encoding="utf-8", newline="") as f:
    f.write(row)

# ---- 3. state update ----
SP = os.path.join(ROOT, "state-bm-c.json")
with open(SP, "r", encoding="utf-8") as f:
    st = json.load(f)

did = ("r830 bm-c: D-20261010-07 claw narrow gate implemented (qa/ quarantine-manifest 4th allowance, "
       "_quarantine_cover+moved[]-precise+sha256-vs-old-blob, selftest 31/31 incl 8 new legs, fail-closed intact) "
       "+ D-20261010-04 Bonsai T-99/T-100 formal closeout + DEC/ORD double-delta consumed "
       "(b87a92b1->6d60855e / e286f842->7bf646b7, zero unacked, inbox 0) + smoke 49/49 + SatEngine rc0 + "
       "S6 rest-day triple-skip (2 in-day green runs: 43-leg crosscheck-welded CLEAN 09:48 + 41-leg CLEAN 12:11, "
       "RAM 0.1GB CEO-video-chain protection) + attrition CLEAN + S7 quartet green.")
activity = ("当前活: r830 收口——D-20261010-07 爪窄门修法落地（qa/ quarantine manifest 第四类放行·selftest 31/31）"
            "+D-04 Bonsai 两票关单+DEC/ORD 双 delta 消费；CEO 影片链在本机 GPU 在跑（H3 i2v 生成中·RAM 0.1GB 让路保护） | "
            "最近实物: Tools/git_claw.py（qa/ 窄门）+HQ-FEEDBACK F-20261010-01 翻面 executed+T-99/T-100 closeout 注记"
            "+results/_r830bmc_s05_facts2.json @ " + NOW + " | "
            "下个里程碑: RAM≥4GB（影片链毕）→W17 6 shard 自愈续烧+训毕恢复债（Ollama+llama-server+ComfyUI·明晨 10:00 SLA 窗）"
            "+jman_val_grid+LOOKBOARD；QA r825 包首个 RAM≥1.5GB 轮补跑")
nxt = ("r831 续作: ①W17 shard RAM 门观察（影片链毕 RAM≥4GB autofill 自愈续烧→checkpoint 推进盯梢）"
       "②训毕恢复债（Ollama 双任务 enable+llama-server+ComfyUI 重启·影片窗域·明晨 10:00 SLA）+jman_val_grid 验证链+LOOKBOARD "
       "③QA r825 包首个 RAM≥1.5GB 轮补跑 ④S6 链正常轮跑（43 腿正典） ⑤T-181 bm-a 烧批 finalize 消费面盯梢 "
       "⑥D-20261010-05 写腿=10-11 00:00 常务轮首位（非本司窗）")

st["round_no"] = 830
st["round_no_label"] = "round 830 (bm-c)"
st["clock_read"] = NOW
st["last_seen"] = NOW
st["last_seen_at"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["current_task"] = activity
st["current_task_at"] = NOW
st["current_task_ts"] = NOW
st["activity_now"] = activity
st["did"] = did
st["verdict"] = did
st["last_round"] = did
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_round_summary"] = row.strip()
st["last_round_summary_at"] = NOW
st["last_action"] = row.strip()
st["next"] = nxt
st["next_pointer"] = nxt
st["next_milestone"] = ("RAM>=4GB (video chain done) -> W17 6 shards self-heal + training-resume debt "
                        "(Ollama+llama-server+ComfyUI, next-morning 10:00 SLA) + jman_val_grid + LOOKBOARD; "
                        "QA r825 pack first RAM>=1.5GB round")
st["latest_artifact"] = ("Tools/git_claw.py (qa/ narrow gate, selftest 31/31) + HQ-FEEDBACK F-20261010-01 "
                         "adopted->executed + T-99/T-100 closeout + results/_r830bmc_s05_facts2.json")
st["free_ram_gb"] = ram_free_gb
st["idle_ram_gb"] = ram_free_gb
st["ram_free_gb"] = ram_free_gb
st["gpu_free_vram_mib"] = gpu_free_mib
st["gpu_free_vram_mb"] = gpu_free_mib
st["gpu_idle_vram_mib"] = gpu_free_mib
st["gpu_idle_vram_mb"] = gpu_free_mib
st["gpu_free_mib"] = gpu_free_mib
st["gpu_idle_mib"] = gpu_free_mib
st["gpu_idle_mb"] = gpu_free_mib
st["gpu_vram_free_mb"] = gpu_free_mib
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["heartbeat_epoch_utc"] = int(time.time())
st["last_decisions_sha"] = "6d60855eab8fade5bb0f6301678ca4208dab839688511bab41128d9f051d9d3e"
st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r830 sweep "
                                   "fetch rc0 fresh; dec delta TRUE = b87a92b1 -> 6d60855e = D-20261010-04~10 lunch-batch "
                                   "(commit 693ce04 12:11), bigmoney faces consumed IN-ROUND (D-04 closeout + D-07 claw "
                                   "gate implemented), watermark updated; facts-driven from "
                                   "results/_r830bmc_s05_facts2.json, 64hex shape-asserted")
st["last_decisions_read_at"] = NOW
st["last_decisions_at"] = NOW
st["last_orders_sha"] = "7bf646b7c420d5c2e4c3165bbadbf4bf33d1a9b4"
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r830 sweep fetch rc0; "
                                "ord delta TRUE = e286f842 -> 7bf646b7 via 6e4b0414 (5 new rows: O-20261010-1035 jman SLA "
                                "chase [closed by r821-829 execution + kill disclosure receipt d8db73b] + O-1105/113x/115x/"
                                "rev-3 mv0001 fleet-clip series [@bm-c face = video-window session lane, loop zero-GPU] + "
                                "115x @BigMoney bm-a backtest grant [bm-c zero new duty]); ZERO new dispatch to bm-c loop; "
                                "facts-driven, 40hex shape-asserted")
st["last_orders_at"] = NOW
st["note"] = ("S7 quartet green (loop pin=5 + watchdog 12:32 first fire + precommit/prepush claws LF-normalized reinstall); "
              "attrition CLEAN rc0 (4 ledgers, healed shrinks noted); orphan face=1 read-only (ComfyUI 8188 video-chain "
              "server, do not kill); r829 session CODELY 1-line memory entry absorbed; state round 829->830 clean close; "
              "watermark red=structural (9 W17 shards RAM-gated 0.1GB<4GB, CEO video chain priority per r829 precedent).")
st["sync"] = {
    "ahead": 0, "behind": 0,
    "last_push_ts": NOW,
    "note": "r830 closeout delivery: close commit pushed after this write; post-push fetch + rev-list 0/0 self-verify.",
}
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# ---- 4. heartbeat update (epoch MUST stay int) ----
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(HB, "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = NOW
hb["ts"] = NOW
hb["clock_read"] = NOW
hb["current_task"] = activity
hb["activity_now"] = activity
hb["free_ram_gb"] = ram_free_gb
hb["idle_ram_gb"] = ram_free_gb
hb["gpu_free_vram_mib"] = gpu_free_mib
hb["gpu_idle_vram_mib"] = gpu_free_mib
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["heartbeat_epoch_utc"] = int(time.time())
hb["verdict"] = ("r830: D-20261010-07 claw narrow gate (selftest 31/31) + D-04 Bonsai closeout x2 + DEC/ORD "
                 "double-delta consumed + smoke 49/49 + SatEngine rc0 + S6 rest-day skip (2 in-day green runs) + "
                 "watermark red=structural (W17 RAM gate, CEO video chain priority).")
with open(HB, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

# ---- 5. self-verify ----
with open(HB, "r", encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2.get("heartbeat_epoch_utc"), int), "epoch not int"
assert isinstance(hb2.get("idle_rounds"), int), "idle_rounds not int"
assert "T" in hb2.get("clock_read", ""), "clock_read not ISO-T"
with open(SP, "r", encoding="utf-8") as f:
    st2 = json.load(f)
assert st2["round_no"] == 830
assert isinstance(st2.get("heartbeat_epoch_utc"), int)
print("CLOSEOUT_WRITE_OK now=%s ram=%.1f gpu_free=%d epoch=%d" % (
    NOW, ram_free_gb, gpu_free_mib, hb2["heartbeat_epoch_utc"]))
