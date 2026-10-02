# -*- coding: utf-8 -*-
"""r578 bm-b S7 close: round report line + CODELY memory + state + heartbeat."""
import json
import os
import time
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_EPOCH = int(time.time())
NOW_SHORT = NOW.strftime("%Y-%m-%dT%H:%M") + "+08:00"


def append_bytes(path, text):
    with open(path, "ab") as f:
        f.write(text.encode("utf-8"))


# --- 1. round report line (bm-b file per fleet README sec.6) ---
REPORT = (
    NOW_SHORT + " | r578 | dept:研究/工程 | watermark verdict=绿：red=false"
    "（probe insufficient_history=引擎暂停窗采样史污染·诚实如实；引擎现活 W91 烧录在飞="
    "机器唯一闸门在役非违令）；做了：①r529 猝死诊断收养=W89 冻结五面遗产"
    "（state 停 576+git 自标 r577+进程扫描零活会话=r577 死于冻结 commit 前·引擎已从"
    "工作树自燃 7 片）→构造式预合并 origin W88（r531 律·theirs-first 同锚·+W89 "
    "selftest print 片段补全=W50 +48 最小披露先例）→carry commit→rebase 同锚冲突="
    "checkout --theirs（=carry=预验证合并件）→r501 假拒绝净路→27a8d9712 送达 "
    "origin（+721 行纯增量守恒=237+289+28 全对账）②W89 12/12 烧毕（shard-11 随 "
    "ride 送达）③W91 席位公示 MSG-20261002-1425-bmb 先推 origin（r565 "
    "early-visibility）→gate ADMIT results/_r578bmb_w91_band_gate.py rc0 三态"
    "（A 225_004..227_003 skip-past-W90-published 链+B 56_501..56_700 "
    "D-20261002-05 钉死于 SEED_REGISTRY p4_batch3_dca=56_500 带内中位 99/199）"
    "→W91 FREEZE 五面+print 片段（生成器 _r578bmb_w91_freeze_edits.py·r560 律锚定"
    "插入+锚后守卫）→a0d6d8287 送达·引擎自燃 W91（shard-0 冻结 commit 后 1 tick "
    "落盘=点火活证据 r325 律）④orders 零差集（143/143 全扫差集法）⑤D-19 水位 "
    "MATCH-unchanged 零动作（937A373D）；验证=smoke 47/47+selftest W2..W91 全链 "
    "PASS（缺省波调用 r522 律）+banned gate W91 ADMIT rc0+S6 32 步全 rc0"
    "（dualrun 排 audit 前·audit CLEAN·attrition CLEAN·假日无新 bar 合法 no-op 面"
    "·bm-b 车道面 astock/etf/rev_osc/minute_feed rc0）+push 送达 fetch+ls-tree 复核；"
    "最近实物=W91 冻结包（a0d6d8287·五面）+W89 12/12 分片（27a8d9712）；"
    "下个里程碑=W91 12/12 烧毕（~15:00）→W88 bm-c 落账后 W89/W90/W91 finalize "
    "链序续落（窗 ≤48h）；下轮指针=W89 finalize one-pass（r538 禁重跑·前置 W88 "
    "bm-c 落账·r518 origin 时序律）+W92 席位+冻结（投影 A 227_004..229_003/B "
    "56_701..56_900 双 CLEAN·下波冻结方必复核非转抄）；本地未达 origin commit 数=0"
    "（push 后 fetch 复核）。\n"
)
append_bytes(os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md"), REPORT)

# --- 2. CODELY.md memory line (S4; one entry, lesson-first) ---
MEM = (
    "- [2026-10-02 14:5x r578 bm-b] 猝死会话冻结遗产收养判例（W89 实弹·r529+r471 "
    "族执行序钉死）：引擎 tick 架构下未 commit 的冻结五面=活供（引擎已从工作树自燃"
    "烧录）——收养六步序=①r529 三面诊断（state 停轮+git 自标轮+进程扫描零活会话）"
    "②构造式预合并 origin 平行波（r531 律·内容锚定·合并件先过 AST+selftest 三证才 "
    "carry commit）③rebase 同锚冲突=checkout --theirs（=carry=预验证合并件·零 "
    "frankenstein 面）④pool jsonl=stage 三方 union（:2: verbatim 底+:3: 尾行去重·"
    "r294/r570 域律）⑤收养窗 materializer 腿断言「per-wave prereg 在场」必红——"
    "origin 侧他机新 prereg 未在本地树→先 git checkout origin/main -- <prereg> "
    "携带（恒等 blob=replay 空 pick skip 合法·r519 先例）⑥五面合同含 PASS-print "
    "描述面：猝死会话漏 W89 print 片段（腿全绿而描述缺·ADMIT/selftest 皆不拦）→"
    "收养按 W50 +48 最小披露先例补全；W91 起冻结生成器内置 print 片段=教训落地"
    "（_r578bmb_w91_freeze_edits.py 五段一体）。How to apply：未来一切猝死冻结收养"
    "照此六步序；五面核验清单必含 print 片段面；手术窗先 schtasks /disable 引擎+"
    "autofill tick（防 appender 劫持 rebase r312 族+冲突标记窗破坏 runner import "
    "r519 族）毕即 re-enable。\n"
)
append_bytes(os.path.join(ROOT, "CODELY.md"), MEM)

# --- 3. state.json (round_no 576 -> 578, skip dead r577 self-label per r529) ---
sp = os.path.join(ROOT, "state.json")
with open(sp, "rb") as f:
    st = json.loads(f.read().decode("utf-8"))
st["round_no"] = 578
st["note"] = (
    "r578: r577 sudden-death estate adoption -- W89 freeze five-face carried+landed "
    "27a8d9712 after constructive merge with origin W88 (r531 law; +W89 print "
    "fragment filled per W50 +48 precedent); W89 12/12 burned, finalize pending "
    "W88 bm-c chain (r518 origin-time-order law); W91 seat MSG-20261002-1425-bmb "
    "pushed first (r565) + W91 FREEZE five-face landed a0d6d8287 (80th engine "
    "wave, bm-b 30th owned; A 225_004..227_003 skip-past-W90-published + B "
    "56_501..56_700 D-20261002-05 pin at p4_batch3_dca=56_500 median 99/199); "
    "engine self-ignited W91 post-freeze (shard-0 within 1 tick, r325 proof); "
    "S6 32-step chain all-green holiday no-ops; orders zero-delta 143/143; D-19 "
    "MATCH-unchanged; next = W91 12/12 burn + W89/W91 finalize after W88 lands"
)
st["last_round_at"] = NOW_EPOCH
st["last_round_ts"] = NOW_ISO
st["ts"] = NOW_ISO
st["updated"] = ("r578 bm-b: W89 estate adoption landed + W91 freeze+ignition "
                 "(80th wave) + S6 all-green")
st["updated_at"] = NOW_ISO
st["last_decisions_at"] = NOW_ISO
with open(sp, "wb") as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1).encode("utf-8"))

# --- 4. heartbeat fleet/machines/bm-b.json ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
with open(hp, "rb") as f:
    hb = json.loads(f.read().decode("utf-8"))
try:
    import psutil
    ram = psutil.virtual_memory()
    free_ram = round(ram.available / (1024 ** 3), 1)
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
    cores = psutil.cpu_count(logical=True)
except Exception:
    free_ram, cpu_pct, cores = hb.get("free_ram_gb"), hb.get("cpu_util_pct"), hb.get("cpu_cores")
hb["last_seen"] = NOW_ISO
hb["heartbeat_epoch_utc"] = int(NOW_EPOCH)  # JSON int type per R170/R178 law
hb["clock_read"] = NOW_ISO  # T-separated per R262 law
hb["current_task"] = ("W91 engine burn in flight (tick self-ignited post-freeze); "
                      "W89 12/12 burned finalize pending W88 bm-c; r577 estate "
                      "adopted + W91 freeze landed")
hb["round_no"] = 578
hb["round_no_label"] = "r578"
hb["verdict"] = ("healthy-burning (W91 engine lane self-ignited post-freeze; "
                 "W89 estate adopted+landed 27a8d9712; D-19 unchanged)")
hb["cpu_cores"] = cores
hb["free_ram_gb"] = free_ram
hb["idle_ram_gb"] = free_ram
hb["ram_free_gb"] = free_ram
hb["cpu_util_pct"] = cpu_pct
with open(hp, "wb") as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1).encode("utf-8"))

# post-write self-verify (smoke F7 contract): epoch int + T clock
with open(hp, "rb") as f:
    chk = json.loads(f.read().decode("utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read T-format"
print("S7 close OK: report+memory+state(578)+heartbeat; epoch int verified")
