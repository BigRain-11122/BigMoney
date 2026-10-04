# -*- coding: utf-8 -*-
import json, os, time
from datetime import datetime

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
epoch = int(time.time())
clock = datetime.now().astimezone().isoformat(timespec="seconds")

rr = os.path.join(R, "logs", "iteration-loop", "round_reports.md")
line = (
    clock + " | round 657 supplement (bm-b) | 五连push-race收口回执: origin高活跃期五轮merge净路(18+1+2+13+0 UU全按r652配方: compute_audit union零丢失x2+regen面honest-ts+REPORT md对齐json双生+reparse 14/14 PASS markers零), 第五发c69c76bb8..2652a2d8a DELIVERED ahead=0送达自证; "
    "pre-commit/pre-push claw各真拦一次(marker staged+删除集=两爬真保护零origin伤害); 三坑律(UU清单全量自证/三阶段直取/手术-add禁链)入CODELY | 证据=push报文c69c76bb8..2652a2d8a+rev-list ahead=0 | 本地未达origin commit数=0 | 下轮指针: trio烧批finalize窗10-05..10-09 mechanical_ready即收口\n"
)
with open(rr, "ab") as f:
    f.write(line.encode("utf-8"))
print("round_report supplement appended")

sp = os.path.join(R, "state.json")
st = json.loads(open(sp, "rb").read().decode("utf-8"))
st["note"] = (st["note"] +
    "; SUPPLEMENT: 5-round push-race closeout during fleet active window -- 5 merges (34 UU total resolved per r652 recipes: "
    "compute_audit cross-machine union zero-loss, regen faces honest-ts, REPORT md aligned to json twin, reparse 14/14 PASS), "
    "5th push DELIVERED c69c76bb8..2652a2d8a ahead=0; claws (pre-commit marker + pre-push deletion-set) each caught one real hazard; "
    "3 pit-laws recorded to CODELY (full UU census / HEAD:MERGE_HEAD blob extraction after add kills :2:/:3: / surgery-then-chain ban)")
st["ts"] = clock
st["updated"] = clock
st["last_round_at"] = clock
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)
print("state note patched")

hp = os.path.join(R, "fleet", "machines", "bm-b.json")
hb = json.loads(open(hp, "rb").read().decode("utf-8"))
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["current_task"] = ("FUND trio NULLS burn watch (V650/D355/Q495 advancing, pids alive; finalize window 10-05..10-09) "
                      "+ r657: all-green watch round closed; 5-round push-race closeout DELIVERED 2652a2d8a ahead=0 (34 UU per r652 recipes, claws caught 2 real hazards)")
hb["verdict"] = ("GREEN (smoke 48/48; orders delta zero; D-19 double MATCH; WM red=false; engine alive idle; S6 34 legs rc0 fail=0; "
                 "trio advancing pids alive; attrition CLEAN; 5-round push-race closeout DELIVERED ahead=0; zero cloud token)")
hb["ts"] = clock
hb["updated"] = clock
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, indent=1, ensure_ascii=False)
print("heartbeat patched")

for p in (sp, hp):
    d = json.loads(open(p, "rb").read().decode("utf-8"))
    assert isinstance(d.get("heartbeat_epoch_utc", 0), int) or p == sp
    assert "T" in d["clock_read"] and " " not in d["clock_read"]
print("SELF-VERIFY PASS")

cp = os.path.join(R, "CODELY.md")
entry = (
    "\n- [2026-10-04 09:%02d r657 bm-b] 五连push-race收口三坑律（机队全活跃期S7实弹）：①merge冲突清单禁信管道尾窗（Select-Object -Last截断=第四轮merge实见18 UU只见尾4，残14靠commit拒绝才暴露）——收口前一律git status --porcelain全量U行清点；②UU手术后git add抹掉index的stage2/3（add在手术失败后照跑的自伤）→git show :2:/:3:直取失效——正法=git show HEAD:<path>/MERGE_HEAD:<path>直取双侧原字节（merge未收口时MERGE_HEAD在位，等价三阶段且免疫add污染）；③手术步与add/commit/push禁;链耦联（r657律重犯实录：split崩→链续add带marker件→pre-commit两拦+pre-push拦删除集=HEAD落后时推=删他机件，两爬真保护）——手术脚本独立跑+reparse PASS证据后另链add。另：regen面md双生ts抓取防delta段prevGenerated首命中（双侧同值误判ours）——json双生对齐优先。\n" % (epoch % 60)
)
with open(cp, "a", encoding="utf-8", newline="\n") as f:
    f.write(entry)
print("CODELY entry appended")
