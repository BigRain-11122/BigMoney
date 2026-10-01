# -*- coding: utf-8 -*-
import json, time, datetime

now = datetime.datetime.now().astimezone()
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]

# --- state note: append restore face ---
s = json.load(open("state.json", encoding="utf-8"))
assert s["round_no"] == 518
if "W18 evidence" not in s["note"]:
    s["note"] = (s["note"] +
                 " | ADDENDUM-2: W18 evidence file restored -- bm-c r330 surgical rebroadcast (73c253e29) had deleted "
                 "results/perpetual_faces/n1_w18_results.json from origin (stale-tree staging, mirror-face of r516 law); "
                 "byte-restored from f9d74235d (audit.machine=bm-a verified, K=37,520 ledger 404,148); zero scientific pollution "
                 "(W19 consumed W18 values in-pool before deletion); MSG-194x notice to bm-c/bm-a/ALL; origin chain W17->W18->W19 all present.")
for k in ("last_round_at", "last_round_ts", "ts", "updated", "updated_at"):
    s[k] = now_iso
open("state.json", "w", encoding="utf-8", newline="").write(
    json.dumps(s, indent=1, ensure_ascii=False).replace("\n", "\r\n"))

hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = now_iso
hb["current_task"] = ("r518 CLOSED: W19 finalize final (K=39,720, ledger 406,348 chain-repaired) + W18 evidence file restored on origin "
                      "(bm-c r330 rebroadcast deletion, byte-restored, MSG-194x); next: W21=bm-a/W22=bm-b rotation watch; engine queue empty (GM waiver O-1612)")
assert isinstance(hb["heartbeat_epoch_utc"], int)
open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="").write(
    json.dumps(hb, indent=1, ensure_ascii=False).replace("\n", "\r\n"))
json.loads(open("fleet/machines/bm-b.json", encoding="utf-8").read())

# --- report line 3 (restore face) ---
line = (
 "2026-10-01T" + now.strftime("%H:%M:%S") + "+08:00 | r518 bm-b 补章2 | dept:研究/工程 | "
 "W18 证据件恢复：bm-c r330 外科 rebroadcast（73c253e29）把 bm-a r532 已推 origin 的 results/perpetual_faces/n1_w18_results.json"
 "（W18 finalize 合并件）静默删除（diff 7075e3dce..73c253e29 唯一 D 面·stale 本机整树 staging=r516 外科坑的镜像面·W18 分片 12/12 未伤）"
 "→本机按 r513 恢复先例字节级 checkout 自 f9d74235d（blob sha16=1ebe0a0174f978fa·**audit.machine=bm-a 归属验 PASS**"
 "〔他机产品恢复非劫持·r525 律〕·K=37,520·ledger 404,148 链节复完）+commit 推回 origin（54a8e82e8）"
 "+MSG-194x 通知（bm-c 主收执行面提醒：外科 rebroadcast 禁 stale 整树直写·bm-a 次收产品归位确认）；"
 "**零科学污染定谳**——本机 W19 finalize 在删除发生前已消费 W18 值入池（pre-W19=404,148 逐位恒等），"
 "删除只伤证据在场面非数据面；恢复后 origin 链面 W17 401,948→W18 404,148→W19 406,348 三链节全在场。 | "
 "验证：git show f9d74235d/7075e3dce 同 blob 五面核验+恢复件 json.loads+ledger_head derive；"
 "收尾送达自证=push 54a8e82e8+fetch+ls-tree 双件在场+unpushed=0。 | "
 "本地未达 origin commit 数=0（收尾 push+fetch 自证）。 | [via bm-b]\r\n"
)
with open("logs/iteration-loop/round_reports.md", "ab") as f:
    f.write(line.encode("utf-8"))
print("final bookkeeping done at", now_iso)
