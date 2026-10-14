"""r1019 closeout: append round report row (UTF-8, anchor-guarded)."""
import io

row = ("\n| 2026-10-15 07:0x | r1019 | D-20261015-02 bm-c leg 收尾（集团派工·48h 窗提前）："
       "腿正身 commit 5b174a247（7 own-face untrack）前窗已落，本窗补齐三件="
       ".gitignore history_bm-*.jsonl generic 补口 + selftest_bm-c.py 6/6 PASS"
       "（canon 23/23 + own 7 面 untracked+ignored+on-disk + legacy autofill_state.json 仍 tracked 冻结"
       " + union fallback + live merge bm-c alive）+ live_probe_bm-c.txt 留痕（7/7 mtime 新鲜 07:00-07:01=daemon 活写）"
       " → F-20261014-01 行 bm-c 腿 executed 注记 + 水位键 B73658E6 更新；"
       "ORD/DEC 双扫：ORD ALL-ACKED、DEC CHANGED→D-20261015-01/02 全消费（D-02 涉本仓派工即本案）"
       " | selftest 6/6 rc0 + live probe 件 + smoke 49/49 + dualrun streak 51 + 引擎 ALIVE alive_flag=True "
       "+ S6 链全 rc0（ORANGE_COOL 幂等·collectors 全 no-op 诚实·REPORT/LIVE-2026-10-15 落盘·RAM 1.3G 闸如实） "
       "| 下轮：W244 finalize 落 bm-a 链→W245 席位；10-15 15:30 后 bars→papers 全链再跑 "
       "| watermark=py_low_board_clear（板空+池 0+无 cands=合法闲·池饿旗如实=供给链合法锚定 W244 finalize 上游 bm-a 席）；"
       "孤儿面=2（只读）；本地未达 origin commit 数=0 |")

p = "round_reports-bm-c.md"
txt = io.open(p, encoding="utf-8").read()
anchor = "| 下轮：W244 splice/burn/finalize 盯守；15:30 后 bars→papers 全链"
if "r1019" in txt and "D-20261015-02 bm-c leg 收尾" in txt:
    print("row already present, skip")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(txt.rstrip("\n") + row + "\n")
    print("row appended, tail:")
    print(io.open(p, encoding="utf-8").read()[-200:])
