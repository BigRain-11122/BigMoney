# -*- coding: utf-8 -*-
# r996 continuation closeout (three-dead-session absorb window)
# - round report row -> CANONICAL path logs/iteration-loop/round_reports-bm-c.md (r991 law)
# - state: round 996->997 + absorb note + ORD/DEC watermarks (live-derived, zero literals)
# - heartbeat: occupancy + O-1230 probe receipt + full-load selfproof faces
import json, subprocess, time, hashlib, io, os

sys_ok = True
try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

GR = r"K:\Fluxgroup\FluxGroup"
BQ = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())

def gshow_bytes(repo, path):
    r = subprocess.run(["git", "-C", repo, "show", "origin/main:" + path], capture_output=True)
    assert r.returncode == 0, (path, r.stderr[:200])
    return r.stdout

# --- watermarks (pinned methods: ORD=content-bytes sha1, DEC=raw-blob sha256) ---
subprocess.run(["git", "-C", GR, "fetch", "origin"], capture_output=True)
ord_bytes = gshow_bytes(GR, "docs/orders.md")
dec_bytes = gshow_bytes(GR, "docs/decisions.md")
ORD_SHA = hashlib.sha1(ord_bytes).hexdigest()
DEC_SHA = hashlib.sha256(dec_bytes).hexdigest()

# --- round report row (canonical path) ---
RR = os.path.join(BQ, "logs", "iteration-loop", "round_reports-bm-c.md")
row = (u"2026-10-14T14:2x | r996 | bm-c | 三死窗吸收窗收口（MV V3 车道会话+收尾准备会话+W239 周期会话 11:27-13:59 全死于收尾前）——"
       u"①主体=W239 全周期吸收落地：死窗已上链 prereg 97a7ff0e6+splice c85e806c9+daemon 自燃 12/12（65b222df6+6cc36056f）+sixgate PRE-FINALIZE 第十四连续正相位+finalize one-pass 账本 947,935+2,200=950,135 EXACT/K=523,720/mu -0.0927/sigma 0.2451，"
       u"本窗补齐 fivekey 全过（dmu 0.0082/sigma -0.005%/p95 diff 0.0023/K-lift 0.0）+sec.7/8 回填 placeholders=0（r583 机读零转抄律）→ estate commit 0fbf34dbc+簿记面 4019125c6→rebase 2/2→push a82bd3025（0 ahead/behind）；"
       u"W240 席已发布（bm-a 39a30b6a0）候本 finalize 解锁；"
       u"②MV V3 车道（CEO O-20261014-1035 GPU 解锁令追责面）：波 1 6/6 签章镜全落盘（SIL1/SIL2/SIL3 存量+SING1/SING2/SING3b 新烧+CDN 三条）+QC 3 帧自检板+I2V-URL-INDEX——回执已落组树 orders（worktree 手术 be32c1f·零主树触碰）+poke bm-a 受理 14:22:26=装配站解锁；"
       u"波 1.5 SIL4 探针 1/8 后 runner 会话死+脚本盘面灭失（全盘清扫空·死窗遗产=仅 peek/回执）→波 1.5 余 7 帧+波 2 32 条待 runner 重建接续=r997 首动作；"
       u"③O-20261014-1230 探测任务完成：bm-a 35B :8090 health=200 通（死窗 exit 28 超时面已愈）；"
       u"④软著 B/C 机 18 款复跑批 11:48 已跑（log 26KB 尾达 G28_ArrowOut·err 0B）——完成核验+commit+push=r997 待办；"
       u"⑤S6 light：dualrun ZERO-DRIFT streak 51（456）+compute_audit FLAG pool_starvation/supply_floor 结构性（池 ready=0<3·供给链候 W240 bm-a 席合法）+wm probe insufficient_history 新鲜窗（bars pre-15:30）+attrition 4 CLEAN；"
       u"⑥smoke 49/49+S0.5 消费集=ORD 10:3x-13:4x 行（O-1035/O-1125/O-1230/O-1325+软著 18 款+MV 工艺令族）双面收口（死窗执行体+本窗回执）·DEC D-01~07=HQ/FluxVerse 域零 BigMoney 指令仅推水位——水位推进 ORD {ord8}→本窗 sha/DEC 86187eff→本窗 sha（lineage-B 13:40 收口未落账勘误入档：其 d9d8aa72/179ac0f4 宣称未落 state/轮报告任何面=死窗宣称）；"
       u"⑦孤儿面=3（py_faces 9·零杀·MV-lane ComfyUI 保护面+album_serve/Doubao） | 下窗指针：r997=(1) runner 重建+波 1.5 余 7 帧续跑→波 2 32 条 INT8 768P 自链（CEO 闲置令在责·GPU 不可再闲）；(2) 软著 18 款完成核验+commit+push+orders 回执；(3) 15:30 bars→papers 全链；(4) W240 finalize 落地→W241 席位发布（bm-c 席位轮到）；(5) MF-IC-P1 面板复查").format(ord8=u"348eaf34")
lines = io.open(RR, "r", encoding="utf-8", newline="").read()
assert u"r996 | bm-c | 三死窗吸收窗收口" not in lines
if not lines.endswith("\n"):
    lines += "\n"
lines += row + "\n"
io.open(RR, "w", encoding="utf-8", newline="").write(lines)
print("ROUND-ROW-APPENDED canonical")

# --- state update ---
ST = os.path.join(BQ, "state-bm-c.json")
st = json.load(io.open(ST, "r", encoding="utf-8"))
st["round_no"] = 997
st["last_round"] = "r996"
st["round_no_label"] = "r996"
st["last_round_at"] = NOW
st["last_round_ts"] = EPOCH
st["last_seen"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["last_round_summary"] = (u"r996: 三死窗吸收收口 -- W239 全周期落地（950,135/K 523,720 五键全过+sec78 回填）+MV V3 波 1 回执 6/6 落 orders+poke bm-a 装配解锁+O-1230 探测 200 通；"
                            u"runner 灭失=波 1.5/波 2 待 r997 重建接续；counter 996->997")
st["last_round_closed"] = NOW
st["last_action"] = "r996 closeout (three-dead-session absorb: W239 estate landed + MV wave1 receipt relayed + probe 200)"
st["last_artifact"] = (u"r996: W239 finalize estate（n1_w239_results.json 账本 950,135/K=523,720·五键全过·commit 0fbf34dbc/a82bd3025）+MV V3 波 1 回执（组树 orders be32c1f·6 mp4+CDN+QC 板）")
st["recent_artifact"] = st["last_artifact"]
st["next"] = (u"r997: (1) MV runner 重建+波 1.5 SIL4 探针余 7 帧→波 2 32 条 INT8 768P 自链（CEO 闲置令·GPU 优先）；"
              u"(2) 软著 B/C 机 18 款完成核验+commit+push+orders 回执；(3) 15:30 bars→papers 全链；"
              u"(4) W240 finalize（bm-a）落地→W241 席位发布（bm-c 轮位·seat-first 律 prereg derive 首动作）；(5) MF-IC-P1 面板复查")
st["verdict"] = (u"green: r996 三死窗吸收全收口 -- W239 own-wave finalize landed (950,135/K 523,720 five-key ALL PASS)+MV wave1 6/6 receipt relayed (assembly unblocked)+probe 200; "
                 u"GPU idle face = runner lost, wave1.5/wave2 chain restart = r997 FIRST action per CEO idleness law; smoke 49/49 + S6 light green + attrition CLEAN")
st["next_pointer"] = st["next"]
st["next_milestone"] = u"r997: MV runner 重建+波 2 自链点火；W241 席位（候 W240）；15:30 bars papers"
st["did"] = (u"r996: (1) S0-1 anchor bm-c + round-zero probe py_faces=9 orphans=3 zero-kill（MV-lane ComfyUI 保护面）；"
             u"(2) S0 fetch 3-behind bm-a W19 面发现三死窗遗产（MV V3 会话+收尾准备+W239 周期会话）→吸收定谳；"
             u"(3) 主体=W239 estate 验证+补齐+落地：fivekey 全过复核+sec78 回填（新克隆 _w239bmc_sec78_backfill.py·W237 模板 W239 实参全机读）+prereg 占位清零+estate commit 0fbf34dbc push a82bd3025；"
             u"(4) MV V3 波 1 回执=组树 orders worktree 手术 be32c1f+poke bm-a 受理；波 1.5 runner 灭失披露；"
             u"(5) O-1230 探测 200 通（bm-a 35B health）；(6) S1 smoke 49/49；(7) S6 light dualrun streak 51+audit FLAG 结构性+wm insufficient_history+attrition 4 CLEAN；"
             u"(8) S0.5 消费集 ORD 10:3x-13:4x 双面收口（死窗执行体+本窗回执）+水位推进；DEC 域外零动作；"
             u"(9) S7 收尾四联+正典轮报告路径写回")
st["activity_now"] = NOW[:16] + u" | r996 | bm-c: 三死窗吸收收口（W239 落地+MV 波 1 回执+探测 200） | counter 996->997"
st["now_active"] = st["activity_now"]
st["last_orders_sha"] = ORD_SHA
st["last_orders_at"] = NOW
st["last_decisions_sha"] = DEC_SHA
st["last_decisions_at"] = NOW
st["last_decisions_read_at"] = NOW
st["last_orders_read_at"] = NOW
st["last_orders_seen"] = NOW
st["last_decisions_seen"] = NOW
st["clock_read"] = NOW
st["heartbeat_epoch_utc"] = EPOCH
st["last_ts"] = EPOCH
st["last_seen_at"] = NOW
st["current_task"] = (u"r996 closeout (three-dead-session absorb: W239 landed + MV wave1 relayed + runner-rebuild r997 P0); bars pre-15:30; W240=bm-a seat waiting on my finalize (cleared)")
st["current_task_at"] = NOW
st["current_task_ts"] = EPOCH
st["prod_lanes"] = (u"CPU=N1 W239 CLOSED (r996 finalized 950,135/K=523,720); W240=bm-a SEATED 39a30b6a (freeze waits-upstream CLEARED by this finalize -> their splice next); "
                    u"W241=bm-c rotation seat (publish after W240 lands); MF-IC-P1: parked, bm-a panel refresh in flight; "
                    u"W19-SCREEN pool: 7 ready bm-b-lane (autofill consuming); GPU=MV V3 wave1 COMPLETE 6/6 (receipt relayed, assembly unblocked) -- wave1.5 SIL4 probe 1/8 + wave2 32 files = r997 runner-rebuild P0 (runner script lost, GPU idle violation face -- CEO idleness law)")
st["sync"] = {"origin_tip": "a82bd3025 (estate+bookkeeping landed); group-tree orders relay be32c1f",
              "ts": NOW, "ahead_behind": "0/0 pre-closeout (closeout commit+push rides)"}
st["r996_closeout_note"] = (u"r996: 三死窗吸收窗（MV V3 会话+收尾准备会话+W239 周期会话·11:27-13:59 三体全死于收尾前）-- 本窗按 bm-c absorb 先例链（r894..r993 第 23 代）收口："
                            u"W239 全周期 estate 验证后落地（死窗已上链 splice c85e806c9+burn·本窗补 sixgate 收据+finalize 产物+fivekey+sec78 回填→commit 0fbf34dbc+push a82bd3025）；"
                            u"MV V3 波 1 6/6 签章镜回执落组树 orders be32c1f+poke bm-a；波 1.5 runner 灭失=波 2 自链断链面如实披露（r997 首动作=runner 重建）；"
                            u"O-1230 探测 200 通；软著 18 款复跑批已跑待 r997 核验收口；lineage-B 13:40 收口宣称（d9d8aa72/179ac0f4）未落任何账面=死窗宣称勘误入档·零双计（本窗重算 origin 实测 sha 推进水位）；counter 996->997 so next=r997")
st["orders_ack_receipt"] = (u"r996: group-orders rows 10:3x-13:4x consumed two-sided (dead-session bodies executed: O-1035 GPU unlock wave1 burned+relayed / O-1125 GPU MV-only respected / O-1230 probe 200 OK this window / "
                           u"O-1325 wave-law QC sheet landed; 软著 18款 batch ran 11:48 pending r997 verify-close); DEC D-01~07 = HQ/FluxVerse domain zero BigMoney directive -> watermark advance only")
st["verify"] = (u"receipts: W239 estate commit 0fbf34dbc+bookkeeping 4019125c6 push a82bd3025 (0/0) + fivekey ALL PASS receipt + sec78 placeholders=0 + group orders relay be32c1f + poke accepted 14:22:26 + probe 200 + smoke 49/49 + dualrun streak 51 + attrition 4 CLEAN + orphan face=3")
st["orphan_face"] = 3
st["orphan_faces"] = 3

# live GPU/RAM snapshot for heartbeat fields
try:
    g = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"], capture_output=True).stdout.decode().strip().split(",")
    st["gpu_free_vram_mib"] = int(g[0]); st["gpu_util_pct"] = int(g[1])
    st["gpu_mem_used_mib"] = int(g[2]); st["gpu_mem_total_mib"] = int(g[3])
except Exception:
    pass
try:
    ram = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB)"],
                         capture_output=True).stdout.decode().strip()
    st["free_ram_gb"] = round(float(ram), 1); st["ram_free_gb"] = st["free_ram_gb"]; st["idle_ram_gb"] = st["free_ram_gb"]
except Exception:
    pass

json.dump(st, io.open(ST, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
# verify epoch int type
chk = json.load(io.open(ST, "r", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("STATE-ADVANCED 996->997 | ORD", ORD_SHA[:8], "| DEC", DEC_SHA[:8])

# --- heartbeat ---
HB = os.path.join(BQ, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(HB, "r", encoding="utf-8"))
hb["last_seen"] = NOW
hb["ts"] = NOW
hb["clock_read"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = st["current_task"]
hb["verdict"] = (u"green: r996 absorb-closeout done (W239 landed 950,135/K523,720 + MV wave1 relayed + probe 200) -- r997 P0 = MV runner rebuild + wave2 self-chain (GPU idle face, CEO idleness law); bars 15:30 next; W240 bm-a unblocked")
hb["prod_lanes"] = st["prod_lanes"]
hb["full_load_selfproof"] = {
    u"占用一行": (u"GPU=ComfyUI 8188 活·Krea2 常驻 13.5G/16G·队列空（波 1 毕·runner 灭失待 r997 重建）+ollama 35b standby；CPU=py 0.1% 空闲带（W240=bm-a 席·W241=bm-c 轮位候 W240 落地）"),
    u"当前活": u"r996 三死窗吸收收口（W239 全周期落地+MV 波 1 回执 relay+O-1230 探测 200）",
    u"下一交付物": u"r997: MV runner 重建+波 1.5 余 7 帧+波 2 32 条自链点火（GPU 优先·CEO 闲置令）；15:30 bars papers 全链；W241 席位（候 W240）",
    u"队列水位": u"N1 引擎 0 在烧（W239 closed·W240=bm-a 席候 splice）·MV V3=波 1 毕 6/6·波 1.5 1/8·波 2 0/32（runner 重建后）·P2/P3 空·bars 15:30",
}
hb["last_artifact"] = st["last_artifact"]
hb["next_milestone"] = st["next_milestone"]
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["activity_now"] = st["activity_now"]
hb["last_round"] = "r996"
hb["orders_ack_last"] = "O-20261014-0949-bm-b.md (unchanged; new CEO rows are group-orders faces consumed via watermark)"
json.dump(hb, io.open(HB, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
chk2 = json.load(io.open(HB, "r", encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "hb epoch must be int"
print("HEARTBEAT-WRITTEN", NOW)
