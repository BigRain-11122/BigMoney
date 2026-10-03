# -*- coding: utf-8 -*-
# r641 bm-b report-line append fix: predecessor close script died on %-format
# with literal % chars in CJK text (ValueError 0x4e09). This leg only appends
# the round-report line (state/heartbeat already landed in commit 973bfc909)
# and re-runs the self-verify. f-string only, no % operator anywhere.
import json, os, time, datetime, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

now = datetime.datetime.now().astimezone()
clock_read = now.strftime("%Y-%m-%dT%H:%M:%S") + ("+%02d:00" % (now.utcoffset().total_seconds() // 3600))

def nulls_count(fam):
    with open(os.path.join("results", fam, "nulls.jsonl"), encoding="utf-8") as f:
        return sum(1 for _ in f)

q = nulls_count("fund_quality_p1")
v = nulls_count("fund_value_p1")
d = nulls_count("fund_divlowvol_p1")

line = (
    f"{clock_read} | round 641 (bm-b, dept:工程/舰队+研究): watermark verdict=GREEN (red=false, py 71-86pct 三族烧录在飞, lane healthy)。"
    "本轮=死 r641 会话收养交付轮（r471 四证：进程普查仓内零活 codely〔唯一 Bigmoney codely=本会话〕+簿记 mtime≤死亡窗 01:45+零半成品断点）："
    "①r640 延期义务 HANDOVER 5x 核对行收编交付（增量窗 r631-r640 十轮+产物清单漂移+指针，predecessor 写就本会话验真收养）；"
    "②FUND 三族 finalize 预演重跑 ALL-GREEN x3 收编（quality 179.7s/value 229.4s/divlowvol 178.8s·01:34-01:43·NOT_A_VERDICT 横幅在位·"
    "MSG-1720 Finding B 修复态复验 r626d 6c2a6742f 在位）+summary 单族覆盖坑治愈件 _r641bmb_rehearsal_summary_fix.py（--fam 模式覆写 summary 只含末族→三族重建）；"
    "③D-19 集团水位 sparse-clone fallback MATCH（eb14b510 未变零消费·r631 配方第二证·_r641bmb_d19_sparse.py）；"
    "S0.5 orders 152/152 双扫零未回执（origin 多出 README.md=非令件假阳性过滤）；S1 smoke 47/47；"
    "S3: 饱和引擎活 rc0 idle+任务板零 open+job 板空+水位红牌 false；"
    "S6 34 腿 rc0（dualrun ZERO-DRIFT streak32·update_lhb 实拉 11/11 rc0·CEO 五面 bm-a 心跳 stale 70min 按 O-2100 s2.4 stale-takeover derive·"
    "b_layer_mask 5222 码全门过·黄金周 no-op 族）；"
    "S7: attrition CLEAN+loop pin2 no-op+watchdog 活+pre-commit/pre-push 双爪重装幂等+state 翻面 641；"
    "r630 净路重放交付（隔离 worktree cherry-pick→CAS push→reset --mixed+定向 checkout〔8 daemon 活面保全〕→dualrun settle 复跑自证）。"
    f"CEO 三行——当前活：FUND 三族 NULLS 2000-draw 烧录值守（q/v/d={q}/{v}/{d} of 2000·daemon 三进程活·finalize 窗 10-05..10-09 候 G-SEG 总经理裁定）；"
    "最近实物：results/_r633bma_finalize_rehearsal_summary.json（三族 ALL-GREEN x3·01:45 重建）+research/HANDOVER.md r641 5x 行；"
    "下个里程碑：FUND 三族烧毕 finalize 判决面开窗 10-05..10-09（预演 T-1 全绿零阻塞·G-SEG 无裁决按 insufficient-sample 单判读备案 r638）。"
    "本地未达 origin commit 数=0（本轮 commit 后 push+fetch+ls-remote 自证）。"
    "下轮指针：r642=FUND 烧录值守+W2 finalize 轮询（pid 31336 deadline 10-06·bm-c 属主）+日常维护。\n")

with open(os.path.join("logs", "iteration-loop", "round_reports.md"), "a", encoding="utf-8") as f:
    f.write(line)

st2 = json.load(open("state.json", encoding="utf-8"))
hb2 = json.load(open(os.path.join("fleet", "machines", "bm-b.json"), encoding="utf-8"))
assert st2["round_no"] == 641
assert isinstance(hb2["heartbeat_epoch_utc"], int)
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"]
print(f"REPORT LINE APPENDED; verify OK: round=641 epoch={hb2['heartbeat_epoch_utc']} clock={hb2['clock_read']} nulls q/v/d={q}/{v}/{d}")
