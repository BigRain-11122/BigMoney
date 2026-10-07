# -*- coding: utf-8 -*-
"""r850 bm-a round-report dual-write: ROOT canonical (GBK face, r844 law) adopts the
r849 line verbatim + appends r850; LOGS face (UTF-8, loop-lineage) appends r850.
GBK-safety: U+2212 and other non-GBK chars substituted for the ROOT face only."""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LINE850 = ("2026-10-08T00:30+08:00 | r850 bm-a (dept:research) | watermark verdict: green "
           "(red=false lane=healthy; engine idle queue0 W179 closed this round) | 当前活: "
           "W179 finalize one-pass landed (ledger head 799,705 / K 391,720 / prereg §7-§8 "
           "machine backfilled; engine chain caught up) | 最近实物: "
           "results/perpetual_faces/n1_w179_results.json + research/PERPETUAL_N1_W179_PREREG.md "
           "§7/§8 回填 @2026-10-08T00:0x (origin 9eb89503a) | 下个里程碑: 10-08 复市首交易日 "
           "15:30 后数据链全门 re-arm 首采+REGIME_GUARD v3 新bar enforce 激活（窗≤今日收盘）; "
           "W180 seat chain next round | did: S0 三连推送竞态正典解（r849 死尾 staged 收养 r752 "
           "三闸 + churn-absorb r642 律 + 17-UU rebase 停窗=merge_lane_views resolve x6 + twins "
           "深扫ts x6 + CODELY origin mini-split面+r849条目追加 + snapshot 取新 x4 + r835 三步假冲突"
           "逃生〔ls-files -u 空第三态·E42 家族〕+ leg2 cherry-pick 残余收口）+ S0.5 orders 51/51 "
           "双扫零未回执 + DEC 水位 771c3a8d→ee659451 同轮消费（10-08 00:09 晨会批 D-20261008-01~04·"
           "零 BigMoney 派工行·ORD 2bb2ee75 恒等零动作）+ S1 smoke 48/48 + S3 主产出=W179 preflight "
           "三闸 GREEN_FINALIZE_READY（半开 r846 血统·Gate1 A2000/B200/nbt2200 恒等·Gate2 seed sweep "
           "EXACT 408604..410603+410604..410803·Gate3 半开铺贴零缝）→ finalize one-pass（pit-95 "
           "防重落账守卫过·ledger 797,505+2,200=799,705 EXACT·K=391,720 EXACT·skill_line 1.1851→1.1850 "
           "K-lift -0.0001·SS5 四预键全过 d1=0.000491/d2=-0.0074%/d3=-0.0010/d4=-0.0001）→ §7/§8 "
           "机械回填（r587 零转抄·CRLF 保形·r773 残段扫描净）→ pf 9/9 + n1 selftest 双绿（W179 mat 腿 "
           "169th wave/95th bm-a owned/39th staircase E36）+ S6 38/38 rc0（dualrun ZERO-DRIFT streak "
           "51@406·复市前全门诚实 no-op cutoff 09-30·REPORT/LIVE-20261008 双面产·token L2 0）+ S7 "
           "quartet 绿（pin=8 no-op·watchdog 00:16 首发·双爪 LF 归一·attrition CLEAN 4件·idle_trigger "
           "--worked idle_rounds=0）+ HANDOVER r850 5x 块（本机 5 倍数轮）+ 轮账本分叉发现如实披露"
           "（ROOT=正典 r844 律·LOGS 面带 r841/r849 行·r849 行本轮收养回 ROOT·双写止增·union-heal "
           "坑已入 r844 队列） | scoring: 2（W179 finalize 能跑/能看/能用实物=链头推进+结果件+prereg "
           "回填）| 记账预算: 4/5（state+轮账行+心跳+HANDOVER 5x）| 宝藏捕获问: 本批零新方法零新宝藏"
           "（preflight/finalize/backfill=r846/r839 血统既有律 verbatim 复用·TREASURE/METHODOLOGY 零 "
           "append·登记簿未触发零清扫动作）| 本地未达 origin commit 数=0（push 9eb89503a 后 "
           "fetch+rev-list 双向 0 自证）| 孤儿面=1（round-zero 探针只读·ComfyUI idle server CEO 属主"
           "免杀档）| next-round pointer: r851=W180 seat chain（post-W179 宇宙重 derive 强制·naive A "
           "410_604..412_603 阶梯第40例预期/naive B 410_804..411_003 W141 leg2）+10-08 15:30 复市数据链 "
           "re-arm+OSS ledger S3/S4/S5 扫描窗 10-09+O-1850 VL 共居 3 读数+CEO 令执行件推进（P-audit "
           "10-12/R-research+REGIME-5 10-14） | [r850 bm-a]")


def gbk_safe(s):
    out = []
    bad = []
    for ch in s:
        try:
            ch.encode("gbk")
            out.append(ch)
        except UnicodeEncodeError:
            bad.append(hex(ord(ch)))
            out.append("-")
    if bad:
        print("GBK substitutions:", set(bad))
    return "".join(out)


# --- ROOT canonical (GBK face): adopt r849 + append r850 ---
r849 = None
for l in open("logs/iteration-loop/round_reports-bm-a.md", encoding="utf-8", errors="replace"):
    if l.startswith("2026-10-07T23:51:32"):
        r849 = l.rstrip("\n")
assert r849, "r849 line not found in LOGS face"

raw = open("round_reports-bm-a.md", encoding="gbk", errors="replace", newline="").read()
assert "r849 bm-a" not in raw, "r849 already in ROOT"
crlf = raw.count("\r\n") > 100
nl = "\r\n" if crlf else "\n"
add = nl.join(["", gbk_safe(r849), gbk_safe(LINE850)]) + nl
with open("round_reports-bm-a.md", "a", encoding="gbk", errors="replace", newline="") as f:
    f.write(add)
print("ROOT: r849 adopted + r850 appended (gbk face, crlf=%s)" % crlf)

# --- LOGS face (UTF-8): append r850 verbatim ---
raw2 = open("logs/iteration-loop/round_reports-bm-a.md", encoding="utf-8", errors="replace", newline="").read()
nl2 = "\r\n" if raw2.count("\r\n") > 100 else "\n"
pre = nl2 if raw2.endswith(nl2) else nl2 * 2
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="") as f:
    f.write(pre + LINE850 + nl2)
print("LOGS: r850 appended (utf-8 face, crlf=%s)" % (nl2 == "\r\n"))
