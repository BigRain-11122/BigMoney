"""r496 bm-c S7-close writer: round-report close row append (r679 idempotence
gate) + state final touch-up (verify/did tails + close timestamps). Zero
console CJK, reparse self-proof after edit."""
import datetime
import json
import os
import re

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
RR = "round_reports-bm-c.md"
ST = "state-bm-c.json"
NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
TS_SP = NOW.strftime("%Y-%m-%d %H:%M:%S")


def fail(msg):
    print("ABORT:", msg)
    raise SystemExit(1)


CLOSE_ROW = (
    TS + "｜r496 bm-c S7-close｜本地未达 origin commit 数=0（DELIVERED：round commit e9e78d655→push#1 被拒"
    "〔bm-a r695/r696 三连波在途：r694-i 认领门落地 Tools/autofill.py+MSG-2105/2110+两轮 17/31 UU merge〕"
    "→merge origin 19f0eb75f 31-UU S6 再生面族逐面解〔23 theirs〔bm-a S6 20:50-51 较新〕+attrition ours 20:56:46"
    "+daily_scorecard tie-ours+token side_pick=0→整面新鲜度 theirs〔r466 回退腿〕+x2 行级 union keep-first"
    "+md/js twins 四面 twin-locked·receipt _r496bmc_merge_resolve.json〕"
    "→push#2 push_verify DELIVERED tip 19f0eb75f ahead=0/behind=0·零强推零 --no-verify）｜"
    "N2 收口终态：池面 merge 后复核=entry done 20:54:57+own shard done owner=bm-c+sibling ready owner=bm-b "
    "keepalive 20:54:14 新鲜保留（r474 per-face newer-wins 兑现）；bm-a MSG-2105 回执=bm-b MSG-2025 三请求全自闭环"
    "（其 20:14:17 烧录 n=954 与本机 20:45:29 n=954 双机确定性互证·其产品 20:29:27 已按让渡定谳退役未推=origin 缺席实证"
    "·本机 canonical 无争议）+r694① one-tick claim gate 已落码 origin（三例复发面根治·selftest S15r/S15r2 ALL PASS）；"
    "bm-c 零新义务｜S0.5 收尾双扫：dual MATCH+0 未回执+自有 MSG-2100 留置 inbox（他机消费面）"
    "+MSG-2105 消费入 processed+MSG-2110（bma→bmb 直达·非本机面）留置｜"
    "在册面行删除类=0（MSG-2105 rename 入 processed=移动模式白名单·无清扫无 quarantine·登记册零命中断言=不适用〔无清扫动作〕）｜"
    "轮产品计分：2（candidates 954 能用实物+翻面收口+S6 38 面再生）"
)

VERIFY_TAIL_NEW = (
    "close: push#1 rejected (bm-a r695/r696 wave) -> close merge 19f0eb75f 31-UU resolve "
    "(receipt _r496bmc_merge_resolve.json) -> push_verify DELIVERED tip 19f0eb75f ahead=0; "
    "post-merge pool recheck entry+own-shard done intact, sibling keepalive 20:54:14 preserved (r474); "
    "S0.5 close rescan dual MATCH 0 unacked; MSG-2105 consumed (bm-a self-closure, zero bm-c obligation); "
    "MSG-2110 (bma->bmb direct) left in inbox."
)

DID_TAIL_NEW = (
    "(7) S7: quartet 4/4 + attrition CLEAN + round commit e9e78d655 + close merge 19f0eb75f "
    "(31 UU per-face ts newer-wins + token r466 fallback + x2 line-union, receipt) + push_verify "
    "DELIVERED + S0.5 close rescan dual MATCH + MSG-2105 consumed (bm-a three-request self-closure: "
    "their burn n=954 == mine n=954 cross-machine determinism proof, their product retired unpushed "
    "per yield continuity = origin-absent verified; r694-i one-tick claim gate landed in Tools/autofill.py at origin)."
)


def rr_append():
    raw = open(RR, "rb").read()
    if b"r496 bm-c S7-close" in raw:
        fail("close-row marker already present (r679 gate)")
    eol = b"\r\n" if raw[-5000:].count(b"\r\n") > 0 else b"\n"
    with open(RR, "ab") as f:
        f.write(CLOSE_ROW.encode("utf-8"))
        f.write(eol)
    back = open(RR, "rb").read()
    if back.count(b"r496 bm-c S7-close") != 1:
        fail("close-row marker count != 1 after append")
    print("RR_CLOSE_ROW_OK marker=1 ts=" + TS)


def st_touchup():
    text = open(ST, encoding="utf-8", newline="").read()
    json.loads(text)
    old_v = "close: push_verify DELIVERED (see close row)."
    if text.count(old_v) != 1:
        fail("state verify tail needle count=%d" % text.count(old_v))
    text = text.replace(old_v, VERIFY_TAIL_NEW)
    old_d = "(7) S7: quartet + attrition + round commit/push per close row."
    if text.count(old_d) != 1:
        fail("state did tail needle count=%d" % text.count(old_d))
    text = text.replace(old_d, DID_TAIL_NEW)
    for k, v in (("last_ts", TS_SP), ("last_seen", TS), ("updated", TS),
                 ("updated_at", TS), ("clock_read", TS), ("last_round_at", TS)):
        pat = re.compile(r'^(\s*)"%s": (.*?)(,?)$' % k, re.M)
        hits = pat.findall(text)
        if len(hits) != 1:
            fail("state key %s hits=%d" % (k, len(hits)))
        vv = json.dumps(v, ensure_ascii=False)
        text = pat.sub(lambda m: "%s\"%s\": %s%s" % (m.group(1), k, vv, m.group(3)), text, count=1)
    doc = json.loads(text)
    assert isinstance(doc["heartbeat_epoch_utc"], int)
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$", doc["clock_read"])
    open(ST, "wb").write(text.encode("utf-8"))
    print("ST_TOUCHUP_OK clock=" + TS)


if __name__ == "__main__":
    rr_append()
    st_touchup()
    print("S7_CLOSE_WRITE_DONE")
