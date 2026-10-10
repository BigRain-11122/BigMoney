# -*- coding: utf-8 -*-
"""r957 bm-a closeout: r956 gap line + r957 round line + state + heartbeat."""
import json, io, datetime, time

NOW = datetime.datetime.now()
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
RR = r"round_reports-bm-a.md"
ST = r"state-bm-a.json"
HB = r"fleet\machines\bm-a.json"
NL = "\r\n"

src = io.open(RR, encoding="utf-8", newline="").read()
assert "r957 |" not in src, "r957 line already present"

if " | r956 | " not in src:
    gap = ("2026-10-10T19:0x+08:00 | r956 | bm-a | "
           "dept:工程（W17 shard handover bm-c->bm-a per O-20261010-1825 sec.1 "
           "〔8 screen+judge·claim-by-file+pool owner transfer·zero-product+stale-heartbeat "
           "证据链〕+fleet MSG-1900 广播）| session 死于 push 前的 rebase 中途态"
           "（crash_fuse.json UU 遗留）·r957 轮收口（本轮报告承接其全链） | "
           "本地未达 origin commit 数=0（r957 收口后自证） | [r956 bm-a]")
    src += gap + NL

r957 = (
    "2026-10-10T" + NOW.strftime("%H:%M") + ":xx+08:00 | r957 | bm-a | "
    "dept:研究/工程（r956 死态收口+W17 让渡竞速三环+O-1906 双点裁决+W17 fuse 手术+SHARD-0 点火） | "
    "WM-VERDICT: green (red=false; S0 接手 r956 rebase 中途 crash_fuse UU→skill 正典 "
    "merge_lane_views resolve 88 sigs union newer-wins；W17 handover 与 bm-c autofill "
    "keepalive tick 三环竞速→union 如实 newer-wins 判 bm-c→按 O-1825 sec.1 让渡令+证据链 "
    "同窗 owner 终态重申 bm-a 9 分片〔_r956bma_w17_reassert.py 外科律〕→push 0/0) | "
    "孤儿面=0 (round-zero orphan_face_probe 只读在飞前段已跑) | "
    "S0.5: O-20261010-1906-bm-c 裁决请求处理完毕（见 S3）+O-1825 执法=分片接收点火 | "
    "S3: ①O-1906 裁决=W139 94_500/W140 94_700 SEED_REGISTRY adjudication "
    "〔r874 镜像+修正论证：请求方假设 spawn-children-only 不实——实测 thermo L283 "
    "default_rng(94500+i) 本体消费=与引擎 L7729 同族同流双消费，无害论证=disjoint "
    "injection faces〔温度计相位 null vs 因子 cell 出场轴两数据面永不相交〕；lhb L267 "
    "random.Random=MT19937 vs 引擎 PCG64 跨 RNG 族=流全异更强隔离〕→ pf 9/9 + n1 "
    "selftest 双绿〔4 in-section carve-outs+ADJUDICATED EXCEPTION 5/6 披露〕→commit "
    "7464be852 + MSG-2026-10-10-1940 回执 bm-c=W204 五面冻结链解锁；②pool EOL 治愈"
    "〔merge_lane_views resolve 写 LF 违 r223/r234 CRLF 生产者镜像律→pf selftest 抓 "
    "EOL face drifted→16599 行全 CRLF 复原→9/9 过〕；③W17 fuse 手术=8 screen sigs "
    "count=1 全系 r791 RAM-gate 40min cap 到期自杀〔12:48-15:42 阶梯=bm-c 复燃时刻 "
    "错开〕非代码缺陷〔KeyError('faces') bm-c r829 已修 selftest 21/21+worker-probe "
    "173/173〕→三面 cleared-tombstone〔共享+bm-a+bm-c lane·reason 如实·新 crash 新 "
    "ts 打败墓碑=保护闭环〕→autofill tick verdict=launched **SHARD-0 IGNITED pid "
    "50996**〔multiproc/BelowNormal/池饿 2219min 首燃〕·1-7 号随 2min tick 序列起燃 | "
    "S6: 核心腿 pool_dualrun/compute_audit/py_watermark/update_daily/daily_scorecard "
    "全 rc0（周六 no-op 快通道；长链余腿由后续 tick/轮补齐） | "
    "S7: 竞速 push 三环全绿 4c65f0654..72a1f876e 0/0 对齐 | "
    "验证: pf selftest 9/9 + n1 selftest PASS + fuse reconcile ZERO-DRIFT + "
    "SHARD-0 pid 50996 进程实证 + push 0/0 自证 | "
    "最近实物: scripts/perpetual_faces.py+n1 W139/W140 adjudication（7464be852）+"
    "W17 screen 烧批在飞〔checkpoint 本机落盘中〕 | "
    "下轮指针: W17 1-7 号起燃盯梢（autofill tick 逐发）→checkpoint 推进→"
    "screen-finalize+judge 链〔machine-local CKPT_DIR r429〕→O-1906 bm-c 复燃 W204 "
    "phase-2 回执窗 | "
    "本轮产品积分:4（W17 8 分片接管+SHARD-0 点火=能跑实物 2+O-1906 裁决双 selftest "
    "绿机制件 2） | 记账预算:4（state+心跳+轮报告+idle） | "
    "方法论捕获: crash fuse 宿主面误伤判例〔r791 RAM cap 到期自杀≠代码缺陷——fuse "
    "code_sha256 匹配跨宿主熔断=宿主资源面 crash 挡死健康宿主；解法=cleared-tombstone "
    "reason 如实+三面清+新 crash 打败墓碑保护闭环〕 | 宝藏捕获:无 | "
    "本地未达 origin commit 数=0（收口 push+fetch+rev-list 自证） | [r957 bm-a]"
)
src += r957 + NL
io.open(RR, "w", encoding="utf-8", newline="").write(src)
print("round report: r956 gap + r957 landed,", len(src), "bytes")

s = json.load(io.open(ST, encoding="utf-8"))
s["round_no"] = 957
s["current"] = "r957 closeout done"
s["current_task"] = "W17 screen shards 1-7 ignition watch (SHARD-0 burning pid 50996)"
s["last_action"] = "O-1906 adjudication + W17 fuse surgery + SHARD-0 ignite"
s["clock_read"] = ISO
io.open(ST, "w", encoding="utf-8", newline="").write(
    json.dumps(s, indent=1, ensure_ascii=False))
print("state round_no -> 957")

m = json.load(io.open(HB, encoding="utf-8"))
ack = m.setdefault("orders_ack", [])
for o in ["O-20261010-1906-bm-c.md"]:
    if o not in ack:
        ack.append(o)
m["last_seen"] = ISO
m["ts"] = ISO
m["clock_read"] = ISO
m["heartbeat_epoch_utc"] = EPOCH
m["current"] = "W17 screen 1-7 ignition watch; SHARD-0 burning"
m["current_task"] = "W17 screen shards burn (O-1825 sec.1 takeover complete)"
m["verdict"] = ("green (r957: O-1906 W139/W140 adjudicated 7464be852 double-selftest-green "
                "=W204 chain unblocked; W17 9 shards owner terminal bm-a + fuse surgery "
                "3-face tombstones; SHARD-0 IGNITED pid 50996; pool_empty_or_busy per-tick "
                "single-launch normal)")
m["idle_rounds"] = 0
m["agenda_starved"] = False
io.open(HB, "w", encoding="utf-8", newline="").write(
    json.dumps(m, indent=1, ensure_ascii=False))
chk = json.load(io.open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
print("heartbeat updated; ack count:", len(chk["orders_ack"]),
      "epoch int ok:", chk["heartbeat_epoch_utc"])
