# -*- coding: utf-8 -*-
"""r464 bm-a closeout: state flip + round report + heartbeat (atomic-ish)."""
import json
import time
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 1. state flip 464 -> 465
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8-sig"))
assert st.get("round_no") == 464, "unexpected round_no %r" % st.get("round_no")
st["round_no"] = 465
st["round"] = 465
st["loop_round"] = 465
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state flipped -> 465")

# 2. round report line
now = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
line = (
    "{ts} | r464 | dept:策略/研究 | WM=py_low_board_clear 绿（板空+bandit 空+无可跑批·合法 idle=W13 手术构建期·red=False healthy）| "
    "W13 runner-build slice-2: surgeon sections 1-10 landed one-pass green "
    "(W13 identity docstring/imports/constants+seeds 20323000 族+tl12 rsqr import faces/"
    "SUMN_SPEC+SUMN_ANCHOR programmatic/kit SUMN_LAYER_TEXT verbatim/grammar sixteen-tuple 282,175,488/"
    "Sobol sumn leg/exclusion 25 源+pads+1/_excluded axis[15]/mask-curve-null SU 链) "
    "-> partial draft py_compile PASS | verify: surgeon rc=0（3 锚修：fifteen-tuple 残文/face 标签换行/段界 banner 归属）+ "
    "draft 接线自验 21/21 OK (_r464bma_w13_draft_verify.py) + smoke 26/26 + orders 122/122 diff-empty + "
    "S6 35 腿 34 绿 1 诚实 rc=3（lhb 源改史守卫：2026-09-28 披露源端重发 42→67 行 netbuy 翻号·本地零写原样上报）+ "
    "dualrun ZERO-DRIFT 44/3 + audit FLAG supply_gap/floor（ready=1<3·W13 GENERATE 泊位待 Slice-B catalog flip 后入池=冻结序合法滞）+ "
    "attrition CLEAN + claw sync + loop pin8 Running + watchdog Ready | "
    "当前活=W13 runner build sections 11-16; 最近实物=results/_r464bma_w13_runner_draft.py 09:2x; "
    "下里程碑=W13 sections 11-15（generate/screen/judge/selftest/residual 读实跑件逐锚）→Slice-B sha16 pin→三命令 identity face→"
    "selftest→formal land→catalog flip+GENERATE 入池 (r465-466, <48h) | "
    "next: extend surgeon 11-15 from SRC lines 1741-4913 实跑锚 → re-run fresh → Slice-B; "
    "supply floor 滞面随 GENERATE 泊位入池自愈 [via bm-a]\n"
).format(ts=now)
with open("round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(line)
print("report appended")

# 3. heartbeat
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8-sig"))
hb["last_seen"] = now
hb["current_task"] = "W13 runner build (surgeon sections 11-16 next)"
hb["verdict"] = "py_low_board_clear legal idle (W13 build window); supply floor breach expected until GENERATE berth lands"
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = now
assert isinstance(hb["heartbeat_epoch_utc"], int)
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written epoch=%d (int verified)" % chk["heartbeat_epoch_utc"])
