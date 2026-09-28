# r415 bm-a: insert 5x HANDOVER recon line (window R411-415) at quote-block head.
import io

P = "research/HANDOVER.md"
b = open(P, "rb").read()
anchor = "> bm-a round 410 五倍数核对".encode("utf-8")
assert b.count(anchor) == 1, "anchor not unique"
key = "> bm-a round 415 五倍数核对".encode("utf-8")
assert key not in b, "r415 recon already present"

text = (
    "> bm-a round 415 五倍数核对（2026-09-29 05:2x）：增量窗 R411-415=bm-a 面（**W5 收官后维护窗"
    "+D-02② 切片 fetch 律立法+r412 台账迁移三线**——"
    "R411 r410 漏 5x 补做〔坑律七十九批「指针写了≠执行」〕+13-UU rebase；"
    "R412 legal-idle 维护收口+W5-JUDGE harvest 复核〔judge-finalize 面 detached bm-b〕"
    "+moneyflow advisory 陈旧修+坑律八十一批+31-UU rebase+台账行误落根目录 stray 件；"
    "R413 死窗 rebase 复活收口〔3 碰撞窗 7+18+6 UU 正典解·x2 多重集 union 1518 行〕+坑律八十三批；"
    "R414 W4 intake zero-face 补链〔n_eligible=0 lawful·vol G1 0/461 全波·r407 W5 schema 先例〕"
    "+T-97/98/114 三票关单〔W3/W4/W5 全链 verified·零注册诚实负锚〕+MSG-0515 声明；"
    "R415 D-20260929-02② 司域即行=fleet/README.md §4「切片/池批 fetch 双闸律」"
    "〔MSG 切片开工前+池 submit 前强制 git fetch 重读 inbox 面·见 rival 声明即冻结〕"
    "+§9 v1.1 版注+r412 台账行迁回正典 logs 面〔stray 根件移除·行内容 verbatim 保全·CRLF 保形〕"
    "）+统一链 328,615 实读线性〔w5_screen.json trials_ledger.total·W6 generate bm-b 在飞未落零新行〕"
    "+池 108 条〔共享==车道双谳〕"
    "+产物 9/9 磁盘在位〔w5_screen.json+cells/w4_intake.json/trial_labor_w6.py/W6 prereg/V3 tournament runner/"
    "GKM digest/sentiment_axes fullhist/grammar ledger〕+下轮 5x=r420"
)
line = text.encode("utf-8") + b"\r\n"
out = b.replace(anchor, line + anchor, 1)
open(P, "wb").write(out)

v = open(P, "rb").read()
assert v.count(key) == 1 and v.count(anchor) == 1
assert v.count(b"\r\n") == b.count(b"\r\n") + 1
print("inserted bytes", len(b), "->", len(v))
