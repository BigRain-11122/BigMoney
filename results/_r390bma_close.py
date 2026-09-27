# -*- coding: utf-8 -*-
"""r390 bm-a round-report append + state round_no 390 (binary-face CRLF)."""
import json

RR = "logs/iteration-loop/round_reports-bm-a.md"
ST = "state-bm-a.json"

LINE = (
    "2026-09-28T07:5x:00+08:00 | R390 bm-a (dept:工程+舰队·D-03(2) 墓碑根修轮+5x HANDOVER 核对轮) | "
    "WM first-line verdict: green (red=false lane healthy; probe 07:26 py_low_board_clear legal-idle: "
    "board 0 open / bandit 0 / pool non-done 8 全 bm-b 车道或门后〔W2B bm-b 燃中 ETA ~10:30+DECISION-CHAIN-V2-P1 ready lane bm-b"
    "+MASS judge x4+W1-JUDGE+W2-JUDGE 全 bm-b declare/RAM 门 frozen sec.9.1 串行〕; audit v2.3 07:26 CLEAN flags=[] py 0.8% load_state pool-supply-gap) | "
    "did: S0-1 锚定 bm-a + S0 clean pull Already-up-to-date（零 UU·S7 复扫在收尾）+ untracked dup 备份件在位（w2_candidates.json.live-bma-dup·r385 留档面零触碰）+ "
    "S0.5 orders 99/99 差集零未回执 + decisions 新行核验：D-20260928-04/05=FluxVerse 域非本仓零动作、D-20260928-06=委员会件 C-20260927-02 补登·席3 意见已在册 F-20260928-01/02（先于补登行落账）+防漏收指针行 F-20260928-02 在册·过会前各司零执行维持·零新动作 + "
    "inbox MSG-0725 (bmb→bma+bmc+ALL) 收讫处理：W2-JUDGE judge-prep 门 2/3 已过（manifest 48 员/census 双轴恒等/survivors 404 非空）·RAM 门 hold=census W2B 燃中实测 1600/5620 ETA ~10:30·flip executor=bm-b·本机 watch 面零动作 + "
    "S1 smoke 25/25（改动后复跑 25/25 零回归）+ S2 双板零开（job_list empty；fleet tasks 96 文件 0 open）+ "
    "S3 主闭环一=D-03(2) cleared-tombstone 设计片落地（r389 漂移族根修·本机 autofill 正典域）：scripts/merge_lane_views.py merge_crash_fuse 墓碑语义〔cleared 键并集 cleared_ts newer-wins+sigs 并集后墓碑过滤（cleared_ts>sig 末事件 ts→抑制他机车道复活）+新代码再崩胜墓碑存活+cleared 键仅非空时附加=零墓碑面 merged==shared 结构恒等〕+Tools/autofill.py 清除点（码变 fix 检测）del 前落墓碑（cleared_ts/cleared_by/reason/crashes/old_code_sha256）双轨写共享+本机车道+任何机清除对全体生效（码变=git 树全局事实 owner 门不适用）+门读 _load_fuse_gate 继承合并视图=门面同步抑制 + "
    "S3 主闭环二=5x HANDOVER 核对（R386-390 增量窗行落 research/HANDOVER.md 头部·统一链 297,428 实读〔live head=trial_labor_w2/w2_screen.json trials_ledger.total·与 R389 同谳〕·池 91 条〔83 done+8 non-done 合并视图实读〕·当窗实弹自坑：行插入 replace 锚用行首片段=新行与锚行残尾同线缝合吞行首（git diff 权威核验 1 insertion 0 deletions 证非外科→接缝拆分回植行首修复+行首前缀枚举复验→坑律入册 CODELY r390）+ "
    "S4 CODELY 新坑律 r390（行插入 replace 整行锚定律）append 后 10,865B 超 ≤10KB 硬线→当窗整编三十四批（r141/r142 两条最老坑律 verbatim 外迁 archive 202609.md〔行级零丢失校验 containment PASS〕+三十四批指针行·热层 8,965B 达标）+ "
    "S6 全链 30+ 腿全 rc=0 周一盘前 no-op 家族零掩盖〔audit CLEAN flags=[]+wm probe+daily 0-new cutoff 09-24+regime ORANGE shadow breadth 0.77+scorecard 6str/28trader/7port 8.4s+clock CALL-2026-09-24 ORANGE_COOL sleeves=4 activated=0 幂等+lhb 23.6min<30min 节流+heat pre-15:30+futures/repo/options/sinaMF cutoff-covered 零网络+MF rank-throttle 23.6min+astock/rev_osc/alloc/fund_premium 四车道护栏诚实 no-op+ths 同日幂等+AH spawn-throttle 23min+fundamental 9.7h fresh-skip+b_layer 落盘+live.paper OK 6 锚+t35v PASS 09-24 zero-pending+t24p 22/22 drift=0+t24m 0/22 honest NOT-ELIGIBLE+aggr/grid/sysv1 marks@cutoff 幂等+t35e 09-24 6traders+dsc 6 traders+daily_report REPORT-2026-09-28 faces=4 token=1+build_status 432combos+token L2 delta=0 fuse refusals=4/3sigs〕+链后 reconcile 全 14 faces ZERO-DRIFT（crash_fuse 3 源含） | "
    "verify: smoke 25/25×2 + 合并器 selftest 全 PASS〔+4 墓碑腿 12b r389 形态三源复放抑制收敛/12c 再崩胜墓碑/12d 墓碑并集 newer-wins/12e 零墓碑零键〕+ autofill selftest ALL PASS〔+S16h 两腿：清除落墓碑共享+本机车道双写/外机车道复活经门抑制 launch proceeds；既有 S16 族零回归〕+ py_compile 隐含（selftest 全链）+ reconcile 全面零漂移（链前链后双跑）+ CODELY 三十四批 containment PASS 8,965B≤10KB + HANDOVER git diff 1 insertion 0 deletions 外科证 + orders 99/99（S7 双扫） | "
    "next: ①W2B census finalize watch（bm-b ETA ~10:30）→RAM 释放→W2-JUDGE flip（bm-b·judge-prep 已过 2/3 门）→judge 烧批链 watch〔survivors 404 喂判〕②今日 09:15 T-91 s3 first-marks auto-fire（IntradayMarks 09:25 armed·首 bar ~15:30→live.paper enforce+t35 verify 链）③MSG-0621 设计切片 (a) done-flip 单件 push/(b) takeover done-probe=下批候选（本机 autofill 正典域）④crash_fuse 墓碑首实弹 watch（下一码变清除事件=设计首验）⑤council C-01 窗 09-29 12:00/C-02 窗 09-29 ~10:0x（席3 意见已出零重发）⑥T-94/T-96 CEO 48h 呈报钟 09-29 22:45 bmb；next 5x=bm-a r395"
)

with open(RR, "rb") as fh:
    rr = fh.read().decode("utf-8")
rr = rr.rstrip("\r\n") + "\r\n\r\n" + LINE + "\r\n"
with open(RR, "wb") as fh:
    fh.write(rr.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))

with open(ST, "rb") as fh:
    st = json.loads(fh.read().decode("utf-8"))
st["round_no"] = 390
st["last_round_at"] = "2026-09-28 07:5x"
st["current_task"] = ("r390 closed: D-03(2) cleared-tombstone landed (merge_crash_fuse "
                      "tombstone semantics + autofill clear-site tombstone dual-write, "
                      "selftest +4 merger legs / +S16h autofill legs, live reconcile "
                      "zero-drift) + 5x HANDOVER R386-390 line landed; next = W2B "
                      "finalize watch -> W2-JUDGE flip (bm-b) + T-91 s3 09:15 auto-fire")
payload = json.dumps(st, ensure_ascii=False, indent=1)
with open(ST, "wb") as fh:
    fh.write(payload.replace("\n", "\r\n").encode("utf-8"))
print("round report appended; state round_no ->", st["round_no"],
      "orders_ack:", len(json.load(open("fleet/machines/bm-a.json",
                                        encoding="utf-8")).get("orders_ack", [])))
