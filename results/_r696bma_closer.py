"""r696 bm-a closer: state 696 absolute write + heartbeat + round-report row
+ CODELY entry append. All programmatic (json.dump) with reparse self-checks
(r645 law) and epoch-int / T-clock proofs (R170/R178/R262 laws)."""
import datetime
import json
import os
import psutil
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
NOW_S = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# --- sample machine posture ---
ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
cpu_pct = psutil.cpu_percent(interval=1.0)

# --- 1) state-bm-a.json: round_no 696 absolute write ---
SP = os.path.join(ROOT, "state-bm-a.json")
st = json.load(open(SP, encoding="utf-8"))
assert st["round_no"] == "695", "unexpected prev round_no %r" % st["round_no"]
st.update({
    "round_no": "696",
    "round": "r696",
    "last_round": "r696",
    "last_round_at": NOW_S,
    "last_round_ts": NOW_S,
    "updated": NOW_S,
    "current_task": "r696: r694-i one-tick claim gate LANDED (Tools/autofill.py, S15r/S15r2, selftest ALL PASS); W3 judge product watch (ETA ~22:1x); N2 dual-seat convergence watch (bm-c bare burn in flight / bm-b canonical waiter)",
    "did": "r696: orders 154/154 zero-unacked + D-19 dual-key MATCH (case-normalized) + smoke 48/48 + guardrail landed + 17-UU merge resolved + S6 38/38 rc0",
    "last_action": "r696: r694-i claim gate (origin-missing -> one-tick defer) + merge origin wave x2 + MSG-2025 three-request receipt (MSG-2105) + daemon churn absorb x3",
    "next": "r697+: (1) W3 judge product FIRST CHECK (_r693bma_w3_adopt_probe.py --live -> ADOPTION_READY -> adoption commit + CEO 48h clock; ETA tonight ~22:1x); (2) N2 product landing watch (bm-c bare shard burn / bm-b canonical waiter -> harvest -> screen-prep -> 12-shard SCREEN enrollment r481+r670); (3) CONTEST-RC MSG-2110 adjudication reply consumption (bm-b owner); (4) trio NULLS finalize watch 10-05..09 (bm-b canonical); (5) W117 finalize on bm-b W116 landing (rehearsal r684 armed)",
    "verify": "smoke 48/48; autofill selftest ALL PASS (S15r/S15r2 new legs); push_verify DELIVERED bccaa5d3c (merge #2); attrition guard CLEAN 4 ledgers; state reparse + hb epoch int/T-clock proof",
})
with open(SP, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
v = json.loads(open(SP, encoding="utf-8").read())
assert v["round_no"] == "696", "state reparse round_no mismatch"

# --- 2) heartbeat fleet/machines/bm-a.json ---
HP = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
hb = json.load(open(HP, encoding="utf-8"))
epoch = int(time.time())
hb.update({
    "clock_read": NOW_S,
    "last_seen": NOW_S,
    "heartbeat_epoch_utc": epoch,
    "last_heartbeat_epoch_utc": hb.get("heartbeat_epoch_utc"),
    "cpu_pct": cpu_pct,
    "cpu_util_pct": cpu_pct,
    "free_ram_gb": ram_free,
    "ram_free_gb": ram_free,
    "idle_ram_gb": ram_free,
    "idle_ram_mb": int(ram_free * 1024),
    "last_round": "r696",
    "round_no": "696",
    "loop_round": "696",
    "last_action": "r696: r694-i one-tick claim gate landed in Tools/autofill.py (origin-absent shard -> defer; S15r/S15r2 legs; selftest ALL PASS) + MSG-2025 receipt (probe: burn completed 20:14:17 honestly, product retired per yield continuity; cleanup superseded by bm-c ownership; guardrail delivered)",
    "current_task": "r696 close -> r697: W3 judge product first-check (ETA ~22:1x) + N2 dual-seat convergence watch + CONTEST-RC adjudication reply window",
    "verdict": "watermark=green; r694-i claim gate landed+pushed (daemon orphan-claim churn loop closed at the root); W3/N2 watches healthy; satengine alive rc0 idle",
    "health": "ok",
})
with open(HP, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
v = json.loads(open(HP, encoding="utf-8").read())
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in v["clock_read"] and "+08:00" in v["clock_read"], "clock format"

# --- 3) round report row append (S5) ---
RP = os.path.join(ROOT, "round_reports-bm-a.md")
row = (
    f"{NOW_S} | r696 (bm-a) | watermark=green (red=false; satengine alive rc0 queue0 idle; py_watermark py_low_board_clear golden-week legal board-clear; "
    "compute_audit CLEAN v2.4.2 cpu 7%; pool dualrun ZERO-DRIFT streak 51) | 当前活: r694-i 认领门护栏落地（MSG-2025 三请求回执窗）——origin-missing 洞闭环"
    " + W3 judge 产物值守（bm-c finalize 在飞·ETA ~22:1x）+ N2 双席收敛值守（bm-c 裸分片烧录 20:35 认领/bm-b canonical waiter 20:44 keepalive） | "
    "最近实物: Tools/autofill.py r694-i one-tick claim gate（S15r origin 缺席→defer 零 git 写/S15r2 在席→正常认领防过度拦截·selftest ALL PASS·f9cba4f78 起 origin 在位）"
    f" + results/_r696bma_merge_resolve.py（17 UU per-face resolver·crash_fuse per-sig max-merge+3 jsonl 行 union 零新增缺陷证明+11 regen ts-newer-wins）"
    f" + fleet/inbox/MSG-2026-10-04-2105-bma-ALL.md + S6 38/38 rc0（_r696bma_s6_log.txt·CEO 面 REPORT/LIVE/scorecard/dashboard 幂等再生） @ {NOW_S} | "
    "下个里程碑: ①W3 judge 产物落地收养+CEO 48h 钟起算（今夜 ~22:3x·探针已就绪）②N2 产品落地→SCREEN 12 分片入池（bm-c/bm-b 任一落地窗≤48h）③CONTEST-RC 裁决回执消费（bm-b 属主） | "
    "DONE-1 S0: daemon churn absorb x3 + merge origin wave x2（8+2 commits·17 UU per-face resolver·merge #2 零 UU·push_verify DELIVERED bccaa5d3c ahead0/behind0） | "
    "DONE-2 S0.5: orders 154/154 双扫零未回执（r477 全名同形态）+ D-19 decisions/orders 双键 MATCH（4E5BE321/82A0CEF9·S4U sparse-clone ssh-first r631/r677 配方+大小写归一复核 r503 律——探针首报 match=false 为 hexdigest 小写 vs stored 大写形态假警·前 16 位恒等当场自纠） | "
    "DONE-3 (主产出·r694-i 认领门): 根因链=20:09:38 本机 daemon 对 origin 已清创裸分片 generate-0of1 三度复发认领并起烧——origin 预读（MSG-0535 族）missing 返回不拦截（只拦 done/活rival）+lane-union 复活回流；修=认领门 origin-missing→延一 tick（未推送入池件等一拍+origin 退休孤儿永不再领）；S15r/S15r2 双腿+S15r 归一化 global 声明修复（E22 块冗余声明删除）+selftest ALL PASS；连带诚实披露=本机 fuse n2|generate crashes=1 为假崩（runner 20:14:17 成功退出 262.4s/954 员日志全尾·崩证判据『runner dead+shard not landed』对 done-flip=session 责短活 runner 误判·不编辑 runner 清 fuse·churn 已随 origin merge 自愈 20:47 后拒绝计数零增长实证） | "
    "DONE-4 S1: smoke 48/48 | DONE-5 S3: satengine alive rc0 idle queue0 + W3 --live=PRODUCT_NOT_LANDED（诚实 rc0·ETA 如期）+ 板扫 0 open 票 | "
    "DONE-6 S6: 38/38 rc0（dualrun ZERO-DRIFT streak51·CALL-2026-09-30 ORANGE_COOL sleeves4 activated0·黄金周 no-op 族诚实·live.paper 4.1s·t35_export 2026-09-30 traders6 pos18 equity 5,998,496·token L2 12944+29044） | "
    "DONE-7 S7: 自愈 4/4（pin8 no-op+watchdog -Force 重注册+双 claw LF 归一重装）+ attrition guard CLEAN 4 账本（healed 5 行照录）+ state 695→696 绝对值写+reparse 自证 + 心跳 epoch int 自证 clock T 格式 + MSG-2025 消费归档+MSG-2105 回执发出 + orders 收尾复扫 154/154 | "
    "记分: 2（可跑/能用实物=认领门护栏 canon 代码+两 selftest 腿全绿落 origin·机队级复发环根因闭环；resolver+S6 管线为基础设施增量） | "
    "记账预算: 5/5（state+心跳+轮报+orders 双扫+自愈扫描）+行 1（MSG-2105=fleet 回执件·r694 先例） | "
    "本地未达 origin commit 数: 0（收口 commit 后 push_verify 自证） | "
    "水位旗: CODELY.md 101,657B=r504 注记线（≈50KB）两倍——阈值重锚/立法合并窗=GM 裁定面·本机按 r504 律不单方整编·如实呈报 | "
    "登记簿零命中断言: 本轮零清扫/归档/删除/恢复类动作（探针 read-only·MSG 归档=inbox 协议移动） | "
    "承接判定: 本批新方法=认领门 origin-missing 延迟语义+resolver 零新增缺陷证明腿（史存量坏行内容子集断言泛化）——非新方法论级资产（既有 r694-①律候选的执行落地+resolver 族自然延伸·不入 METHODOLOGY_ASSETS） | "
    "宝藏捕获: 无（判决批未落地——W3/N2 均在飞·非收口窗） | "
    "坑例捕获: 1 条（认领门 missing 洞×lane-union 复活环——CODELY r696 条目·S15r 腿=活体防复发证明） | "
    "下轮指针: ①W3 产物首查 --live→ADOPOTION_READY→收养 commit+CEO 48h 钟②N2 harvest→screen-prep→SCREEN 12 分片入池观察（bm-c 裸分片先落则 bm-c session 收口责·r244 律）③CONTEST-RC MSG-2110 回执消费④trio NULLS finalize watch 10-05..09⑤W117 finalize on W116 landing\n"
)
with open(RP, "a", encoding="utf-8", newline="") as f:
    f.write(row)
assert open(RP, encoding="utf-8").read().count("r696 (bm-a) | watermark") >= 1

# --- 4) CODELY.md entry append (S4, one entry, <=1.5KB) ---
CP = os.path.join(ROOT, "CODELY.md")
entry = (
    "- [2026-10-04 21:0x r696 bm-a] 认领门 origin 预读「missing」洞×lane-union 复活环（r694-i 护栏实弹闭环·第三次复发窗根因）：20:09:38 本机 daemon 对 origin 已清创裸分片 generate-0of1 再认领起烧——根因=19:58 双面清创后裸分片经 lane 镜像 union 回流本地合并视图，而认领时 origin 预读（MSG-0535 族 _origin_shard_state）对 origin 无此分片返回 (\"missing\",None,None) 不拦截（只拦 done/活 rival）→已退休孤儿被复活认领+churn 环。修=Tools/autofill.py 认领门 r694-i one-tick gate：missing=延一 tick（未推送入池件等一拍+origin 退休孤儿永不再领），S15r/S15r2 双腿+selftest ALL PASS。连带两披露：①daemon 崩证判据「runner dead+shard not landed」对 done-flip=session 责（r244）的短活一次性 runner 误记假崩（本例 runner 20:14:17 成功 262.4s/954 员日志全尾·fuse crashes=1 为假记录勿据此判 runner 病·禁编辑 runner 清 fuse）；②merge resolver 证明腿遇双侧史存量坏行（pool_red_flags 10-03 00:53 行）=「零新增缺陷」内容子集断言放行勿 fail-closed 卡死（r641 族泛化·_r696bma_merge_resolve.py 范式）。How to apply：池面认领门改动必配 origin 真值三态全覆盖腿（done/rival/missing）；fuse 崩证消费先核 runner 日志尾再定谳。\n"
)
with open(CP, "a", encoding="utf-8", newline="") as f:
    f.write(entry)
assert open(CP, encoding="utf-8").read().count("r696 bm-a] 认领门") == 1

print("CLOSER OK: state 696 + hb epoch %d int + RR row + CODELY entry" % epoch)
print("ram_free=%.1fGB cpu=%.1f%%" % (ram_free, cpu_pct))
