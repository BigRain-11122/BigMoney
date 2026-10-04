# -*- coding: utf-8 -*-
"""r656 bm-b closeout: round report append + state.json increment + heartbeat.
Programmatic writes only (json.dump), json.loads self-verify after every write
(r645 trailing-comma law; R170/R178 epoch-int law)."""
import datetime
import json
import os
import subprocess

RB = os.getcwd()
NOW = datetime.datetime.now().astimezone().replace(microsecond=0)
CLOCK = NOW.isoformat()
EPOCH = int(NOW.timestamp())


def jload(p):
    with open(p, "rb") as f:
        return json.loads(f.read().decode("utf-8"))


def jdump(p, obj):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=True, indent=1)
        f.write("\n")
    jload(p)  # self-verify parse


# ---------- 1) round report append (mixed-encoding file: utf-8, no CRLF xlation) ----------
block = f"""{CLOCK} | round 656 (bm-b, dept:工程/研究): watermark verdict=GREEN (red=false; engine alive rc0 idle; dualrun ZERO-DRIFT streak 48; py 62-86% 三族烧批+车道占用合法)
当前活: FUND 三族 NULLS 烧录在飞推进实证 Q480→489/V634→645/D343→350（08:0x 新鲜行数 +9/+11/+7 自 07:37 探针·dup_k=0·三 pid 34396/57116/30208 实活）——r655 探针「Q/V 率 0.0」定谳=lumpy 采样伪影非停摆；GM 双裁令 O-20261004-0808 裁决二已结 G-SEG 裁决窗（冻结 insufficient-sample 路径维持·在飞三判决禁中途换分段法）→ finalize 治理面 resolve=mechanical_ready 即开窗（r638 fallback armed）
最近实物: ①死会话 merge 遗产收养+双波送达：r655 会话 07:46 断气于 merge origin bm-c r451 波中途（21 UU 悬空+resolver 未跑）→ 本轮按 r643 收养律分类器先行（r440/r652 配方：工具面 5=merge_lane_views 单源·jsonl union·快照 deep-ts+twin 同侧律）解毕 7c574497f → 首推被 pre-push claw 真拦截（origin 已前进=r452 波+GM 令·强推会抹他机新件=claw 达成设计目的）→ r437 序 absorb 4b198b7e8+二番 merge 19 UU（本窗 theirs 新 1-2min·两 probe-miss 面诚实 MERGE_HEAD-vs-HEAD 复核翻 theirs〔attrition 07:44:46>07:42:31·summary 07:42:45>07:41:24〕·post_review 双面自动并+四 append 面零丢失父本行集 containment PASS）→ 958cf23b5 DELIVERED——r655 未送达的 P2 retro（research/auto/retro-20261004.md）随本推送首次落 origin；②S6 34 腿 rc0 CEO 面刷新（REPORT/LIVE-20261004 再生·bm-a 宿主面 stale-takeover derive per STALE_MIN law〔bm-a 心跳 24min 陈旧〕·dualrun streak 48）
下个里程碑: 三族烧满 2000 → mechanical_ready=true → finalize+E1 判决落窗 10-05..10-09（G-SEG 治理已由 GM 令结案=冻结路径确认·r638 单读 fallback armed）；窗 ≤48h 首查=烧录完成度+finalize 开窗执行
做了什么: S0-1 bm-b 锚定（r98 律）→ S0 死会话遗产收养双 merge 收口（21+19 UU·证据 results/_r656bmb_merge_resolve.py + _r656bmb_merge_resolve2.py + _r656bmb_verify.py + _r656bmb_zeroloss.py）+ claw 真拦截合规绕行（fetch+merge 净路非 --no-verify）+ push_verify DELIVERED；S0.5 令扫 153/152 差集=1 新令 GM 双裁令 O-20261004-0808-bm-a（W14 停泊维持+G-SEG 冻结路径维持+假期算力轨道对齐·P1 代决·否决窗 7 天）回执消费：trio NULLS=基线/nulls 豁免线照跑·W14 停泊维持不解冻·10,000 帽悬置不影响 V-NULLS 线 + D-19 sparse-clone fallback 双 MATCH 零消费（decisions=EB14B510/orders=82A0CEF9）；S1 smoke 48/48（第 48 腿=merge 带入的 update_fund_statements selftest）；S2 双板 0 open（fleet 46 claimed 旧票册+T-166 bm-a 在跑不碰·job_list 空）；S3 门全绿+trio 活性深查（新鲜行数+pid 三活）；S6 34 腿 rc0；S7 pin=2 no-op+watchdog 重注册+双爪幂等重装+attrition CLEAN+inbox 零件+CODELY 43.8KB<50KB 线内
验证证据: push_verify DELIVERED tip=958cf23b5 ahead=0 behind=0；merge 解毕面 21+19 marker 零残留+parse 全过（results/_r656bmb_verify.py PASS 21/21）+append 四面零丢失（post_review 5312 行逐行 JSON 过·nulls trio 双亲行集 containment 0/0 丢失）；smoke 48/48；S6 evidence 34/34 rc=0（results/_r656bmb_s6_evidence.txt·dualrun streak 48）；trio 新鲜行数 489/645/350+pid 三活；attrition 4 ledger CLEAN；D-19 双 MATCH；令差集 153=152+O-0808 唯一新令；state/心跳 json.loads 双自证 epoch int·clock T 分隔
下轮指针: r657 = trio watch 续（mechanical_ready=true 即执行三族 finalize+E1·r638 fallback；任一族 ETA>10-09 12:00 走合规护栏）；CODELY 新坑律=ts 探针 fullmatch 时区后缀坑（+08:00 值 fullmatch 失配→probe-miss 默认面静默误向·唯诚实双侧复核可救——已修 _r656bmb_merge_resolve.py WALL_RE match 化）；W14-GENERATE 治理停泊待 GM 解冻一行声明；retro 复线健康纳入 watch
本地未达 origin commit 数=0（以收尾 push_verify 输出为准；失败则 addendum 留痕）
"""
p = "logs/iteration-loop/round_reports.md"
with open(p, "a", encoding="utf-8", newline="") as f:
    f.write(block + "\n")
print("round report appended")

# ---------- 2) state.json ----------
sp = os.path.join(RB, "state.json")
st = jload(sp)
st["round_no"] = st.get("round_no", 0) + 1
st["round_no_label"] = "round %d (bm-b)" % st["round_no"]
st["note"] = ("r656: dead-session merge estate adopted + dual-wave delivered -- r655 died mid-merge "
              "(21 UU dangling, resolver unrun); adopted per r643, classified per r440/r652 (tool 5 + "
              "jsonl union + snapshot deep-ts + twin same-side), 7c574497f; first push blocked by "
              "pre-push claw = REAL protection (origin advanced: bm-c r452 + GM order) -> r437 "
              "sequence: absorb daemon faces 4b198b7e8 + second merge 19 UU (theirs newer window; two "
              "probe-miss faces flipped theirs after honest MERGE_HEAD-vs-HEAD ts check; append faces "
              "zero-loss containment PASS) -> 958cf23b5 DELIVERED incl previously-undelivered r655 P2 "
              "retro; S0.5 new order GM dual ruling O-20261004-0808 receipted (W14 parking kept, "
              "G-SEG frozen path confirmed = trio finalize governance resolved, r638 fallback armed; "
              "trio NULLS exempt line per ruling text); D-19 double MATCH zero-consume; S1 48/48 "
              "(new 48th leg = fund_statements selftest via merge); S2 board 0 open; S3 gates green + "
              "trio liveness deep-check Q489/V645/D350 (+9/+11/+7 since 07:37, pids alive, r655 zero-"
              "rate = lumpy sampling artifact); S6 34 legs rc0 (dualrun streak 48, CEO faces refreshed, "
              "stale-takeover derive per STALE_MIN); S7 pin=2 no-op + watchdog + claws + attrition "
              "CLEAN + inbox zero; CODELY 43.8KB under line; ts-probe tz-suffix fullmatch pit fixed in "
              "r656 resolver (WALL_RE match semantics)").replace('"', "")
st["last_round_at"] = st["ts"] = st["updated"] = st["last_seen"] = st["clock_read"] = CLOCK
jdump(sp, st)
print("state.json round_no =", st["round_no"])

# ---------- 3) heartbeat ----------
hp = os.path.join(RB, "fleet", "machines", "bm-b.json")
h = jload(hp)
h["round_no"] = st["round_no"]
h["round_no_label"] = st["round_no_label"]
h["last_seen"] = h["ts"] = h["updated"] = h["clock_read"] = CLOCK
h["heartbeat_epoch_utc"] = EPOCH
h["current_task"] = ("FUND trio NULLS burn watch (Q489/V645/D350 of 2000 advancing, fresh line counts "
                     "+9/+11/+7 since 07:37, dup_k=0, pids 34396/57116/30208 alive; finalize fires on "
                     "mechanical_ready, window 10-05..10-09; G-SEG governance RESOLVED by GM dual "
                     "ruling O-20261004-0808 ruling-2, r638 fallback armed) + r656: dead r655 merge "
                     "estate adopted, dual-wave 958cf23b5 DELIVERED (incl r655 P2 retro first "
                     "delivery), S6 34 legs rc0")
h["verdict"] = ("GREEN (smoke 48/48; GM order O-20261004-0808 receipted; D-19 double MATCH "
                "zero-consume; WM red=false; engine alive rc0 idle; dualrun ZERO-DRIFT streak 48; "
                "S6 34 legs rc0; attrition CLEAN; trio burns healthy advancing with pids alive; "
                "merge estate adopted and DELIVERED ahead=0 behind=0; zero cloud token)")
ack = h.setdefault("orders_ack", [])
new_order = "O-20261004-0808-bm-a.md"
if new_order not in ack:
    ack.append(new_order)
try:
    import psutil
    vm = psutil.virtual_memory()
    h["free_ram_gb"] = h["idle_ram_gb"] = h["ram_free_gb"] = h["ram_avail_gb"] = round(vm.available / 1e9, 2)
    h["total_ram_gb"] = h["ram_gb"] = round(vm.total / 1e9, 2)
    h["cpu_util_pct"] = psutil.cpu_percent(interval=0.5)
except Exception:
    pass
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=10,
                       creationflags=0x08000000)
    mib = int((r.stdout or "").strip().splitlines()[0])
    h["gpu_idle_vram_gb"] = h["gpu_free_vram_gb"] = round(mib / 1024.0, 2)
    h["gpu_idle_vram_mb"] = h["gpu_free_vram_mb"] = mib
    h["gpu_vram_free"] = mib
    h["gpu_free_vram_mib"] = mib
except Exception:
    pass
jdump(hp, h)
back = jload(hp)
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in back["clock_read"], "clock not T-separated"
assert "O-20261004-0808-bm-a.md" in back["orders_ack"], "order ack missing"
print("heartbeat updated; epoch int + clock T + order-ack verified")
