"""R318 bm-b closeout: state round bump + round report line + heartbeat refresh."""
import json
import time
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

# --- state.json (bm-b uses the shared iteration-loop state file) ---
sp = "logs/iteration-loop/state.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 318
st["last_round_ts"] = ts
json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# --- round report line (bm-b file) ---
rp = "logs/iteration-loop/round_reports.md"
line = (
    f"- {ts} | r318 | 水位=绿（red=false·py_low_board_clear 合法闲=板全闭环 18/18+bandit 0）"
    f"S0 rebase 2+2 分叉（autostash UU 两撞均 r317 stage-union 正典解·push 落 653568d4→f90df66e）|"
    f"S0.5 令 96/96 零未回执（无新令）+集团 decisions 台账无新行（..\\..\\docs 不存在·firm\\DECISIONS.md 尾=09-26 无新）|"
    f"S1 smoke 25/25|"
    f"**T-93 收件面 COMPLETE**（checkout 30 件+R90 restore+探针 .probe-bak 防毒+同构 staging 树双 manifest **VERIFY PASS 30/30·80,984,350B·逐件 sha256 全等**；两通道发现修诚=CRLF 通道归一 30/30 LF→CRLF 恢复断言 + Windows 大小写碰撞 checkout 静默跳过→探针改名先于 checkout+listdir 精确比对；票 done 翻面 result_ref=双侧 manifest）|"
    f"**T-89 收割 finalize PASS**（G-ANCHOR 22/22+G-CENSUS legacy 22×1256=27,632/deep 22×1506=33,132 全过·trials 63,526·ledger 269,975；池面 legacy 0.5134/deep 0.4122 双低于 0.70 线·**进攻军候选 0/22 两轴**·角色 bear/chop 双型；MARKET_STAGE_TABLE 44 行落表+变更日志）|"
    f"**T-90 收割 verdict 落地**（全门过 G-V3/6 锚/G-REPRO 12/12 bit-equal；**chain_win=False·j_target_pass=False**（12 格全败 beat_gt_b·最差 legacy-x2-24m A1 0.0228 vs B 0.5758·dd -0.3194）·J-L 半梯 PASS 双面·四环定位=ring1 温度分歧 73% 无救援/ring2 路由全段负（A1−D 熊 -0.0613/牛 -0.0528/震 -0.0795）/ring3 摩擦 45.6 次切换 -0.0665pp（A1' 零费反事实仍负）/ring4 席位 0 在册·GREEN 起点略优仍负）|"
    f"MSG-1105 收讫回执（MF_IC_P1 立场=选 c 并行：EM 面 parked 诚实等+sina 深面板 N=250 落成后起草 sina-construct 新 prereg·已回 MSG-1210）|"
    f"S6 29 lanes rc=0（无新 bar 周日·collectors 全诚实 no-op·t35_export 再生 09-24 面·daily_report 4 面）|"
    f"下轮指针：①T-89 slice-3 进攻军供给提速 memo（0/22 候选+T-90 ring4 证据已硬化·提案面归 GM）②T-90 deliverable-4 月度 chain-health 四件套接线（verdict 面已存在）③sina 深面板 complete 后 sina-construct prereg 起草（开工门=N≥250）④r312bm-a-pool_flip 常设动作解除（18/18 全 flipped）\n")
with open(rp, "a", encoding="utf-8") as fh:
    fh.write(line)

# --- heartbeat (bm-b single-writer file) ---
hp = "fleet/machines/bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = ts
h["clock_read"] = ts
h["heartbeat_epoch_utc"] = epoch
h["round_no"] = 318
h["current_task"] = ("r318: T-93 receive COMPLETE + T-89/T-90 harvest finalize BOTH landed; "
                      "next= T-89 slice-3 supply memo + T-90 chain-health wiring + "
                      "sina-construct prereg after deep panel complete")
h["verdict"] = ("green; r318: watermark green (py_low_board_clear legit, board closed); "
                "T-93 30/30 dual-manifest VERIFY PASS 80,984,350B (CRLF channel-normalization "
                "reversed 30/30 sha256-asserted + Windows case-collision lesson canonized); "
                "T-89 finalize PASS (G-CENSUS 22x1256+22x1506, pooled 0.5134/0.4122, "
                "0/22 attack candidates, MARKET_STAGE_TABLE refreshed); "
                "T-90 verdict chain_win=False j_target_pass=False (J-L ladder pass; "
                "four-ring: routing negative all regimes + friction +0.73 temp disagreement + 0 seats); "
                "S0.5 96/96 zero-unacked; S6 29 lanes rc=0; smoke 25/25")
json.dump(h, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# --- self-assertions (smoke F7 discipline) ---
chk = json.loads(open(hp, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be ISO with T separator"
print(f"state round_no=318 | report line appended | heartbeat epoch={epoch} "
      f"clock={ts} | self-assert PASS")
