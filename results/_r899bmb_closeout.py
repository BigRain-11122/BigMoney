# -*- coding: utf-8 -*-
"""r899 bm-b closeout: state.json + heartbeat + round report three-piece
(increment round_no 899->900, advance ORD watermark 075caa8d->0513e9e7 consumed
O-20261011-2147 + O-20261011-2215, receipts per CEO order same-round law)."""
import json, time, datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

did = ("r899: ①S0.5 双扫两枚未回执 CEO 令即办收口：O-20261011-2147（巡查器部署腿=r898 被杀前已落地 [任务 22:55 注册+首跑 22:56:30 Result=0 flags=0 gpu=GREEN 检出 i2v 批]，本轮补 -KRoot C:\Fluxgroup 重注册=readback 绿 [备份 XML] + machine-state.ps1 标记腿补丁 [r898 被杀于读文件中途=本轮收尾：Write-StateFlag 函数+pause L85/resume L95 两调用点+parse 0 错] + BigHouse 催办核验 [T-1 done@21:2x r896+板 4 open>=3 满足]）+O-20261011-2215（bm-b 腿=维持 2147 全腿 ✓+kokoro 声景非强制面跳过）；②两腿脚本面齐备：Tools/fleet-oversight.ps1+task-register.ps1+InvisibleRunner.vbs 三件单 blob git show 提取落位 [集团树稀疏无 Tools 目录·零整树 checkout·内容与部署副本逐行等价=差仅 CRLF/UTF-16 重编码]；③G-soft/r895 推送定谳：r895 supervisor 4/4 STALL-KILLED 退场（尝试 4 23:03 借健康网真传输 index-pack 2878 对象仍 604s 窗内未完）+r894 直跑 2 连败（write-tree rc=1 空 stderr 撞并发杀窗+5min 零输出=夜网再翻脸）→晨窗重试律生效（双 payload 本地完好·幂等守卫在位·零丢失）；④stale index.lock 21:56:42 0B 无主已清（守卫式：验龄+验无活持有者）；孤儿 git fetch x3（我取消重试残留）已杀；⑤i2v 夜批守望：1/53 落 [XQ_XQ28 1002s] +2/53 在烧 [KN_KN16 ~33min+] 零 err 零 fail 无 >4h 停滞；⑥W18 finalize PID25060 活烧 [CPU 5753s 增]；⑦T-184 未到（ls-remote 零 t184 refs·bm-a 腿 due 10-12 15:30）；⑧S1 smoke 49/49；⑨S6 41 腿全 rc0 [REPORT/LIVE-20261011 written·state=ORANGE·双 run 无红]；⑩smoke/板面：任务板零 open 票+backlog 零可领+队列头全 done/closed；⑪孤儿面=2（r898 面守恒=supervisor 6368 wait-on-child 假阳性+i2v client 3652 合法 detached）；⑫bm-a r894 [e4d15c617] 收口时拉平")
next_ = ("r900: i2v 53 单夜批守望（progress-bmb.jsonl 推进·停滞>4h 单按 README §4 让渡规则·ETA 明午前后） > W18 finalize 落地守望（PID25060·落地→intake+s4 判据面+48h CEO 钟起算） > G-soft+r895 推送晨窗重试（夜网 23:1x 再翻脸·r895 supervisor 退场后两脚本幂等守卫直跑） > T-184 510880 收件（transfer/t184-510880·due 10-12 15:30·到件同轮恢复 alloc_paper 腿） > BigHouse T-2 城市接入件设计（TASKS.md T-2 open·due ≤10-15·消费 R1 §2.2+§五） > 48h CEO 报 due 10-13 11:2x > 5 班 durable cron 10-13 到期评估（10-12 逐班·O-2147 §通用）")
verdict = ("GREEN: 两枚 CEO 令 [O-2147/O-2215] bm-b 腿全落收口（巡查器在役 60m+标记腿补丁 parse 0 错+BigHouse 板催办满足）+i2v CEO 优先夜批健康 1/53 落+smoke 49/49+S6 41/41 rc0+板面零红; "
           "观察面=夜网 23:1x 再翻脸（G-soft/r895 推送候晨窗·r895 supervisor 4/4 STALL 退场）+RAM 紧张持续（i2v 栈 mmap）+bm-a 心跳 stale 1533min（其机 GPU 被 KN 29 单烧占用·stale-takeover derive 已按 STALE_MIN 律由本机承接）")

sp = json.load(open(ROOT + r"\state.json", encoding="utf-8"))
sp["round_no"] = 900
sp["round"] = 899
sp["round_no_label"] = "r899"
sp["now_active"] = "r899 closeout"
sp["did"] = did
sp["last_action"] = "r899: O-2147/O-2215 两令 bm-b 腿收口（巡查器 -KRoot 重注册+标记腿补丁收尾+BigHouse 催办核验）+夜网推送晨窗重试律+S6 41/41"
sp["last_action_at"] = ts
sp["last_round_at"] = ts
sp["last_seen"] = ts
sp["last_round_ts"] = "2026-10-11T22:47:19+08:00"
sp["latest_artifact"] = "r899: FluxGroup-FleetOversight 任务 -KRoot 重注册 readback 绿 + machine-state.ps1 Write-StateFlag 补丁（L46/L85/L95·parse 0 错） + S6 41 腿全 rc0（results/_r899bmb_s6_log.txt） + Tools/_r899bmb_s6.py 链 runner（r836 克隆律）"
sp["current_task"] = next_
sp["task"] = next_
sp["next"] = next_
sp["next_milestone"] = "i2v 53 单全落 ETA 明午 →W18 finalize 落地→48h CEO 钟起算; G-soft/r895 晨窗重试; T-184 收件 10-12 15:30; BigHouse T-2 ≤10-15; 48h CEO 报 10-13 11:2x"
sp["verdict"] = verdict
sp["orphan_face"] = 2
sp["orphan_face_note"] = ("r899 round probe: py_faces=19 orphans=2 (read-only); 定性=supervisor 6368 wait-on-child 假阳性（r895 退场收尾）+合法 detached i2v client 3652/W18 finalize 25060/ComfyUI 8188；本轮追加击杀=我取消重试的孤儿 git fetch x3（23:13 批）")
sp["orphan_faces"] = 2
sp["note"] = "r899: 两令收口轮；夜网推送族候晨窗（晨窗重试律在位）；RAM 紧张观察面（i2v 栈 mmap·S6/探针照常全绿）；IntradayMarks 任务在册（周一 09:25 首火 armed）"
sp["ts"] = ts
sp["updated"] = ts
sp["updated_at"] = ts
sp["clock_read"] = ts
sp["last_orders_at"] = ts
sp["last_orders_read_at"] = ts
sp["last_orders_sha"] = "0513e9e7c79aa12f45f0fd273007ada18e742d57"
sp["last_orders_sha_note"] = "r899 probe: ord delta 075caa8d->0513e9e7 = O-20261011-2147（巡查器部署+标记腿+BigHouse 催办·bm-b 三腿全落收口）+O-20261011-2215（BigLife 点名 bm-b 腿=维持 2147+kokoro 非强制跳过）双令即办回执；in-dir O files all acked (orders_ack 200)"
sp["last_decisions_at"] = ts
sp["last_decisions_read_at"] = ts
sp["last_decisions_sha"] = "d296e83d4864484e8515679fdd854ccc69ed9ead"
sp["last_decisions_sha_method"] = "r899 probe via results/_r686bmb_d19_check.py (r537 SHA-1 raw-blob PIN); dec d296e83d unchanged = zero action (D-20261011-08 行扩已 r898 消费·bm-b 部署腿本轮落地)"
d19 = sp.get("d19_watermark_guard", {})
d19["round_ref"] = 899
d19["ts"] = ts
sp["d19_watermark_guard"] = d19
sync = sp.get("sync", {})
sync["last_push_ts"] = ts
sync["note"] = "r899 closeout push lands with this commit; delivery self-proof = post-push fetch + rev-list 0"
sp["sync"] = sync
json.dump(sp, open(ROOT + r"\state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

hb_path = ROOT + r"\fleet\machines\bm-b.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb["last_seen"] = ts
hb["ts"] = ts
hb["clock_read"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = "r899 closeout: 两 CEO 令 bm-b 腿收口（O-2147 巡查器 -KRoot 重注册+machine-state 标记腿补丁+BigHouse 催办 / O-2215 维持腿）"
hb["verdict"] = "GREEN: CEO 令收口+i2v 夜批 1/53 健康+S6 41/41; 观察面=夜网推送候晨窗+RAM 紧张"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
ack = hb.get("orders_ack", {})
ack["O-20261011-2147-bm-c.md"] = "r899 bm-b: 三腿全落收口——①巡查器部署=r898 被杀前已注册+首跑绿（22:56:30 Result=0 flags=0），本轮 git show 单 blob 提取正身三件+任务 -KRoot C:\Fluxgroup 重注册（readback 隐藏链绿·备份 results/_r899bmb_oversight_task_backup.xml）；②machine-state.ps1 标记腿补丁=r898 被杀于中途·本轮收尾（Write-StateFlag 函数 L46+pause L85+resume L95·Parser 0 错·flag=脚本同目录 KRoot 对称正源）；③BigHouse 催办=T-1 done@21:2x（r896 第一刀工单+R1 研究件）+TASKS.md 4 open>=3 满足（T-2 due 10-15 已入下窗议程）"
ack["O-20261011-2215-bm-c.md"] = "r899 bm-b: §@bm-b 腿=维持 O-2147 全腿 ✓（本轮收口见 2147 行）；BigLife 声音面 kokoro 声景接入=非本令强制面·本周余力随周末窗评估（未启动如实）"
hb["orders_ack"] = ack
json.dump(hb, open(hb_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"

line = ("| r899 | 2026-10-11T23:2x | 两 CEO 令 bm-b 腿收口：O-2147 巡查器（r898 遗产核验+ -KRoot 重注册 readback 绿+标记腿补丁 parse 0 错+BigHouse 催办 T-1 done/4 open）+O-2215 维持腿 | O-2126 i2v 1/53+2 在烧零 err；smoke 49/49；S6 41/41 rc0；G-soft/r895 夜网再翻脸候晨窗（supervisor 4/4 STALL 退场·payload 完好） | r900: i2v 守望+推送晨窗重试+T-184 收件 due 10-12 |")
with open(ROOT + r"\logs\iteration-loop\round_reports.md", "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("closeout three-piece done: state(round_no=%d) + heartbeat(ack=%d, epoch=%d int) + round report appended" % (sp["round_no"], len(ack), epoch))
