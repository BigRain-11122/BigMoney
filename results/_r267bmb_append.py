import io

mem = ("- [2026-09-26 19:0x] 坑律（bm-b r267·S7 收尾 push 撞 bm-a 同窗 S6·r242 ts 探针族新维·E1 解后自捕）："
        "**跨机快照族冲突解的 ts 探针必须递归嵌套 dict——dashboard_status.json 的时戳藏在 health.smoke.at/meta 等二级键，"
        "顶层键族扫空=两面 tie 假读数、按 r140 tie→HEAD 律误取 base 旧面（实弹：本机 18:52 build 面更新却先取了 bm-a 18:44 面，"
        "幸为全量可再生视图+下一轮 build_status 即覆写=零持久损失，REBASE_HEAD 取回翻正）**；"
        "正律=①快照类件 ts 探针先递归展平两级再比（展平键路径做比较键）②无可辨 ts 键的快照件以生产者构建窗定性、禁默认 tie "
        "③tie 语义只适用于实证同值非探针失明。指针=results/_r267bmb_resolve.py 修正段\n")
with io.open("CODELY.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(mem)

rep = ("2026-09-26T18:58:00+08:00 | r267 addendum (bm-b) | dept:工程 | "
       "S7 closeout push collided with bm-a R263 same-window S6 run (e7e4441e 18:51:53): "
       "rebase 15-UU snapshot-family batch resolved per skill recipes (classifier 11 classified + 4 manual: "
       "autofill launches union-cap50-asc 50+50->50 last_tick ours 18:50:01; compute_audit history union 201u201=202 zero-loss; "
       "regime/sc scorecards/token/status/report-pair take-new ours 18:49-51 vs base 18:44; "
       "dashboard pair first-pass tie->base was probe-blind misread, re-resolved take-ours via REBASE_HEAD after nested-ts lesson -> CODELY.md line) "
       "+ T-83 claim collision CONFIRMED resolved per s4 law: bm-a 18:47:11 yielded to bm-b 18:46:30, "
       "L9 orders index donation results/orders_index.json (83 orders/33 real cross-refs) received as s2 input, "
       "supersession adjudication stays GM s3; resolver archived results/_r267bmb_resolve.py; "
       "DDCTL batch landed+judged negative by bm-a (pool 48/48 done, no harvest face for bm-b); all pushes green\n")
with io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(rep)
print("appended both")
