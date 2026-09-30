# r495 bm-b S7 closeout: state round_no++, heartbeat, round report line, CODELY pit entry
import json, time, datetime, os

ROOT = os.path.dirname(os.path.abspath(__file__))  # results/
REPO = os.path.dirname(ROOT)
now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# --- state.json: round_no 494 -> 495 ---
sp = os.path.join(REPO, "state.json")
st = json.load(open(sp, encoding="utf-8"))
assert st.get("round_no") == 494, st.get("round_no")
st["round_no"] = 495
st["note"] = ("r495: W9-W13 JUDGE ghost shard heal x5 (r489 dual-layer law pre-fix residue; evidence=judge products in-tree "
              "243/283/229/188/99) + dead-session takeover (06:0x stream-timeout, probe files reused) + S6 38 legs rc0 "
              "(reconcile ZERO-DRIFT 12/3; batch-1 PS splat char-explode pit -> runner .ps1 explicit-array fix) + "
              "EXCLUSION/FACEB=astock data-wait self-heal lane (2 tail failures -> 3-strike quarantine) + W14 stays "
              "governance-parked (MSG-0540, GM dual-ruling pending)")
for k in ("last_round_at", "last_round_ts", "ts", "updated", "updated_at"):
    st[k] = iso
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state.json round_no ->", 495)

# --- heartbeat fleet/machines/bm-b.json ---
hp = os.path.join(REPO, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = iso
hb["current_task"] = ("r495 done: W9-W13 judge ghost-shard heal x5 (dual-layer r489 debt) + S6 38 legs rc0; "
                      "EXCLUSION/FACEB astock data-wait self-ignite pending; W14 governance-park intact")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = iso
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), type(chk["heartbeat_epoch_utc"])
print("heartbeat epoch int ok:", chk["heartbeat_epoch_utc"], chk["clock_read"])

# --- round report line (bm-b lane = logs/iteration-loop/round_reports.md) ---
rp = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")
line = (
    "2026-10-01T06:3x:00+08:00 | r495 bm-b | dept:工程/治理 | "
    "[watermark verdict: RED runnable-work-idle-low-cpu py_tail 0.8/1.6/0.1——成因链三面如实点名："
    "①W14-GENERATE=治理停放（MSG-0540·GM 双裁定待署名·本机禁自解锁）②EXCLUSION/FACEB=astock 面板 data-wait"
    "（5217/5229·刷新在飞节流中·尾部 2 失败 001381 KeyError-date/300269 SSLError 走 3 次熔断隔离律·机制自愈非永久饥饿"
    "——完备判据=todo 集合扣隔离符号实证）③RAM 6.6GB<8GB daemon floor（四游戏会话并跑占用·非本司车道面）] | "
    "本轮主产出（实物）：**W9-W13 JUDGE 幽灵 ready 分片翻 done×5**（results/runnable_pool.json 5 行外科 diff——r489 双层翻面律"
    "「缺一=幽灵面」的 pre-fix 残留收口；证据=5 判决产物在树 w9=243/w10=283/w11=229/w12=188/w13=99 cells+entry 层 done_at/"
    "finalize 回执在案；W1-W8 分片=done 正典形态对齐；reconcile 采样 ZERO-DRIFT 12/3 连绿证实零漂移）+ "
    "S6 38 腿全 rc0（含批 1 PS splat 字符炸坑补跑：reconcile/py_watermark 首跑 rc=2 假失败→修正后 rc0；reconcile 本轮后置于 "
    "compute_audit settle=证据腿降级窗如实披露）| 会话面：前会话（06:04-06:07 落 _r495bmb 探针件后）流超时死亡，本会话接管 r495 "
    "复用其 S0.5 扫描件与 probe 件（反重复铁律）；orders 133/133 双扫 EMPTY；D-19 ED4E0EAB UNCHANGED 零动作；"
    "T-131 仍候 GM 署名禁认领；W14 泊位 PERPETUAL_FACES v1.1 同候 GM；bm-a 心跳 05:34/bm-c 05:45 停滞 ~50min 观察"
    "（t35_verify/daily_scorecard stale-takeover derive 合法 O-2100 s2.4；其机自愈域非本司债务）；smoke 47/47；"
    "attrition CLEAN（4 账本·bm-a 侧 healed 4 行照录）；HANDOVER r495 五倍数核对行落位（r481-495 增量窗）| "
    "三行实况: 当前活=EXCLUSION/FACEB 等 astock 面板齐后 daemon 自燃（两边际扫描批·预计 ≤08:0x）；"
    "最近实物=results/runnable_pool.json（W9-W13 shard heal 5 行）@06:2x+docs/live_usage/LIVE-2026-10-01.md（ORANGE cap50 COOL）@06:3x；"
    "下个里程碑=W14 泊位 GM 双裁定→解冻 generate（窗≤10-02 白天）·N1-W3 供给面待 v1.1 署名（窗≤10-03）"
)
with open(rp, "a", encoding="utf-8") as f:
    f.write("\n" + line + "\n")
print("round report appended")

# --- CODELY.md pit entry (memory gate: S6-every-round value, one-thing, <1.5KB) ---
cp = os.path.join(REPO, "CODELY.md")
size_before = os.path.getsize(cp)
pit = (
    "\n- [2026-10-01 06:3x r495 bm-b] PS @splat 标量字符串炸字符坑（S6 链首跑实弹）：命令 splat `@rest` 当 $rest 为标量字符串时"
    "按 IEnumerable(char) 逐字符展开——'run'→r,u,n 三参、argparse 报 invalid choice 'r'、py_watermark probe 同炸（rc=2 假失败）；"
    "连带 reconcile 被排到 compute_audit settle 之后=证据腿降级窗（后置如实披露照录）。正解=腿参显式 @() 数组"
    "（results/_r495bmb_s6_runner.ps1 范式：hashtable a=@('run')）或 [string[]] 强转；splat 消费前判 -is [array]。"
    "How to apply：一切 PS 循环器传子命令参数必显式数组；遇 argparse「invalid choice 单字母」先查 splat 字符炸面。\n"
)
with open(cp, "a", encoding="utf-8") as f:
    f.write(pit)
print("CODELY.md appended, size:", size_before, "->", os.path.getsize(cp), "(50KB line:", os.path.getsize(cp) > 50 * 1024, ")")
