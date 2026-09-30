# r480 bm-b wrap: inbox self-ALL archive, HANDOVER 5x entry, round report line,
# state round_no, heartbeat (epoch int + T-sep clock_read), all per OS prompt.
import json, os, shutil, sys, time, datetime
sys.stdout.reconfigure(encoding="utf-8")

# 1. inbox: archive my own ALL message (content fully receipted: bm-a r492 +
#    bm-c r289 both responded to the S2-burn/harvest-flips/merge-fix content)
src = "fleet/inbox/MSG-20260930-2150-bmb-ALL-p2null-s2-burned-harvest-flips-merge-fix.md"
if os.path.exists(src):
    shutil.move(src, "fleet/inbox/processed/" + os.path.basename(src))
    print("inbox: own ALL message archived to processed/")

# 2. HANDOVER 5x entry (round 480 = 5x96; last bm-b entry r475, latest head = bm-a r490)
hb_path = "research/HANDOVER.md"
txt = open(hb_path, encoding="utf-8").read()
lines = txt.splitlines()
entry = ("> bm-b round 480 五倍数核对（2026-09-30 22:3x）：增量窗 r476-480=bm-b 侧（r476 W14 runner engine leg 建毕 selftest 16/16 "
         "+种子带撞号修正 20329000→20329500；r477 EXCLUSION-MARGINAL 越界修复〔d>=cal[0] 日历行守卫+全史 age250〕；r478 _Mkt dict 契约修复 "
         "〔compile rc0+selftest 16/16〕+MA200 探针；r479 O-2054 e-item S2 烧批 550 runs 批 3/4+merge_lane_views owner_since-null 坑修"
         "+EXCLUSION/FACEB defer 泊位+push 风暴三连拒〔备份分支 machine/bm-b-r479〕；r480=本核对轮：S0 15+1 UU 撞车正典解"
         "〔EOL 异面行级 union 假阳性坑+origin 污染件 _attrition_guard_scan.json 修复+pool defer 蓄意注记裁定〕"
         "+CENSUS-588000-FULLHIST 落地〔O-1858/O-2054 e-item leg-1·廉价普查门范式〕+S6 37 腿全 rc0+watchdog S4U 合规修"
         "〔InteractiveToken→S4U·09-29 律〕+CODELY 热冷整编 9703B）。产物清单漂移=scripts/census_588000_fullhist.py "
         "+results/census_588000_fullhist.json〔r480 新〕+results/_r480_resolve.py+_r480bmb_s6_chain.py+_r480bmb_memreorg.py"
         "+Tools/register_watchdog_task.ps1〔S4U 修正〕；统一锚=K2200 判定面 bm-c r289 收口 364,589 不变；指针：astock 全宇宙刷新在飞 "
         "pid47564〔~400/5082〕完成后 W14-GENERATE+EXCLUSION/FACEB 三票解冻烧〔预计 10-01 晨〕+census leg-2 入 O-1147 组合书 "
         "sleeve 证据面+10-01 月首轮三件套〔science_audit/monthly_briefing/self_review〕+REGIME_GUARD v3 日期门自动激活 hands-off；"
         "下一 5x=bm-b r485")
# insert after the first line (title)
lines.insert(1, entry)
open(hb_path, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
print("HANDOVER: 5x entry inserted")

# 3. round report line (S5, bm-b ledger file)
rr_path = "logs/iteration-loop/round_reports.md"
rr = ("2026-09-30 22:3x | r480 bm-b | dept:研究/工程 | WM=绿（red=false lane healthy；py 0.4-7.6% 低位=合法白名单：astock 全宇宙刷新在飞 "
      "I/O-bound〔pid47564·400+/5082·sina 已通〕+池 0 ready 全 gated+板全闭环；audit 旗 supply_floor 供给泊位如实）| 当前活:O-1858/O-2054 "
      "e-item「588000 全史 stress 批」leg-1 普查落地；最近实物:scripts/census_588000_fullhist.py（selftest 6/6）+results/"
      "census_588000_fullhist.json（evidence_cutoff=2026-09-30·1427 bars 完整干净·maxDD 59.6% 1166 天水下〔2021-07-08→2024-09-23→"
      "2026-05-06 复原〕·ann 1.7%/31.9%·best 2024-09-30 +18.2%/worst 2025-04-03 -9.6%·corr vs 510300 p50 0.71〔z≥2 压力旗 57 天·"
      "上市锚窗 0/69〕·MA200 下 46.5% 最长 308 天·fwd20 below +0.15%/above +1.21%·成本 x1RT 26.082bp/x2RT 52.164bp·流动性日额 "
      "0.86B→6.18B=7.2×）+S6 37 腿全 rc0（scorecard/daily_scorecard/build_status=合法 stale-takeover〔bm-a hb 23min 陈旧〕）；"
      "S0=push 风暴撞车 15+1 UU 正典解（分类器 14+3UNKNOWN 手裁：快照 deep-ts 取新/ledger ts-union 零丢失/pool done-absorb 4 +"
      "defer 蓄意注记胜 2/CODELY EOL 异面坑=归一后真新仅 2 行入 Project 节/shard 取 ours〔仅 audit 元数据差〕；origin 污染件 "
      "_attrition_guard_scan.json 携 bm-a r492 未清冲突标记=当窗取 HEAD 侧修复+json.loads 验；rebase 4 波全过+push 8b496c2fa.."
      "1b8af05a6 一次过）；S7=watchdog S4U 合规修正〔InteractiveToken→S4U·注册脚本同步改〕+loop pin=2 no-op+claw identical+"
      "attrition CLEAN（2 历史 shrink 均 healed）+自发 ALL MSG 归档；CODELY 热冷整编（r479 两行 verbatim→archive+r480 EOL 坑律入·"
      "9703B≤10KB 硬线）；下轮指针:astock 刷新完成〔~10-01 晨〕→W14-GENERATE+EXCLUSION/FACEB 三票解冻烧（autofill 自动）+"
      "census leg-2 入 O-1147 L3 组合书 sleeve 证据面+10-01 月首轮三件套+REGIME_GUARD v3 日期门自动激活禁手碰")
with open(rr_path, "a", encoding="utf-8", newline="") as f:
    f.write(rr + "\n")
print("round report: r480 line appended")

# 4. state.json round_no 479 -> 480
st = json.load(open("state.json", encoding="utf-8"))
st["round_no"] = st.get("round_no", 0) + 1
st["last_round_at"] = "2026-09-30 22:3x"
st["ts"] = datetime.datetime.now().isoformat(timespec="seconds")
st["updated"] = True
json.dump(st, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state.json: round_no ->", st["round_no"])

# 5. heartbeat fleet/machines/bm-b.json (epoch MUST be int, clock_read T-sep)
now = datetime.datetime.now().astimezone()
hb_path2 = "fleet/machines/bm-b.json"
hb = json.load(open(hb_path2, encoding="utf-8"))
hb["last_seen"] = now.isoformat(timespec="seconds")
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = now.isoformat(timespec="seconds")
hb["current_task"] = ("r480 closeout: O-2054 e-item 588000 fullhist census landed (leg-1) + "
                      "S0 push-storm 15+1 UU canon-resolved + S6 37 legs rc0; next: astock refresh "
                      "completes ~10-01 morning -> W14-GENERATE + EXCLUSION/FACEB unfreeze burns")
hb["cpu_cores"] = os.cpu_count()
try:
    import psutil
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / 1e9, 1)
except Exception:
    hb["free_ram_gb"] = None
try:
    hb["gpu_free_vram_gb"] = None  # no local discrete GPU on this node (16-core data node)
except Exception:
    pass
hb["verdict"] = "green-legal-idle: pool fully gated on astock refresh (I/O-bound in flight), board closed"
json.dump(hb, open(hb_path2, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# self-verify: epoch int + clock T-sep (R170/R178/R262 laws)
back = json.load(open(hb_path2, encoding="utf-8"))
e = back.get("heartbeat_epoch_utc")
c = back.get("clock_read", "")
assert isinstance(e, int) and not isinstance(e, bool), "epoch not int"
assert "T" in c, "clock_read missing T separator"
print("heartbeat: epoch=", e, "(int OK) clock_read=", c)
print("WRAP DONE")
